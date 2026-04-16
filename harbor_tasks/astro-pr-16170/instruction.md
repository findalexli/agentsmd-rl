# Task: Fix Edge Middleware HTTP Method and Body Dropping

## Problem

Edge middleware in `@astrojs/vercel` is dropping the HTTP method and request body when calling `next()` to forward requests to the serverless function.

### Symptoms

- Non-GET API routes (POST, PUT, PATCH, DELETE) return 404 errors
- The requests appear to be forwarded as GET requests to the `/_render` serverless function
- Request bodies are silently lost in the forwarded request

### Affected File

`packages/integrations/vercel/src/serverless/middleware.ts`

The `next()` function calls `fetch()` to forward the incoming request to the internal serverless function, but it doesn't pass through the HTTP method or body from the original request.

### Verification

After fixing, verify that:
1. The fetch call properly forwards the original HTTP method
2. When a request body exists, it's properly forwarded with appropriate streaming configuration
3. The package builds successfully
4. Existing tests pass
