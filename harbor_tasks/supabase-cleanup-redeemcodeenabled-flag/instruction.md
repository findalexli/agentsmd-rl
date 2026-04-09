# chore: cleanup redeemCodeEnabled flag

## Problem

The Supabase Studio dashboard has a feature flag `redeemCodeEnabled` that controls whether the credit code redemption feature is visible to users. This feature flag is no longer needed as the feature is now fully launched and should be available to all users.

Currently, the code checks `useFlag('redeemCodeEnabled')` in two places:
1. `CreditCodeRedemption.tsx` - conditionally renders the redemption UI based on the flag
2. `redeem.tsx` - shows a "Code redemption coming soon" message when the flag is disabled

This creates a poor user experience where users might see a "coming soon" message or have the feature hidden when it should be available.

## Expected Behavior

The credit code redemption feature should always be visible and available. The feature flag checks should be removed and the feature should render unconditionally.

## Files to Look At

- `apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx` - Remove the `useFlag('redeemCodeEnabled')` hook call and the early return that hides the component when the flag is disabled
- `apps/studio/pages/redeem.tsx` - Remove the `useFlag('redeemCodeEnabled')` hook call and the conditional rendering that shows "Code redemption coming soon"; the organization cards should always render

## Notes

- Clean up the `useFlag` import from `common` in both files if it's no longer used
- The feature should work the same way as it does when the flag is enabled - just without the flag check
