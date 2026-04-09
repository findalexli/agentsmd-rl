#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if [ -f "CLAUDE.md" ] && grep -q "Next.js Development Guide" CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create the CLAUDE.md file
cat > CLAUDE.md << 'EOF'
# Next.js Development Guide

## Git Workflow

**Use Graphite for all git operations** instead of raw git commands:

- `gt create <branch-name> -m "message"` - Create a new branch with commit
- `gt modify -a --no-edit` - Stage all and amend current branch's commit
- `gt checkout <branch>` - Switch branches (use instead of `git checkout`)
- `gt sync` - Sync and restack all branches
- `gt submit --no-edit` - Push and create/update PRs (use `--no-edit` to avoid interactive prompts)
- `gt log short` - View stack status

**Note**: `gt submit` runs in interactive mode by default and won't push in automated contexts. Always use `gt submit --no-edit` or `gt submit -q` when running from Claude.

**Graphite Stack Safety Rules:**

- Graphite force-pushes everything - old commits only recoverable via reflog
- Never have uncommitted changes when switching branches - they get lost during restack
- Never use `git stash` with Graphite - causes conflicts when `gt modify` restacks
- Never use `git checkout HEAD -- <file>` after editing - silently restores unfixed version
- Always use `gt checkout` (not `git checkout`) to switch branches
- `gt modify --no-edit` with unstaged/untracked files stages ALL changes
- `gt sync` pulls FROM remote, doesn't push TO remote
- `gt modify` restacks children locally but doesn't push them
- Always verify with `git status -sb` after stack operations
- When resuming from summarized conversation, never trust cached IDs - re-fetch from git/GitHub API

**Safe multi-branch fix workflow:**

```bash
gt checkout parent-branch
# make edits
gt modify -a --no-edit        # Stage all, amend, restack children
git show HEAD -- <files>      # VERIFY fix is in commit
gt submit --no-edit           # Push immediately

gt checkout child-branch      # Already restacked from gt modify
# make edits
gt modify -a --no-edit
git show HEAD -- <files>      # VERIFY
gt submit --no-edit
```

## Build Commands

```bash
# Build the Next.js package (dev server only - faster)
pnpm --filter=next build:dev-server

# Build everything
pnpm build

# Run specific task
pnpm --filter=next taskfile <task>
```

## Fast Local Development

For iterative development, use watch mode + fast test execution:

**1. Start watch build in background:**

```bash
# Runs taskr in watch mode - auto-rebuilds on file changes
# Use Bash(run_in_background=true) to keep working while it runs
pnpm --filter=next dev
```

**2. Run tests fast (no isolation, no packing):**

```bash
# NEXT_SKIP_ISOLATE=1 - skip packing Next.js for each test (much faster)
# testonly - runs with --runInBand (no worker isolation overhead)
NEXT_SKIP_ISOLATE=1 NEXT_TEST_MODE=dev pnpm testonly test/path/to/test.ts
```

**3. When done, kill the background watch process.**

Only use full `pnpm --filter=next build` for one-off builds (after branch switch, before CI push).

**Always rebuild after switching branches:**

```bash
gt checkout <branch>
pnpm build   # Required before running tests (Turborepo dedupes if unchanged)
```

## Testing

```bash
# Run specific test file (development mode with Turbopack)
pnpm test-dev-turbo test/path/to/test.test.ts

# Run tests matching pattern
pnpm test-dev-turbo -t "pattern"

# Run development tests
pnpm test-dev-turbo test/development/
```

**Test commands by mode:**

- `pnpm test-dev-turbo` - Development mode with Turbopack (default)
- `pnpm test-dev-webpack` - Development mode with Webpack
- `pnpm test-start-turbo` - Production build+start with Turbopack
- `pnpm test-start-webpack` - Production build+start with Webpack

**Other test commands:**

- `pnpm test-unit` - Run unit tests only (fast, no browser)
- `pnpm testonly <path>` - Run tests without rebuilding (faster iteration)
- `pnpm new-test` - Generate a new test file from template

## Linting and Types

```bash
pnpm lint              # Full lint (types, prettier, eslint, ast-grep)
pnpm lint-fix          # Auto-fix lint issues
pnpm prettier-fix      # Fix formatting only
pnpm types             # TypeScript type checking
```

## Investigating CI Test Failures

**Use `/ci-failures` for automated analysis** - analyzes failing jobs in parallel and groups by test file.

**CI Analysis Tips:**

- Don't spawn too many parallel agents hitting GitHub API (causes rate limits)
- Prioritize blocking jobs first: lint, types, then test jobs
- Use `gh api` for logs (works on in-progress runs), not `gh run view --log`

**Quick triage:**

```bash
# List failed jobs for a PR
gh pr checks <pr-number> | grep fail

# Get failed job names
gh run view <run-id> --json jobs --jq '.jobs[] | select(.conclusion == "failure") | .name'

# Search job logs for errors (completed runs only - use gh api for in-progress)
gh run view <run-id> --job <job-id> --log 2>&1 | grep -E "FAIL|Error|error:" | head -30
```

**Common failure patterns:**

- `rust check / build` → Run `cargo fmt -- --check` locally, fix with `cargo fmt`
- `lint / build` → Run `pnpm prettier --write <file>` for prettier errors
- Test failures → Run the specific test locally with `pnpm test-dev-turbo <test-path>`

**Run tests in the right mode:**

```bash
# Dev mode (Turbopack)
pnpm test-dev-turbo test/path/to/test.ts

# Prod mode
pnpm test-start-turbo test/path/to/test.ts
```

