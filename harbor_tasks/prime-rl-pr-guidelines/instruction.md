# Update AGENTS.md with PR/GitHub guidelines

The repository's `AGENTS.md` file gives agents working in this codebase a
short set of conventions to follow. Today the file has a `## Git` section
that mentions branch prefixes, but it has nothing to say about how to
actually open pull requests, and recent friction has shown that two pieces
of guidance are missing.

## What to do

Edit `AGENTS.md` so that it documents the following two new conventions for
agents working in this repository. Both belong under a brand-new `## GitHub`
section that you will add (the existing `## Git` section should remain in
place — the new section is sibling to it, not nested inside it).

1. **Default to draft pull requests.** When opening a pull request from
   this repo, agents should create it as a draft instead of a regular PR,
   to avoid kicking off the full CI matrix on work that is not yet ready
   for review. The exact CLI invocation that produces a draft PR is
   `gh pr create --draft`; this command must appear verbatim in the
   guidance so an agent reading the file can copy it.

2. **No "test plan" boilerplate.** Some agents reflexively add a
   "test plan" section to every PR description, even when they did not
   actually run any tests. The new rule should make explicit that a
   "test plan" section must NOT be included in a PR description unless
   either (a) the agent actually ran tests to verify the changes, or
   (b) the user explicitly asked for one. The literal phrase
   `"test plan"` (in quotes) should appear in the rule so it is
   unambiguous what term is being referenced.

While you are editing the file, also bring the existing branch-prefix line
in the `## Git` section into line with the bullet/bold formatting used by
the other rules in `AGENTS.md` (compare for example the bullets under
`## Running code`). The set of allowed prefixes itself does not change —
`feat/`, `fix/`, and `chore/` are still the only ones.

## Code Style Requirements

This repository enforces Python code style with `ruff` (configured in
`pyproject.toml`). Your edit to `AGENTS.md` does not affect any Python
source files, so the `ruff check` CI job should continue to pass without
any additional work on your part.

## Constraints

- Only `AGENTS.md` should be modified.
- Do not change the existing `## Writing code`, `## Running code`,
  `## Skills`, or `## Testing` sections.
- The new `## GitHub` heading must be present as a top-level (`##`) section.
- Place the new section after the existing `## Git` section so the
  flow goes Git → GitHub.
