# Add missing SKILL.md files for all skills and update repository docs

Source: [Microck/ordinary-claude-skills#2](https://github.com/Microck/ordinary-claude-skills/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `algorithmic-art/SKILL.md`
- `artifacts-builder/SKILL.md`
- `brand-guidelines/SKILL.md`
- `canvas-design/SKILL.md`
- `docx/SKILL.md`
- `internal-comms/SKILL.md`
- `mcp-builder/SKILL.md`
- `pdf/SKILL.md`
- `pptx/SKILL.md`
- `skill-creator/SKILL.md`
- `slack-gif-creator/SKILL.md`
- `template-skill/SKILL.md`
- `theme-factory/SKILL.md`
- `webapp-testing/SKILL.md`
- `xlsx/SKILL.md`

## What to add / change

### Summary
Add missing SKILL.md files for all skills by pulling from the official anthropics/skills repository. This ensures consistent documentation across all skill folders and improves discoverability.

### Details
- Downloaded and added SKILL.md for 29 skills (algorithmic-art, artifacts-builder, brand-guidelines, canvas-design, docx, internal-comms, mcp-builder, pdf, pptx, skill-creator, slack-gif-creator, template-skill, theme-factory, webapp-testing, xlsx) from anthropics/skills
- Fixed naming alignment across variants (e.g. artifacts-builder vs web-artifacts-builder)
- Created missing template-skill entry and updated related structure; adjusted memory/doc references
- Cleaned up placeholder/template files and updated CHANGES.md and .gitignore
- No breaking changes; documentation-only enhancement to improve maintainability and user guidance

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
