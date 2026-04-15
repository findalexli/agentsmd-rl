# Fix Duplicate Toast Messages in Billing Route

## Problem

The billing settings screen is showing duplicate "Payment successful" toast messages after users complete Stripe checkout. The toast fires multiple times (2-4 times) instead of exactly once. The same duplication issue affects the cancellation toast when users cancel checkout.

## Context

The billing route component at `frontend/src/routes/billing.tsx` handles Stripe checkout redirects. After a successful checkout, the user is redirected to a URL like:

```
/settings/billing?checkout=success&amount=25&session_id=xxx
```

The component reads URL parameters using `useSearchParams()` from React Router. The parameter-to-variable naming convention used in this component is:

- `checkout` parameter → variable `checkoutStatus`
- `amount` parameter → variable `amount`
- `session_id` parameter → variable `sessionId` (note: camelCase)

## Requirements

1. The success toast must display exactly **once** after a successful checkout redirect
2. The error toast must display exactly **once** after a cancelled checkout redirect
3. Analytics tracking (`trackCreditsPurchased`) must fire exactly once with the correct `amountUsd` and `stripeSessionId`
4. The URL parameter variables must be named `checkoutStatus`, `amount`, and `sessionId` respectively

## Verification

After your fix, all of the following must pass:

```bash
cd frontend && npm run test -- billing.test.tsx --run
cd frontend && npm run lint
cd frontend && npm run typecheck
cd frontend && npm run build
```
