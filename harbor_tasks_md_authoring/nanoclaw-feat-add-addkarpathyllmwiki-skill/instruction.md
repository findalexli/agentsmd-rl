# feat: add /add-karpathy-llm-wiki skill

Source: [qwibitai/nanoclaw#1649](https://github.com/qwibitai/nanoclaw/pull/1649)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/add-karpathy-llm-wiki/SKILL.md`
- `.claude/skills/add-karpathy-llm-wiki/llm-wiki.md`

## What to add / change

## Summary
- Adds `/add-karpathy-llm-wiki` skill for setting up persistent wiki knowledge bases on NanoClaw
- Includes Karpathy's LLM Wiki gist as the reference material (`llm-wiki.md`)
- Setup skill guides collaborative design of directory structure, container skill, and group CLAUDE.md based on the pattern — no pre-written opinions
- NanoClaw-specific additions: source handling skill checks, curl for full document downloads, agent-browser for webpages

## Test plan
- [ ] Run `/add-karpathy-llm-wiki` and verify it reads the pattern, walks through group selection and design
- [ ] Verify the collaboratively created container skill and CLAUDE.md work in the agent container
- [ ] Test ingesting a URL and a file into the wiki

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
