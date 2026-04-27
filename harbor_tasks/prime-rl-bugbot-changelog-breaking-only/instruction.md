# Scope changelog enforcement to breaking changes only

The repository's BugBot rule (`.cursor/BUGBOT.md`, the Cursor agent
instructions) and the description line of `CHANGELOG.md` currently treat
**any** configuration-shape edit — including additive fields, default-value
tweaks, and minor logic touch-ups — as something that must be recorded in
`CHANGELOG.md`. This has produced changelog clutter from non-breaking
additions, and the per-file source paths the rule enumerates are also
stale: the project recently consolidated all config modules under a single
`src/prime_rl/configs/` package, so the rule's bullet list points at paths
that no longer exist.

Both files describe the same policy and must agree. Update them so the
policy applies to **breaking** configuration changes only.

## What "breaking" means here

A change is **breaking** if it forces an existing user to edit their config
file before the new release will run. Concretely, the three categories
that count as breaking are:

- **Renamed** config fields — the old name is no longer accepted.
- **Removed** config fields — the field is deleted, or moved to a
  different path so the old path is no longer valid.
- **Moved** config fields — the field is relocated within the config
  hierarchy.

Everything else is **non-breaking**:

- Adding a new field with a default value.
- Adding a new optional feature.
- Changing the default value of an existing field.

Non-breaking changes must not require a `CHANGELOG.md` entry.

## Required edits

### 1. `.cursor/BUGBOT.md` — `## Changelog Enforcement` section

Rewrite the body of the `## Changelog Enforcement` section so that it:

1. States that the rule applies only when a PR introduces **breaking**
   configuration changes (and explicitly uses the word **breaking** in
   bold so the rule's emphasis is unambiguous).
2. Enumerates the three breaking-change categories — **Renamed**,
   **Removed**, and **Moved** — as a markdown bullet list, each with a
   one-line gloss explaining why it forces users to update.
3. Explicitly states that **Additive** changes and **default value**
   changes do **not** require a changelog entry. The exact phrase
   `do **not** require` should appear in this exclusion sentence so
   readers (and BugBot) can't miss it. (Capitalize "Additive" at the
   start of that sentence to match the surrounding sentence-case style.)
4. Lists the current location where config files live as a single bullet:

   - `src/prime_rl/configs/`

   The previous list of paths (`src/prime_rl/*/config.py`,
   `src/prime_rl/rl.py`, `src/prime_rl/utils/config.py`) is stale and must
   be removed.
5. Keeps the closing instruction telling BugBot to ask the author for an
   entry when a **breaking** change is detected without a corresponding
   `CHANGELOG.md` update.

The top-level `# BugBot Instructions` heading and the `## Changelog
Enforcement` subheading must remain unchanged.

### 2. `CHANGELOG.md` — header description

`CHANGELOG.md` begins with a `# Changelog` heading, a blank line, and then
a one-line description of the file's scope. Replace **only that
description line** so it announces the new breaking-only scope:

- It must use the bolded word **breaking** when describing what the file
  documents.
- It must call out the three categories that qualify (renamed, removed,
  moved fields).
- It must convey that these are changes that require users to update
  existing configs.

Drop the old wording about "added/moved/removed/renamed fields, notable
logic changes" — that phrasing is too broad now.

### 3. Leave everything else alone

- Do **not** edit any of the historical entries already listed in
  `CHANGELOG.md`. The bullet list of past changes below the description
  must be preserved verbatim.
- Do **not** modify any other files in the repository.
- Do **not** add a "test plan" or other PR-meta sections inside the
  markdown files themselves.

## Style notes

- Match the surrounding markdown style of each file. Use bolded inline
  emphasis (`**word**`) consistently — the rest of `CHANGELOG.md` and
  `BUGBOT.md` already follow this convention.
- Be concise. The goal is a clearer, narrower rule, not a longer one.
