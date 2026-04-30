# feat(skills): add monitor-pr for driving PR reviews to green

Source: [sageox/ox#497](https://github.com/sageox/ox/pull/497)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/monitor-pr/SKILL.md`
- `AGENTS.md`

## What to add / change

## Summary

- Adds a new `/monitor-pr` skill at `.claude/skills/monitor-pr/SKILL.md` that drives an open PR to a clean state by streaming its state through the `Monitor` tool and reacting the moment a check fails or a new review comment lands.
- Updates `AGENTS.md` to point at the skill from the existing PR-conventions cluster, replacing the prior one-line CodeRabbit protocol.

## Motivation

CodeRabbit reviews on ox PRs produce a mix of actionable items, "nitpicks", and comments that get flagged `isOutdated` after rebases. The prior one-liner in `AGENTS.md` told the agent *what* to do at the protocol level (reply `"Fixed."`, resolve via GraphQL) but not *how to triage* the comments or how to keep the loop efficient.

The skill captures the judgment rules we actually want applied:

- **Nitpicks are not auto-skippable.** CodeRabbit is often overly polite — real issues hide under "nitpick". Each one gets judged on merit.
- **`isOutdated` is not "ignore".** It means the line moved since the comment was written, not that the feedback no longer applies. Re-read against current code and decide.
- **Poll via `Monitor` with `persistent: true`, not a Bash `sleep` loop.** A sleep-loop blocks the agent between ticks; Monitor streams state transitions as events and lets the agent keep agency between them. Script emits one line only when state changes — quiet PRs produce zero events.
- **60s poll floor** to avoid rate-limiting GitHub API.
- **Keep the monitor running across push cycles** 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
