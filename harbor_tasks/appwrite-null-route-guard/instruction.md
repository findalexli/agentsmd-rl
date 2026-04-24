# Fix Null Route Handling in API Middleware

## Problem

Requests to `GET /console/` (and potentially other unmatched routes) are causing a fatal error:

```
Call to a member function getLabel() on null
```

The API middleware assumes route matching has always succeeded and attempts to call methods on the route object without first verifying it exists. When a request reaches the middleware without a matched route, this causes a server error instead of a proper 404 response.

## Your Task

Investigate the API middleware code to find where route objects are being used without null checks, then add proper error handling:

1. When no route is matched, the middleware should detect this condition before attempting to access route properties or methods
2. Return a proper 404-style error response using `AppwriteException::GENERAL_ROUTE_NOT_FOUND` when no route is matched
3. Ensure all code paths that access `$route` after retrieving it from `$utopia->getRoute()` are protected

## Validation

After your changes:
- Requests to `/console/` should return a 404 status code with `type: general_route_not_found`
- PHP syntax should remain valid (`php -l` on the modified file passes)
- The existing code style should be maintained

## Notes

- Keep the fix minimal - only add the necessary null-safety guards
- Follow the existing code style (4-space indentation, brace placement)
- The exception constant `GENERAL_ROUTE_NOT_FOUND` is the appropriate error type for unmatched routes
