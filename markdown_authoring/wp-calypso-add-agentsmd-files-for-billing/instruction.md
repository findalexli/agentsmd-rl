# Add AGENTS.md files for Billing & Payments directories

Source: [Automattic/wp-calypso#108838](https://github.com/Automattic/wp-calypso/pull/108838)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `client/AGENTS.md`
- `client/dashboard/AGENTS.md`
- `client/dashboard/me/billing-purchases/AGENTS.md`
- `client/dashboard/me/billing-purchases/CLAUDE.md`
- `client/me/purchases/AGENTS.md`
- `client/me/purchases/CLAUDE.md`
- `client/my-sites/checkout/AGENTS.md`
- `client/my-sites/checkout/CLAUDE.md`

## What to add / change

Part of SHILL-1666

## Proposed Changes

* Rewrite `client/AGENTS.md` from a generic coding assistant prompt into a focused AGENTS.md guide: general section (architecture overview, commands, conventions). Billing content lives in spoke files, not here.
* Add `client/my-sites/checkout/AGENTS.md` — checkout spoke: 3 hard-coded steps, 4 state systems, payment processing paths, package boundaries, 7-step payment method addition guide, 11 pitfalls
* Add `client/dashboard/me/billing-purchases/AGENTS.md` — Dashboard billing spoke: architecture context (snake_case Purchase type, query keys, API layer), cancel purchase flow (3 flow types with silent `flowType` override), payment method factory pattern, sibling directory traps, 8 pitfalls
* Add `client/me/purchases/AGENTS.md` — Classic purchases spoke: architecture context (camelCase Purchase type), two cancel paths (cancel vs remove), `canAutoRenewBeTurnedOff` name-lie, Redux selector loading traps, 10 pitfalls
* Add companion `CLAUDE.md` files (`@AGENTS.md`) for auto-loading via chain mechanism
* Add sub-bullets to root `AGENTS.md` for billing area discoverability

## Why are these changes being made?

AI coding agents working in billing directories had no project-specific guidance, leading to repeated mistakes: copying logic between Classic and Dashboard without field name conversion (camelCase vs snake_case), putting queries in `client/dashboard/` instead of `packages/api-queries/`, conflating the three cancel flow types, and missi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
