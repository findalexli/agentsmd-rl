# chore: add claude.md and agents.md

Source: [artsy/eigen#13266](https://github.com/artsy/eigen/pull/13266)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

### Description

In this PR, I am adding `AGENTS.md` and `CLAUDE.md` files to make AI tools more efficient inside Eigen.

## How was this built?

### 1. Gathered best practices
Sources:
https://www.builder.io/blog/claude-md-guide
https://skills.sh/mounirdhahri/skills/agentsmd-claudemd-generator
https://acjay.com/2026/02/18/the-ai-landslide-is-happening/
https://agents.md/
Force agents.md https://github.com/artsy/force/blob/main/AGENTS.md
https://code.claude.com/docs/en/memory

### 2. Combined best practices into a skill
Using the above files and docs, I generated a skill to generate a `CLAUDE.md` and `AGENTS.md` skill that we can use in our repos

### 3. Manually review that it makes sense and that it follows our best practices and the community best practices. Mainly:
- import `AGENTS.md` inside `CLAUDE.md`
- reference docs instead of copying them
- Prefer docs over what's in the folders (double edged sword)
- Warn about context window
- ...

### 4. Published the skill (maybe it's useful to someone else)

I published the skill here https://skills.sh/mounirdhahri/skills/agentsmd-claudemd-generator and installed it to generate the docs


### 5. Used the skill to generate `AGENTS.md` and `CLAUDE.md` inside Eigen.

### 6. Review generated docs and update the skill accordingly


**What will be the impact of this on the context window?**


| Source | Lines | Est. Tokens | % of 200k context |
  |---|---|---|---|
  | AGENTS.md (without import)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
