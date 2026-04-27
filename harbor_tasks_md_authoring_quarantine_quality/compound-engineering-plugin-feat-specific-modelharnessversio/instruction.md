# feat: specific model/harness/version in PR attribution

Source: [EveryInc/compound-engineering-plugin#283](https://github.com/EveryInc/compound-engineering-plugin/pull/283)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`
- `plugins/compound-engineering/skills/ce-work/SKILL.md`

## What to add / change

## Summary
- Replace generic "Generated with Claude Code" footer with dynamic attribution
- LLMs fill in model, context window, thinking level, harness, and plugin version at commit/PR time
- Subagents explicitly instructed to do the same in multi-agent workflows

## Before / After

| Before | After |
|--------|-------|
| `🤖 Generated with Claude Code` | `🤖 Generated with Claude Opus 4.6 (1M context, extended thinking) via Claude Code` |
| `Co-Authored-By: Claude` | `Co-Authored-By: Claude Opus 4.6 (1M context, extended thinking)` |
| `[![Compound Engineered](...)]` | `[![Compound Engineering v2.40.0](...)]` |

## Substitution table (from the new docs)

| Placeholder | Value | Example |
|-------------|-------|---------|
| `[MODEL]` | Model name | Claude Opus 4.6, GPT-5.4 |
| `[CONTEXT]` | Context window (if known) | 200K, 1M |
| `[THINKING]` | Thinking level (if known) | extended thinking |
| `[HARNESS]` | Tool running you | Claude Code, Codex, Gemini CLI |
| `[HARNESS_URL]` | Link to that tool | `https://claude.com/claude-code` |
| `[VERSION]` | `plugin.json` → `version` | 2.40.0 |

## Files changed
- `CLAUDE.md` — updated commit convention footer + substitution table
- `plugins/compound-engineering/skills/ce-work/SKILL.md` — updated commit template, PR badge, checklist, and substitution table

## Test plan
- [ ] Next PR created via `/ce:work` includes specific model, harness, and version in footer
- [ ] Badge renders correctly with version number

---

[![Compound Engineeri

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
