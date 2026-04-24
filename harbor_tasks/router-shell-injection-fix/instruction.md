# Fix Shell Injection Vulnerability in Release Script

## Problem

The `scripts/create-github-release.mjs` file contains a **shell injection vulnerability**.

The code uses `execSync` with a template literal to run a `git show` command. The `relPath` variable comes from filesystem glob results and is interpolated directly into the shell command string. If a malicious directory name (containing shell metacharacters like `;`, `|`, `$()`, etc.) exists in the filesystem, it could execute arbitrary commands during the release process.

## Security Requirement

Your fix must use a command execution function from Node.js's `child_process` module that passes arguments as an array (rather than a template literal string) to prevent shell injection. User-controlled path data (such as `relPath` from filesystem glob results) must be passed as separate array elements, never interpolated into a shell command string.

The script must:
- Use `execFileSync` imported from `node:child_process` with array-style arguments
- Continue to retrieve package.json content from the previous release commit
- Parse that content as JSON
- Maintain existing functionality

## Constraints

- Do NOT change the overall logic of the script
- Do NOT modify any other files
- Only modify `scripts/create-github-release.mjs`
- The script must remain syntactically valid JavaScript

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `prettier (JS/TS/JSON/Markdown formatter)`
- `eslint (JS/TS linter)`
