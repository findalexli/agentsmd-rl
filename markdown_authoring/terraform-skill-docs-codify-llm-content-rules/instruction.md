# docs: codify LLM content rules in CLAUDE.md

Source: [antonbabenko/terraform-skill#19](https://github.com/antonbabenko/terraform-skill/pull/19)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Codifies the LLM-content-format rules that came out of consulting GPT/Codex on PR #18's Provider Removal section. Rules are now **mandatory** in `CLAUDE.md § LLM Consumption Rules` with a pre-merge checklist reviewers must apply.

## Why

PR #18 started as a ~500-token draft in human-pedagogical format (phases → alternatives → "why this matters"). Codex review produced a ~340-token decision-table-first version with identical decision value. Without codifying the rules, the next contributor ships the same too-verbose shape and we repeat the compression round.

## Rules codified

1. **Shape** — decision table before playbook (LLM classify → branch → execute path)
2. **Cut human scaffolding** — no before/after diffs that just restate phase steps, no "Why this matters" paragraphs
3. **Compress prose → ❌/✅ rules** — terse imperative bullets, one fact per bullet
4. **Every artifact earns its tokens** — no restating blocks/tables "for completeness"
5. **Anchor stability** — preserve `### Heading` referenced from SKILL.md diagnose table
6. **Retrieval-first ordering** — decision → procedure → alternatives → rules/gotchas

Plus:
- **Token target:** subsection under 400 tokens (~1,600 chars)
- **Pre-merge checklist** of 7 items reviewers apply
- Explicit recommendation: consult external LLM (e.g. `mcp__codex__codex`) for format review on substantive new content

## Changes

Single file: `CLAUDE.md` — added `### LLM Consumption Rules` subsection under `## SKILL.md Architectu

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
