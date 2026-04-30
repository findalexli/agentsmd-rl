# Created AGENTS.md and CLAUDE.md

Source: [mozilla/rhino#2210](https://github.com/mozilla/rhino/pull/2210)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

I've created an AGENTS.md file with some basic rules and information about the project. I've tried to keep it very synthetic, according to the best practices I've been reading about.

I've also created a CLAUDE.md because apparently Claude Code [doesn't (yet?) support](https://github.com/anthropics/claude-code/issues/6235) the standard AGENTS.md file. According to what I've been [reading](https://www.reddit.com/r/GithubCopilot/comments/1nee01w/agentsmd_vs_claudemd/), it seems the best thing to do is to either symlink it, or create a one-line CLAUDE.md that references the standard AGENTS.md - which is what I have done.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
