# Task: Update LoginCTA Component for Device Verification Page

## Problem

The device verification page currently uses an `EnterpriseBanner` component. We need to replace it with the `LoginCTA` component, but the `LoginCTA` needs a new `source` prop to handle different behaviors:

1. When `source="device_verify"`: The "Learn More" button should link to `https://openhands.dev/enterprise` in a new tab
2. When `source="login_page"` (default): The "Learn More" button should continue routing to `/information-request` using the internal router

Additionally, the layout needs updating so the CTA card stretches to match the height of the device authorization card on larger screens.

## Files to Modify

1. `frontend/src/components/features/auth/login-cta.tsx` - Add `source` prop with device_verify behavior
2. `frontend/src/routes/device-verify.tsx` - Replace EnterpriseBanner with LoginCTA

## Requirements

- Add a `source` prop to `LoginCTA` with values `"login_page" | "device_verify"`
- When source is `"device_verify"`, use an external `<a>` tag with:
  - `href="https://openhands.dev/enterprise"`
  - `target="_blank"`
  - `rel="noopener noreferrer"`
- When source is `"login_page"`, use the existing `<Link>` to `/information-request`
- Track the location properly: `trackSaasSelfhostedInquiry({ location: source })`
- Update layout classes to support card stretching:
  - Container should use `lg:items-stretch`
  - Device card should have `rounded-2xl` and `border-[#242424]`
  - LoginCTA should receive `className="lg:self-stretch"` when used on device-verify
- Refactor the button classes into a shared constant

## Testing

Run the following to verify your changes:
- `cd frontend && npm run test` - Run unit tests
- `cd frontend && npm run lint` - Check linting
- `cd frontend && npx tsc --noEmit` - Type check

The existing tests expect the `LoginCTA` component to be found by `data-testid="login-cta"` on the device verification page when the feature flag is enabled.
