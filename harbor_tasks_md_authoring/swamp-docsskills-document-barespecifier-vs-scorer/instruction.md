# docs(skills): document bare-specifier vs scorer hermeticity (swamp-club#161)

Source: [systeminit/swamp#1220](https://github.com/systeminit/swamp/pull/1220)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/swamp-extension-publish/references/publishing.md`
- `.claude/skills/swamp-extension-quality/SKILL.md`
- `.claude/skills/swamp-extension-quality/references/templates.md`

## What to add / change

## Summary

Closes swamp-club#161. Following #1218 shipping `swamp extension quality`, authors now discover locally that the scorer strips the tarball's `deno.json` and writes a controlled one with no imports map — so bare `"zod"` imports fail with `deno doc --json failed: Import "zod" not a dependency` before factor scoring even begins. This PR teaches that pattern to authors through the two skills that previously led them into the trap.

**Three files, +50/-7 lines:**

- **`swamp-extension-quality/references/templates.md`** — the JSDoc entrypoint skeleton was showing bare `"zod"`; switched to `"npm:zod@4"` with a rationale bullet explaining hermeticity. An author who copies the template literally now produces an extension that scores.
- **`swamp-extension-publish/references/publishing.md`** — the Import Rules had two contradictory bullets (`"npm:zod@4"` is "always required" vs. bare specifiers "can be used" with `deno.json`). Rewritten into one coherent paragraph that carries both load-bearing signals: hermeticity at score time AND zod-specific externalization (why zod in particular is called out, not merely a consequence of hermeticity).
- **`swamp-extension-quality/SKILL.md`** — added a gotcha block under "Essential mechanics authors get wrong" that names the failure mode explicitly, calls out the Deno `no-import-prefix` default that activates when a `deno.json` with `imports` is present (which is every swamp repo's default state, creating a catch-22), and gives concrete 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
