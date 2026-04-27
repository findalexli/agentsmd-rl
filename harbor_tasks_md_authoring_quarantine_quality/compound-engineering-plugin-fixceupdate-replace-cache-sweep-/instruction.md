# fix(ce-update): replace cache sweep with claude plugin update

Source: [EveryInc/compound-engineering-plugin#656](https://github.com/EveryInc/compound-engineering-plugin/pull/656)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-update/SKILL.md`

## What to add / change

## Summary

`/ce-update` now recommends `claude plugin update compound-engineering@every-marketplace` instead of sweeping the plugin cache directly. The bespoke cache handling (listing `~/.claude/plugins/cache/<marketplace>/compound-engineering/`, comparing version folder names, `rm -rf`ing stale ones) is gone. Claude Code's own CLI subcommand already handles version comparison, marketplace refresh, and install updates in one call.

The refactor surfaced via a bug fix. `/ce-update` had been silently returning "no marketplace cache found" for everyone, even when stale versions were piled up in the cache, because the pre-resolution used `${CLAUDE_PLUGIN_ROOT:-}` inside `$(dirname ...)` and Claude Code's skill-body substitution does not recognize the `${VAR:-}` form (only bare `${VAR}` is in the [documented substitution set](https://code.claude.com/docs/en/skills#available-string-substitutions)). Fixing the detection by switching to `${CLAUDE_SKILL_DIR}` (commit 1) made it clear that the whole cache-walking approach was unnecessary: delete it and call the right command instead (commit 2).

Net change: 3 pre-resolved values instead of 4, no path-derivation of plugin cache or marketplace name, no `rm -rf` in the skill, and the recommended action is a single copy-paste command.

## Test plan

- **Marketplace cache path:** normal launch (no `--plugin-dir`), run `/ce-update`. Should report current vs. latest and either "up to date" or the `claude plugin update` recommendation.
- **De

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
