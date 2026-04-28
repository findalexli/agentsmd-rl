# AI: Consolidate Claude and Cursor rules into AGENTS.md

Source: [Automattic/wp-calypso#108787](https://github.com/Automattic/wp-calypso/pull/108787)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/e2e-testing.md`
- `.cursor/rules/a4a.mdc`
- `.cursor/rules/calypso-client.mdc`
- `.cursor/rules/dashboard.mdc`
- `CLAUDE.md`
- `client/AGENTS.md`
- `client/CLAUDE.md`
- `client/a8c-for-agencies/AGENTS.md`
- `client/a8c-for-agencies/CLAUDE.md`
- `client/dashboard/AGENTS.md`
- `client/dashboard/CLAUDE.md`
- `test/e2e/AGENTS.md`
- `test/e2e/CLAUDE.md`

## What to add / change

See: peGwbA-4jG-p2

## Proposed Changes

We have duplicate rules for Claude and Cursor, so I'm proposing to unify them as follows:

- if the rule affects a subdirectory tree, convert that into AGENTS.md, and an additional CLAUDE.md which `@`-references to it.
- if the rule affects multiple directory tree, keep it as-is for now. (e.g. `dashboard-testing.md`)

## Why are these changes being made?

It is easy to modify one rule and miss the other one.

## Testing Instructions

Check out this locally, verify that it still behaves as expected. For example, work on some files under `client/dashboard/`, and verify `client/dashboard/AGENTS.md` is loaded.

## Pre-merge Checklist

<!--
Complete applicable items on this checklist **before** merging into trunk. Inapplicable items can be left unchecked.

Both the PR author and reviewer are responsible for ensuring the checklist is completed.
-->

- [X] Has the general commit checklist been followed? (PCYsg-hS-p2)
- [ ] [Have you written new tests](https://wpcalypso.wordpress.com/devdocs/docs/testing/index.md) for your changes?
- [ ] Have you tested the feature in Simple (P9HQHe-k8-p2), Atomic (P9HQHe-jW-p2), and self-hosted Jetpack sites (PCYsg-g6b-p2)?
- [ ] Have you checked for TypeScript, React or other console errors?
- [ ] Have you tested accessibility for your changes? Ensure the feature remains usable with various user agents (e.g., browsers), interfaces (e.g., keyboard navigation), and assistive techno

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
