# docs: compress AGENTS.md (~55%)

Source: [pollinations/pollinations#10304](https://github.com/pollinations/pollinations/pull/10304)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

- Reduces ~399 lines / ~5.7k tokens → ~197 lines / ~2.6k tokens
- Merges duplicate rules (branch checks, biome, reimplementation)
- Collapses verbose examples (repo tree, curl blocks, platform table)
- Preserves every actionable rule, command, path, label, token name
- Keeps CRITICAL/IMPORTANT markers on YAGNI, Tinybird, Common Mistakes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
