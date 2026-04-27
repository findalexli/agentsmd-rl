# Add an AGENTS.md for the Build Tools API area

The Kotlin repository organises documentation for AI agents around named
**areas**. Each area has its own `AGENTS.md` listed in the table under
`## Areas` in `.ai/guidelines.md`. The Build Tools API (BTA) area —
all modules under `compiler/build-tools/` — currently has no
`AGENTS.md`, so an agent landing in that part of the tree has no
area-level guidance.

Your task: write area documentation for the Build Tools API so it
follows the same conventions as the other areas already listed in
`.ai/guidelines.md`.

## What to deliver

You should produce three changes:

1. **A new `compiler/build-tools/AGENTS.md`** that documents the BTA area.
   The file should be substantive — covering the purpose of the area,
   the modules it contains, the architecture, the conventions for
   running and writing tests, and any notable pitfalls — at a level of
   detail comparable to the existing `compiler/AGENTS.md`,
   `analysis/AGENTS.md`, and the other AGENTS.md files referenced from
   the Areas table.

2. **A new `compiler/build-tools/CLAUDE.md`** that follows the
   convention `.ai/guidelines.md` documents at the bottom of its
   `## Areas` section for adding new area docs.

3. **An update to `.ai/guidelines.md`** that adds a row to the `## Areas`
   table for the new area. The row's `Docs` column must link to the
   new `compiler/build-tools/AGENTS.md` you wrote, and the link must
   resolve correctly given that `.ai/guidelines.md` lives at
   `.ai/guidelines.md` in the repo (i.e. the link is relative to the
   `.ai/` directory). The row's `Location` column must point to the
   `compiler/build-tools/` directory. The row should sit inside the
   existing Areas table, not in some other section.

## Discovering the content

Read the existing `AGENTS.md` files referenced from the Areas table to
learn the house style — section ordering, how modules are listed,
how Gradle commands are presented, how cross-references are written.
Walk `compiler/build-tools/` to learn the modules and their READMEs.
Read the source under `kotlin-build-tools-api/src/` to learn the key
public abstractions; read the test setup under
`kotlin-build-tools-api-tests/` to learn the test conventions.

The substance must come from the code in the repo, not from generic
templates. An AGENTS.md for this area must mention the BTA modules
that actually exist on disk under `compiler/build-tools/` — at a
minimum the public API module and its default implementation.

## What you must NOT do

- Do not modify any file outside of the three above. The Areas table is
  the only edit to `.ai/guidelines.md`; existing rows for other areas
  must remain unchanged.
- Do not invent modules, classes, or commands that do not exist in the
  repo. The doc is meant to direct future agents — wrong information
  is worse than no doc.
