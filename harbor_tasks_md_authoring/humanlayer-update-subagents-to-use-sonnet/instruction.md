# Update sub-agents to use sonnet model

Source: [humanlayer/humanlayer#695](https://github.com/humanlayer/humanlayer/pull/695)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/codebase-analyzer.md`
- `.claude/agents/codebase-locator.md`
- `.claude/agents/codebase-pattern-finder.md`
- `.claude/agents/thoughts-analyzer.md`
- `.claude/agents/thoughts-locator.md`
- `.claude/agents/web-search-researcher.md`

## What to add / change

## What problem(s) was I solving?

Sub-agents were using `model: inherit` which caused them to inherit the model from the parent session. This meant that when running with Opus, all sub-agents would also use Opus, which is unnecessary and expensive for simple search/grep/read operations.

By switching to `model: sonnet`, sub-agents will automatically use the latest sonnet version regardless of what model the parent session is using, providing a good balance of performance and cost.

## What user-facing changes did I ship?

No direct user-facing changes. This is an internal configuration change that affects cost and performance:

- Sub-agents will now use Sonnet instead of inheriting the parent model
- When a user runs a session with Opus, sub-agents will use Sonnet instead of Opus
- The `sonnet` alias automatically resolves to the latest sonnet version

## How I implemented it

Updated the `model` field in all 6 sub-agent configuration files (`.claude/agents/*.md`):
- Changed from `model: inherit` to `model: sonnet`

Affected agents:
- `codebase-analyzer.md`
- `codebase-locator.md`
- `codebase-pattern-finder.md`
- `thoughts-analyzer.md`
- `thoughts-locator.md`
- `web-search-researcher.md`

## How to verify it

- [x] I have ensured `make check test` passes ✅ All checks and tests passed

### Manual Testing
1. Launch a session with Opus model
2. Trigger a sub-agent (e.g., use codebase-locator)
3. Verify the sub-agent uses Sonnet instead of Opus (check logs/API calls)

## Descrip

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
