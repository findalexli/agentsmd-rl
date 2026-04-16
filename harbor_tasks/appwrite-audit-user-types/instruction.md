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
| `ACTIVITY_TYPE_ADMIN` | `'admin'` | Console admin operating in `APP_MODE_ADMIN` mode |
| `ACTIVITY_TYPE_GUEST` | `'guest'` | Unauthenticated guest user |
| `ACTIVITY_TYPE_KEY_PROJECT` | `'keyProject'` | Standard/dynamic project-scoped API key |
| `ACTIVITY_TYPE_KEY_ACCOUNT` | `'keyAccount'` | Account-scoped API key |
| `ACTIVITY_TYPE_KEY_ORGANIZATION` | `'keyOrganization'` | Organization-scoped API key |

Remove the old `ACTIVITY_TYPE_APP` constant.

### 2. Update `app/controllers/shared/api.php`

**Mode-based user type assignment:** When setting the audit user type for authenticated users, the code must determine whether the request is in admin mode and assign the appropriate activity type constant (`ACTIVITY_TYPE_ADMIN` for admin mode, `ACTIVITY_TYPE_USER` for regular users).

**Existing type preservation:** User type values that are already set on the user object should not be overwritten by subsequent type assignments.

**API key type mapping:** API keys have three types that must map to their corresponding activity types:
- `API_KEY_STANDARD` → `ACTIVITY_TYPE_KEY_PROJECT`
- `API_KEY_ACCOUNT` → `ACTIVITY_TYPE_KEY_ACCOUNT`
- `API_KEY_ORGANIZATION` → `ACTIVITY_TYPE_KEY_ORGANIZATION`

**Mode parameter access:** The API controller action must have access to the current application mode to determine if the request is in admin context.

### 3. Update `src/Appwrite/Utopia/Response/Model/Log.php`

Add a `userType` field to the Log response model. The field must have:
- Description: "User type who triggered the audit log. Possible values: user, admin, guest, keyProject, keyAccount, keyOrganization."

### 4. Include `userType` in all log response builders

All log listing endpoints must return the `userType` field from the log data:

- `app/controllers/api/users.php` - include both `userType` and `mode` fields
- `app/controllers/api/messaging.php` - include `userType` field in 4 locations
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
