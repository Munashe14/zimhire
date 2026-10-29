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


def test_legacy_uppercase_role_strings_are_accepted():
    assert UserRole("ADMIN") is UserRole.CLERK
    assert UserRole("BOOKING_CLERK") is UserRole.CLERK
    assert UserRole("DEPOT_SUPERVISOR") is UserRole.SUPERVISOR
    assert UserRole("OPERATIONS_MANAGER") is UserRole.MANAGER


def test_require_roles_dependency_factory_exists():
    assert callable(deps.require_roles)

    class DummyUser:
        role = UserRole.MANAGER

    dummy_user = DummyUser()
    dependency = deps.require_roles(UserRole.MANAGER)
    assert dependency(dummy_user) is dummy_user

    dependency = deps.require_roles("manager")
    assert dependency(dummy_user) is dummy_user

    class ClerkUser:
        role = UserRole.CLERK

    clerk_user = ClerkUser()
    dependency = deps.require_roles("admin")
    assert dependency(clerk_user) is clerk_user

    dependency = deps.require_roles("booking_clerk")
    assert dependency(clerk_user) is clerk_user
