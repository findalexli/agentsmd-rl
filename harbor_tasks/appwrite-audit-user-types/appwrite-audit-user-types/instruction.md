# Add granular user type tracking to audit logs

The audit logging system currently categorizes all authenticated activity as either `user` (regular user) or `app` (API key). This is too coarse-grained. We need to distinguish between different types of users and API keys.

## Current behavior

- All API key requests are logged with `type: 'app'`
- Console admins are logged as regular `user` type
- No way to tell if an action was performed by an admin vs regular user
- No way to distinguish between different API key scopes (project, account, organization)

## Required changes

Replace the single `app` type with granular user types:

1. **New constants in `app/init/constants.php`:**
   - `ACTIVITY_TYPE_USER = 'user'` (regular authenticated user)
   - `ACTIVITY_TYPE_ADMIN = 'admin'` (console admin in APP_MODE_ADMIN)
   - `ACTIVITY_TYPE_GUEST = 'guest'` (unauthenticated guest)
   - `ACTIVITY_TYPE_KEY_PROJECT = 'keyProject'` (standard/dynamic project API key)
   - `ACTIVITY_TYPE_KEY_ACCOUNT = 'keyAccount'` (account-scoped API key)
   - `ACTIVITY_TYPE_KEY_ORGANIZATION = 'keyOrganization'` (organization-scoped API key)
   - Remove the old `ACTIVITY_TYPE_APP` constant

2. **Update `app/controllers/shared/api.php`:**
   - When setting audit user type, check `$mode === APP_MODE_ADMIN` to assign `ACTIVITY_TYPE_ADMIN` vs `ACTIVITY_TYPE_USER`
   - Only set the type if it's not already set (`empty($user->getAttribute('type'))`)
   - For API keys, use a match expression on `$apiKey->getType()`:
     - `API_KEY_STANDARD` → `ACTIVITY_TYPE_KEY_PROJECT`
     - `API_KEY_ACCOUNT` → `ACTIVITY_TYPE_KEY_ACCOUNT`
     - `API_KEY_ORGANIZATION` → `ACTIVITY_TYPE_KEY_ORGANIZATION`
   - Inject the `mode` parameter in the relevant action handler

3. **Update `src/Appwrite/Utopia/Response/Model/Log.php`:**
   - Add a `userType` rule to the Log model with description and possible values

4. **Update log response builders to include `userType`:**
   - `app/controllers/api/users.php` - add `userType` and `mode` to log response
   - `app/controllers/api/messaging.php` - add `userType` to all 4 log response locations
   - `src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Logs/XList.php`
   - `src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Logs/XList.php`
   - `src/Appwrite/Platform/Modules/Databases/Http/Databases/Logs/XList.php`
   - `src/Appwrite/Platform/Modules/Databases/Http/TablesDB/Logs/XList.php`
   - `src/Appwrite/Platform/Modules/Teams/Http/Logs/XList.php`

All log listing endpoints should return the `userType` field from `$log['data']['userType'] ?? null`.

## Files to modify

- `app/init/constants.php` - define new constants
- `app/controllers/shared/api.php` - set correct user type based on mode and API key type
- `src/Appwrite/Utopia/Response/Model/Log.php` - add userType field to response model
- `app/controllers/api/users.php` - include userType and mode in response
- `app/controllers/api/messaging.php` - include userType in 4 log response places
- 5 XList.php files in database and teams modules - include userType in log responses

See the AGENTS.md files for Appwrite's module structure and conventions.
