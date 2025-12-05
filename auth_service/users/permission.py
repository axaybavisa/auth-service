from rest_framework.permissions import BasePermission

# Generic RBAC permission
class RolePermission(BasePermission):
    allowed_roles = []

    def has_permission(self, request, view):
        user = request.user

        if not user or not user.is_authenticated:
            return False

        roles = getattr(view, "allowed_role", self.allowed_roles)
        
        return user.role in roles


# Role-Specific permission
class IsAdmin(RolePermission):
    allowed_roles = ["Admin"]

class IsManager(RolePermission):
    allowed_roles = ["Manager"]

class IsTechnician(RolePermission):
    allowed_roles = ["Technician"]

class IsCustomer(RolePermission):
    allowed_roles = ["Customer"]

class IsHR(RolePermission):
    allowed_roles = ["HR"]        

