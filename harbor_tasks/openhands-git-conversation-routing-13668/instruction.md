Add a "Git Conversation Routing" section to the organization management page that allows admins and owners to claim and disconnect GitHub/GitLab organizations.

## What to Build

Create a new section on the manage organization page where users with appropriate permissions can view and manage Git organization claims. The section should display a list of organizations from GitHub/GitLab with buttons to claim or disconnect them.

## Requirements

### New Components (in `frontend/src/components/features/org/`)

1. **claim-button.tsx** - A stateful button component that handles the claim/disconnect actions:
   - Shows "Claim" for unclaimed orgs (dark/black style)
   - Shows "Claimed" for claimed orgs (green style)
   - Shows "Disconnect" on hover of claimed orgs (red style)
   - Disabled state during transitions (claiming/disconnecting)
   - Export `getButtonState` helper function for determining button state

2. **git-org-row.tsx** - A row component displaying an organization:
   - Shows provider/name (e.g., "GitHub/OpenHands")
   - Includes the ClaimButton for actions
   - Proper styling with border separators

3. **git-conversation-routing.tsx** - Main section component:
   - Title and description text
   - Renders list of GitOrgRow components
   - Uses the custom hook for data and actions

### New Hook (in `frontend/src/hooks/organizations/`)

**use-git-conversation-routing.ts** - Custom hook managing org data:
- Define `GitOrg` interface with id, provider (GitHub/GitLab), name, and status
- Status types: "unclaimed", "claimed", "claiming", "disconnecting"
- `claimOrg(id)` function - handles claiming with async simulation
- `disconnectOrg(id)` function - handles disconnecting with async simulation
- For now, use mock data and simulated async behavior (setTimeout)

### Integration

1. **permissions.ts** - Add `manage_org_claims` permission:
   - Add to PermissionKey union type
   - Include in adminOnly permissions array

2. **manage-org.tsx** - Render the new section:
   - Import GitConversationRouting component
   - Check `manage_org_claims` permission
   - Conditionally render behind feature flag check

3. **i18n** - Add translation keys in `declaration.ts` and `translation.json`:
   - ORG$GIT_CONVERSATION_ROUTING (section title)
   - ORG$GIT_CONVERSATION_ROUTING_DESCRIPTION
   - ORG$CLAIM, ORG$CLAIMED, ORG$DISCONNECT (button labels)
   - ORG$CLAIM_SUCCESS, ORG$DISCONNECT_SUCCESS, ORG$CLAIM_ERROR (toasts)
   - Support 15 locales (en, ja, zh-CN, zh-TW, ko-KR, no, it, pt, es, ar, fr, tr, de, uk, ca)

## Key Technical Details

- Use existing project patterns (Tailwind CSS classes, i18n with I18nKey enum)
- Follow the existing code style in the frontend directory
- The component should be gated by both permission check and feature flag
- Use `displaySuccessToast` and `displayErrorToast` from custom-toast-handlers for notifications
- Reference existing components like `delete-org-confirmation-modal` for patterns

## Testing

After implementing, run `npm run test` in the frontend directory to verify the existing test suite passes. The repository has unit tests that validate component behavior.
