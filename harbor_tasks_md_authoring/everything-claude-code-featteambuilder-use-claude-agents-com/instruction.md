# feat(team-builder): use `claude agents` command for agent discovery

Source: [affaan-m/everything-claude-code#1021](https://github.com/affaan-m/everything-claude-code/pull/1021)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/team-builder/SKILL.md`

## What to add / change

Replace file glob probe order with `claude agents` as the primary discovery mechanism so ECC marketplace plugin agents are included automatically, regardless of install path or version.

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Switch agent discovery to use the `claude agents` command so ECC marketplace plugin agents are included automatically, regardless of install path or version. Keep file globbing as a fallback for reading user agent markdown.

- **New Features**
  - Primary discovery via `claude agents`, merged and deduped by name.
  - Precedence: user > plugin > built-in; built-ins skipped by default.
  - Fallback file globs: `./agents/**/*.md` and `~/.claude/agents/**/*.md`.
  - Improved empty state: "No agents found. Run `claude agents` to verify your setup."

<sup>Written for commit 6e8297cd629bd2c0421d21323b9da3250694aaea. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->



<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Improvements**
  * Enhanced agent discovery workflow with improved handling of user, plugin, and built-in agents with updated precedence rules.
  * Strengthened fallback mechanism for locating agent configurations.
  * Clarified error messages to provide better guidance when agents cannot be found.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
