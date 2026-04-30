# fix: restore general-purpose CLAUDE.md (GH-3078)

Source: [gastownhall/beads#3169](https://github.com/gastownhall/beads/pull/3169)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Fixes #3078.

The upstream `CLAUDE.md` was overwritten with Emma rig-specific release engineering notes (GitHub API rate limit warnings, goreleaser config, version bump procedures). These are private operational notes for the Emma crew member/worktree, not general project instructions for all contributors.

This PR:
- Restores `CLAUDE.md` to the general-purpose agent instructions (last correct version at `7e70de1f`)
- Moves Emma's release notes to `.claude/emma-release-notes.md`, which is already covered by the `.claude/` gitignore entry

## Test plan

- [ ] Verify `CLAUDE.md` contains general beads project instructions (issue tracking workflow, code standards, visual design system, etc.)
- [ ] Verify Emma's release notes are preserved in `.claude/emma-release-notes.md` (gitignored, not committed)
- [ ] Confirm `.claude/` is listed in `.gitignore`

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
