# Add SAML login support to Superset

The Superset codebase under `/workspace/superset` already passes OAuth and database authentication providers through to the React login page via the bootstrap data produced by `cached_common_bootstrap_data` in `superset/views/base.py`. Flask-AppBuilder 5.1.0 is installed and exposes a SAML authentication mode (`AUTH_SAML = 5`), but the Superset glue is missing — so when a deployment is configured with `AUTH_TYPE = AUTH_SAML`, the login page renders blank and SAML POST callbacks from the IdP get rejected.

Make SAML a first-class auth mode end to end.

## What is broken

1. **Bootstrap payload omits SAML providers.** When `AUTH_TYPE` equals `AUTH_SAML` (the integer `5`), the `AUTH_PROVIDERS` key is missing from the frontend config dict that `cached_common_bootstrap_data` returns. With `AUTH_TYPE = AUTH_OAUTH` the function builds a list of `{"name": ..., "icon": ...}` entries from `appbuilder.sm.oauth_providers`. SAML deserves the equivalent treatment, reading from `appbuilder.sm.saml_providers`. SAML providers may omit the `icon` key — when missing, fall back to the literal string `"fa-sign-in"`.

2. **Recaptcha is incorrectly required for SAML.** The function currently sets `should_show_recaptcha = auth_user_registration and (auth_type != AUTH_OAUTH)`, meaning federated SAML sign-ins still trigger the recaptcha form key. Federated identity providers (both OAuth and SAML) bypass the self-registration form entirely, so neither should produce a `RECAPTCHA_PUBLIC_KEY` in the bootstrap payload. Extend the exclusion to cover SAML as well.

3. **CSRF rejects the SAML ACS endpoint.** Flask-AppBuilder exposes the SAML Assertion Consumer Service at the view path `flask_appbuilder.security.views.acs`. The IdP POSTs the SAML response cross-site without a CSRF token, so this endpoint must be added to Superset's `WTF_CSRF_EXEMPT_LIST` in `superset/config.py` (alongside the other entries already in that list).

4. **Frontend login page has no AUTH_SAML branch.** The `AuthType` enum in the React login component (under `superset-frontend/src/pages/Login/`) currently maps `AuthDB = 1`, `AuthLDAP = 2`, `AuthOauth = 4`. Add a SAML entry mapped to the integer `5`. The render block that emits provider buttons for OAuth must also fire when the auth type is SAML — both modes share the `{name, icon}` provider shape and use the `/login/<provider>` URL pattern, so the same render path applies.

## Constraints

- Do not change unrelated behavior: OAuth provider rendering, DB/LDAP recaptcha behavior, and the `/saml/acs/` URL routing must continue to work as before.
- The default icon string for SAML providers without an explicit icon must be exactly `"fa-sign-in"`.
- The CSRF exempt entry must be the dotted path `"flask_appbuilder.security.views.acs"` so it matches FAB's view name.
- Use the `AUTH_SAML` constant imported from `flask_appbuilder.const` rather than hard-coding the integer `5` in Python (the React side uses the integer because TypeScript enums don't import from Flask-AppBuilder).

## How the change is verified

The test harness exercises `cached_common_bootstrap_data` with several `AUTH_TYPE` values:

- `AUTH_TYPE = AUTH_SAML` with `SAML_PROVIDERS = [{"name": "okta", "icon": "fa-okta"}, {"name": "entra_id", "icon": "fa-microsoft"}]` — expects `AUTH_PROVIDERS` to equal that list verbatim.
- `AUTH_TYPE = AUTH_SAML` with `SAML_PROVIDERS = [{"name": "onelogin"}]` (no icon) — expects `AUTH_PROVIDERS == [{"name": "onelogin", "icon": "fa-sign-in"}]`.
- `AUTH_TYPE = AUTH_OAUTH` or `AUTH_SAML` with registration enabled — `RECAPTCHA_PUBLIC_KEY` must NOT be in the conf payload.
- `AUTH_TYPE = AUTH_DB` or `AUTH_LDAP` with registration enabled — `RECAPTCHA_PUBLIC_KEY` must still appear (regression guard).

It also greps `superset/config.py` for the SAML ACS exempt entry and `superset-frontend/src/pages/Login/index.tsx` for the AuthType enum extension.

## Code Style Requirements

- Follow the repo's existing Python conventions: type hints on new code, `pre-commit run` clean (ruff/mypy).
- TypeScript: no `any` types, functional component pattern. The repo uses Jest + React Testing Library.
- New Python files require the Apache Software Foundation license header (existing files don't need re-stamping).
- Don't use time-specific language ("now", "currently") in code comments.

## Working directory

The Superset checkout is at `/workspace/superset` (Python package importable as `superset`). Flask-AppBuilder 5.1.0 is already installed, so `from flask_appbuilder.const import AUTH_SAML` succeeds at the base.
