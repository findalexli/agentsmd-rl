# Add accuracy, signal density, and invariant checks to agents-md-sync skill

Source: [PrefectHQ/prefect#21076](https://github.com/PrefectHQ/prefect/pull/21076)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/agents-md-sync/SKILL.md`

## What to add / change

## Summary

- Adds three new analysis categories to the agents-md-sync skill's step 4 (Analyze each relevant AGENTS.md): **Accuracy**, **Signal density**, and **Missing invariants**
- Updates the example report format with examples of the new finding types
- Reinforces the guidelines section with matching principles

<details>
<summary>Motivation</summary>

While reviewing a generated concurrency AGENTS.md, three classes of issues were found that the skill didn't check for:

1. **Factual inaccuracies from day one** — lease renewal timing, event emission attribution, and error handling flow were all wrong from initial creation, not stale due to code changes
2. **Low-signal content** — full function signatures, trivial usage examples, and file-by-file architecture listings duplicated what's readable from code
3. **Missing invariants** — the sync/async lockstep contract wasn't documented despite being critical

The skill's existing drift categories (structural, command, convention, description) all assume content was once correct and became stale. These new categories catch content that was never correct, content that shouldn't exist, and content that's missing.
</details>

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
