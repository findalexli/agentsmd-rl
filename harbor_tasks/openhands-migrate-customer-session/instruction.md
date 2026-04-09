# Task: Fix Foreign Key Violation in User Migration

## Problem

During user migration, the system fails with a foreign key violation error:
```
sqlalchemy.exc.IntegrityError: FK violation on stripe_customers table
```

The issue is in how database sessions are handled when migrating Stripe customer data.

## Root Cause

The `migrate_customer` function in `enterprise/integrations/stripe_service.py` creates its own database session:

```python
async def migrate_customer(user_id: str, org: Org):
    async with a_session_maker() as session:  # Creates NEW session
        # ... queries stripe_customer ...
        stripe_customer.org_id = org.id  # FK violation! org not committed in this session
        await session.commit()
```

The problem is that the `org` was created in the caller's session (in `user_store.py`) but hasn't been committed yet. When `migrate_customer` creates its own session and tries to set `stripe_customer.org_id`, the database rejects it because that org ID doesn't exist in this new session's transaction.

## Required Fix

Modify the code so `migrate_customer` uses the caller's session instead of creating its own:

1. **In `enterprise/integrations/stripe_service.py`:**
   - Change `migrate_customer(user_id: str, org: Org)` to `migrate_customer(session, user_id: str, org: Org)`
   - Remove the `async with a_session_maker() as session:` wrapper
   - Remove the `await session.commit()` at the end

2. **In `enterprise/storage/user_store.py`:**
   - Update the call to `migrate_customer` to pass `session` as the first argument

Also fix the typo in the comment: "temprorary" → "temporary".

## Files to Modify

- `enterprise/integrations/stripe_service.py`
- `enterprise/storage/user_store.py`

## Verification

Run `pytest test_outputs.py -v` to verify the fix works.

## Relevant Code Sections

Look for:
- `migrate_customer` function definition in `stripe_service.py`
- The comment about "circular reference" and "temprorary" in `user_store.py`
- The call to `migrate_customer` within `migrate_user` in `user_store.py`
