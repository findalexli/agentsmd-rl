# Return More Sensible User Error for AI Binding Authentication Failures

## Problem

The AI binding in Wrangler uses a proxy for doing inference. If a session runs long, the API token expires and users receive a confusing 403 error with an opaque response body. The response body from the AI proxy contains `{"errors": [{"code": 1031, "message": "Forbidden"}]}` on authentication failures.

Currently, this 403 error is passed through to the user without any explanation or remediation guidance.

## Expected Behavior

When the AI binding receives a **403 response** whose body contains an error with **code 1031**, it should log a user-friendly error message that:

1. Identifies this as an authentication error (code 1031)
2. Explains the likely cause: the API token may have expired or lacks permissions
3. Provides remediation: run `wrangler login` to refresh the token

The exact error message must be:

```
Authentication error (code 1031): Your API token may have expired or lacks the required permissions. Please refresh your token by running `wrangler login`.
```

## Constraints

- Do **not** log an error message for 403 responses that do NOT contain error code 1031
- Do **not** crash or throw if the 403 response body is not parseable JSON (e.g., `"not json"`)
- The original response must still be returned to the caller unchanged (status, headers, body preserved)
- Follow the repo's coding conventions (see `AGENTS.md`):
  - Use the `logger` singleton for output, never `console.*`
  - In vitest tests, use `expect` from test context destructuring, never from an import
  - Include a changeset for any user-facing change

## Verification

The fix is verified by behavioral tests that:

1. Confirm the authentication error message is logged when the AI API returns 403 with error code 1031
2. Confirm no error is logged for 403 responses with other error codes (e.g., code 9999)
3. Confirm no crash occurs and no error is logged for 403 responses with an unparseable body

## Code Style Requirements

- Format with oxfmt by running `pnpm prettify` before committing
- TypeScript with strict mode
