# Add a Releases & Environment pointer to `CLAUDE.md`

You are working in the PRQL compiler repository. The repo's
`CLAUDE.md` (at the project root) tells Claude how to work in this
codebase: it documents the inner/outer test loops, how to run the CLI,
how to lint, and where to find generated docs.

It currently has nothing to say about **releases** or **environment**
issues, even though the project keeps detailed instructions for those
topics in
`web/book/src/project/contributing/development.md`. As a result Claude
ends up re-discovering or guessing this information instead of just
reading the existing docs.

## What to change

Append a new top-level section to `CLAUDE.md` that points future
agents at the development guide. The section must:

- Use the heading `## Releases & Environment` (exactly that text — the
  ampersand is intentional; this is meant to mirror the style of the
  other `## Foo` sections already in the file).
- Briefly explain that this section is for **releases or environment**
  topics, and direct the reader to the existing development guide at
  the path `web/book/src/project/contributing/development.md`.
- Be added at the end of the file, after the existing `## Documentation`
  section. Do not move, rename, reformat, or delete any of the existing
  sections (`# Claude`, `## Development Workflow`, `## Tests`,
  `## Running the CLI`, `## Linting`, `## Documentation`).

Keep the new section short — just a couple of lines of prose is enough.
The point is to leave a discoverable pointer, not to duplicate the
contents of `development.md`.

## Files in scope

- `CLAUDE.md` (the only file you should be editing for this task).

The path you reference (`web/book/src/project/contributing/development.md`)
already exists in the repo at the base commit; you do not need to create
or modify it.
