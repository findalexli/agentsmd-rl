# Fix missing warning banner in NoProjectsOnPaidOrgInfo

## Problem

The `NoProjectsOnPaidOrgInfo` component in `apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx` displays a warning `Admonition` banner when an organization is on a paid plan but has zero projects. Currently, the component always returns `null` and the banner never appears.

The component currently defines a `NoProjectsOnPaidOrgInfoProps` interface and accepts `organization` as a prop. However, no caller provides this prop, so `organization` is always `undefined`.

## Required Change

The component should use the `useSelectedOrganizationQuery` hook (importable from `@/hooks/misc/useSelectedOrganization`) to obtain the organization data internally, rather than receiving it via props. After the change, the component should take no parameters and have no props interface.

## Expected Result

- The `Admonition` banner renders correctly when the organization is eligible, displaying the organization's `plan.name` and a `Link` to billing settings
- The `NoProjectsOnPaidOrgInfoProps` interface is removed
- The component's existing plan-eligibility checks and project-count query logic remain intact
- All existing tests, linting (`pnpm run lint`), and formatting (`prettier`) continue to pass