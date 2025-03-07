from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Custom permission to allow:
    - Any user to GET data.
    - Authenticated users to POST.
    - Only the item creator can PUT.
    - Only the creator or admin can DELETE.
    """

    def has_permission(self, request, view):
        # Allow GET requests for everyone
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow POST, PUT, DELETE only for authenticated users
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Allow GET for all users
        if request.method in permissions.SAFE_METHODS:
            return True
        # Allow PUT only for the creator of the object
        if request.method == 'PUT' and obj.created_by == request.user:
            return True
        # Allow DELETE only for creator or admin
        if request.method == 'DELETE' and (obj.created_by == request.user or request.user.is_superuser):
            return True
        return False
    

class CustomPermissions(permissions.BasePermission):

    def has_permission(self, request, view):
        """Global permission check for the API view."""
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET, OPTIONS, HEAD for all authenticated users
        return request.user.is_authenticated  # Allow POST for authenticated users

    def has_object_permission(self, request, view, obj):
        """Object-level permission check."""
        if request.method in permissions.SAFE_METHODS:
            return True  # Allow GET, OPTIONS, HEAD for all authenticated users

        # Custom logic to determine if user is the "owner" (even if no owner field exists)
        user_is_creator = self.is_user_creator(obj, request.user)

        # Allow PUT, PATCH, DELETE only if user is the creator or an admin/superuser
        if request.method in ['PUT', 'PATCH', 'DELETE']:
            return request.user.is_superuser or request.user.is_staff or user_is_creator

        return False  # Deny everything else

    def is_user_creator(self, obj, user):
        """
        Custom logic to check if the requesting user created the object.
        - If the model has a 'created_by' or similar field, check against it.
        - If not, deny ownership.
        """
        # Possible creator fields to check dynamically
        possible_creator_fields = ['created_by', 'author', 'user', 'owner']

        for field in possible_creator_fields:
            if hasattr(obj, field):  # Check if the field exists in the model
                return getattr(obj, field) == user  # Compare field value with request.user
        
        return False  # If no creator field exists, deny ownership check

