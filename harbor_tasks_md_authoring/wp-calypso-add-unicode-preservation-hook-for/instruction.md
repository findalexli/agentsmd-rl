# Add Unicode preservation hook for Claude agents

Source: [Automattic/wp-calypso#108717](https://github.com/Automattic/wp-calypso/pull/108717)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Proposed Changes

A real bugbear of mine!

From pgz0xU-xz-p2#comment-655

* Add `.claude/hooks/check-unicode-preservation.sh` — a post-tool hook that detects when an Edit tool corrupts smart quotes, em-dashes, or other Unicode characters in string literals
* The hook runs after every Edit tool call and rejects edits that replace Unicode chars with ASCII equivalents

## Why are these changes being made?

Agents frequently corrupt typographic Unicode characters in string literals — replacing curly quotes with straight quotes, ellipsis with `...`, etc. A `.claude/rules/` instruction wasn't reliable enough, so this uses a hook that actually checks the diff and blocks bad edits.

## Testing Instructions

* Have a Claude agent edit a string containing smart quotes (e.g. `'` or `"`) and verify the hook blocks corruption
* Verify `.claude/hooks/check-unicode-preservation.sh` is executable

It would be annoying to get false positives, so I'm going to run this hook for a bit in my `~/.claude` files for a bit just to make sure it isn't getting in the way.

## Pre-merge Checklist

- [ ] Has the general commit checklist been followed? (PCYsg-hS-p2)
- [ ] Have you written new tests for your changes?
- [ ] Have you tested the feature in Simple (P9HQHe-k8-p2), Atomic (P9HQHe-jW-p2), and self-hosted Jetpack sites (PCYsg-g6b-p2)?
- [ ] Have you checked for TypeScript, React or other console errors?
- [ ] Have you tested accessibility for your changes? Ensure the fe

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
