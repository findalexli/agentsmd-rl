# Small improvement to DV skill

Source: [JuliaGenAI/julia-agent-skills#2](https://github.com/JuliaGenAI/julia-agent-skills/pull/2)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/documenter-vitepress/SKILL.md`

## What to add / change

# New Skill: `skill-name`

**Description:** Brief description of what this skill does.

**Julia packages/topics covered:** e.g., DocumenterVitepress.jl, Makie.jl

## Checklist

- [x] Skill directory is under `skills/` with a lowercase-hyphenated name
- [x] `SKILL.md` has `name` and `description` in YAML frontmatter
- [x] `name` field matches directory name
- [x] Description explains **when** the skill should activate
- [x] Added a row to the "Available Skills" table in README.md
- [x] Instructions are Julia-specific and include working code examples

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
