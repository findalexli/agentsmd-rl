# Expand memory-recall skill description for better trigger coverage

Source: [zilliztech/memsearch#353](https://github.com/zilliztech/memsearch/pull/353)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/claude-code/skills/memory-recall/SKILL.md`
- `plugins/codex/skills/memory-recall/SKILL.md`
- `plugins/openclaw/skills/memory-recall/SKILL.md`
- `plugins/opencode/skills/memory-recall/SKILL.md`

## What to add / change

## Summary

- Claude Code 2.1.105 raised the skill description cap from 250 to 1,536 chars and warns on truncation. The current `memory-recall` description sits close to the old cap.
- Rewrite the description (~740 chars) to include example trigger phrasings, the search/expand/deep-drill flow, and skip conditions, so the model matches the right situations on first shot.
- Apply the same body across every harness plugin variant for consistent trigger behavior.

## Test plan

- [x] All four `SKILL.md` frontmatters remain valid YAML.
- [x] Description length under the 1,536-char cap.
- [x] No behavioral changes; skill body content unchanged.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
