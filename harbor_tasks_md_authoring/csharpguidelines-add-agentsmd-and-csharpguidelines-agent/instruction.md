# Add AGENTS.md and csharp-guidelines agent skill

Source: [dennisdoomen/CSharpGuidelines#394](https://github.com/dennisdoomen/CSharpGuidelines/pull/394)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/csharp-guidelines/SKILL.md`
- `.agents/skills/csharp-guidelines/references/class-design.md`
- `.agents/skills/csharp-guidelines/references/commenting.md`
- `.agents/skills/csharp-guidelines/references/framework.md`
- `.agents/skills/csharp-guidelines/references/layout.md`
- `.agents/skills/csharp-guidelines/references/maintainability.md`
- `.agents/skills/csharp-guidelines/references/member-design.md`
- `.agents/skills/csharp-guidelines/references/misc-design.md`
- `.agents/skills/csharp-guidelines/references/naming.md`
- `.agents/skills/csharp-guidelines/references/performance.md`
- `AGENTS.md`

## What to add / change

## Summary

Adds agent-agnostic instructions and a structured agent skill so that any AI coding agent (GitHub Copilot, Cursor, Codex, etc.) can automatically apply these C# guidelines when generating or reviewing code.

## Files added

| File | Purpose |
|------|---------|
| \AGENTS.md\ | Root-level agent instructions — describes the repo structure, rule format, build commands, and points to the skill |
| \.agents/skills/csharp-guidelines/SKILL.md\ | Agent skill with YAML frontmatter and a compact rule index (all 114 rules across 9 categories in table form) |
| \.agents/skills/csharp-guidelines/references/*.md\ | Per-category detailed reference files (progressive disclosure — loaded only when the agent needs deeper context) |

## Design decisions

- **\AGENTS.md\** follows the [agents.md](https://agents.md) open format, compatible with GitHub Copilot, OpenAI Codex, Cursor, Amp, Jules, and others.
- **\SKILL.md\** follows the [Agent Skills specification](https://agentskills.io/specification): YAML frontmatter with \
ame\ + \description\, compact body under 500 lines, with detailed content split into \eferences/\ for progressive disclosure.
- The skill \description\ is written to trigger automatically whenever an agent is generating or reviewing C# code.
- Reference files are organised by the same 9 categories already used in the site navigation.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
