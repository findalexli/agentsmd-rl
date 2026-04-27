# fix: correct source_repo field for faf-expert and faf-wizard skills

Source: [sickn33/antigravity-awesome-skills#477](https://github.com/sickn33/antigravity-awesome-skills/pull/477)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/faf-expert/SKILL.md`
- `skills/faf-wizard/SKILL.md`

## What to add / change

## Summary
Corrects the `source_repo` field in both FAF skills from incorrect `Wolfe-Jam/faf-cli` to correct `Wolfe-Jam/faf-skills`.

This fixes the source-validation CI failure in the previous submission (commit 99ba667).

## Changes
- **faf-expert/SKILL.md**: Updated `source_repo: Wolfe-Jam/faf-skills` 
- **faf-wizard/SKILL.md**: Updated `source_repo: Wolfe-Jam/faf-skills`

## Test Plan
- [x] Verified source repository exists at https://github.com/Wolfe-Jam/faf-skills
- [x] Confirmed both skill files have correct frontmatter metadata
- [x] Skills Registry CI should now pass source-validation step

## Quality Bar Checklist
- [x] **Completeness**: Skills have comprehensive documentation with examples
- [x] **Accuracy**: All metadata fields are correctly specified
- [x] **Clarity**: Descriptions clearly explain what each skill does
- [x] **Usability**: Skills provide actionable guidance for users
- [x] **Standards**: Follows SKILL.md format and frontmatter requirements
- [x] **Testing**: Verified source repository exists and is accessible
- [x] **Validation**: Both skills pass frontmatter validation

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
