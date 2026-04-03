# Improve Contributor Setup Experience for Tuist Server

## Problem

Setting up the Tuist server for local development currently requires external contributors to obtain a private key from 1Password and create a `priv/secrets/dev.key` file. This blocks anyone who doesn't have access to the team's 1Password vault. Additionally, there's no quick way to log into the dev server — contributors must manually enter the test user credentials every time.

The setup documentation in both `server/README.md` and `docs/docs/en/contributors/code/server.md` includes steps that are either unnecessary for external contributors (like exporting `TUIST_SECRET_KEY_BASE`) or misleading (like pointing to the old `tuist/server` repo URL instead of the monorepo).

## Expected Behavior

1. **Dev login shortcut**: The login page should include a convenient way to sign in with the pre-made test account (`tuistrocks@tuist.dev`) when running in the development environment. This shortcut must NOT appear in production.

2. **Simplified setup docs**: The contributor documentation should be updated to remove steps that block external contributors (1Password key, secret key base export). The docs should make it clear that `priv/secrets/dev.key` is optional — the server works without it, just with third-party integrations disabled.

## Files to Look At

- `server/lib/tuist_web/live/user_login_live.ex` — the Phoenix LiveView for the login page
- `server/README.md` — contributor setup instructions for the server
- `docs/docs/en/contributors/code/server.md` — public-facing contributor documentation

After making the code change, update the relevant documentation files to reflect the simplified setup process and the new dev login feature. Check the project's agent config files for any documentation conventions to follow.
