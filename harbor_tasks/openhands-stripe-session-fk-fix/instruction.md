# Fix Foreign Key Violation in Stripe Customer Migration

## Problem

When migrating users, the system calls `migrate_customer()` from `stripe_service.py` to update Stripe customer records with the new organization ID. However, this function creates its own database session using `async with a_session_maker() as session`.

This causes a foreign key violation error because:
1. The caller (`migrate_user` in `user_store.py`) creates a new `Org` object in its session
2. The caller hasn't committed yet - the org exists only in that session's identity map
3. `migrate_customer()` creates a NEW session where the org doesn't exist yet
4. When trying to set `stripe_customer.org_id = org.id`, the FK constraint fails

The error manifests as:
```
sqlalchemy.exc.IntegrityError: FK violation on stripe_customers table
```

## Your Task

Fix the `migrate_customer()` function in `enterprise/integrations/stripe_service.py` and its caller in `enterprise/storage/user_store.py` to prevent this foreign key violation.

### Key Requirements

1. **Function signature must accept a database session**: The `migrate_customer()` function in `enterprise/integrations/stripe_service.py` must accept a database session as its first parameter.

2. **No new session creation**: The `migrate_customer()` function must NOT create a new session using `a_session_maker()`. It must use the passed session for all database operations.

3. **Session parameter usage**: All database operations in `migrate_customer()` (including `session.execute()`) must use the passed session parameter directly.

4. **No session commit in callee**: The `migrate_customer()` function must NOT call `session.commit()`. The caller manages the session lifecycle and will commit when appropriate.

5. **Caller must pass session**: The call to `migrate_customer()` in `enterprise/storage/user_store.py` must pass the current database session as the first argument.

### Test Assertions

The tests verify the following literal strings are present:
- The call pattern `migrate_customer(session, user_id, org)` must exist in `user_store.py`
- The function `migrate_customer` in `stripe_service.py` must have `session` as its first parameter
- The function body must NOT contain `a_session_maker`
- The function body must NOT contain `session.commit()`
- The function body must contain `session.execute`

## Files to Modify

- `enterprise/integrations/stripe_service.py` - Modify `migrate_customer()` function
- `enterprise/storage/user_store.py` - Update the call to `migrate_customer()`
