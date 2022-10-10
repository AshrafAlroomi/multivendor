from rest_framework import permissions


class IsVendor(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile_user.status == 'vendor':
            return True
        else:
            return False


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.profile_user.status == 'customer':
            return True
        else:
            return False


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if obj.product_vendor == request.user.profile_user:
            return True
        else:
            return False
