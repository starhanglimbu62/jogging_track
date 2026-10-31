from rest_framework import permissions


def role_for(user):
    profile = getattr(user, 'profile', None)
    return profile.role if profile else None


class UserAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and role_for(request.user) in ('MANAGER', 'ADMIN')

    def has_object_permission(self, request, view, obj):
        return role_for(request.user) in ('MANAGER', 'ADMIN')


class EntryAccessPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        role = role_for(request.user)
        return role == 'ADMIN' or obj.user_id == request.user.id
