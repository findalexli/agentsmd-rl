# Fix Null Route Handling in API Middleware

## Problem

Requests to `GET /console/` (and potentially other unmatched routes) are entering `app/controllers/shared/api.php` with a null route object. The middleware assumes route matching has already succeeded and directly dereferences `$route`, causing a fatal error:

```
Call to a member function getLabel() on null
```

## Your Task

Modify `app/controllers/shared/api.php` to guard against null routes before dereferencing them.

### Requirements

1. **First location**: In the `Http::init()` action, after `$route = $utopia->getRoute();`, add a null check before any use of `$route`. If `$route` is null, throw an `AppwriteException` with error code `GENERAL_ROUTE_NOT_FOUND`.

2. **Second location**: In the shutdown action, after the second occurrence of `$route = $utopia->getRoute();`, add the same null guard before `$route` is used.

### Validation

After your changes:
- Unmatched console requests should fail cleanly with a 404-style error instead of generating a server error
- The `GENERAL_ROUTE_NOT_FOUND` error type should be returned for unmatched routes
- PHP syntax should remain valid (`php -l app/controllers/shared/api.php`)

### Notes

- Do not modify any other files
- Follow the existing code style in the file (4-space indentation, brace placement)
- The fix should be minimal - only add the two null guards as described
