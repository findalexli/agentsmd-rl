# fix(skills): quote SKILL.md description values containing ': '

Source: [gsd-build/gsd-2#4594](https://github.com/gsd-build/gsd-2/pull/4594)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `src/resources/skills/verify-before-complete/SKILL.md`
- `src/resources/skills/write-docs/SKILL.md`

## What to add / change

## Summary

- Two shipped skills failed to load because their frontmatter `description:` value was a plain YAML scalar containing `: ` (colon-space), which `yaml.parse` rejects as a nested mapping.
- Wrapped the affected descriptions in double quotes (escaping internal `"`) so the frontmatter parses cleanly.

Fixes #4593

## Test plan

- [x] `yaml.parse` on the fixed frontmatter returns the expected `name` / `description` for both skills
- [ ] Launch the CLI and confirm `[Skill issues]` no longer lists `verify-before-complete` or `write-docs`
- [ ] Invoke each skill via `/verify-before-complete` / `/write-docs` to confirm it loads and is callable

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Chores**
  * Fixed description formatting in skill documentation to ensure proper parsing and consistent display across the platform.

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
