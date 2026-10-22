
from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAnalystOrAdmin(BasePermission):
    """
    Authenticated users may read security data.
    Staff and superusers may create events and update alerts.
    """

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        if request.method in SAFE_METHODS:
            return True

        return user.is_staff or user.is_superuser

class IsAdminUserOnly(BasePermission):
    """
    Only staff users and superusers may access audit logs.
    """

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_staff or user.is_superuser)
        )
