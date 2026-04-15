# Add granular user type tracking to audit logs

The audit logging system currently categorizes all authenticated activity as either `user` (regular user) or `app` (API key). This is too coarse-grained. We need to distinguish between different types of users and API keys.

## Current behavior

- All API key requests are logged with `type: 'app'`
- Console admins are logged as regular `user` type
- No way to tell if an action was performed by an admin vs regular user
- No way to distinguish between different API key scopes (project, account, organization)

## Required changes

### 1. Define new activity type constants in `app/init/constants.php`

Replace the single coarse-grained type system with granular constants:

| Constant | Value | Description |
|----------|-------|-------------|
| `ACTIVITY_TYPE_USER` | `'user'` | Regular authenticated user |
| `ACTIVITY_TYPE_ADMIN` | `'admin'` | Console admin operating in `APP_MODE_ADMIN` |
| `ACTIVITY_TYPE_GUEST` | `'guest'` | Unauthenticated guest user |
| `ACTIVITY_TYPE_KEY_PROJECT` | `'keyProject'` | Standard/dynamic project-scoped API key |
| `ACTIVITY_TYPE_KEY_ACCOUNT` | `'keyAccount'` | Account-scoped API key |
| `ACTIVITY_TYPE_KEY_ORGANIZATION` | `'keyOrganization'` | Organization-scoped API key |

Remove the old `ACTIVITY_TYPE_APP` constant.

### 2. Update `app/controllers/shared/api.php`

**Mode-based user type assignment:** When setting the audit user type for authenticated users, distinguish between console admin mode and regular user mode. The appropriate constants are `ACTIVITY_TYPE_ADMIN` and `ACTIVITY_TYPE_USER`.

**Existing type preservation:** User type values that are already set should not be overwritten.

**API key type mapping:** API keys have three types (`API_KEY_STANDARD`, `API_KEY_ACCOUNT`, `API_KEY_ORGANIZATION`) that must map to their corresponding activity types (`ACTIVITY_TYPE_KEY_PROJECT`, `ACTIVITY_TYPE_KEY_ACCOUNT`, `ACTIVITY_TYPE_KEY_ORGANIZATION`).

**Mode parameter access:** The action handler needs access to the current application mode to determine if the request is in admin context.

### 3. Update `src/Appwrite/Utopia/Response/Model/Log.php`

Add a `userType` field to the Log response model with:
- Description: "User type who triggered the audit log"
- Possible values: `user`, `admin`, `guest`, `keyProject`, `keyAccount`, `keyOrganization`

### 4. Include `userType` in all log response builders

All log listing endpoints must return the `userType` field from `$log['data']['userType'] ?? null`:

- `app/controllers/api/users.php` - include both `userType` and `mode`
- `app/controllers/api/messaging.php` - include `userType` (4 locations)
- `src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Documents/Logs/XList.php`
- `src/Appwrite/Platform/Modules/Databases/Http/Databases/Collections/Logs/XList.php`
- `src/Appwrite/Platform/Modules/Databases/Http/Databases/Logs/XList.php`
- `src/Appwrite/Platform/Modules/Databases/Http/TablesDB/Logs/XList.php`
- `src/Appwrite/Platform/Modules/Teams/Http/Logs/XList.php`

## Files to modify

- `app/init/constants.php` - define new constants, remove `ACTIVITY_TYPE_APP`
- `app/controllers/shared/api.php` - mode-based type assignment, API key mapping, mode access
- `src/Appwrite/Utopia/Response/Model/Log.php` - add `userType` field definition
- `app/controllers/api/users.php` - include `userType` and `mode` in log response
- `app/controllers/api/messaging.php` - include `userType` in log responses
- 5 XList.php files in Databases and Teams modules - include `userType` in log responses

See the AGENTS.md files for Appwrite's module structure and conventions.
