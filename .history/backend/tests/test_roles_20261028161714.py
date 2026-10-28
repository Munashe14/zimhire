from app.models.user import UserRole
from app.core import deps


def test_canonical_roles_match_required_names():
    assert UserRole.CLERK.value == "clerk"
    assert UserRole.SUPERVISOR.value == "supervisor"
    assert UserRole.MANAGER.value == "manager"
    assert UserRole.CLIENT.value == "client"


def test_legacy_role_aliases_remain_compatible():
    assert UserRole.ADMIN == UserRole.CLERK
    assert UserRole.BOOKING_CLERK == UserRole.CLERK
    assert UserRole.DEPOT_SUPERVISOR == UserRole.SUPERVISOR
    assert UserRole.OPERATIONS_MANAGER == UserRole.MANAGER


def test_require_roles_dependency_factory_exists():
    assert callable(deps.require_roles)
    assert deps.require_roles(UserRole.MANAGER)
