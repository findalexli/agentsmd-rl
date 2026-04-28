# Update skills

Source: [dotnet/efcore#38126](https://github.com/dotnet/efcore/pull/38126)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/analyzers/SKILL.md`
- `.agents/skills/bulk-operations/SKILL.md`
- `.agents/skills/cosmos-provider/SKILL.md`
- `.agents/skills/dbcontext-and-services/SKILL.md`
- `.agents/skills/make-custom-agent/SKILL.md`
- `.agents/skills/make-skill/SKILL.md`
- `.agents/skills/migrations/SKILL.md`
- `.agents/skills/query-pipeline/SKILL.md`
- `.agents/skills/servicing-pr/SKILL.md`
- `.agents/skills/testing/SKILL.md`
- `.agents/skills/tooling/SKILL.md`
- `.agents/skills/update-pipeline/SKILL.md`
- `.github/copilot-instructions.md`

## What to add / change

Based on https://github.com/dotnet/efcore/settings/copilot/memory

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
