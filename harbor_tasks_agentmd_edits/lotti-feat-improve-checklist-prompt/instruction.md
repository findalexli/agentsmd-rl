# Improve Checklist Updates Prompt with Entry-Scoped Directives

## Problem

The Checklist Updates feature in `lib/features/ai/util/preconfigured_prompts.dart` extracts checklist items from user-provided entries. When a user dictates an implementation plan or includes meta-instructions (like "ignore this for checklist purposes"), the prompt has no way to handle these — it tries to extract multiple items from content that should either be ignored entirely or collapsed into a single tracking item like "Draft implementation plan."

This produces noisy, unhelpful suggestions that require manual cleanup.

## Expected Behavior

The checklist updates prompt should support **per-entry directives** so that:

1. If an entry says something like "Don't consider this for checklist items" or "Ignore for checklist", that entry is skipped for item extraction.
2. If an entry says "The rest is an implementation plan" or "Single checklist item for this plan", the entire entry collapses to at most one created item.
3. Directives must be scoped to individual entries — they should not affect neighboring entries.

Both the **system message** and **user message** portions of the checklist updates prompt need updates.

## Files to Look At

- `lib/features/ai/util/preconfigured_prompts.dart` — contains the checklist updates prompt template (both system and user messages)
- `lib/features/ai/README.md` — documents the AI feature's checklist behavior

After implementing the prompt changes, update the feature README to document the new per-entry directive behavior so that future developers and AI agents understand how directives work in checklist updates.
