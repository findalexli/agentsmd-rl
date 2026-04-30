# Restructure CLAUDE.md "Development Workflow" into a tiered testing approach

The PRQL/prql repository ships a root `CLAUDE.md` that tells coding agents
how to run tests on the repo. The current "Development Workflow" section
frames testing as a two-step **inner loop / outer loop**: a fast feedback
loop during development, and a comprehensive `task test-all` (~1min)
mandated "before returning to user".

In practice, `task test-all` runs the full multi-language matrix
(prqlc + JS bindings + Python bindings + wasm), which takes ~2min and is
overkill for the vast majority of changes — those changes only touch the
core Rust prqlc crate. The repo provides a faster `task prqlc:pull-request`
target that runs comprehensive prqlc tests in ~30s, which is sufficient
whenever the change does not affect bindings.

Rewrite the **Development Workflow** section of `CLAUDE.md` so that the
testing guidance is split into **three distinct tiers**, each with a bold
heading, a timing estimate, and a fenced `sh` code block. The three tiers
are:

1. **Inner loop, during development (~5s).** The fast feedback loop used
   while iterating. Keep the existing `task prqlc:test` example and the
   two existing filtered `cargo insta test` examples (one against
   `-p prqlc --lib -- resolver`, one against
   `-p prqlc --test integration -- date`).
2. **Before returning to user (~30s).** The new default validation step
   for most changes. This tier runs `task prqlc:pull-request`. A short
   inline comment in the code block should make it clear that this is
   sufficient for most changes.
3. **Cross-binding changes only (~2min).** This tier runs `task test-all`,
   and the comment in its code block should make it clear that it is only
   needed when changes affect JS, Python, or wasm bindings.

Update the section's preamble (the one-or-two-line sentence that
introduces the tiers) so it frames the new structure as a **tiered testing
approach** rather than an inner/outer-loop split.

## Constraints

- Edit **only** the "Development Workflow" section. The rest of `CLAUDE.md`
  (the `## Tests`, `## Running the CLI`, `## Linting`, `## Error Handling`,
  `## Error Messages`, `## Documentation`, and `## Releases & Environment`
  sections) must remain byte-identical to the base commit.
- The reframing replaces — not augments — the existing "Inner loop /
  Outer loop" content. Do not leave the old framing in place alongside the
  new one.
- Match the surrounding markdown style: bold tier headings of the form
  `**Heading** (timing):`, fenced code blocks tagged ```` ```sh ````, and
  the file's existing hard-wrapped paragraph width.
- The repo's CLAUDE.md is intentionally token-frugal (see the
  "minimize token usage" note in `## Tests`). Keep each tier's preamble
  short — one bold heading plus one short inline comment per code block is
  enough; avoid adding extra prose explaining what each command does.

## Files

- `CLAUDE.md` (repository root)

## Verification

The change is purely a documentation edit; there is no behavioral test
suite to run. A reviewer (and the automated grader) will compare your
final `CLAUDE.md` against the project's expected wording for semantic
equivalence — wording may differ as long as the three tiers, their
timings, the new `task prqlc:pull-request` default, and the binding-only
scoping of `task test-all` are clearly conveyed.
