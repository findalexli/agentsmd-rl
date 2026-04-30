# Feat/data structure protocol

Source: [sickn33/antigravity-awesome-skills#114](https://github.com/sickn33/antigravity-awesome-skills/pull/114)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/data-structure-protocol/SKILL.md`

## What to add / change

# Pull Request Description

## Summary

Adds **data-structure-protocol** — a skill that gives LLM coding agents persistent structural memory of a codebase.

DSP externalizes the project's dependency graph into a `.dsp/` directory: entities (modules, functions, external deps), their imports, public APIs (shared/exports), and explicit "why" reasons for every connection. Agents use a Python CLI (`dsp-cli.py`) to query and maintain the graph instead of re-reading the entire source tree on every task.

The skill covers:
- Core concepts (UID identity, graph model, storage format)
- Bootstrap procedure (DFS from root entrypoints)
- Full workflow rules (create/update/delete/navigate)
- CLI command reference with examples
- Best practices and integration notes

**Risk:** `safe` — read/write operations are limited to a `.dsp/` directory within the project; no network, no execution of arbitrary code.

**Source:** https://github.com/k-kolomeitsev/data-structure-protocol

## Quality Bar Checklist ✅

**All items must be checked before merging.**

- [x] **Standards**: I have read `docs/QUALITY_BAR.md` and `docs/SECURITY_GUARDRAILS.md`.
- [x] **Metadata**: The `SKILL.md` frontmatter is valid (checked with `scripts/validate_skills.py`).
- [x] **Risk Label**: I have assigned the correct `risk:` tag (`none`, `safe`, `critical`, `offensive`).
- [x] **Triggers**: The "When to use" section is clear and specific.
- [x] **Security**: If this is an _offensive_ skill, I incl

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
