from fastapi import Request, Depends, HTTPException, status

from src.entity.models import Role, User
from src.services.auth import auth_service


class RoleAccess:
    """
    A FastAPI dependency class for checking user roles.

    This class is used as a dependency to restrict access to certain routes based on user roles.

    :param: allowed_roles: A list of roles that have permission to access the route.
    :type: allowed_roles: list[Role]
    """
    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, user: User = Depends(auth_service.get_current_user)):
        """
        Check if the current user has the required role to access the route.

        :param request: FastAPI Request object.
        :type request: Request
        :param user: Current user obtained from the authentication service.
        :type user: User
        :raises HTTPException: Raises a 403 Forbidden exception if the user does not have the required role.
        """
        print(user.role, self.allowed_roles)
        if user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="FORBIDDEN")
