# feat: add result-to-claim + ablation-planner skills

Source: [wanshuiyin/Auto-claude-code-research-in-sleep#67](https://github.com/wanshuiyin/Auto-claude-code-research-in-sleep/pull/67)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/ablation-planner/SKILL.md`
- `skills/result-to-claim/SKILL.md`

## What to add / change

## Summary

Adds two skills that fill the gap between "experiments done" and "ready for paper" — a stage where ARIS currently goes directly from experiments to `/auto-review-loop` without systematically evaluating what the results mean or designing targeted ablations.

### The Gap

Currently after experiments complete:
- There's no structured evaluation of whether results actually support the intended claims
- Ablation studies are ad-hoc (suggested by reviewer in `/auto-review-loop`) rather than systematically designed upfront
- It's easy to over-claim or under-claim based on partial evidence

### What's Added

#### `skills/result-to-claim/SKILL.md`

**"Do my results support my claims?"**

Collects experiment results from available sources (EXPERIMENT_LOG.md, EXPERIMENT_TRACKER.md, W&B, log files) and sends them to Codex MCP for objective evaluation against the intended claims.

Codex returns a structured judgment:
- `claim_supported: yes | partial | no`
- What results support, what they don't, missing evidence, suggested claim revision
- `confidence: high | medium | low`

Auto-routes based on verdict:
- **no** → postmortem in findings.md, pivot to next idea from IDEA_CANDIDATES.md
- **partial** → narrow claim, run supplementary experiments, re-evaluate
- **yes** → confirm claim, trigger `/ablation-planner`

Key design: **Codex is the judge, not CC** — prevents post-hoc rationalization where the executor inflates its own results.

#### `skills/ablation-planner/SKILL.md`

**"W

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
