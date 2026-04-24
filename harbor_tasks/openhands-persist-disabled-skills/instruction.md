# Task: Fix disabled_skills persistence in SaaS settings

## Problem Description

In the enterprise SaaS application, toggling skills in Settings > Skills appears to save successfully (HTTP 200 response, success toast displayed), but after a page refresh the toggled changes revert. The `disabled_skills` setting is not being persisted to the database. Investigate the enterprise storage layer in `enterprise/storage/` to identify and fix the root cause.

## Your Task

1. **Investigate and fix the persistence issue:**
   - The fix requires adding a column named `disabled_skills` with SQLAlchemy type `JSON` (imported from `sqlalchemy`), nullable: `True`
   - Follow the existing column definition patterns in the storage model you identify as needing the fix

2. **Create a new Alembic migration file:**
   - File name: `104_add_disabled_skills_to_user.py`
   - Place it in `enterprise/migrations/versions/`
   - Include `upgrade()` and `downgrade()` functions
   - The `upgrade()` function should call `op.add_column('user', ...)` to add the `disabled_skills` JSON column (nullable)
   - The `downgrade()` function should drop the column
   - Set `revision` to `'104'` and `down_revision` to `'103'`
   - Follow the existing migration patterns for import structure

## Tips

- Examine the models in `enterprise/storage/` to understand how settings map to database columns
- Look at how other JSON columns are defined in those models
- Check existing migrations in `enterprise/migrations/versions/` for the numbering and structure pattern

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
