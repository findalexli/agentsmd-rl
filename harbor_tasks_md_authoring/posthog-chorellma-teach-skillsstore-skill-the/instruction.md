# chore(llma): teach skills-store skill the per-file edit primitives

Source: [PostHog/posthog#55897](https://github.com/PostHog/posthog/pull/55897)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `products/llm_analytics/skills/skills-store/SKILL.md`

## What to add / change

## Problem

The `skills-store` agent skill is the primary entry point we point coding agents at when teaching them how to use the PostHog skills API. Until now it only documented the lossy `skill-update` shape — full `body` and replace-all `files` — which is exactly the shape #55729 (file_edits) and #55814 (per-file CRUD) were built to steer callers away from.

An agent reading `skills-store` today still reaches for the dangerous primitive even though safer ones now exist.

## Changes

`products/llm_analytics/skills/skills-store/SKILL.md`:

- **Available tools table** — added rows for `skill-file-create`, `skill-file-delete`, `skill-file-rename`.
- **"Updating a skill" section** — rewritten with worked examples for:
  - body `edits` (incremental find/replace)
  - per-file `file_edits` (one-file find/replace, no round-trip of other files)
  - per-file CRUD tools (atomic add/remove/rename)
- Reframed the `files` replace-all path as an opt-in for intentional bundle wipes, not the default update shape.
- **Local /phs bridge skill** — added the new tools to its `allowed-tools` list and a tiny "Edit one part of an existing skill" section so the bridge can route to them.

## How did you test this code?

Automated only — I'm an agent. `hogli lint:skills` passes (12/12 skills OK). `hogli build:skills` fails on an unrelated Jinja template needing a DB Team — this skill is plain markdown with no Jinja so it's not affected.

## Publish to changelog?

no — agent-facing internal skill upda

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
