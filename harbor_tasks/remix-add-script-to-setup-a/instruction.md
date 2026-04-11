# Add a script to create pnpm-installable branches from GitHub

## Problem

The Remix monorepo currently has no way to let users test unreleased code without publishing nightly/canary releases to npm. Publishing nightlies clutters the npm registry and version history. Contributors and early adopters need a way to install the latest `main` branch directly from GitHub.

## What's Needed

Create a new TypeScript script that prepares the current branch to be installable directly from GitHub via pnpm's git install syntax (e.g., `pnpm install "remix-run/remix#nightly&path:packages/remix"`).

The script should:
1. Accept a target branch name (defaulting to `nightly`)
2. Check out the new branch and run a build
3. Remove `dist/` from `.gitignore` so built code is committed
4. Update all internal `@remix-run/*` package dependencies to use the GitHub branch format
5. Move `@remix-run/*` peerDependencies to regular dependencies to avoid install warnings
6. Apply `publishConfig` overrides so exports point to `dist/` instead of `src/`
7. Commit the changes

The existing `logAndExec` utility in `scripts/utils/process.ts` currently returns void and passes all options through to `execSync`. It needs to be updated to support capturing command output (returning it as a string), since the new script needs to read the output of git commands like `git branch --show-current` and `git status --porcelain`.

Also add a GitHub Actions workflow (`.github/workflows/nightly.yml`) that runs this script on a daily schedule to keep the `nightly` branch up to date, with manual dispatch support for custom base/installable branch combinations.

After implementing the code changes, update the project documentation to reflect this new capability:
- The README should document how to install Remix (including the nightly build option)
- The CONTRIBUTING guide should explain the nightly build process for contributors

## Files to Look At

- `scripts/utils/process.ts` — the `logAndExec` utility that needs output capture support
- `scripts/` — where the new setup script belongs
- `package.json` — register the new npm script
- `README.md` — project documentation
- `CONTRIBUTING.md` — contributor guide
- `AGENTS.md` — code style and conventions to follow
