# Refactor domainVerification and cookieDomain to Request-Scoped Resources

## Problem

`domainVerification` and `cookieDomain` are currently stored in global mutable state via `Config::getParam()`. These values are derived from request-specific data (hostname, origin, project context). Using global config means global state is mutated on every request, which can cause request-scoped data to pollute global state and potentially leak between requests.

## Required Outcome

Move `domainVerification` and `cookieDomain` from global config to request-scoped resources. Controllers that currently read these values from `Config::getParam()` should receive them via dependency injection instead.

## Technical Requirements

### Request-scoped resources

Define two new request-scoped resources in `app/init/resources.php`:

1. **`domainVerification`** — a `bool` resource with a closure that takes `Request $request` as dependency. The `Utopia\Domains\Domain` class must be imported in this file.

2. **`cookieDomain`** — a `?string` resource with a closure that takes `Request $request` and `Document $project` as dependencies.

### Remove global config mutations

`app/controllers/general.php` must not contain any `Config::setParam()` calls that set `domainVerification` or `cookieDomain`.

### Update controllers to use injection

Two controller files must be updated to receive `domainVerification` and `cookieDomain` via injection instead of `Config::getParam()`:

- `app/controllers/api/account.php` — action callbacks must declare `bool $domainVerification` and `?string $cookieDomain` parameters. The `$createSession` closure must also accept these parameters.
- `src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php` — the action method must declare `bool $domainVerification` and `?string $cookieDomain` parameters.

Both files must not contain `Config::getParam('domainVerification')` or `Config::getParam('cookieDomain')`.

## Verification Requirements

After implementation:
- All modified PHP files must pass `php -l` (valid syntax)
- Code must pass `vendor/bin/pint --test` (linting)
- Code must pass `vendor/bin/phpstan analyse` (static analysis)