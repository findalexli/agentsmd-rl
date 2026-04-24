# Task: Add New V1 User Git Info Endpoint

## Problem

The OpenHands project is deprecating old V0 API endpoints and migrating to V1 endpoints. User git information is currently available via an old endpoint, but a new V1 endpoint needs to be created to replace it.

## What You Need to Do

Create a new API endpoint at `GET /api/v1/users/git-info` that returns user git information. The existing endpoint should continue to work for backwards compatibility.

### Requirements

1. **New endpoint behavior**: The new endpoint at `GET /api/v1/users/git-info` should:
   - Return user metadata including: a user ID, login name, avatar URL, and optionally company, name, and email
   - Return HTTP 401 Unauthorized when the user is not authenticated (error message should contain "Not authenticated")

2. **Model requirements**: The response model should be a Pydantic model with these fields:
   - `id` (str, required)
   - `login` (str, required)
   - `avatar_url` (str, required)
   - `company` (str, optional, defaults to None)
   - `name` (str, optional, defaults to None)
   - `email` (str, optional, defaults to None)

   The model class must be named `UserGitInfo` and must be importable from `openhands.integrations.service_types`.

3. **Endpoint implementation**: The endpoint handler must be an async function named `get_current_user_git_info` importable from `openhands.app_server.user.user_router`. It must return `UserGitInfo` and raise `HTTPException(401, detail="Not authenticated")` when the user is not authenticated.

4. **Backwards compatibility**: A type alias `User` must be available from `openhands.integrations.service_types` that refers to `UserGitInfo` so existing code continues to work.

5. **User context integration**: The `get_user_git_info` method must be added to the following classes:
   - `UserContext` in `openhands.app_server.user.user_context` — decorated with `@abstractmethod`, returns `UserGitInfo | None`
   - `SpecifyUserContext` in `openhands.app_server.user.specifiy_user_context` — returns `UserGitInfo | None`
   - `AuthUserContext` in `openhands.app_server.user.auth_user_context` — async method that returns `UserGitInfo | None`
   - `UserAuth` in `openhands.server.user_auth.user_auth` — async method that returns `UserGitInfo | None`

6. **Deprecation**: The old `/info` endpoint in `openhands.server.routes.git` should be marked as deprecated in the FastAPI router by adding `deprecated=True` to its route decorator.

### Testing Notes

The repository uses pytest for backend testing. After implementing the changes:
- The new `UserGitInfo` model should be importable from `openhands.integrations.service_types`
- The `get_current_user_git_info` function should be importable from `openhands.app_server.user.user_router`
- The endpoint should return 401 when not authenticated
- The old endpoint should remain functional with a deprecation flag
- The `User` alias should work for existing code
- All user context classes should have the `get_user_git_info` method

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `mypy (Python type checker)`
