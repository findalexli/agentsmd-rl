# chore(release-skill): use --help (not version) for Step 1.5 smoke probe

Source: [coleam00/Archon#1359](https://github.com/coleam00/Archon/pull/1359)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/release/SKILL.md`

## What to add / change

## Summary

Fixes a false positive in the /release skill's Step 1.5 pre-flight binary smoke — hit during the 0.3.8 release attempt, where the smoke aborted despite the actual binary being healthy.

## Root cause

Step 1.5 does a bare \`bun build --compile\` for speed — it deliberately skips \`scripts/build-binaries.sh\`, so \`packages/paths/src/bundled-build.ts\` keeps its dev defaults, including \`BUNDLED_IS_BINARY = false\`.

\`version.ts\` branches on that constant: when \`true\` it returns the embedded version string, when \`false\` it calls \`getDevVersion()\`, which reads \`SCRIPT_DIR/../../../../package.json\`. Inside a compiled binary \`SCRIPT_DIR\` resolves under \`\$bunfs/root/\`, the walk produces a CWD-relative path that doesn't exist, and we get \"Failed to read version: package.json not found (bad installation?)\".

The skill even said "version or --help are both acceptable" — which isn't true for this project.

## Change

Use \`--help\` instead. It exercises the same module-init graph (so it still catches the real failure modes the skill calls out: Pi package.json init crash, Bun --bytecode output bugs, CJS wrapper issues, circular imports under minify) but has no dev/binary branch, so no false positive. Expanded the comment block to explain why, so this doesn't get "normalized" back to \`version\` by a future drive-by.

## Verification

- Ran the updated Step 1.5 locally against current dev: \`Pre-flight binary smoke: PASSED\` (was falsely failing on \`version

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
