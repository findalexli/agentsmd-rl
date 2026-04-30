# Move SKILL.md into skills/next-browser/ subfolder

Source: [vercel-labs/next-browser#23](https://github.com/vercel-labs/next-browser/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/next-browser/SKILL.md`

## What to add / change

Fixes #22.

## Problem

`npx skills add vercel-labs/next-browser` dumps ~1 MB of repo content into the user's skills directory — `dist/`, `extensions/react-devtools-chrome/` (~3 MB unpacked, full of `.js`/`.map`/`.png`), `src/`, `pnpm-lock.yaml`, changesets, etc. osulli flagged this because CI and lint tools were choking on the pile of unexpected files in a skills folder.

## Root cause

The `skills` CLI treats the folder containing `SKILL.md` as the skill root and delegates the actual file list to `https://skills.sh/api/download/<owner>/<repo>/<slug>`, which returns every file in that folder. With `SKILL.md` sitting at the repo root, the "skill folder" *was* the whole repo.

Verified by curling the endpoint directly — it returned the entire repo tree.

## Fix

Move `SKILL.md` into `skills/next-browser/`. The `skills` CLI explicitly lists `skills/` as a priority prefix when walking the repo tree (see `skills@1.4.9` `cli.mjs` around the `PRIORITY_PREFIXES` constant), and the slug still resolves from the frontmatter `name: next-browser`, so the install command is **unchanged**:

```bash
npx skills add vercel-labs/next-browser
```

This skill's payload is purely the markdown — the CLI itself ships via `@vercel/next-browser` on npm — so nothing else needs to live alongside `SKILL.md`.

## Notes

- `README.md` needs no update (it only references the `npx skills add` command, no paths).
- `CLAUDE.md` mentions `SKILL.md` in prose only — no hardcoded paths.
- `.claude-plugin/` is unt

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
