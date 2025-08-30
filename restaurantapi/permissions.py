from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrSuperUser(BasePermission):
    """
    Superuser can do anything.
    Normal users can only act on their own reservations.
    """

    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True
        return obj.user == request.user

class IsSuperUserOrReadOnly(BasePermission):
    """
    Read-only requests are allowed for anyone.
    POST, PUT, PATCH, DELETE require superuser.
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:  # GET, HEAD, OPTIONS
            return True
        return request.user and request.user.is_authenticated and request.user.is_superuser