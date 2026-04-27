# Improve skill tooling: allowed-tools, AskUserQuestion, task tracking

Source: [vladikk/modularity#1](https://github.com/vladikk/modularity/pull/1)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/document/SKILL.md`
- `skills/high-level-design/SKILL.md`
- `skills/review/SKILL.md`

## What to add / change

Hey Vladik! 👋

I went through all four skills and noticed the tool declarations were missing or incomplete. This PR adds proper `allowed-tools` frontmatter and updates the tool usage patterns — without touching any of the domain content (the Balanced Coupling model, analysis methodology, etc. are all untouched).

## What changed

### `review/SKILL.md`
- **Added `allowed-tools`**: `Read, Grep, Glob, LSP, AskUserQuestion, TaskCreate, TaskUpdate` — these are all tools the skill body already references but weren't declared, meaning users got unexpected permission prompts
- **Added Interaction Rules section**: Consistent with the pattern already established in `high-level-design` — one question at a time, multiple choice preferred, short headers
- **Added `TaskCreate` directive**: Progress tracking for the 4-step review process (shows up in the terminal status bar)
- **Replaced plain-text questions with `AskUserQuestion`**: Steps 1.2 (scope selection) and 1.4 (domain classification, team structure, pain points) now use structured multiple-choice prompts instead of prose. Each question is asked separately per the one-at-a-time principle

### `high-level-design/SKILL.md`
- **Added `allowed-tools`**: `Read, Write, Edit, AskUserQuestion, TaskCreate, TaskUpdate` — Write and Edit are needed for creating design documents in Steps 3-5, and Edit for the iterative loop in Step 6
- **Input section now uses `AskUserQuestion`**: When no file path is provided, the skill now uses the proper tool

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
