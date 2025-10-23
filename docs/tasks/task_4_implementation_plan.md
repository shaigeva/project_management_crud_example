# Task 4 Implementation Plan: Bootstrap Super Admin User

**Task**: Bootstrap Super Admin user
**Implements**: System bootstrap, foundation for REQ-AUTH-004
**Created**: 2025-01-23

## Requirements Analysis

### What we need:
1. **CLI command** to create the initial Super Admin user
2. **Idempotent** - don't create duplicates if Super Admin already exists
3. **Secure** - generate random password, display it once
4. **Simple** - easy to run during development and deployment
5. **Optional override** - allow setting username/email via environment variables

### Bootstrap behavior:
- Check if any Super Admin users exist
- If yes: skip creation, display message
- If no: create Super Admin with:
  - Username from env var or default "admin"
  - Email from env var or default "admin@example.com"
  - Full name: "System Administrator"
  - Role: SUPER_ADMIN
  - organization_id: None (Super Admins have no org)
  - Generated random password
  - is_active: True

## Implementation Plan

### 1. Environment Variables (`.env` or settings)
```python
# Optional - defaults provided
BOOTSTRAP_ADMIN_USERNAME=admin
BOOTSTRAP_ADMIN_EMAIL=admin@example.com
```

### 2. Bootstrap Script (`project_management_crud_example/bootstrap.py`)
```python
def bootstrap_super_admin(db: Database) -> None:
    """Create initial Super Admin user if none exists."""
    with db.get_session() as session:
        repo = Repository(session)

        # Check if Super Admin exists
        existing_admins = # query for super admins

        if existing_admins:
            print("Super Admin already exists, skipping bootstrap")
            return

        # Create Super Admin
        password = generate_password()
        user = repo.users.create(UserCreateCommand(...))

        # Display credentials
        print(f"""
        Super Admin created successfully!

        Username: {user.username}
        Email: {user.email}
        Password: {password}

        IMPORTANT: Save this password - it will not be shown again!
        """)
```

### 3. CLI Entry Point (add to `pyproject.toml` or standalone script)
```bash
# Option A: As a package script
[project.scripts]
bootstrap = "project_management_crud_example.bootstrap:main"

# Option B: Simple Python script
python -m project_management_crud_example.bootstrap
```

### 4. Integration with App Startup (optional)
Could add to `app.py` lifespan to auto-bootstrap on first run.

## Test Plan

### Manual Testing:
1. Run bootstrap command - verify Super Admin created and password displayed
2. Run bootstrap command again - verify "already exists" message
3. Test login with generated credentials - verify authentication works
4. Test that Super Admin can access system

### Automated Testing (`tests/test_bootstrap.py`):
1. `test_bootstrap_creates_super_admin` - Fresh DB creates admin
2. `test_bootstrap_is_idempotent` - Second run doesn't create duplicate
3. `test_bootstrap_uses_env_vars` - Respects BOOTSTRAP_ADMIN_USERNAME
4. `test_bootstrap_generates_random_password` - Password is random
5. `test_created_admin_can_login` - Generated credentials work

## Implementation Order
1. Add environment variables to settings
2. Create bootstrap.py module with bootstrap_super_admin()
3. Add CLI entry point / script
4. Write tests
5. Run validations
6. Test manually with login
7. Update task status

## Notes
- Password is displayed ONCE and never stored in plain text
- Super Admin has organization_id=None (special case)
- Consider adding to README.md setup instructions
- Could extend later to bootstrap default organizations/roles
