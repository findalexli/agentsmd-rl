# Add "Upgrade to Pro" Button to Dashboard Header

## Problem

The Supabase Studio dashboard has no always-visible upgrade call-to-action for users on the free plan. There is currently no way to surface an upgrade prompt in the main header navigation, which means free-plan users may miss upgrade opportunities while using the dashboard.

## Expected Behavior

Add a new `HeaderUpgradeButton` component to `apps/studio/components/layouts/Navigation/LayoutHeader/HeaderUpgradeButton.tsx` that:

1. Displays an "Upgrade to Pro" button in the dashboard header for free-plan users only (check `organization.plan.id === 'free'`)
2. Is gated behind a PostHog experiment with ID `headerUpgradeCta` — only the `test` variant shows the button; the `control` variant is tracked but shows nothing
3. Tracks experiment exposure for all free-plan users in the experiment (both control and test variants)
4. Tracks a click telemetry event named `header_upgrade_cta_clicked` when the button is clicked
5. Reuses the existing `UpgradePlanButton` component (which needs a new `onClick` callback prop) for routing, permissions, and billing logic

The button should appear in both the desktop `LayoutHeader` and the `MobileNavigationBar`.

## Telemetry Requirements

The click telemetry event must follow these conventions:

- **Event name**: `header_upgrade_cta_clicked` (snake_case, follows `[object]_[verb]` pattern)
- **Approved verbs**: `opened`, `clicked`, `submitted`, `created`, `removed`, `updated`, `intended`, `evaluated`, `added`, `enabled`, `disabled`, `copied`, `exposed`, `failed`, `converted`, `closed`, `completed`, `applied`, `sent`, `moved`
- **Hook**: Use `useTrack` from `@/lib/telemetry/track` (not the deprecated `useSendEventMutation`)
- **Interface name**: `HeaderUpgradeCtaClickedEvent`
- **Interface location**: `packages/common/telemetry-constants.ts`
- **JSDoc**: Interface must have a `@group Events` JSDoc annotation
- **Union type**: The interface must be added to the `TelemetryEvent` union type in the same file
- **Interface shape**:
  ```typescript
  export interface HeaderUpgradeCtaClickedEvent {
    action: 'header_upgrade_cta_clicked'
    groups: Omit<TelemetryGroups, 'project'>
  }
  ```

## Files to Look At

- `apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx` — Desktop header layout where the button should be added
- `apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx` — Mobile navigation bar where the button should also appear
- `apps/studio/components/ui/UpgradePlanButton.tsx` — Existing upgrade button component to reuse (add an `onClick?: () => void` prop and forward it to the rendered Button)
- `packages/common/telemetry-constants.ts` — Where telemetry event interfaces are defined
- `apps/studio/hooks/ui/useFlag.ts` — PostHog feature flag hook (`usePHFlag`)
- `apps/studio/hooks/misc/useTrackExperimentExposure.ts` — Experiment exposure tracking hook
- `apps/studio/lib/telemetry/track.ts` — Telemetry tracking hook (`useTrack`)
