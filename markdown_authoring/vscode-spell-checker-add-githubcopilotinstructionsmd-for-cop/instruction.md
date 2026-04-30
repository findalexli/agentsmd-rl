# Add .github/copilot-instructions.md for Copilot coding agent onboarding

Source: [streetsidesoftware/vscode-spell-checker#5117](https://github.com/streetsidesoftware/vscode-spell-checker/pull/5117)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds a `copilot-instructions.md` file so a Copilot coding agent encountering this repo for the first time can orient quickly and work effectively without manual exploration.

## What's documented

- **Repo layout** — all packages under `packages/` with their roles (client, LSP server, webview UI, RPC helpers, utilities)
- **Tech stack** — TypeScript (`.mts` for ESM), npm workspaces only (yarn/pnpm blocked), Node 22+, tsdown+tsc, Vitest, ESLint flat config, Prettier, CSpell, Svelte
- **Essential commands** — install, build, test, lint, per-workspace variants, and `.vsix` packaging
- **Code style** — single quotes, 4-space indent, 140 print width, LF, strict TypeScript, `.mts`/`.mjs` import conventions
- **Adding settings** — step-by-step: extend `CSpellUserSettings.mts` → update `configFields.ts` → regenerate schema via `npm run build-package-schema`
- **CI workflows** — what each workflow gates and which paths are excluded
- **Common gotchas** — `patch-package` post-install, `cspell` enforcement on all source, schema regeneration requirement, `noUnusedLocals`/`noUnusedParameters` strictness
- **Architecture** — client↔server JSON-RPC flow, webview Svelte app + RPC bridge, shared API types in `json-rpc-api`

<!-- START COPILOT CODING AGENT TIPS -->
---

✨ Let Copilot coding agent [set things up for you](https://github.com/streetsidesoftware/vscode-spell-checker/issues/new?title=✨+Set+up+Copilot+instructions&body=Configure%20instructions%20for%20this%20repository%20as%20documen

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
