# feat: add Bright Data local search skill

Source: [davila7/claude-code-templates#426](https://github.com/davila7/claude-code-templates/pull/426)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `cli-tool/components/skills/development/brightdata-local-search/SKILL.md`

## What to add / change

## Summary
- Adds new skill `brightdata-local-search` for setting up local web search using Bright Data SERP API
- Based on the [unfancy-search](https://github.com/yaronbeen/unfancy-search) pipeline (query expansion, SERP retrieval, RRF reranking)
- Guides users through: clone repo → configure Bright Data API key → run locally via Docker/Node.js → use search API from agents
- Local-only — does not use the hosted endpoint

## Test plan
- [ ] Install skill via `npx claude-code-templates@latest --skill development/brightdata-local-search`
- [ ] Verify SKILL.md renders correctly
- [ ] Regenerate component catalog after merge

🤖 Generated with [Claude Code](https://claude.com/claude-code)

<!-- This is an auto-generated description by cubic. -->
---
## Summary by cubic
Adds the `brightdata-local-search` skill to run local web search via Bright Data SERP API using the `unfancy-search` pipeline. Enables agents to use local-only search with query expansion and RRF reranking.

- Area: components (`cli-tool/components/`); added `skills/development/brightdata-local-search/SKILL.md`.
- New component added; regenerate catalog (`docs/components.json`) after merge.
- Env vars: `BRIGHT_DATA_API_TOKEN` (req), `BRIGHT_DATA_SERP_ZONE` (req), `ANTHROPIC_API_KEY` (optional for expansion).
- Purpose: provide local search via Bright Data using `unfancy-search`; agents call `http://localhost:3000` endpoints.
- No changes to CLI, API, website, or workers.

<sup>Written for commit 642aec40a43327f72d16

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
