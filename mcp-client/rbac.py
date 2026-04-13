"""
RBAC checker — fetches user permissions from the admin panel API
and enforces access control before any MCP tool is called.
"""

import httpx
from models import UserPermissions
from exceptions import UserNotFoundError, UserInactiveError, PermissionDeniedError, MCPConnectionError


class RBACClient:
    def __init__(self, admin_panel_url: str):
        self.admin_panel_url = admin_panel_url.rstrip("/")

    async def get_permissions(self, telegram_id: str) -> UserPermissions:
        """Fetch user + permissions from admin panel."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                res = await client.get(f"{self.admin_panel_url}/api/users")
                res.raise_for_status()
                users = res.json()
        except httpx.RequestError as e:
            raise MCPConnectionError(f"Cannot reach admin panel: {e}")

        user = next(
            (u for u in users if u.get("telegramId") == str(telegram_id)),
            None,
        )

        if not user:
            return UserPermissions(
                allowed=False,
                reason="You are not registered. Contact an admin.",
            )

        if not user.get("isActive"):
            return UserPermissions(
                allowed=False,
                reason="Your account is inactive. Contact an admin.",
                user=user,
            )

        permissions = [
            rp["permission"]["name"]
            for rp in user["role"]["rolePermissions"]
        ]

        return UserPermissions(allowed=True, permissions=permissions, user=user)

    async def enforce(self, telegram_id: str, tool: str) -> UserPermissions:
        """
        Raise an exception if user cannot use the tool.
        Returns UserPermissions on success.
        """
        perms = await self.get_permissions(telegram_id)

        if not perms.allowed:
            if perms.user is None:
                raise UserNotFoundError(perms.reason)
            raise UserInactiveError(perms.reason)

        if tool not in perms.permissions:
            raise PermissionDeniedError(
                f"Your role '{perms.user['role']['name']}' does not have permission to use `{tool}`."
            )

        return perms
