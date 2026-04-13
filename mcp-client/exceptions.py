class MCPError(Exception):
    """Base MCP client error."""

class MCPConnectionError(MCPError):
    """Cannot reach MCP server."""

class MCPToolError(MCPError):
    """Tool execution failed on server."""

class RBACError(MCPError):
    """User not allowed to use the tool."""

class UserNotFoundError(RBACError):
    """Telegram user not registered in admin panel."""

class UserInactiveError(RBACError):
    """User account is inactive."""

class PermissionDeniedError(RBACError):
    """User role doesn't have this permission."""
