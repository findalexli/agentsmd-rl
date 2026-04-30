# Fix code review agent timeouts caused by gpt-5.4

Source: [dotnet/runtime#126783](https://github.com/dotnet/runtime/pull/126783)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/code-review/SKILL.md`

## What to add / change

> [!NOTE]
> This PR was developed with Copilot assistance based on analysis of workflow run logs and duration data.

## Problem

~20% of custom code review agent runs hit the 20-minute workflow timeout. Analysis of all 43 timeout runs from the last 1000 workflow executions shows:

- **93% of timeouts** are caused by GPT-5.4 sub-agents that never return
- GPT-5.4 is present in **100% of timeout runs** (24/24 checked in detail)
- GPT-5.2-only runs have **0 timeouts** in 6+ successful runs
- 86% of timed-out runs had already posted the review — they time out waiting for hung sub-agents
- Each timeout causes the agent job to fail, making the overall workflow **red in CI** (even though the `conclusion` job succeeds) — PR authors must manually rerun

The current SKILL.md rule "pick the highest version number" causes gpt-5.4 to always be selected when available.

## Changes (SKILL.md only)

1. **Block gpt-5.4** — it has known reliability issues. Recommend `gpt-5.3-codex` as the GPT-family pick instead. If that also exhibits hangs, we can block the GPT family entirely with no expected quality loss.
2. **Exit after posting** — the agent was lingering 2-3 minutes after successfully posting the review comment, waiting for hung sub-agents. Now it exits immediately once the comment is visible.
3. **Reduce max sub-agents from 4 to 3** — with only 2-3 model families available in practice, 4 was never fully utilized.

## What this does NOT change

- The 10-minute sub-a

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
