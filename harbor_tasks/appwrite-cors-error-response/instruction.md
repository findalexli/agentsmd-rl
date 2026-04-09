# Fix Missing CORS Headers on Error Responses

## Problem

When Appwrite's API returns an error response (such as HTTP 403 Forbidden on a paused project), browsers block the response with a CORS error instead of showing the actual error message to the client SDK. This happens because CORS headers are not being added to error responses.

## Files to Modify

- `app/controllers/general.php` - The `Http::error()` handler needs to add CORS headers

## Context

The application uses the Utopia PHP framework with dependency injection. The `Http::init()` handler already adds CORS headers to successful responses, but the `Http::error()` handler is missing this logic.

The error handler is responsible for formatting and sending error responses to clients. It currently sets cache headers but doesn't set CORS headers, which causes browser-based clients to receive a generic "CORS error" instead of the actual error message.

## Required Changes

1. The error handler needs access to the `cors` resource (similar to how `init()` has it)
2. Before sending the error response, CORS headers should be added
3. The CORS header addition should be defensive - if resolving the cors resource fails (e.g., due to a database failure), the error response should still be sent (just without CORS headers)
4. Use `override: true` when adding headers to avoid duplicates if `init()` already set them

## Reference Pattern

Look at how `Http::init()` handles CORS headers in the same file - it retrieves the cors resource and adds headers to the response. The error handler should follow a similar pattern.

## Agent Context

From AGENTS.md: Actions use the injection pattern with `->inject('resourceName')` and receive the resource as a callback parameter. This is how other parts of the codebase access shared resources like `cors`, `response`, `request`, etc.
