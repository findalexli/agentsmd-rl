# Fix Null Route Handling in API Middleware

## Problem

Requests to `GET /console/` (and potentially other unmatched routes) are entering `app/controllers/shared/api.php` with a null route object. The middleware assumes route matching has already succeeded and directly dereferences `$route`, causing a fatal error:

```
Call to a member function getLabel() on null
```

This is happening because there are two places in `app/controllers/shared/api.php` where `$route` is obtained from `$utopia->getRoute()` and then used without checking if it's null.

## Your Task

Modify `app/controllers/shared/api.php` to guard against null routes before dereferencing them.

### Specific Requirements

1. **First location (Http::init action)**: After `$route = $utopia->getRoute();`, add a null check. If `$route` is null, throw an `AppwriteException` with the error code `GENERAL_ROUTE_NOT_FOUND`.

2. **Second location (shutdown action)**: There's another place in the file where `$route = $utopia->getRoute();` is called, followed by `$route->getMatchedPath()`. Add the same null guard here before the route is used.

### Error Handling Pattern

Use this exact pattern for both guards:

```php
$route = $utopia->getRoute();
if ($route === null) {
    throw new AppwriteException(AppwriteException::GENERAL_ROUTE_NOT_FOUND);
}
```

### Relevant Files

- **Primary**: `app/controllers/shared/api.php` - This is where the fix must be implemented

### Validation

After your changes:
- Unmatched console requests should fail cleanly with a 404-style error instead of generating a server error
- The `GENERAL_ROUTE_NOT_FOUND` error type should be returned for unmatched routes
- PHP syntax should remain valid (`php -l app/controllers/shared/api.php`)

### Notes

- Do not modify any other files
- Follow the existing code style in the file (4-space indentation, brace placement)
- The fix should be minimal - only add the two null guards as described
