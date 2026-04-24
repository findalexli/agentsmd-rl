# Fix: Persist disabled_skills in SaaS Settings Store

## Problem Description

In the OpenHands enterprise/SaaS deployment, users can toggle skills on/off in the Settings > Skills page. When a user toggles a skill off:

1. The UI shows a success toast notification
2. The HTTP API returns 200 OK
3. **However, after refreshing the page, the skill toggle reverts to its previous state**

The skill toggle appears to save but doesn't actually persist across page refreshes.

## Relevant Files

The issue involves the enterprise storage layer that handles user settings:

- `enterprise/storage/user.py` - Contains the User SQLAlchemy model that stores user data
- `enterprise/migrations/versions/` - Directory containing Alembic database migrations

## Context

The `SaasSettingsStore` class persists settings via `hasattr`/`setattr` across `User`, `Org`, and `OrgMember` models. When a setting is saved, it checks if the model has the corresponding attribute and stores the value there.

Migration 102 added `disabled_skills` to a legacy user settings table, but that table is only used for one-time migration of old users. The active SaaS flow reads from and writes directly to the `User` model - not the legacy table. The `User` model is missing the `disabled_skills` column entirely.

## Expected Behavior

When a user toggles a skill off and the page refreshes, the toggle should remain in the "off" position (the setting should persist).

## Requirements

### User Model (`enterprise/storage/user.py`)

The `User` class in `enterprise/storage/user.py` must have a `disabled_skills` column that:
- Uses the `JSON` type from `sqlalchemy`
- Is nullable (allows NULL values)
- Follows the pattern: `disabled_skills = Column(JSON, nullable=True)`

### Migration File (`enterprise/migrations/versions/`)

A new Alembic migration file must be created with:
- **Revision ID**: `104`
- **Down revision**: `'103'` (the migration depends on revision 103)
- **Upgrade operation**: Adds a `disabled_skills` column of type `JSON` (with `sa.JSON()`, nullable) to the `user` table
- **Downgrade operation**: Drops the `disabled_skills` column from the `user` table

The migration filename should follow the pattern `104_add_disabled_skills_to_user.py`.

## Your Task

1. Identify why `disabled_skills` values are being silently dropped on save and missing on load
2. Add the necessary database column to make the `disabled_skills` setting persist properly
3. Create the appropriate Alembic migration file if needed

The fix should be minimal and focused - only adding what's needed to make the existing SaaS settings persistence work correctly for the `disabled_skills` field.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
