# feat(skills): redesign /dependabot-fix skill

Source: [axsaucedo/kaos#149](https://github.com/axsaucedo/kaos/pull/149)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/dependabot-fix/SKILL.md`

## What to add / change

Replaces the initial `/dependabot-fix` skill with a comprehensive 5-phase workflow.

## Why
The first version of the skill was shaped only by PR #142 (the simplest Go `@latest`-pin case). It led with "classify the update" triage and a pattern table, and it committed a REPORT.md instead of posting it as a PR comment.

## What's new
5 phases, context-first:

- **A · Context** (no deep dive yet) — fetch PR metadata, produce a one-paragraph summary, enumerate high-level symptoms from failing jobs.
- **B · Ingestion via subagents** — three parallel `explore` subagents load the relevant `.github/instructions/*`, `docs/*`, and source-code map for the ecosystems touched by the PR.
- **C · Diagnosis** — only now dive into the failing-job logs, informed by B. Classify each failing check independently.
- **D · Fix design** — risk-rated plan with reproduction, alternatives, and **tiered manual testing**: isolated → cross-module reproduce-first → runtime smoke with Docker + KIND.
- **E · Finalise** — branch from main, cherry-pick dependabot commit, apply fix, open replacement PR, monitor CI, merge, close original, and **post REPORT.md as a PR comment (never commit)**.

## Breadth
Appendix cheat-sheet covers all four ecosystems observed on bundled Dependabot PRs in this repo:
- `github_actions` (PR #142)
- `gomod` (PR #141)
- `uv`/`pip` (PRs #125, #145)
- `npm` kaos-ui (PRs #143, #146) and docs/
- `docker`

## Removed
- Version-vs-security classification block
- Pattern table as the primar

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
