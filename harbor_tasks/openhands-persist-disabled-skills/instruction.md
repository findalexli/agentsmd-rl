# Task: Fix disabled_skills persistence in SaaS settings store

## Problem Description

The skill toggles in Settings > Skills appear to save successfully (HTTP 200, success toast), but the change reverts after page refresh. This is a data persistence bug.

## Root Cause

The `SaasSettingsStore` persists settings via `hasattr`/`setattr` across `User`, `Org`, and `OrgMember` models. However, the `User` model is missing a column needed to store `disabled_skills`. When the store tries to save this value, it gets silently dropped because the column doesn't exist on the model.

## Your Task

1. Add the missing column to the User model in `enterprise/storage/user.py`
   - The column should be named `disabled_skills`
   - It should use SQLAlchemy's JSON type
   - It should be nullable

2. Create a new Alembic migration file to add this column to the database
   - Place it in `enterprise/migrations/versions/`
   - Use the next sequential migration number
   - Follow the existing migration patterns in that directory

## Files to Modify

- `enterprise/storage/user.py` - Add the column definition
- `enterprise/migrations/versions/` - Create a new migration file

## Tips

- Look at how other columns are defined in `enterprise/storage/user.py`
- Check existing migrations in `enterprise/migrations/versions/` for the pattern
- The `SaasSettingsStore` uses generic column mapping, so adding the column to the User model should automatically make it work
