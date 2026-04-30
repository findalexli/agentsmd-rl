# Add CLAUDE.md and .claude/rules/ for Claude Code guidance

Source: [MFlowCode/MFC#1255](https://github.com/MFlowCode/MFC/pull/1255)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/common-pitfalls.md`
- `.claude/rules/fortran-conventions.md`
- `.claude/rules/gpu-and-mpi.md`
- `.claude/rules/parameter-system.md`
- `.github/copilot-instructions.md`
- `CLAUDE.md`

## What to add / change

## **User description**
## Summary
- Adds `CLAUDE.md` (168 lines) with project identity, CLI commands, development workflow contract, system identification/module loading, architecture overview, critical rules, and code review priorities
- Adds 4 modular `.claude/rules/` files for domain-specific knowledge:
  - `fortran-conventions.md` — naming, precision system (`wp`/`stp`), forbidden patterns, module structure
  - `gpu-and-mpi.md` — GPU macro abstraction (`GPU_*` → OpenACC/OpenMP target offload), preprocessor defines, compiler-backend matrix, MPI halo exchange patterns
  - `parameter-system.md` — Python→Fortran parameter flow, 3-location checklist for new parameters
  - `common-pitfalls.md` — array bounds, blast radius warnings, compiler portability, PR checklist

Core CLAUDE.md stays under the ~200-line threshold for optimal instruction adherence. Rules files load automatically as part of Claude Code's memory system.

Designed for two audiences: Claude Code interactive development sessions and automated PR reviews.

## Test plan
- [ ] Verify `CLAUDE.md` loads correctly: run `claude` in repo root and check `/memory`
- [ ] Verify `.claude/rules/` files load alongside core: check `/memory` output
- [ ] Spot-check that Claude follows workflow contract (format → precheck → build → test before commit)
- [ ] Spot-check that Claude uses `./mfc.sh` commands rather than raw CMake/Python

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
