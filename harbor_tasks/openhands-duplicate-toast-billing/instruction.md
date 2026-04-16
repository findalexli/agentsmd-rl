# Fix Duplicate Payment Toast in Billing Component

## Problem Description

In the billing settings page (`frontend/src/routes/billing.tsx`), users are seeing duplicate toast notifications after completing or canceling a Stripe checkout. Toasts appear multiple times instead of just once.

## Steps to Reproduce

1. Navigate to `/settings/billing?checkout=success&amount=25&session_id=sess_123`
2. Observe that the success toast notification appears more than once

## Expected Behavior

After the fix, all of the following must hold:

1. **Success toast displays exactly once** when `checkout=success` is in the URL query parameters — the test case named `"should display success toast exactly once"` must pass
2. **Error toast displays exactly once** when `checkout=cancel` is in the URL query parameters — the test case named `"should display error toast exactly once"` must pass
3. **Credits tracking fires exactly once** on checkout success — the test case named `"track credits on checkout success"` must pass
4. The component still renders the payment form — the test case `"renders the payment form"` must pass

## Code Structure Requirements

The tests verify that the component extracts the `amount` and `session_id` URL query parameters as local constants before the `useEffect` that handles checkout callbacks, and uses those extracted primitives (not the query parameter object) in the effect's dependency array. This ensures the effect runs exactly once per checkout completion.

Do not modify the test file.
