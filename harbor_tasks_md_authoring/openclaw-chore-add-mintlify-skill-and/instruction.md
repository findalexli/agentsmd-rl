# chore: add mintlify skill and wire it into AGENTS.md

Source: [openclaw/openclaw#14123](https://github.com/openclaw/openclaw/pull/14123)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/mintlify/SKILL.md`
- `AGENTS.md`

## What to add / change

Adds a Mintlify best-practices skill (`.agents/skills/mintlify/SKILL.md`) and points `AGENTS.md` at it so agents automatically load it when working on docs.

**What changed**

- **New skill** — `.agents/skills/mintlify/SKILL.md`: covers page structure, component usage, navigation (`docs.json`), frontmatter, and common pitfalls. Agents load it whenever a docs task matches.
- **AGENTS.md** — one-line addition under "Docs Linking": _"When working with documentation, read the mintlify skill."_

No docs content, runtime code, or tests are affected.

<!-- greptile_comment -->

<h2>Greptile Overview</h2>

<h3>Greptile Summary</h3>

Added a comprehensive Mintlify best-practices skill file at `.agents/skills/mintlify/SKILL.md` and wired it into `AGENTS.md` with a one-line instruction to read the skill when working with documentation. The skill file provides detailed guidance on Mintlify-based documentation including page structure, components, navigation, frontmatter, writing standards, and common pitfalls.

<h3>Confidence Score: 5/5</h3>

- This PR is safe to merge with minimal risk
- The changes are purely additive (new skill file and one-line reference in AGENTS.md), provide clear documentation guidelines, and don't affect any runtime code or tests. The content is well-structured and follows the existing pattern of other skill files in the repository.
- No files require special attention

<!-- greptile_other_comments_section -->

<!-- /greptile_comment -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
