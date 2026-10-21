
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
