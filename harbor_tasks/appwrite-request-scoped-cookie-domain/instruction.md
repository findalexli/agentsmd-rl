# Refactor domainVerification and cookieDomain to Request-Scoped Resources

## Problem

`domainVerification` and `cookieDomain` are currently stored in global mutable state via `Config::getParam()` and `Config::setParam()`. These values are derived from request-specific data (hostname, origin, project context). Using global config means global state is mutated on every request, which can cause request-scoped data to pollute global state and potentially leak between requests.

## Required Outcome

Move `domainVerification` and `cookieDomain` from global config to request-scoped resources. Controllers that currently read these values from `Config::getParam()` should receive them via dependency injection instead.

## Technical Requirements

### Request-scoped resources

Define two new request-scoped resources in the initialization layer (in `app/init/resources.php`):

1. **`domainVerification`** — a `bool` resource computed from the request (using `Utopia\Domains\Domain` for domain comparison). Takes `Request` as a dependency.

2. **`cookieDomain`** — a `?string` resource computed from request and project context. Must handle localhost, IP addresses, and custom hostnames. Takes `Request` and `Document $project` as dependencies.

### Remove global config mutations

Identify and remove `Config::setParam()` calls that set `domainVerification` and `cookieDomain` from request-handling code. The logic currently computing these values inline and storing them in global state should be moved into the resource closures.

### Update controllers to use injection

Controllers that currently read `domainVerification` or `cookieDomain` from `Config::getParam()` must instead receive these values via Utopia PHP's dependency injection system (`->inject()` method). This includes controllers that handle session creation/deletion and any helper functions that reference these values.

Controllers must declare the injected parameters with proper type hints (`bool` and `?string`) in their action callbacks.

## Files to modify

The files that require changes are:
- `app/init/resources.php` — add the new resource definitions
- `app/controllers/general.php` — remove Config::setParam calls for these values
- Controllers that call `Config::getParam('domainVerification')` or `Config::getParam('cookieDomain')` — update to use injection instead

## Verification Requirements

After implementation:
- All modified PHP files must pass `php -l` (valid syntax)
- Code must pass `vendor/bin/pint --test` (linting)
- Code must pass `vendor/bin/phpstan analyse` (static analysis)

## Reference: Current Implementation Pattern

The codebase uses Utopia PHP's dependency injection system where resources are registered with `Http::setResource()` and injected into controllers using chained `->inject()` calls. The `Config::getParam()` and `Config::setParam()` methods represent the old global state approach that should be avoided for request-scoped data.

Example resource definition pattern:
```php
Http::setResource('resourceName', function (DependencyType $dependency) {
    return computedValue;
}, ['dependencyName']);
```

Example controller injection pattern:
```php
Http::post('/v1/endpoint')
    ->inject('resourceName')
    ->action(function (TypeHint $resourceName) {
        // use $resourceName instead of Config::getParam('resourceName')
    });
```