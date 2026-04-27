# feat: add vibe-code-auditor skill

Source: [sickn33/antigravity-awesome-skills#156](https://github.com/sickn33/antigravity-awesome-skills/pull/156)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/vibe-code-auditor/SKILL.md`

## What to add / change

## Summary

Adds `vibe-code-auditor`, a new specialized skill for auditing rapidly generated or AI-produced code before it reaches production.

This skill targets the specific failure modes of vibe coding and LLM-assisted development: silent error swallowing, hallucinated imports, hardcoded credentials, business logic buried inside HTTP handlers, and technical debt invisible to casual review.

## What this skill does

- Confirms scope and context before starting (does not halt if optional inputs are missing)
- Evaluates code across 7 audit dimensions: Architecture, Consistency, Robustness, Production Risks, Security, Dead/Hallucinated Code, and Technical Debt Hotspots
- Produces a structured audit report with severity tags ([CRITICAL], [HIGH], [MEDIUM], [LOW]), exact location per finding, and a 0–100 Production Readiness Score with rubric-based deductions
- Outputs a Refactoring Priorities section with effort estimates (S/M/L)
- Enforces strict behavioral rules: no invented findings, no unnecessary rewrites, no inflated scores

## Why it is not redundant with existing skills

No existing skill in the repository targets AI-generated or vibe-coded code specifically. The 7-dimension framework and the "Dead or Hallucinated Code" dimension are unique to this skill and address failure modes specific to LLM output that generic code review skills do not cover.

## Checklist

- [x] I have read `docs/QUALITY_BAR.md` and `docs/SKILL_ANATOMY.md`
- [x] Skill name is u

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
