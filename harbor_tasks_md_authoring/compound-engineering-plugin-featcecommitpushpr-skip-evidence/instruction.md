# feat(ce-commit-push-pr): skip evidence prompt when judgment allows

Source: [EveryInc/compound-engineering-plugin#663](https://github.com/EveryInc/compound-engineering-plugin/pull/663)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-commit-push-pr/SKILL.md`

## What to add / change

## Summary

`ce-commit-push-pr` previously walked the full evidence-decision ladder on every invocation, asking a blocking user question whenever the branch diff showed observable behavior. That prompt fires often on chained `ce-commit` → `ce-commit-push-pr` runs, where the agent just authored the commits and already knows the change's character — so the prompt rarely adds value and interrupts flow.

Two short-circuits now run before the full decision:

1. **User-requested evidence.** If the invocation explicitly asked for a demo or screenshot, proceed directly to capture, with graceful fallback when capture is infeasible (no runnable surface, missing credentials, docs-only diff).
2. **Agent judgment on authored changes.** For commits authored this session that are clearly non-observable (internal plumbing, backend refactors, type-level changes), skip the prompt without asking. The categorical skip list is not exhaustive — the agent trusts its own read of the change it just wrote.

The full decision still runs for cold invocations and ambiguous changes; standalone use is unaffected.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.7_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
