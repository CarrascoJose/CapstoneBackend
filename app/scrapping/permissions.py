from rest_framework import permissions

class CheckIfAnonymousUser(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if obj.user is None:
            return True
        return request.user.is_authenticated
