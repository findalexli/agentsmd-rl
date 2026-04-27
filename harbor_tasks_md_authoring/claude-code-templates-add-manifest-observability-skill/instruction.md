# Add Manifest observability skill

Source: [davila7/claude-code-templates#371](https://github.com/davila7/claude-code-templates/pull/371)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/development/manifest/SKILL.md`

## What to add / change

## Description

Adds the **Manifest** skill to the development category — an observability plugin setup guide for AI agents.

## What it does

- 6-step setup walkthrough: stop gateway, install plugin, get API key, configure, restart, verify
- Troubleshooting table for common errors (missing key, invalid format, connection refused, duplicate OTel)
- Best practices for configuration and security

## Who uses this

Developers who need real-time visibility into agent costs, tokens, messages, and performance via the [Manifest](https://manifest.build) observability platform.

## Component location

`cli-tool/components/skills/development/manifest/SKILL.md`

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds a new Manifest observability skill to guide plugin setup, verification, and troubleshooting. Helps developers enable real-time telemetry for agent costs, tokens, messages, and performance.

- Area: components (cli-tool/components/); new file added at cli-tool/components/skills/development/manifest/SKILL.md
- Why: Provide a clear 6-step setup, common error fixes, and best practices for the Manifest plugin
- New components: Yes; regenerate catalog (docs/components.json) to include this skill
- Secrets: Requires a Manifest API key (mnfst_); optional custom endpoint; no new repo env vars

<sup>Written for commit 4224a5ab4d603d7c77498373273176216f5bd362. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
