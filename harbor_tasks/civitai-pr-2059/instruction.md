# Task: Prevent Civitai Staff Impersonation

## Problem Statement

Civitai is experiencing issues with users creating accounts with usernames that impersonate staff members. These impersonation attempts use variations of "civit" (the company name) including:
- Direct substrings like `civitmod`, `the_civit_team`
- Leet-speak variants where characters are substituted (such as `1` for `i` or `0` for `o`), e.g., `c1vitai`, `civ1tai`

The current username blocklist only contains general offensive terms but does not specifically block these Civitai-specific impersonation patterns.

## Observable Behavior

### Current Problem
When a user attempts to register with a username containing "civit" or its variants (case-insensitive), the registration succeeds when it should be rejected.

### Expected Behavior
Usernames containing impersonating variations of "civit" should be rejected at registration. The username availability check should return `false` for these usernames.

## Technical Context

The username blocklist is defined in `src/utils/blocklist-username.json`. This JSON file has two arrays:
- `partial`: Array of substrings - any username containing these should be rejected
- `exact`: Array of exact matches - usernames exactly matching these should be rejected

The username permission check is performed by the `isUsernamePermitted` function in `src/server/services/user.service.ts`.

## Requirements

1. **Block impersonating usernames**: The blocklist must prevent registration of usernames that contain or are variants of "civit" (case-insensitive), including common character-substitution variations used in impersonation attempts.

2. **Preserve existing functionality**: Ensure the blocklist's existing entries (such as exact match `"civitai"`) continue to work correctly.

## Verification

After your changes, the following usernames must be REJECTED:
- `civitmod`, `civitai_support`, `the_civit_team`, `Civit`, `CIVITADMIN`
- `c1vitai`, `civ1tai`, `c1v1tai`, `C1VIT_staff`, `xCIV1Tx`

The following usernames must be ALLOWED:
- `alice`, `bob_123`, `ModelMaker99`, `PixelArtist`
- `civic`, `civil` (these do not contain impersonating variants)

## Implementation Notes

- The blocklist is case-insensitive (matching is done with `username.toLowerCase()`)
- The `partial` array uses substring matching
- Changes should be made only to `src/utils/blocklist-username.json`
- Run `pnpm run typecheck` to verify TypeScript compilation succeeds