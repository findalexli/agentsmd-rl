# exploring-codebases v2.2.0: step-0 setup, ref variants, sanity check, drill-optional

Source: [oaustegard/claude-skills#561](https://github.com/oaustegard/claude-skills/pull/561)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `exploring-codebases/SKILL.md`

## What to add / change

v2.2.0 — follow-up to #560 based on dogfooding.

After #560 merged (v2.0.0 → v2.1.0, the TODO-list rewrite), I ran the v2.1.0 skill on this repo itself. Counted tool calls: **11 when 5–6 would have sufficed**. Concrete failures the skill should have prevented:

1. **Dependencies section read as decorative setup** → skipped install → treesit silently returned `Scanned 0 files` → three diagnostic calls before I realized the language pack wasn't loaded.
2. **`REF=main` hardcoded** with no mention of branches/tags/PRs → fetched stale tarball (missing unmerged PR changes) → had to refetch.
3. **No post-extract sanity check** → I added `ls` separately when something looked wrong.
4. **Step 2 implied drill-always** → I drilled into a prose-only subdir (`exploring-codebases/` itself, no code) and got empty results.
5. **No diagnostic pointer** for the silent-failure mode in (1).

## v2.2.0 changes

- **New step 0 (setup)**: explicit `uv venv` + install + env exports. Once per session. Includes the silent-failure diagnostic inline: *"if step 2 reports `Scanned 0 files`, the language pack isn't loaded — come back here."*
- **Step 1 ref guidance**: `REF=main` now annotated with `# branch name, tag, or SHA. For a PR: pull/N/head`. Plus explicit note that default `main` silently gives stale code for unmerged work.
- **Step 1 sanity check**: `ls /tmp/$REPO | head` appended to the tarball block.
- **Step 2 drill-optional**: *"for pure 'what is this repo' exploration, skip drilling and go to

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
