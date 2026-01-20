from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsSellerOrReadOnly(BasePermission):
    """Allows read-only access to everyone; only the item's seller can modify it."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        seller = getattr(obj, "seller", None)
        return bool(request.user and request.user.is_authenticated and seller == request.user)
