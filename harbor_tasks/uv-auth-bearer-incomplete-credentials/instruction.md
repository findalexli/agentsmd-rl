# Bearer Authentication Rejected with "Missing password" Error

## Bug Description

When using Bearer token authentication with an index that has `auth-policy = "always"`, uv
incorrectly rejects the request with a "Missing password" error — even though a valid Bearer
token is present.

The root cause is in `crates/uv-auth/src/middleware.rs`, in the `complete_request` method. The
code checks whether the credentials have a password to decide if authentication is complete.
However, Bearer authentication uses a token, not a username/password pair. The `password()`
method on Bearer credentials always returns `None`, so the "always" auth policy guard
incorrectly treats valid Bearer tokens as missing credentials.

A similar issue exists in `complete_request_with_request_credentials`, where a comment and
trace message incorrectly describe authentication as "username and password", even though the
code path handles both Basic and Bearer auth.

## Relevant Files

- `crates/uv-auth/src/middleware.rs` — the `complete_request` method (around line 555) and
  `complete_request_with_request_credentials` (around line 585)
- `crates/uv-auth/src/credentials.rs` — defines `Credentials` enum with `Basic` and `Bearer`
  variants, including methods that distinguish between the two

## Expected Behavior

Bearer token authentication should be treated as complete authentication when
`auth-policy = "always"` is set. The credential completeness check should account for all
authentication types, not just password-based ones.
