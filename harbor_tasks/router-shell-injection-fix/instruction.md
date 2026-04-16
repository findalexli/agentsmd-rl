# Fix Shell Injection Vulnerability in Release Script

## Problem

The `scripts/create-github-release.mjs` file contains a **shell injection vulnerability** in how it retrieves package content from previous git commits.

The code executes a `git show` command using `execSync` with a template literal that includes the `relPath` variable. The `relPath` value comes from filesystem glob results and is interpolated directly into the shell command string. If a maliciously crafted directory name (e.g., containing shell metacharacters like `;`, `|`, `$()`, etc.) were present in the filesystem, it could execute arbitrary commands during the release process.

## Requirements

Your fix must satisfy all of the following:

1. **Import statement must include `execFileSync`** from `node:child_process` using exactly this format:
   ```
   import { execSync, execFileSync } from 'node:child_process'
   ```

2. **The `git show` command execution must use `execFileSync`** instead of `execSync`. The call must pass the command and its arguments separately:
   - First argument to `execFileSync`: `'git'`
   - Second argument: an array where the first element is `'show'`

3. **No shell interpolation with `relPath`** - the `relPath` variable must not appear inside a template literal passed to `execSync`

4. **Maintain existing functionality** - the script must continue to retrieve package.json content from the previous release commit and parse it as JSON

## Constraints

- Do NOT change the overall logic of the script
- Do NOT modify any other files
- Only modify `scripts/create-github-release.mjs`
- The script must remain syntactically valid JavaScript
