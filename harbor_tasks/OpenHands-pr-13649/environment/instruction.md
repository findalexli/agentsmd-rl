# Task: Fix Duplicate Payment Successful Toast

## Problem

After completing a Stripe checkout, the "Payment successful" toast message is displayed **multiple times** instead of just once. This happens because the `useEffect` hook that shows the toast is re-firing on every re-render.

## Files to Modify

- `frontend/src/routes/billing.tsx` - The main billing page component
- `frontend/__tests__/routes/billing.test.tsx` - The test file (add new tests)

## What You Need to Do

The issue is in the `BillingSettingsScreen` component in `billing.tsx`. Look at the `useEffect` that handles the checkout status (`checkoutStatus === "success"`).

The problem is in the **dependency array** of that `useEffect`. Currently, it includes:
- `checkoutStatus` (primitive string - stable)
- `searchParams` (object - **unstable reference**)
- `setSearchParams` (function - potentially unstable)
- `t` (function - potentially unstable)
- `trackCreditsPurchased` (function - **unmemoized**)

When `searchParams` (the object) or `trackCreditsPurchased` have new references on every render, the effect re-fires, showing the toast multiple times.

## The Fix

**Extract primitive values outside the effect.** Instead of using the `searchParams` object in the dependency array:

1. Extract `amount` and `sessionId` as primitive strings **outside** the `useEffect`
2. Use those primitives (`amount`, `sessionId`) in the dependency array instead of the `searchParams` object
3. Remove the calls to `searchParams.get()` from inside the effect body

This follows the pattern where dependencies should be **stable primitives** rather than objects with unstable identity.

## Testing

Add tests to verify:
1. On checkout success: the success toast is displayed **exactly once** and `trackCreditsPurchased` is called with the correct arguments
2. On checkout cancel: the error toast is displayed **exactly once**

You will need to mock:
- `displaySuccessToast` and `displayErrorToast` from `#/utils/custom-toast-handlers`
- `trackCreditsPurchased` from `#/hooks/use-tracking`

## Requirements

Before considering this task complete:
- Run `npm run lint:fix` in the frontend directory and fix any issues
- Run `npm run build` in the frontend directory - it must succeed
- The billing tests must pass: `npm run test -- --run billing.test.tsx`

Per AGENTS.md: "If you've made changes to the frontend, you should run `cd frontend && npm run lint:fix && npm run build`"
