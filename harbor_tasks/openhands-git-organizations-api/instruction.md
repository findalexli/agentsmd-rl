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
   - For GitLab: delegate to a method on the provider handler that calls `get_user_groups` on the GitLab service (use `min_access_level=10` to get all groups)
   - For Bitbucket: delegate to a method that retrieves workspaces from installations
4. Return JSON like: `{"provider": "github", "organizations": ["org1", "org2"]}`

## Implementation Details to Implement

The implementation must provide the following as implementable components:

- A handler function `saas_get_user_git_organizations` exposed at `GET /git-organizations` in the enterprise server user routes (importable as `server.routes.user`)
- On the GitLab service: a method `get_user_groups` that fetches user groups via the GitLab `/groups` API with parameters `min_access_level` and `per_page` — both passed as **string** values (e.g., `{'min_access_level': '10', 'per_page': '100'}`)
- On the provider handler: methods `get_github_organizations` and `get_gitlab_groups` that delegate to the appropriate service for each provider type
- For the GitLab groups API: the response should return the `path` field from each group dict

## Testing

The implementation should include tests similar to existing patterns in the codebase:
- Mock external API calls (don't make real network requests)
- Test both success and error cases
- Test each provider type separately
- Test the error case for unsupported providers (Azure DevOps)

## References

Look at existing endpoints in the enterprise server routes for patterns on how to structure the endpoint, handle authentication, and return responses. The response should be a JSON object with `provider` and `organizations` keys.