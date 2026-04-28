# docs(agents): drop hardcoded local paths in astro-developer SKILL.md

Source: [withastro/astro#16476](https://github.com/withastro/astro/pull/16476)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/astro-developer/SKILL.md`

## What to add / change

## Changes

Fix two broken links in `.agents/skills/astro-developer/SKILL.md` that pointed at absolute filesystem paths on someone's local dev machine (`/Users/ema/www/withastro/astro/...`) rather than at the intended repo files. Readers clicking either link on GitHub or in a local markdown previewer got a 404.

```diff
-- Root: [/AGENTS.md](/Users/ema/www/withastro/astro/AGENTS.md)
-- Root: [/CONTRIBUTING.md](/Users/ema/www/withastro/astro/CONTRIBUTING.md)
+- Root: [/AGENTS.md](../../../AGENTS.md)
+- Root: [/CONTRIBUTING.md](../../../CONTRIBUTING.md)
```

The SKILL.md lives at `.agents/skills/astro-developer/SKILL.md`, so `../../../AGENTS.md` and `../../../CONTRIBUTING.md` resolve to the repo-root files. Display labels preserved.

## Testing

- `grep -rn '/Users/ema' .` after the change → 0 hits.
- `ls ../../../AGENTS.md ../../../CONTRIBUTING.md` from `.agents/skills/astro-developer/` resolves both files.
- Rendered the file in a markdown previewer — both links are now clickable and land on the right targets.

## Docs

No user-facing doc updates needed. The change is inside `.agents/` (internal agent skill catalog), not in `packages/*` or `examples/*`.

## Changeset

No changeset added — per `CONTRIBUTING.md` §"Non-packages (`examples/*`) do not need changesets", and `.agents/skills/*` is not a published package.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
