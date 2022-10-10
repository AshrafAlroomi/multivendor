from rest_framework import permissions


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile_user.status == 'customer':
            return True
        else:
            return False


class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile_user.status == 'vendor':
            return True
        else:
            return False


class IsAccepted(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.status != 'PENDING':
            return False
        else:
            return True
