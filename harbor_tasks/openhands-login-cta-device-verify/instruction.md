# Task: Update LoginCTA Component for Device Verification Page

## Problem

The device verification page currently uses an `EnterpriseBanner` component. It needs to use the `LoginCTA` component instead, but `LoginCTA` currently only supports internal routing for the "Learn More" button. The component needs to handle two different behaviors:

1. **When used on the device verification page**: The "Learn More" button should link to `https://openhands.dev/enterprise` in a new tab using an `<a>` tag with `target="_blank"` and `rel="noopener noreferrer"`. The implementation should include a comment explaining that `<a>` is used for external destinations while react-router `<Link>` is for internal routes.
2. **When used on the login page** (default/current behavior): The "Learn More" button should continue routing to `/information-request` using the internal router `<Link>` component.

Additionally, the layout on the device verification page needs updating so the CTA card stretches to match the height of the device authorization card on larger screens.

## Requirements

### LoginCTA Component Changes (`frontend/src/components/features/auth/login-cta.tsx`)

The following specific implementation details must be present:

1. **Accept a `source` prop** with type `type LoginCTAProps` allowing values `"login_page" | "device_verify"`. The default value should be `"login_page"`.

2. **Accept a `className` prop** that gets merged with the existing card classes.

3. **Track location based on source**: When tracking analytics via `trackSaasSelfhostedInquiry`, the `location` field should reflect the source value (either `"login_page"` or `"device_verify"`).

4. **Handle link rendering differently based on source**:
   - When source is `"device_verify"`: Use an `<a>` tag (external link) with:
     - `href` set to a constant named `ENTERPRISE_URL` with value `"https://openhands.dev/enterprise"`
     - `target="_blank"`
     - `rel="noopener noreferrer"`
   - When source is `"login_page"`: Use the existing `<Link>` component to `/information-request` (internal router navigation)
   - The conditional logic should use a variable named `isDeviceVerifySource` to determine which link type to render
   - Include the comment: `Use <a> for external destination; react-router <Link> is only for internal app routes.`

5. **Layout adjustments**:
   - The card's inner content container should stretch to fill available height using `h-full`
   - The button container should use `mt-auto` to push the button to the bottom
   - The "Learn More" button classes should be refactored into a shared variable (e.g., `learnMoreButtonClassName`) used by both the `<a>` and `<Link>` render paths

### Device Verify Page Changes (`frontend/src/routes/device-verify.tsx`)

1. **Replace EnterpriseBanner with LoginCTA**:
   - Remove the import of `EnterpriseBanner` from `#/components/features/device-verify/enterprise-banner`
   - Remove the usage of `<EnterpriseBanner />` component
   - Add import for `LoginCTA` from `#/components/features/auth/login-cta`
   - Render `<LoginCTA />` in place of where `EnterpriseBanner` was, passing `source="device_verify"` and `className="lg:self-stretch"`

2. **Layout class updates**: The flex container and cards should stretch to equal height:
   - The container flex row should use `lg:items-stretch` instead of `lg:items-start`
   - The device authorization card should use `rounded-2xl` and `border-[#242424]` for its styling
   - The device authorization card should also have `lg:self-stretch` when the enterprise banner is shown

## Testing

Run the following to verify your changes:
- `cd frontend && npm run test` - Run unit tests
- `cd frontend && npm run lint` - Check linting
- `cd frontend && npm run typecheck` - Type check
- `cd frontend && npm run build` - Production build

The tests expect the `LoginCTA` component to be found by `data-testid="login-cta"` on the device verification page when the feature flag is enabled.
