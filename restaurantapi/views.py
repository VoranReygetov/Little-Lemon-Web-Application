from rest_framework import generics, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from restaurant.models import Menu, Booking
from .serializers import MenuSerializer, BookingSerializer
from .permissions import IsOwnerOrSuperUser, IsSuperUserOrReadOnly
from rest_framework.exceptions import ValidationError


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
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrSuperUser]

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser:
            return Booking.objects.all()
        return Booking.objects.filter(user=user)

    def perform_create(self, serializer):
        """
        If the user already has a booking on this date:
            - Update the existing booking with new data
        Otherwise:
            - Create a new booking
        """
        reservation_date = serializer.validated_data['reservation_date']
        reservation_slot = serializer.validated_data['reservation_slot']
        user = self.request.user

        # Try to get existing booking for this user and date
        booking, created = Booking.objects.get_or_create(
            user=user,
            reservation_date=reservation_date,
            defaults={
                'first_name': serializer.validated_data['first_name'],
                'reservation_slot': reservation_slot,
            }
        )

        if not created:
            # Update existing booking
            booking.first_name = serializer.validated_data['first_name']
            booking.reservation_slot = reservation_slot
            booking.save()

        # Attach the instance to the serializer so DRF knows what was saved
        serializer.instance = booking

