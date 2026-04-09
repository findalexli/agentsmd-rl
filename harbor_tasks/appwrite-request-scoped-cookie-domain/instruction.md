# Task: Move domainVerification and cookieDomain to Request-Scoped Resources

## Problem
The `domainVerification` and `cookieDomain` values are currently stored in global mutable Config (`Config::getParam()` and `Config::setParam()`). This is problematic because these values are request-dependent - they depend on the hostname, origin, and project context. Using global config forces the application to mutate global state on each request.

## Goal
Move `domainVerification` and `cookieDomain` from global Config to request-scoped resources that are injected into controllers via Utopia PHP's dependency injection system.

## Files to Modify

### 1. `app/init/resources.php`
Add two new resources using `Http::setResource()`:
- `domainVerification`: A boolean indicating if the request origin matches the request hostname
- `cookieDomain`: The cookie domain string (or null for localhost/IP)

Both resources should depend on the `Request` object. The `cookieDomain` resource also needs the `project` document.

Key behaviors to preserve:
- `domainVerification`: Compare `getRegisterable()` of the hostname vs origin hostname
- `cookieDomain`: Return `null` for localhost or IP addresses; return registerable domain prefixed with `.` for console project with root session enabled; return `.` + hostname for regular requests

### 2. `app/controllers/general.php`
Remove the `Config::setParam('domainVerification', ...)` and `Config::setParam('cookieDomain', ...)` calls from the request handling flow.

### 3. `app/controllers/api/account.php`
Update all endpoints that use `Config::getParam('domainVerification')` or `Config::getParam('cookieDomain')`:
- Add `->inject('domainVerification')` and `->inject('cookieDomain')` to the action chain
- Update action function signatures to accept `bool $domainVerification` and `?string $cookieDomain`
- Replace all `Config::getParam('domainVerification')` calls with `$domainVerification`
- Replace all `Config::getParam('cookieDomain')` calls with `$cookieDomain`

The `$createSession` closure at the top of the file also needs these parameters.

### 4. `src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php`
Update the membership status endpoint:
- Add `->inject('domainVerification')` and `->inject('cookieDomain')` to the action chain
- Update the `action()` method signature to accept these parameters
- Replace `Config::getParam()` calls with the injected variables

## Pattern Reference
The Utopia framework uses `Http::setResource()` to define request-scoped resources. Controllers use `->inject('resourceName')` to declare dependencies, and the action function receives them as parameters.

Example from the codebase:
```php
Http::setResource('myResource', function (Request $request) {
    return $request->getHostname();
}, ['request']);

Http::post('/v1/example')
    ->inject('myResource')
    ->action(function (string $myResource) {
        // Use $myResource
    });
```

## Notes
- The app uses `Utopia\Domains\Domain` class for domain parsing
- Look at the existing `allowedOrigins` resource in `app/init/resources.php` for a similar pattern
- Ensure all 4 files are modified consistently - partial changes will break the application
