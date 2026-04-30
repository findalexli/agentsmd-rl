# chore: publish CLAUDE.md / AGENTS.md repo conventions

Source: [okhsunrog/vpnhide#115](https://github.com/okhsunrog/vpnhide/pull/115)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

## Why

Two reasons to bring this file into the repo:

1. **Auto-review utility**. The \`claude-code-review\` workflow runs four parallel agents per PR; **two of them are CLAUDE.md compliance checks**. Without a checked-in CLAUDE.md they just report "no CLAUDE.md to check" — half the review goes idle. With this file, those agents start verifying things like "changelog fragment present?", "no \`#NN\` cross-refs in the commit?", "VERSION untouched?".
2. **Quick orientation for contributors**. Plain markdown summary of what to read (CONTRIBUTING / docs / kmod/BUILDING), the workflow rules, build entry points, and the KPatch-Next design note. Useful regardless of any AI tool — it's basically a CONTRIBUTING-quickref.

## Summary

- \`CLAUDE.md\` (new, 100644) — canonical source.
- \`AGENTS.md\` (new, 120000 symlink → CLAUDE.md) — exposes the same file under the vendor-neutral \`AGENTS.md\` convention used by Codex / Cursor / etc. Stored as a real git symlink (mode 120000), not a duplicate, so there's only one place to update.
- Wording is neutral — no Claude-specific addressing — so the file reads naturally to humans and to other AI tooling.

## Notes

- **Windows without Developer Mode**: \`AGENTS.md\` may materialise as a one-line text file containing \`CLAUDE.md\` instead of a real symlink. Not a blocker — contributor sees the target name and opens \`CLAUDE.md\`. Most of this project's contributors are on Linux/macOS anyway.
- This file does **not** replace \`CONTRIBUTING.md\`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
