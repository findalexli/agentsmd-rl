# docs(agents): refresh AGENTS.md and Cursor rules to current state

Source: [aptos-labs/explorer#1599](https://github.com/aptos-labs/explorer/pull/1599)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursor/rules/architect.mdc`
- `.cursor/rules/coder.mdc`
- `.cursor/rules/cost-cutter.mdc`
- `.cursor/rules/modernizer.mdc`
- `.cursor/rules/tester.mdc`
- `AGENTS.md`

## What to add / change

<!-- CURSOR_AGENT_PR_BODY_BEGIN -->
### Description

Brings the agent-facing context (`AGENTS.md`, which `CLAUDE.md`, `GEMINI.md`, `WARP.md`, and `.github/copilot-instructions.md` symlink to, plus the role-specific Cursor rules under `.cursor/rules/`) up to date with the current codebase.

The previous wording still described things like a `src/`-heavy layout, `app/` with only the original five subfolders, an outdated `.env` example, and a Vitest-only test setup. Several recent changes had not been reflected in the agent docs:

- Settings page (`/settings`) and decompilation opt-in
- Per-network Aptos API Gateway keys (`VITE_APTOS_<NETWORK>_API_KEY` / `APTOS_<NETWORK>_API_KEY`)
- Playwright smoke tests (`e2e/`, `playwright.config.ts`, `pnpm test:e2e`, `pnpm test:e2e:install`)
- `docs/FEATURES_SPECIFICATION.md` and `docs/LLM_ACCESS.md`
- `src/` having been drained down to `IndividualPageContent`
- New top-level app directories: `settings/`, `data/`, `hooks/`, `lib/`, `wasm/`, `global-config/`
- Node 24 baseline (`.node-version`)

### What changed

- **`AGENTS.md`**
  - Quick Reference adds `pnpm test --run`, `pnpm test:e2e`, `pnpm test:e2e:install`.
  - Project Structure now matches the actual `app/` layout and lists `docs/`, `e2e/`, `scripts/`, `typings/`. Notes that `src/` only has `IndividualPageContent` left.
  - "Tests and mocks" splits Vitest vs. Playwright, mentions the `e2e/**` Vitest exclusion and the CI mapping of `APTOS_<NETWORK>_API_KEY` to both `VITE_APTOS_*` and 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
