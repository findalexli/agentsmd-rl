# Secure guest order access in the ecommerce template

## Problem

The ecommerce template's "Find My Order" feature (`/find-order`) is insecure. When a guest enters their email and order ID, the app directly navigates to `/orders/{id}?email={email}`, allowing anyone who knows (or guesses) an order ID and email to view order details. There is no verification step — the order page simply checks if the email matches. This makes the system vulnerable to order enumeration attacks where a malicious user could iterate through sequential order IDs.

## What needs to change

1. **Add an `accessToken` field to orders**: The ecommerce plugin's orders collection needs a unique, auto-generated token (UUID) created when an order is placed. This token acts as a secret that proves the requester has legitimate access.

2. **Return the `accessToken` from payment confirmation**: When Stripe confirms an order, the response should include the `accessToken` so the checkout flow can redirect the customer to their order with the token in the URL.

3. **Require `accessToken` for guest order access**: The order detail page should require both `email` and `accessToken` query parameters for guest access, not just the email. Logged-in users accessing their own orders should still work as before.

4. **Replace direct navigation with email verification**: The `FindOrderForm` should no longer navigate directly to the order page. Instead, it should call a server action that verifies the email/order match and sends an email containing a secure link (with the `accessToken`). The UI should show a "check your email" confirmation.

5. **Update checkout redirects**: Both `ConfirmOrder` and `CheckoutForm` components should pass the `accessToken` in the redirect URL after successful payment.

6. **Update the ecommerce README**: After making the code changes, update `templates/ecommerce/README.md` to document the new guest order access flow, the security model with `accessToken`, and how it prevents enumeration attacks. The access control section and guest checkout section should reflect the new behavior.

## Files to Look At

- `templates/ecommerce/src/plugins/index.ts` — ecommerce plugin configuration, where collection overrides are set
- `packages/plugin-ecommerce/src/payments/adapters/stripe/confirmOrder.ts` — Stripe payment confirmation handler
- `templates/ecommerce/src/app/(app)/(account)/orders/[id]/page.tsx` — order detail page with guest access logic
- `templates/ecommerce/src/components/forms/FindOrderForm/index.tsx` — the "find my order" form component
- `templates/ecommerce/src/components/checkout/ConfirmOrder.tsx` — post-checkout order confirmation redirect
- `templates/ecommerce/src/components/forms/CheckoutForm/index.tsx` — checkout form with payment redirect
- `templates/ecommerce/README.md` — template documentation covering access control and guest checkout
