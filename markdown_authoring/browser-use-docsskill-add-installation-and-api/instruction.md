# docs(skill): add installation and API key configuration to SKILL.md

Source: [browser-use/browser-use#3962](https://github.com/browser-use/browser-use/pull/3962)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/browser-use/SKILL.md`

## What to add / change

## Summary
- Add Installation section with `uvx`/`uv pip` commands and `browser-use install`
- Add API Key Configuration section explaining resolution order (flag → env var → config file)
- Document CLI aliases (`bu`, `browser`, `browseruse`)
- Add `browser-use install` to Setup commands and Troubleshooting

The SKILL.md was missing critical information for users who don't have the CLI installed - they had no way to know how to install it or configure API keys.

## Test plan
- [x] Verify SKILL.md renders correctly
- [ ] Confirm installation commands work as documented

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Added installation steps and API key setup to SKILL.md so new users can install the browser-use CLI and configure keys quickly. Documented uvx/uv pip commands, the browser-use install command for Chromium dependencies, API key resolution order (flag → env var → config file), CLI aliases, and updates to Setup and Troubleshooting.

<sup>Written for commit 6d476f056e4b5fd9f7d91e23245a5c9c0697d077. Summary will update on new commits.</sup>

<!-- End of auto-generated description by cubic. -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
