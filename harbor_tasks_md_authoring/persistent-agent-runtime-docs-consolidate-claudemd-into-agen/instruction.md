# Docs: consolidate CLAUDE.md into AGENTS.md; tighten agent guide

Source: [shenjianan97/persistent-agent-runtime#76](https://github.com/shenjianan97/persistent-agent-runtime/pull/76)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`
- `CLAUDE.md`

## What to add / change

## Summary
- Replace `CLAUDE.md` with a symlink to `AGENTS.md` so agent instructions live in one place — the two mandatory rules (read AGENTS.md first, use superpowers) were already covered there.
- Tighten AGENTS.md from **1431 → 1143 words (-20%)** while adding higher-value guidance at the top.

## What's new in AGENTS.md
- **Tech stack one-liner** in Project section — answers the most-asked cold-read question without a file read.
- **Common Commands cheat sheet** (with `make help`) placed right after Services.
- **Boundaries** section consolidating *Never / Ask first / Always* rules with `§`-backrefs to contextual homes.

## What was fixed / cut
- Structural bug: "Task spec detail level" subsection was interrupting the numbered Phase Workflow list, causing steps 5–6 to render as a broken sub-list.
- Redundancy in Documentation Map (removed empty-placeholder dirs), the Phase 2 example, Agent Skills, External PR References, Local Validation, Testing, and Browser Verification.
- `make test` vs. narrowest-scope tension clarified: narrowest scope is primary; the full `make test` suite is not required when a single file/package covers the change.

## Methodology
Pass 1 used [github.blog's "How to write a great agents.md"](https://github.blog/ai-and-ml/github-copilot/how-to-write-a-great-agents-md-lessons-from-over-2500-repositories/) (2,500-repo analysis) and the agents.md spec to decide what belongs at the top of a frequently-loaded file. Pass 2 was a Codex second-opinion revie

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
