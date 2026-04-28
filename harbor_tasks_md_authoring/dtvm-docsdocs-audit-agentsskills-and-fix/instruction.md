# docs(docs): audit .agents/skills and fix stale references

Source: [DTVMStack/DTVM#479](https://github.com/DTVMStack/DTVM/pull/479)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/archive/SKILL.md`
- `.agents/skills/dev-workflow/SKILL.md`
- `.agents/skills/dmir-compiler-analysis/SKILL.md`
- `.agents/skills/dmir-compiler-analysis/cost-model.md`
- `.agents/skills/dmir-compiler-analysis/evm-to-dmir.md`
- `.agents/skills/dtvm-perf-profile/SKILL.md`

## What to add / change

## Summary

Audited every SSOT `SKILL.md` and companion doc under `.agents/skills/` against the current tree on `upstream/main` (`a21b40f`). Found that most skills accumulated stale path, line-number, and symbol references since the code they describe had drifted, plus one concrete rule conflict. This PR fixes the provable issues; nothing is changed in the auto-generated `.claude/skills/*/SKILL.md` mirrors.

Scope is docs only — no code, no build, no tests.

## Fixes (per commit)

### `docs(docs): fix dev-workflow and archive skills for reality` (e4aed34)

- **dev-workflow**: drop "Add the entry to the table in `docs/changes/README.md`". `docs/changes/README.md` has no per-change table, only status definitions and a pointer to `ls docs/changes/*/README.md`, so the instruction was unfollowable.
- **archive**: same reference to the nonexistent per-change table removed (the README has a Status Definitions table, but no table of individual changes to update).
- **archive**: replace `git worktree remove <path>` with `rm -rf <path> && git worktree prune`. The previous recommendation directly contradicts `.claude/rules/dtvm-perf-worktree-lab.md:34`, which explicitly forbids `git worktree remove` because it fails on DTVM's submodule-bearing worktrees.

### `docs(docs): correct perf_profile.sh path in dtvm-perf-profile skill` (bd253fc)

- Invocation example used `./scripts/perf_profile.sh`, which does not exist at repo root.
- Explanatory note pointed to `.claude/skills/dtvm-perf-prof

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
