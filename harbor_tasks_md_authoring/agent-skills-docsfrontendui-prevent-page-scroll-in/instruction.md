# docs(frontend-ui): prevent page scroll in custom button example

Source: [addyosmani/agent-skills#79](https://github.com/addyosmani/agent-skills/pull/79)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/frontend-ui-engineering/SKILL.md`

## What to add / change

## Summary

Prevent page scroll in the custom button keyboard example by calling `e.preventDefault()` for `Space` before triggering `handleClick()`.

## Problem

PR #58 correctly added `Space` activation to the non-native button example, but the current snippet still allows the browser's default `Space` action on a custom `role="button"` element.

That means the example can both:
- activate the handler, and
- scroll the page

In a local browser reproduction of the current pattern:
- one `Space` press triggered the click handler once
- `window.scrollY` changed from `0` to `660`

With the updated snippet in this PR:
- one `Space` press still triggered the click handler once
- `window.scrollY` stayed at `0`

## Fix

Keep the change docs-only and limited to the existing example in `skills/frontend-ui-engineering/SKILL.md`.

The updated snippet:
- prevents the default `Space` action on the custom button
- preserves `Enter` and `Space` activation behavior
- stays aligned with the accessibility intent of the skill

## Verification

- Local WKWebView/browser reproduction of the current snippet
- Local WKWebView/browser reproduction of the patched snippet
- `git diff --check`

Closes #78

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
