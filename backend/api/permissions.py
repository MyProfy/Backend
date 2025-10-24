from rest_framework.permissions import BasePermission

class IsOwner(BasePermission):
    """
    Custom permission for Owner Order
    """
    def has_object_permission(self, request, view, obj):
        return obj.client_id == request.user.id