# Add AGENTS.md and .github/copilot-instructions.md

Source: [cdxgen/cdxgen#3862](https://github.com/cdxgen/cdxgen/pull/3862)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

AI agents working on cdxgen have no documented guide to the project's conventions, making it easy to generate code that violates established patterns (wrong import style, direct syscall wrappers, hand-rolled purls, etc.). These files codify what an agent needs to produce idiomatic contributions.

## `AGENTS.md` (repo root)
Comprehensive reference for AI coding agents covering:
- **Module system** — pure ESM, `node:` prefix mandatory, Biome-enforced three-group import order
- **Key abstractions** — `options` object threading, `createBom`/`postProcess`/`prepareEnv` pipeline, `PackageURL`, `cdxgenAgent` (never raw `got`)
- **Safe wrappers** — `safeExistsSync`, `safeMkdirSync`, `safeSpawnSync` over their raw Node equivalents; `isSecureMode` guard
- **Logging** — `thoughtLog` / `traceLog` / `DEBUG_MODE`-gated `console.*` and when each applies
- **Testing** — poku + esmock + sinon, co-located `*.poku.js` files, async patterns
- **Biome rules** that are notably off (`noParameterAssign`, `noForEach`, `noDelete`) vs. error-level (`noUndeclaredVariables`, `useSingleVarDeclarator`, `useDefaultParameterLast`)
- **How to add a new ecosystem** — end-to-end checklist
- **Explicit anti-patterns** list

## `.github/copilot-instructions.md`
Condensed (~120-line) version of the same rules with inline code examples, tuned for Copilot inline completion context where brevity matters.

```js
// Patterns explicitly called out to generate correctly:

// node: prefix always
import { readFileSync } fro

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
