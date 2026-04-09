# fix(studio): use hook for org in NoProjectsOnPaidOrgInfo

## Problem

The `NoProjectsOnPaidOrgInfo` component in the billing section is supposed to show a warning banner when an organization is on a paid plan but has no projects. However, the component is not receiving the `organization` prop from its parent, causing it to always return `null` and never display the banner.

This was a follow-up fix to a previous PR where the prop wasn't actually being wired through the component tree.

## Expected Behavior

The component should display an `Admonition` banner when:
1. The current organization is on a paid plan (not 'free', 'platform', or 'enterprise')
2. The organization has 0 projects

The banner should display the organization's plan name and provide a link to billing settings.

## Files to Look At

- `apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx` — Component that displays the warning banner

## Notes

- The component currently receives `organization` as a prop but it's not being passed in by parent components
- Consider using data fetching hooks available in the studio codebase to get the current organization
- The component should still use `useOrgProjectsInfiniteQuery` to check project count
- Keep the `EXCLUDED_PLANS` logic unchanged
