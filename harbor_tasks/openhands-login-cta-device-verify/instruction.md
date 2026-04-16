# Task: Update LoginCTA Component for Device Verification Page

## Problem

The device verification page currently uses an `EnterpriseBanner` component. It needs to use the `LoginCTA` component instead, but `LoginCTA` currently only supports internal routing for the "Learn More" button. The component needs to handle two different behaviors:

1. **When used on the device verification page**: The "Learn More" button should link to `https://openhands.dev/enterprise` in a new tab. The implementation should explain the distinction between external links and internal router links.
2. **When used on the login page** (default/current behavior): The "Learn More" button should continue routing to `/information-request` using the internal router.

Additionally, the layout on the device verification page needs updating so the CTA card stretches to match the height of the device authorization card on larger screens.

## Requirements

### LoginCTA Component Changes (`frontend/src/components/features/auth/login-cta.tsx`)

1. **Accept a `source` prop** with type allowing values `"login_page"` and `"device_verify"`. The default should be `"login_page"`.

2. **Accept a `className` prop** that gets merged with the existing card classes.

3. **Track location based on source**: When tracking analytics via `trackSaasSelfhostedInquiry`, the `location` field should reflect the source value.

4. **Handle link rendering differently based on source**:
   - When source indicates device verification: Use an `<a>` tag for the external enterprise URL with appropriate security attributes (`target="_blank"` and `rel="noopener noreferrer"`). Document the reason for using `<a>` vs the router's `<Link>` component.
   - When source indicates login page: Use the router's `<Link>` component to `/information-request`
   - The conditional logic should be clearly structured for maintainability

5. **Layout adjustments**:
   - The card's inner content container should stretch to fill available height
   - The button container should be pushed to the bottom of the available space
   - Share button styling between the two link render paths

### Device Verify Page Changes (`frontend/src/routes/device-verify.tsx`)

1. **Replace EnterpriseBanner with LoginCTA**:
   - Remove the `EnterpriseBanner` component import and usage
   - Import and render `LoginCTA` in place of `EnterpriseBanner`, passing appropriate props for the device verification context and layout

2. **Layout class updates**: The flex container and cards should stretch to equal height on larger screens:
   - Update container alignment for stretching
   - Apply rounded styling and appropriate border color to the device authorization card
   - Ensure cards can stretch to equal height when the CTA is shown

## Testing

Run the following to verify your changes:
- `cd frontend && npm run test` - Run unit tests
- `cd frontend && npm run lint` - Check linting
- `cd frontend && npm run typecheck` - Type check
- `cd frontend && npm run build` - Production build

The tests expect the `LoginCTA` component to be found by `data-testid="login-cta"` on the device verification page when the feature flag is enabled.