# Document naming conventions in CLAUDE.md

Source: [zoidsh/meru#523](https://github.com/zoidsh/meru/pull/523)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Adds three naming-convention rules to `CLAUDE.md`, all anchored in identifiers that exist in the codebase today:

- **Variable naming** — flag generic/contextless locals (`raw`, `data`, `parsed`, `record`, `result`, `value`, `item`, `obj`, `tmp`). Cites real examples: `gtkDecorationLayout` (`packages/app/lib/linux.ts:58`), `savedLanguages` (`packages/app/spellchecker.ts:12`), `accountConfigs` (`packages/app/accounts.ts:90`).
- **Function naming** — boolean-returning functions use the bare predicate prefix (`is`/`has`/`can`/`should`/`did`/`will`), matching Node.js/Lodash/React/typescript-eslint convention. Cites real predicates: `isWithinNotificationTimes` (`packages/app/notifications.ts:10`, called inline at `packages/app/gmail/index.ts:462`), `isMailtoUrl` (`packages/app/protocol.ts:19`), `hasOverlap` (`packages/renderer/routes/settings/notifications.tsx:41`). Discourages `getIs*` workarounds; resolves collisions by inlining or purpose-based local names.
- **File naming** — prefer domain/topic file names (`lib/linux.ts`, `lib/fs.ts`) over single-function names (`lib/linux-window-controls.ts`, `lib/file-exists.ts`) so related helpers can accrete without renames.

Docs-only — no code touched.

## Test plan

- [ ] Read the three new bullets and confirm every cited identifier exists on `main`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
