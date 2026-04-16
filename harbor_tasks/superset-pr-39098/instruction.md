# Custom Auth View Registration Conflicts in SupersetSecurityManager Subclasses

## Problem

When subclassing `SupersetSecurityManager` to provide a custom authentication view (e.g., for OAuth providers), the `/login/` endpoint breaks. The parent class's `register_views()` method unconditionally registers `SupersetAuthView` and `SupersetRegisterUserView`, which conflicts with custom views that subclasses provide.

## Location

The issue is in `superset/security/manager.py` in the `SupersetSecurityManager` class, specifically in the `register_views()` method.

## Expected Behavior

- Existing SupersetSecurityManager subclasses that don't customize view registration should continue to work unchanged.
- Subclasses that provide their own auth views should be able to disable the default view registrations.
- The security manager file must pass `ruff check` linting.
- All Python files in the `superset/security/` directory must remain syntactically valid.