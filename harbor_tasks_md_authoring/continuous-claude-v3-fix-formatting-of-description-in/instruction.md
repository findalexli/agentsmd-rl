# Fix formatting of description in SKILL.md

Source: [parcadei/Continuous-Claude-v3#48](https://github.com/parcadei/Continuous-Claude-v3/pull/48)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/completion-check/SKILL.md`

## What to add / change

it causes Failed to parse YAML frontmatter: incomplete explicit mapping pair; a key node is missed; or followed by a non-tabulated empty line this fix should fix that, before it might work with cc but with opencode or other agents gives an error

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## Summary by CodeRabbit

* **Chores**
  * Updated documentation metadata formatting.

<sub>✏️ Tip: You can customize this high-level summary in your review settings.</sub>

<!-- end of auto-generated comment: release notes by coderabbit.ai -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
