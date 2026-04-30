# chore(skills): simplify sl-commit and sl-submit-diff skill docs

Source: [flora131/atomic#264](https://github.com/flora131/atomic/pull/264)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/sl-commit/SKILL.md`
- `.claude/skills/sl-submit-diff/SKILL.md`
- `.github/skills/sl-commit/SKILL.md`
- `.github/skills/sl-submit-diff/SKILL.md`
- `.opencode/skills/sl-commit/SKILL.md`
- `.opencode/skills/sl-submit-diff/SKILL.md`

## What to add / change

Streamlines Sapling skill documentation by removing unused commands, duplicate content, and focusing on the recommended Meta workflow. This reduces cognitive load and ensures coding agents use the most appropriate commands.

## Summary

This PR cleans up the Sapling skill documentation to focus on the essential, commonly-used commands and removes outdated or Meta-internal workflow references. Changes are applied consistently across all three agent configurations (Claude Code, GitHub Copilot, OpenCode).

## Changes

### sl-commit skill
**Removed unused commands:**
- `sl bookmark` - Not needed for basic commit workflow
- `sl smartlog -l 5` - Advanced feature, not essential
- `sl absorb` - Advanced feature removed from command reference

**Simplified commands:**
- `sl diff --stat` → `sl diff` (simpler, more commonly used)

**Removed duplicate content:**
- Entire "Conventional Commits Format" section (already documented elsewhere in the codebase)
- Smartlog and Absorb documentation from "Key Sapling Differences" section

### sl-submit-diff skill
**Standardized on draft workflow:**
- Updated all `jf submit` commands to `jf submit --draft`
- Emphasizes DRAFT mode as the default submission method

**Removed Meta-internal references:**
- Removed `arc diff` mentions (Meta-internal tool not available in open source)
- Updated description to only reference `jf submit` (Meta workflow)

**Simplified command reference:**
- Removed `sl ssl` from commands list
- Removed advanced operations f

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
