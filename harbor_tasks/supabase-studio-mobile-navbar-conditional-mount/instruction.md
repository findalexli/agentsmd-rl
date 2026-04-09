# Mobile Navigation Bar Mounts Unnecessarily on Desktop

## Problem

The `MobileNavigationBar` component in Studio is always mounted on desktop viewports, even though it's visually hidden with CSS (`md:hidden`). This causes unnecessary data fetching - specifically, the component triggers org/project queries that consume resources even when the user will never see the mobile navigation.

When viewing Studio on a desktop browser, the `MobileNavigationBar` component:
1. Mounts to the DOM (wastes render cycles)
2. Fires React Query hooks for organization and project data
3. Uses up network bandwidth and CPU for data the user never sees

## Expected Behavior

The `MobileNavigationBar` should only mount when the viewport is at or below the `md` breakpoint (mobile/tablet). This prevents unnecessary data fetching and improves desktop performance.

Use the `useBreakpoint('md')` hook from the `common` package to detect mobile viewport size. This hook returns `true` when the viewport is at or below the specified breakpoint.

## Files to Look At

- `apps/studio/components/layouts/DefaultLayout.tsx` — The base layout component that renders `MobileNavigationBar`. Look for where `MobileNavigationBar` is rendered and wrap it with a conditional based on viewport size.
- `apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx` — The mobile nav component that does the unnecessary data fetching (for reference, don't modify this file).

## Implementation Notes

The `common` package exports a `useBreakpoint` hook that takes a breakpoint name ('sm', 'md', 'lg', 'xl'). Import it alongside `useParams`:

```typescript
import { LOCAL_STORAGE_KEYS, useBreakpoint, useParams } from 'common'
```

Then use it in the component:

```typescript
const isMobile = useBreakpoint('md')
```

Wrap the `MobileNavigationBar` component with a conditional render:

```tsx
{isMobile && (
  <MobileNavigationBar
    hideMobileMenu={hideMobileMenu}
    backToDashboardURL={backToDashboardURL}
  />
)}
```

Keep `LayoutHeader` rendering unconditionally - it should appear on all viewports.
