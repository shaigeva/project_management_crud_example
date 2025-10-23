"""Bootstrap initial system data.

This module provides functionality to create the initial Super Admin user
and other system bootstrap operations.
"""

import sys

from project_management_crud_example.dal.sqlite.database import Database
from project_management_crud_example.dal.sqlite.repository import Repository
from project_management_crud_example.domain_models import UserCreateCommand, UserData, UserRole
from project_management_crud_example.utils.password import generate_password


def bootstrap_super_admin(db: Database) -> tuple[bool, str | None]:
    """Create initial Super Admin user if none exists.

    Args:
        db: Database instance to use for operations

    Returns:
        Tuple of (created: bool, password: str | None)
        - created: True if Super Admin was created, False if already exists
        - password: Generated password if created, None otherwise

    Note: This function is idempotent - it will not create duplicate Super Admins.
    """
    # Import settings dynamically to allow test overrides
    from project_management_crud_example.config import get_settings

    current_settings = get_settings()

    with db.get_session() as session:
        repo = Repository(session)

        # Check if any Super Admin users exist
        all_users = repo.users.get_all()
        existing_super_admins = [u for u in all_users if u.role == UserRole.SUPER_ADMIN]

        if existing_super_admins:
            return False, None

        # Create Super Admin with generated password
        password = generate_password()

        user_data = UserData(
            username=current_settings.BOOTSTRAP_ADMIN_USERNAME,
            email=current_settings.BOOTSTRAP_ADMIN_EMAIL,
            full_name=current_settings.BOOTSTRAP_ADMIN_FULL_NAME,
        )

        command = UserCreateCommand(
            user_data=user_data,
            organization_id=None,  # Super Admin has no organization
            role=UserRole.SUPER_ADMIN,
        )

        # Create the user (repository will hash the password)
        # But we need to set a known password, so we'll need to update the approach
        user = repo.users.create(command)

        # Update the password to our generated one
        from project_management_crud_example.dal.sqlite.orm_data_models import UserORM
        from project_management_crud_example.utils.password import hash_password

        orm_user = session.query(UserORM).filter(UserORM.id == user.id).first()
        if orm_user:
            orm_user.password_hash = hash_password(password)
            session.commit()

        return True, password


def main() -> None:
    """CLI entry point for bootstrapping the system."""
    from project_management_crud_example.config import get_settings

    current_settings = get_settings()

    print("Bootstrapping system...")
    print()

    # Create database and initialize tables
    db = Database("stub_entities.db")
    db.create_tables()

    # Bootstrap Super Admin
    created, password = bootstrap_super_admin(db)

    if created and password:
        print("✓ Super Admin created successfully!")
        print()
        print("=" * 60)
        print("SUPER ADMIN CREDENTIALS")
        print("=" * 60)
        print(f"Username: {current_settings.BOOTSTRAP_ADMIN_USERNAME}")
        print(f"Email:    {current_settings.BOOTSTRAP_ADMIN_EMAIL}")
        print(f"Password: {password}")
        print("=" * 60)
        print()
        print("⚠️  IMPORTANT: Save this password - it will not be shown again!")
        print()
    else:
        print("✓ Super Admin already exists, skipping creation")
        print()

    db.dispose()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nBootstrap cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Bootstrap failed: {e}")
        sys.exit(1)
