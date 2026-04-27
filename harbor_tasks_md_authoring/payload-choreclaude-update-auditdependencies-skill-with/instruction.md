# chore(claude): update audit-dependencies skill with lockfile strategy and override rules

Source: [payloadcms/payload#16106](https://github.com/payloadcms/payload/pull/16106)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/audit-dependencies/SKILL.md`

## What to add / change

# Overview

Updates the audit-dependencies skill to include a lockfile-update strategy as an intermediate fix between direct dependency bumps and pnpm overrides. Also adds documentation for common pnpm override pitfalls learned from recent audit work.

## Key Changes

- **Added lockfile update as a fix strategy**
  - When a transitive dependency's parent uses a semver range that already includes the fixed version, `pnpm update --recursive` is enough. No `package.json` changes needed. The workflow now checks pinned vs ranged before falling back to overrides.

- **Documented pnpm override syntax rules**
  - Added guidance on using `^` ranges instead of `>=` (which can cross major versions), single-level parent scoping limitations, unsupported version selectors in keys, and risks of global overrides across multiple major versions.

- **Added user confirmation step before applying fixes**
  - The workflow now requires presenting a summary table of proposed fixes and getting user confirmation before making changes. This prevents wasted effort from incorrect fix strategies.

## Design Decisions

The fix priority order is now: direct bump > lockfile update > override. The lockfile update step was added because several audit vulnerabilities were resolvable without any `package.json` changes — the parent's semver range already covered the fix, but the lockfile had a stale resolution. Recognizing this case avoids unnecessary overrides that add long-term maintenance burden.

The overrid

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
