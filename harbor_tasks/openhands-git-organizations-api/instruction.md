# Task: Add Git Organizations API Endpoint

## Problem

The OpenHands enterprise backend needs a new API endpoint to retrieve git organizations for the current user from their connected git provider (GitHub, GitLab, or Bitbucket).

Currently, there's no way to get the list of organizations/groups/workspaces a user belongs to in their connected git provider. This is needed for features like repository discovery and organization-scoped operations.

## What You Need to Do

Implement an API endpoint that:

1. **Returns organizations for the authenticated user** - Given a user's provider tokens, fetch their organizations from the appropriate git provider
2. **Supports multiple providers** - GitHub, GitLab, and Bitbucket each have different APIs for fetching organizations:
   - GitHub: Get organizations from app installations
   - GitLab: Get user's groups from the GitLab API
   - Bitbucket: Get workspaces from installations
3. **Returns proper error handling** - Return 400 for unsupported providers, 401 when no tokens available
4. **Returns structured response** - Response should include provider name and list of organization identifiers

## Expected Behavior

The endpoint should:
1. Check for provider tokens, fall back to IDP if none (existing pattern in similar endpoints)
2. Determine which provider is active (SaaS users sign in with one provider at a time)
3. Fetch organizations from the appropriate provider:
   - For GitHub: delegate to a method on the provider handler that calls `get_organizations_from_installations` on the GitHub service
   - For GitLab: delegate to a method on the provider handler that calls `get_user_groups` on the GitLab service to get the user's groups
   - For Bitbucket: delegate to a method that retrieves workspaces from installations
4. Return JSON like: `{"provider": "github", "organizations": ["org1", "org2"]}`

## API Contract

The following components are expected:

- An async endpoint handler `saas_get_user_git_organizations` at `GET /git-organizations` in the enterprise server user routes
- A `get_user_groups` method on the GitLab service that fetches groups via the GitLab `/groups` API and returns a list of group path strings (e.g., `['my-team', 'open-source']`)
- Methods `get_github_organizations` and `get_gitlab_groups` on the provider handler that delegate to the appropriate service and return empty lists on error

## Testing

The implementation should include tests similar to existing patterns in the codebase:
- Mock external API calls (don't make real network requests)
- Test both success and error cases
- Test each provider type separately
- Test the error case for unsupported providers (Azure DevOps)

## References

Look at existing endpoints in the enterprise server routes for patterns on how to structure the endpoint, handle authentication, and return responses. The response should be a JSON object with `provider` and `organizations` keys.

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `ruff format and ruff check`