## Key Directories

- `packages/next/src/` - Main Next.js source code
  - `server/` - Server runtime (dev server, router, rendering)
  - `client/` - Client-side code
  - `build/` - Build tooling (webpack, turbopack configs)
  - `cli/` - CLI entry points
- `packages/next/dist/` - Compiled output
- `turbopack/` - Turbopack bundler (Rust)
- `test/` - Test suites
  - `development/` - Dev server tests
  - `production/` - Production build tests
  - `e2e/` - End-to-end tests

## Development Tips

- The dev server entry point is `packages/next/src/cli/next-dev.ts`
- Router server: `packages/next/src/server/lib/router-server.ts`
- Use `DEBUG=next:*` for debug logging
- Use `NEXT_TELEMETRY_DISABLED=1` when testing locally

## Commit and PR Style

- Do NOT add "Generated with Claude Code" or co-author footers to commits or PRs
- Keep commit messages concise and descriptive
- PR descriptions should focus on what changed and why

## Development Anti-Patterns

### Test Gotchas

- Mode-specific tests need `skipStart: true` + manual `next.start()` in `beforeAll` after mode check
- Don't rely on exact log messages - filter by content patterns, find sequences not positions

### Rust/Cargo

- cargo fmt uses ASCII order (uppercase before lowercase) - just run `cargo fmt`

### Node.js Source Maps

- `findSourceMap()` needs `--enable-source-maps` flag or returns undefined
- Source map paths vary (webpack: `./src/`, tsc: `src/`) - try multiple formats
- `process.cwd()` in stack trace formatting produces different paths in tests vs production
EOF

# Create the .claude/commands/ci-failures.md file
mkdir -p .claude/commands

cat > .claude/commands/ci-failures.md << 'EOF'
# Check CI Failures

Analyze failing tests from PR CI runs with parallel subagent log analysis.

## Usage

```
/ci-failures [pr-number]
```

If no PR number provided, detect from current branch.

## Instructions

1. Get the PR number from argument or current branch:

   ```bash
   gh pr view --json number,headRefName --jq '"\(.number) \(.headRefName)"'
   ```

2. **CRITICAL: Always fetch fresh run IDs** - never trust cached IDs from conversation summaries:

   ```bash
   gh api "repos/vercel/next.js/actions/runs?branch={branch}&per_page=10" \
     --jq '.workflow_runs[] | select(.name == "build-and-test") | "\(.id) attempts:\(.run_attempt) status:\(.status) conclusion:\(.conclusion)"'
   ```

3. **Prioritize the MOST RECENT run, even if in-progress:**
   - If the latest run is `in_progress` or `queued`, check it FIRST - it has the most relevant failures
   - Individual jobs complete before the overall run - analyze them as they finish
   - Only fall back to older completed runs if the current run has no completed jobs yet

4. Get all failed jobs from the run (works for in-progress runs too):

   ```bash
   gh api "repos/vercel/next.js/actions/runs/{run_id}/jobs?per_page=100" \
     --jq '.jobs[] | select(.conclusion == "failure") | "\(.id) \(.name)"'
   ```

   **Note:** For runs with >100 jobs, paginate:

   ```bash
   gh api "repos/vercel/next.js/actions/runs/{run_id}/jobs?per_page=100&page=2"
   ```

5. Spawn parallel haiku subagents to analyze logs (limit to 3-4 to avoid rate limits):
   - **CRITICAL: Use the API endpoint for logs, NOT `gh run view --log`**
   - `gh run view --job --log` FAILS when run is in-progress
   - **Do NOT group by job name** (e.g., "test dev", "turbopack") - group by failure pattern instead
   - Agent prompt should extract structured data using:
     ```bash
     # Extract assertion failures with context:
     gh api "repos/vercel/next.js/actions/jobs/{job_id}/logs" 2>&1 | \
       grep -B3 -A10 "expect.*\(toBe\|toContain\|toEqual\|toStartWith\|toMatch\)" | head -100
     # Also check for test file paths:
     gh api "repos/vercel/next.js/actions/jobs/{job_id}/logs" 2>&1 | \
       grep -E "^\s+at Object\.|FAIL\s+test/" | head -20
     ```

## Common Gotchas

### In-Progress Runs

- `gh run view {run_id} --job {job_id} --log` **FAILS** when run is in-progress
- `gh api "repos/.../actions/jobs/{job_id}/logs"` **WORKS** for any completed job
- Always use the API endpoint for reliability

### Pagination

- GitHub API paginates at 100 jobs per page
- Next.js CI has ~120+ jobs - always check page 2:
  ```bash
  gh api ".../jobs?per_page=100&page=1" --jq '[.jobs[] | select(.conclusion == "failure")] | length'
  gh api ".../jobs?per_page=100&page=2" --jq '[.jobs[] | select(.conclusion == "failure")] | length'
  ```

### Multiple Attempts

- CI runs can have multiple attempts (retries)
- Check attempt count: `.run_attempt` field
- Query specific attempt: `.../runs/{id}/attempts/{n}/jobs`
- 404 on attempt endpoint means that attempt doesn't exist
EOF

# Update .gitignore
cat >> .gitignore << 'EOF'

# Claude Code (local settings and session files)
.claude/settings.local.json
.claude/plans/
.claude/todos.json
CLAUDE.local.md
EOF

# Update .alexignore
cat >> .alexignore << 'EOF'
.claude/
CLAUDE.md
EOF

echo "Patch applied successfully."
