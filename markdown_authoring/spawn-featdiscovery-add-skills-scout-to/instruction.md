# feat(discovery): add skills scout to discovery team

Source: [OpenRouterTeam/spawn#3252](https://github.com/OpenRouterTeam/spawn/pull/3252)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/rules/discovery.md`
- `.claude/skills/setup-agent-team/discovery-team-prompt.md`

## What to add / change

## Summary
- Adds a **Skills Scout** teammate to the discovery cycle
- The scout researches, verifies, and curates the best skills per agent
- Updates `manifest.json` skills catalog automatically via PRs

## What the Skills Scout does
1. For each agent in manifest.json, researches:
   - Popular community skills (awesome-{agent}, GitHub trending)
   - MCP servers that work with the agent
   - Native agent configs that unlock full potential
2. Verifies each skill:
   - `npm view PACKAGE version` — package exists
   - `timeout 5 npx -y PACKAGE` — server starts
   - Checks prerequisites (apt, Chrome, API keys)
3. Updates manifest.json with the skill entry including:
   - Package name, prereqs, MCP config, SKILL.md content
   - `headless_compatible: false` for OAuth-requiring skills
4. Files PRs (max 5 skills per PR for reviewability)

## Three skill types
| Type | What | Example |
|------|------|---------|
| `mcp` | npm package giving agents tool access | `@playwright/mcp`, `@upstash/context7-mcp` |
| `skill` | SKILL.md following agentskills.io standard | `obra/superpowers`, `planning-with-files` |
| `config` | Native agent config files | Cursor `.mdc` rules, OpenClaw SOUL.md |

## Files changed
- `.claude/skills/setup-agent-team/discovery-team-prompt.md` — new Phase 3 with Skills Scout
- `.claude/rules/discovery.md` — new section 5: skills curation guidelines

## Test plan
- [x] 2032 tests pass (no code changes, just prompts)
- [ ] Manual: run discovery cycle, verify skills scou

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
