# Add a script to create pnpm-installable branches from GitHub

## Problem

The Remix monorepo currently has no way to let users test unreleased code without publishing nightly/canary releases to npm. Publishing nightlies clutters the npm registry and version history. Contributors and early adopters need a way to install the latest `main` branch directly from GitHub.

## What's Needed

Create a new TypeScript script at `scripts/setup-installable-branch.ts` that prepares the current branch to be installable directly from GitHub via pnpm's git install syntax (e.g., `pnpm install "remix-run/remix#nightly&path:packages/remix"`).

### New script: `scripts/setup-installable-branch.ts`

The script must contain references to the following (these strings must appear in the file):

- **`logAndExec`** — the script must import and use the `logAndExec` utility from `scripts/utils/process.ts` for all command execution
- **`parseArgs`** or **`argv`** — the script must accept a target branch name (defaulting to `nightly`) via command-line argument parsing (using `process.argv` or Node.js's `util.parseArgs`)
- **`gitignore`** — the script must handle `.gitignore` updates (removing `dist/` so built code is committed)
- **`dependencies`** — the script must update package `dependencies` (specifically, update all internal `@remix-run/*` package dependencies to use the GitHub branch format, move `@remix-run/*` peerDependencies to regular dependencies, and apply `publishConfig` overrides so exports point to `dist/` instead of `src/`)

The script should also check out the new branch, run a build, and commit the changes.

### Update `logAndExec` in `scripts/utils/process.ts`

The existing `logAndExec` utility currently returns void and passes all options through to `execSync`. Update it to support capturing command output:

- The function must always **return a `string`** (never void or undefined) — when called without capture mode, it should return an empty string
- The function must accept an optional **second boolean parameter**: when `true`, capture and return the command's stdout as a string; when omitted or `false`, execute normally (inheriting stdio) and return an empty string

This is needed because the new script has to read the output of git commands like `git branch --show-current` and `git status --porcelain`.

### Register the npm script

Register the new script in `package.json` under the `"scripts"` field with the exact key **`"setup-installable-branch"`**, pointing to the new TypeScript file.

### GitHub Actions workflow: `.github/workflows/nightly.yml`

Create a GitHub Actions workflow at `.github/workflows/nightly.yml` that runs this script on a daily schedule to keep the `nightly` branch up to date, with manual dispatch support. The workflow file must contain:

- A **`schedule`** trigger (for the daily cron)
- A reference to **`setup-installable-branch`** (to invoke the script)

### README.md updates

Add a **`## Installation`** section to `README.md` documenting how to install Remix. The section must include:

- npm install instructions
- A nightly build option mentioning the word **`nightly`**
- The git install format using the string **`remix-run/remix#`** and the **`path:`** parameter (e.g., `pnpm install "remix-run/remix#nightly&path:packages/remix"`)

### CONTRIBUTING.md updates

Add a section with a **`Nightly`** heading to `CONTRIBUTING.md` that documents the nightly build process. The section must reference the **`setup-installable-branch`** script by name.

## Files to Look At

- `scripts/utils/process.ts` — the `logAndExec` utility that needs output capture support
- `scripts/setup-installable-branch.ts` — the new script to create
- `package.json` — register the new npm script
- `.github/workflows/nightly.yml` — the new GitHub Actions workflow
- `README.md` — project documentation
- `CONTRIBUTING.md` — contributor guide
- `AGENTS.md` — code style and conventions to follow
