# docs(agents): refresh AGENTS.md — fix stale facts, expand plugins/skills sections

Source: [NousResearch/hermes-agent#14763](https://github.com/NousResearch/hermes-agent/pull/14763)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary
Brings AGENTS.md back into sync with current main. The old version had several outright-wrong facts (default model, config version, test count, MESSAGING_CWD) and was missing entire subsystems (plugins/, optional-skills/, memory providers, centralized logging).

## Fixes (wrong facts)
- `source venv/bin/activate` → `.venv` preferred, `venv` fallback (matches `scripts/run_tests.sh`)
- AIAgent default `model = "anthropic/claude-opus-4.6"` → actual is `""` (resolved from config/provider)
- Test suite `~3000` → `~15k tests across ~700 files`
- `tools/mcp_tool.py (~1050 lines)` → `~2.6k LOC`
- `_config_version (currently 5)` → stale; rule clarified (bump only when migration is actually needed, not for every new key)
- **`MESSAGING_CWD`** listed as the messaging cwd var — it has been removed in favor of `terminal.cwd` in config.yaml (config.py prints a deprecation warning if set). AGENTS.md was teaching the removed pattern.
- `.env` clarified as **secrets only** (API keys/tokens/passwords); non-secret settings belong in config.yaml
- `simple_term_menu` pitfall reframed: existing sites are legacy fallback, rule is no new usage

## Additions
- Gateway platforms list expanded to reflect actual adapters (matrix, mattermost, email, sms, dingtalk, wecom, weixin, feishu, bluebubbles, webhook, api_server, …)
- New **Plugins** section: general plugins, memory-provider plugins, dashboard/context-engine/image-gen directories, plus the May-2026 rule that plugins must not touch core 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
