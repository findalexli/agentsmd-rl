# fix: Correct data path in SKILL.md (coding-agent)

Source: [openclaw/openclaw#11009](https://github.com/openclaw/openclaw/pull/11009)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/coding-agent/SKILL.md`

## What to add / change

not stale, still relevant

Just an old "clawd" folder that needed update to ".openclaw".

<!-- greptile_comment -->

<h2>Greptile Overview</h2>

<h3>Greptile Summary</h3>

- Updates the Coding Agent skill documentation to reference the new `~/.openclaw/` directory instead of the legacy `~/clawd/` path.
- Change is limited to a single “rules” bullet in `skills/coding-agent/SKILL.md` and doesn’t affect runtime code.
- Aligns the doc guidance with the repo’s current configuration/storage naming conventions (`openclaw` paths).

<h3>Confidence Score: 5/5</h3>

- This PR is safe to merge with minimal risk.
- Single-line documentation-only change; verified diff matches stated intent and doesn’t introduce code-path or build/test impact.
- No files require special attention

<!-- greptile_other_comments_section -->

<sub>(5/5) You can turn off certain types of comments like style [here](https://app.greptile.com/review/github)!</sub>

**Context used:**

- Context from `dashboard` - CLAUDE.md ([source](https://app.greptile.com/review/custom-context?memory=fd949e91-5c3a-4ab5-90a1-cbe184fd6ce8))
- Context from `dashboard` - AGENTS.md ([source](https://app.greptile.com/review/custom-context?memory=0d0c8278-ef8e-4d6c-ab21-f5527e322f13))

<!-- /greptile_comment -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
