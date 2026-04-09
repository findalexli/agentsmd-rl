# Fix Duplicate Toast Messages in Billing Route

## Problem

The billing settings screen is showing duplicate "Payment successful" toast messages after users complete Stripe checkout. The toast appears multiple times instead of just once.

## Expected Behavior

After a user completes Stripe checkout and is redirected back to `/settings/billing?checkout=success&amount=25&session_id=xxx`, the success toast should display exactly once. The same applies to the cancellation flow with `?checkout=cancel`.

## Actual Behavior

The toast appears multiple times (2-4 times) rapidly after the redirect.

## Root Cause (Do Not Reveal in Solution)

The `useEffect` hook in the billing component has unstable dependencies in its dependency array. Specifically:
- `searchParams` is an object that gets a new reference on every render
- `trackCreditsPurchased` is a function that's not memoized

When either of these unstable values changes reference, React re-runs the effect, causing the toast to display multiple times.

## Files to Modify

- `frontend/src/routes/billing.tsx` - The billing route component

## Relevant Context

The billing route uses:
- `useSearchParams()` from React Router for URL parameters
- `React.useEffect()` for handling checkout redirect
- `displaySuccessToast()` and `displayErrorToast()` for showing messages
- `trackCreditsPurchased()` for analytics tracking

## Testing

The repo has existing tests in `frontend/__tests__/routes/billing.test.tsx`. You can run them with:

```bash
cd frontend && npm run test -- billing.test.tsx --run
```

## Steps to Fix

1. Identify the `useEffect` hook that handles checkout success/cancel in `billing.tsx`
2. Look at the dependency array - you'll likely see `searchParams` directly in the deps
3. Extract the URL parameter values (`amount`, `session_id`) as primitive strings **outside** the effect
4. Use these stable primitive values in the dependency array instead of the `searchParams` object
5. Keep the `checkoutStatus` extraction pattern consistent with the other params

## Verification

After your fix:
- The toast should display exactly once per checkout redirect
- The `useEffect` dependency array should contain primitive values (strings) rather than object references
- All existing tests should pass
- Frontend lint and type checks should pass (`npm run lint`, `npm run typecheck`)
