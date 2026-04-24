# Cleanup redeemCodeEnabled Feature Flag

## Problem

The Supabase Studio dashboard has a feature flag `redeemCodeEnabled` that gates the credit code redemption feature. This flag is no longer needed as the feature is fully launched and should be available to all users.

Currently, when the flag is disabled:
- The credit code redemption component is hidden entirely in billing settings
- Users see a "Code redemption coming soon" message on the redeem credits page instead of the organization listing

This creates a poor user experience where users might see a "coming soon" message or have the feature hidden when it should always be available.

## Expected Behavior

The credit code redemption feature should always be visible and available to all users. There should be no feature flag gating — the redemption UI should render unconditionally with no remaining references to `redeemCodeEnabled`. Any imports that become unused as a result of this cleanup should also be removed.

## Relevant Files

- `apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx`
- `apps/studio/pages/redeem.tsx`

## Notes

- The feature should work exactly as it does when the flag is enabled — the CreditCodeRedemption component must still render its Dialog UI, and the redeem page must still render the organization listing

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
