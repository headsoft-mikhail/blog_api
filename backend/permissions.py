from rest_framework import permissions
from backend.models import User, Post, UserSubscription, NotViewedPost


class IsAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsNotAuthenticated(permissions.BasePermission):
    def has_permission(self, request, view):
        return not request.user.is_authenticated


class IsActive(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return request.user.is_active
        else:
            return False


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if type(obj) is User:
            return request.user.id == obj.id
        if (type(obj) is Post) or (type(obj) is UserSubscription):
            return request.user.id == obj.owner.id
        if type(obj) is NotViewedPost:
            return request.user.id == obj.user.id
        if 'owner' in dir(obj):
            return request.user.id == obj.owner.id
        else:
            return False

