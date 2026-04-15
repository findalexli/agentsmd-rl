# Fix missing warning banner in NoProjectsOnPaidOrgInfo

## Problem

The `NoProjectsOnPaidOrgInfo` component in `apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx` should display a warning `Admonition` banner when an organization is on a paid plan but has zero projects. Currently the component returns `null` and the banner never appears.

## Expected Behavior

The component must:

1. Render an `Admonition` banner from `ui-patterns` (imported as `import { Admonition } from 'ui-patterns'`)
2. Import and use `Link` from `next/link`
3. Check whether the current organization is on a paid plan (i.e., its `plan.id` is not one of: `free`, `platform`, `enterprise`)
4. Display the organization's `plan.name` in the banner
5. Provide a link to billing settings

The eligibility check uses `isEligible = organization != null && !EXCLUDED_PLANS.includes(organization.plan.id ?? '')`, where `EXCLUDED_PLANS = ['free', 'platform', 'enterprise']`.

The project count is obtained via `useOrgProjectsInfiniteQuery`.

## Constraints

- The component's parameter list must not include `organization` as a destructured prop
- No `NoProjectsOnPaidOrgInfoProps` interface should be present
- The `EXCLUDED_PLANS` array and `isEligible` logic must remain unchanged