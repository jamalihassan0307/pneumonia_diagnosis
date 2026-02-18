"""
Custom permissions for Pneumonia Diagnosis System
"""

from rest_framework import permissions


class IsAuthenticated(permissions.BasePermission):
    """
    Allow access only to authenticated users
    """
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


class IsOwned(permissions.BasePermission):
    """
    Allow access only if user owns the object
    """
    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
