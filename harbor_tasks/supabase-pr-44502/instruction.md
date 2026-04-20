# Instruction: Supabase Studio — Subscription Preview Currency Precision

## Context

You are working in the `supabase/supabase` monorepo. The relevant code lives in:
`apps/studio/components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx`

The `formatCurrency` utility (defined in `apps/studio/lib/helpers.ts`) formats numbers as USD currency strings. For amounts >= $0.01, it uses JavaScript's `Intl.NumberFormat` with `minimumFractionDigits: 2` and `maximumFractionDigits: 2`, meaning it always produces exactly 2 decimal places.

## The Bug

In the subscription upgrade preview dialog, two currency totals are displayed with incorrect precision:

1. **"Total per month (excluding other usage)"** — in the detailed breakdown table
2. **"Monthly invoice estimate"** — in the billing summary row

For example, a sum of `10.256` (dollars) is displayed as `"$10.00"` instead of `"$10.26"`. The display is stripping all decimal places before rendering, causing billing totals to appear wrong.

The root cause is that an intermediate rounding step happens before the value is passed to `formatCurrency`, stripping fractional cents that the formatter is designed to preserve.

## What Is Expected

`formatCurrency` should receive the raw monetary sum and format it with full 2-decimal precision. For amounts >= $0.01, `formatCurrency` always outputs exactly 2 decimal places (e.g., `10.256` → `"$10.26"`, `10.254` → `"$10.25"`, `10.005` → `"$10.01"`).

You can verify this by checking how `formatCurrency` behaves in `apps/studio/lib/helpers.ts` — it delegates to `Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', minimumFractionDigits: 2, maximumFractionDigits: 2 })`.

## How to Find the Problem

In `SubscriptionPlanUpdateDialog.tsx`, look at the two places where `subscriptionPreview?.breakdown?.reduce(...)` and `subscriptionPreview?.breakdown.reduce(...)` are used inside `formatCurrency` calls. These two reduce-sum expressions compute the billing totals, but something is wrapping them and stripping precision before the value reaches `formatCurrency`.

Check the git diff for this PR to see exactly what changed, or trace the value flow from each reduce to its surrounding expression.

## Verification

After making the change, the "Total per month" and "Monthly invoice estimate" displays will show correct 2-decimal precision (e.g., `$10.26` instead of `$10.00`).

Run the Studio tests to verify no regressions: `pnpm test:ci` from the `apps/studio` directory.

## Agent Configuration

This repo uses CLAUDE.md at the root and several SKILL.md files under `.claude/skills/`. Relevant configs:
- `.claude/CLAUDE.md` — monorepo structure, pnpm commands, Studio conventions
- `.claude/skills/studio-best-practices/SKILL.md` — component structure, TypeScript, state management
- `.claude/skills/studio-ui-patterns/SKILL.md` — UI patterns for Studio pages
- `.claude/skills/studio-testing/SKILL.md` — testing strategy and test file conventions
- `.claude/skills/studio-queries/SKILL.md` — React Query patterns
- `.claude/skills/studio-error-handling/SKILL.md` — error display patterns
- `.claude/skills/telemetry-standards/SKILL.md` — event tracking conventions
- `.github/copilot-instructions.md` — GitHub-specific guidance