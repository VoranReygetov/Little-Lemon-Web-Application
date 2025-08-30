from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from restaurant.models import Menu, Booking
from .serializers import MenuSerializer, BookingSerializer
from .permissions import IsOwnerOrSuperUser, IsSuperUserOrReadOnly


# --- Menus ---
class MenuViewSet(ModelViewSet):
    """
    Menu endpoint:
    - GET: anyone
    - POST/PUT/DELETE: superuser only
    """
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsSuperUserOrReadOnly]


# --- Reservations ---
class BookingViewSet(ModelViewSet):
    """
    Handles reservations.
    - list(): superuser -> all reservations, user -> only their reservations
    - create(): authenticated user makes a reservation
    - destroy(): superuser can delete any, user only their own
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)   # only own reservations

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
