# Add .github/copilot-instructions.md

Source: [Azure/openapi-diff#452](https://github.com/Azure/openapi-diff/pull/452)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configure repository instructions for GitHub Copilot coding agent per [best practices](https://gh.io/copilot-coding-agent-tips).

Covers:
- **Project context** — dual TypeScript + C#/.NET codebase, `@azure/oad` npm package
- **Build/test/lint commands** — `npm run tsc`, `npm run ts.test`, `npm run lint`, `npm run prettier`, etc.
- **Code conventions** — no semicolons, 140 char print width, no trailing commas, strict TS, CommonJS ESLint config
- **Repo structure** — `src/` (TS), `openapi-diff/` (C#), `src/test/` (Jest, `*[tT]est.ts` pattern)
- **CI** — GitHub Actions on Ubuntu + Windows: lint, prettier, full test suite
- **Guidelines** — pre-submit checks, test expectations, files to avoid modifying

> [!WARNING]
>
> <details>
> <summary>Firewall rules blocked me from connecting to one or more addresses (expand for details)</summary>
>
> #### I tried to connect to the following addresses, but was blocked by firewall rules:
>
> - `gh.io`
>   - Triggering command: `/home/REDACTED/work/_temp/ghcca-node/node/bin/node /home/REDACTED/work/_temp/ghcca-node/node/bin/node --enable-source-maps /home/REDACTED/work/_temp/copilot-developer-action-main/dist/index.js` (dns block)
>
> If you need me to access, download, or install something from one of these locations, you can either:
>
> - Configure [Actions setup steps](https://gh.io/copilot/actions-setup-steps) to set up my environment, which run before the firewall is enabled
> - Add the appropriate URLs or hosts to the custom allowlist i

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
