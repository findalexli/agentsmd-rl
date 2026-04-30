# Add doc-writer skill.md for AI-assisted documentation efforts

Source: [mitchdenny/hex1b#23](https://github.com/mitchdenny/hex1b/pull/23)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/skills/doc-writer/SKILL.md`

## What to add / change

Adds a skill file to guide AI coding agents in producing accurate, maintainable documentation across the repository's two documentation systems.

## Documentation Types Covered

**XML API Documentation** (`src/Hex1b/`)
- Public API documentation standards (summaries, parameters, returns, examples)
- XML tag usage (`<summary>`, `<remarks>`, `<example>`, `<see>`)
- HTML encoding requirements for code examples
- Cross-referencing conventions

**End-User Documentation** (`src/content/`)
- VitePress/Markdown structure and components
- Progressive disclosure patterns (tutorials → guides → deep dives)
- Working code examples and visual aids
- Consistent voice and linking strategy

## Additional Guidance

- Documentation workflow for new features, bug fixes, breaking changes
- Quality checklist before finalization
- Common pitfalls with corrections
- Tool references (xmldocmd, DocFX, VitePress)

## File Location

`/doc-writer skill.md` (491 lines, 15KB)

Ready for targeted documentation improvements.

<!-- START COPILOT CODING AGENT SUFFIX -->



<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

> I want to create a new doc-writer skill.md file to the repo. The purpose of this skill is to make it easier on maintainers to produce accurate and easy to maintain documentation with the help of coding agents.
> 
> The first step is that I want the skill.md file to out line the different kinds of documentation that we have within the repository.
> 
> T

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
