# Add agent skills for plugin development

Source: [NomaDamas/AutoRAG-Research#298](https://github.com/NomaDamas/AutoRAG-Research/pull/298)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agents/skills/create-generation-plugin/SKILL.md`
- `.agents/skills/create-ingestor-plugin/SKILL.md`
- `.agents/skills/create-metric-plugin/SKILL.md`
- `.agents/skills/create-retrieval-plugin/SKILL.md`

## What to add / change

## Summary

Add 4 agent skills under `.agents/skills/` following the [Vercel agent skills standard](https://skills.sh) that guide developers through the full plugin development lifecycle for AutoRAG-Research:

- **create-retrieval-plugin** — step-by-step guide for custom retrieval pipelines
- **create-generation-plugin** — step-by-step guide for custom generation pipelines
- **create-metric-plugin** — step-by-step guide for custom evaluation metrics (retrieval & generation)
- **create-ingestor-plugin** — step-by-step guide for custom data ingestors

Each SKILL.md follows the Vercel standard with:
- YAML frontmatter (`name`, `description`, `allowed-tools`)
- Kebab-case directory names matching the skill name
- Architecture overview, class hierarchy, required methods
- Step-by-step walkthrough with code examples verified against the codebase
- Reference section with key files and example implementations

### Installation

Skills are auto-detected when working inside the project. They can also be installed globally via:

```bash
npx skills add NomaDamas/AutoRAG-Research --skill create-retrieval-plugin
npx skills add NomaDamas/AutoRAG-Research --skill create-generation-plugin
npx skills add NomaDamas/AutoRAG-Research --skill create-metric-plugin
npx skills add NomaDamas/AutoRAG-Research --skill create-ingestor-plugin
```

## Original Issue

We need agent skills (follow Vercel agent skills rules) to help the developers who wants to implement their own plugins. The skill should con

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
