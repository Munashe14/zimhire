from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import decode_token
from app.models.user import User, UserRole

security = HTTPBearer()


def _normalize_role_name(role_value) -> str:
    """Normalize canonical and legacy role names to their canonical value."""
    if role_value is None:
        return ""
    if isinstance(role_value, UserRole):
        role_value = role_value.value
    if not isinstance(role_value, str):
        return ""

    normalized = role_value.strip().lower()
    aliases = {
        "admin": "clerk",
        "booking_clerk": "clerk",
        "depot_supervisor": "supervisor",
        "operations_manager": "manager",
    }
    return aliases.get(normalized, normalized)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get the current authenticated user from the JWT token."""
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_type = payload.get("type")
    if token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: Optional[int] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    
    return user


def require_roles(*allowed_roles):
    """Dependency factory to require specific user roles.

    Accepts canonical role names and older alias names while preserving the
    canonical values as the source of truth.
    """
    allowed_values = {_normalize_role_name(role) for role in allowed_roles}

    def role_checker(current_user: User = Depends(get_current_user)) -> User:
        user_role_values = {
            _normalize_role_name(current_user.role),
            _normalize_role_name(current_user.role.value),
            _normalize_role_name(current_user.role.name),
        }
        if user_role_values.intersection(allowed_values):
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions",
        )

    return role_checker


# Canonical role dependencies
require_clerk = require_roles(UserRole.CLERK, UserRole.MANAGER, UserRole.SUPERVISOR)
require_supervisor = require_roles(UserRole.SUPERVISOR, UserRole.MANAGER)
require_manager = require_roles(UserRole.MANAGER)
require_client = require_roles(UserRole.CLIENT)
require_staff = require_roles(UserRole.CLERK, UserRole.SUPERVISOR, UserRole.MANAGER)

# Backward-compatible aliases for existing endpoints and modules.
require_admin = require_roles(UserRole.MANAGER)
require_booking_clerk = require_roles(UserRole.CLERK, UserRole.MANAGER)
require_depot_supervisor = require_roles(UserRole.SUPERVISOR, UserRole.MANAGER)
require_operations_manager = require_roles(UserRole.MANAGER)
