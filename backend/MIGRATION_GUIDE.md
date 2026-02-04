# Database Migration Guide

## Overview

Project Aegis uses **Alembic** for database schema versioning and migrations. This ensures consistent database state across development, staging, and production environments.

## Quick Start

### 1. Initial Setup (First Time)

```bash
# Create the database with initial schema
alembic upgrade head
```

### 2. Creating a New Migration

After modifying models in `models.py`:

```bash
# Auto-generate migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Review the generated migration file in alembic/versions/
# Edit if necessary to add custom logic

# Apply the migration
alembic upgrade head
```

### 3. Applying Migrations

```bash
# Upgrade to latest version
alembic upgrade head

# Upgrade one version
alembic upgrade +1

# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>
```

## Common Commands

```bash
# Show current database version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic heads

# Stamp database with specific revision (without running migrations)
alembic stamp head
```

## Migration Workflow

### Development

1. **Modify Models**: Update `models.py` with your schema changes
2. **Generate Migration**: `alembic revision --autogenerate -m "Add user table"`
3. **Review Migration**: Check the generated file in `alembic/versions/`
4. **Test Migration**: `alembic upgrade head`
5. **Test Rollback**: `alembic downgrade -1` then `alembic upgrade head`
6. **Commit**: Add migration file to version control

### Production Deployment

```bash
# 1. Backup database first!
# 2. Apply migrations
alembic upgrade head

# 3. Verify application starts correctly
python main.py
```

## Environment Variables

Alembic reads the database URL from:

1. **Environment Variable**: `DATABASE_URL` (highest priority)
2. **alembic.ini**: Default fallback

```bash
# Set database URL for migrations
export DATABASE_URL="sqlite:///./data/aegis_trust_vault.db"

# Or for PostgreSQL
export DATABASE_URL="postgresql://user:password@localhost/aegis_db"
```

## Migration File Structure

```python
"""Description of migration

Revision ID: abc123
Revises: xyz789
Create Date: 2024-01-01 12:00:00

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'xyz789'

def upgrade():
    # Schema changes to apply
    op.create_table('users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('name', sa.String(50))
    )

def downgrade():
    # How to revert the changes
    op.drop_table('users')
```

## Best Practices

### ✅ DO

- **Always review** auto-generated migrations before applying
- **Test migrations** in development before production
- **Backup database** before running migrations in production
- **Keep migrations small** and focused on one change
- **Write descriptive** migration messages
- **Test rollback** (downgrade) functionality

### ❌ DON'T

- **Don't edit** applied migrations (create a new one instead)
- **Don't delete** migration files from version control
- **Don't skip** migration testing
- **Don't run** migrations without backups in production

## Troubleshooting

### "Target database is not up to date"

```bash
# Check current version
alembic current

# Check what migrations are pending
alembic heads

# Apply pending migrations
alembic upgrade head
```

### "Can't locate revision identified by 'xyz'"

Migration file is missing. Check version control or restore from backup.

### "Multiple heads detected"

Branched migration history. Merge branches:

```bash
alembic merge heads -m "Merge migration branches"
```

### Starting Fresh (Development Only)

```bash
# Delete database
rm data/aegis_trust_vault.db

# Recreate with migrations
alembic upgrade head
```

## Integration with Application

The application automatically creates tables on startup using `Base.metadata.create_all()`. For production:

1. **Disable auto-creation** in `main.py`
2. **Use migrations only** for schema management
3. **Run migrations** before starting the application

## Current Schema

### Tables

1. **security_logs** - Immutable audit trail for scam calls and transactions
2. **pending_approvals** - Items requiring Trusted Advocate review
3. **pending_bills** - Legacy bill tracking (to be migrated)

## Future Enhancements

- [ ] Add database seeding for test data
- [ ] Implement migration testing in CI/CD
- [ ] Add data migrations for schema changes
- [ ] Support for multiple database backends
