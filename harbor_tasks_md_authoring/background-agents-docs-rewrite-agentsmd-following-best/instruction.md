# docs: rewrite AGENTS.md following best practices

Source: [ColeMurray/background-agents#213](https://github.com/ColeMurray/background-agents/pull/213)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Rewrites `AGENTS.md` from a flat 272-line ops-focused dump into a focused 151-line agent orientation file
- Removes deployment/operational docs already covered by package READMEs (Modal secrets CLI, HMAC mechanics, D1 table schemas, GitHub token flows, KV migration scripts, curl test examples)
- Adds missing sections: project description, architecture overview with data flow, package table, testing guidance (frameworks, file locations, integration test patterns), commit conventions, key gotchas

## What changed

| Section | Before | After |
|---|---|---|
| Project description | Missing | 3-line overview with tech stack |
| Architecture | Scattered across sections | Consolidated with data flow and dependency graph |
| Package overview | Missing | Table with all 7 packages |
| Common commands | Included Modal deploy commands | Focused on build/test/lint (what agents run) |
| Testing | Only curl-based E2E examples | Framework info, file locations, integration test patterns |
| Coding conventions | Present (kept) | Kept + added commit message conventions |
| Key gotchas | Scattered | Distilled into 6 actionable bullets |
| Modal Infrastructure | 96 lines of ops docs | Removed (in `packages/modal-infra/README.md`) |
| GitHub App Auth | 40 lines of ops docs | Removed (in `packages/control-plane/README.md`) |
| Control Plane D1/DO | 55 lines of schema docs | Removed (in `packages/control-plane/README.md`) |

## Test plan

- [x] CLAUDE.md symlink still resolves correctl

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
