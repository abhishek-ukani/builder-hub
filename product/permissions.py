from rest_framework import permissions

class IsAdminStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method is permissions.SAFE_METHODS:
            return True
        
        return bool(request.user and (request.user.is_staff or request.user.is_superuser))