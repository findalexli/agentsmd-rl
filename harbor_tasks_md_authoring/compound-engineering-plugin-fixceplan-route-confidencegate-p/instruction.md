# fix(ce-plan): route confidence-gate pass to document-review

Source: [EveryInc/compound-engineering-plugin#462](https://github.com/EveryInc/compound-engineering-plugin/pull/462)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/AGENTS.md`
- `plugins/compound-engineering/skills/ce-plan/SKILL.md`

## What to add / change

Phase 5.3.2 in ce:plan told the model to "proceed to Phase 5.4" when the confidence gate passed, which skipped document-review (5.3.8) entirely. Plans that didn't need deepening never got reviewed. The fix routes the gate-pass case to 5.3.8 so document-review always runs — it catches different issues than the confidence check and should never be skipped.

Also adds a "Debugging Plugin Bugs" section to the plugin AGENTS.md. Developers of this plugin use it via their marketplace install, which can be older than the repo. When investigating a reported usage bug, agents should now diff the installed version against the repo before diving in — avoiding wasted effort on already-fixed issues or misdiagnosis when the two versions diverge.

---

[![Compound Engineering v2.59.0](https://img.shields.io/badge/Compound_Engineering-v2.59.0-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
