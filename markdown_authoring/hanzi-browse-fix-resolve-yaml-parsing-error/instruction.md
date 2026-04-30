# fix: resolve YAML parsing error in apartment-finder/SKILL.md frontmatter

Source: [hanzili/hanzi-browse#112](https://github.com/hanzili/hanzi-browse/pull/112)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `server/skills/apartment-finder/SKILL.md`

## What to add / change

This fixes a YAML parsing error in the skill.md frontmatter.

The `description` field was unquoted and contained `Examples:`, which caused the YAML parser to fail with:
`mapping values are not allowed in this context`.

The fix wraps the `description` value in single quotes so the content stays exactly the same while parsing correctly.

No functional changes.
<img width="1076" height="264" alt="Screenshot 2026-04-16 at 6 37 41 PM" src="https://github.com/user-attachments/assets/ca906bcb-ba4c-49d9-acb5-a478ed614f89" />

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
