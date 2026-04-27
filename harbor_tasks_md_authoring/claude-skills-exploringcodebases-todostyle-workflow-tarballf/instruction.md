# exploring-codebases: TODO-style workflow (tarball-first, batched treesit)

Source: [oaustegard/claude-skills#560](https://github.com/oaustegard/claude-skills/pull/560)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `exploring-codebases/SKILL.md`

## What to add / change

Rewrites the Workflow section as an explicit 4-step TODO list.

## Why

Diagnosis from a MoDA repo review (@oaustegard flagged — chat thread 2026-04-20):

1. **Preamble waste** — before invoking the skill, I curl'd the README and cat'd individual `__init__.py` files via the GitHub contents API. All of that data was already in the tarball that got downloaded seconds later. Double fetch.
2. **No batching** — tree-sitting ran as 4–5 separate invocations (stats, tree, symbols, names, kernels) instead of batching queries into one scan. Each separate call re-scans the repo.
3. **Phase-framed prose** invited interpreting the skill as guidance rather than a checklist. Easy to reorder, easy to "just peek at the README first."

## What changes

- **Step 1 is tarball-first, mandatory**: one `curl` to `/tarball/$REF`, extract to `/tmp/$REPO`. Explicit "do NOT curl README or cat individual files before this" note.
- **Step 2 emphasizes batching**: shows combined `'find:...' 'source:...' 'refs:...'` in one treesit call, with note that separate invocations re-scan.
- **Step 3/4 unchanged in substance** but moved into numbered steps rather than "phases."
- Heuristics, scaling, monorepo notes demoted to a `## Notes` section at the bottom — they're reference material, not steps.
- Version bumped `2.0.0` → `2.1.0`.

## Not changed

- Dependencies section
- "When to Use This vs Other Skills" triage table
- Overall skill scope and positioning vs searching-codebases


## Update: v2.2.0 based on do

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
