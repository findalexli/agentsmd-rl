# Add "Upgrade to Pro" Button to Dashboard Header

## Problem

The Supabase Studio dashboard has no always-visible upgrade call-to-action for users on the free plan. There is currently no way to surface an upgrade prompt in the main header navigation, which means free-plan users may miss upgrade opportunities while using the dashboard.

## Expected Behavior

Add a new `HeaderUpgradeButton` component that:

1. Displays an "Upgrade to Pro" button in the dashboard header for free-plan users only
2. Is gated behind a PostHog experiment (`headerUpgradeCta`) with `control` and `test` variants — only `test` variant users see the button
3. Tracks experiment exposure for all free-plan users in the experiment (both control and test)
4. Tracks a click telemetry event when the button is clicked
5. Reuses the existing `UpgradePlanButton` component for routing, permissions, and billing logic

The button should appear in both the desktop `LayoutHeader` and the `MobileNavigationBar`.

## Files to Look At

- `apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx` — Desktop header layout where the button should be added
- `apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx` — Mobile navigation bar where the button should also appear
- `apps/studio/components/ui/UpgradePlanButton.tsx` — Existing upgrade button component to reuse (may need modification to support click callbacks)
- `packages/common/telemetry-constants.ts` — Where telemetry event interfaces are defined
- `apps/studio/hooks/ui/useFlag.ts` — PostHog feature flag hook
- `apps/studio/hooks/misc/useTrackExperimentExposure.ts` — Experiment exposure tracking hook
