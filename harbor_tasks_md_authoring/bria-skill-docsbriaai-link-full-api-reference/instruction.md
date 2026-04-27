# docs(bria-ai): link full API reference at docs.bria.ai/llms.txt

Source: [Bria-AI/bria-skill#30](https://github.com/Bria-AI/bria-skill/pull/30)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/bria-ai/SKILL.md`

## What to add / change

<!-- CURSOR_AGENT_PR_BODY_BEGIN -->
## Summary

Updates the main **bria-ai** skill so assistants know where to find the complete, agent-oriented Bria API documentation when they are stuck on request shapes, parameters, or endpoints.

## Changes

- Short note under the intro directing agents to [https://docs.bria.ai/llms.txt](https://docs.bria.ai/llms.txt) as the canonical LLM-ready reference.
- Expanded **API Reference** section to call out **llms.txt** as the full spec and escape hatch beyond the in-repo summary.
- Added **llms.txt** as the first item under **Additional Resources**.

## Rationale

The in-skill quick reference and `references/api-endpoints.md` do not cover every edge case. Pointing stuck agents at the official **llms.txt** reduces guesswork and aligns implementation with agent-ready docs.
<!-- CURSOR_AGENT_PR_BODY_END -->

[Slack Thread](https://bria-talk.slack.com/archives/D098W339N94/p1774183964766259?thread_ts=1774183964.766259&cid=D098W339N94)

<div><a href="https://cursor.com/agents/bc-7fdebca9-6d96-59a9-8280-dca6854ca9c7"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/assets/images/open-in-web-dark.png"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/assets/images/open-in-web-light.png"><img alt="Open in Web" width="114" height="28" src="https://cursor.com/assets/images/open-in-web-dark.png"></picture></a>&nbsp;<a href="https://cursor.com/background-agent?bcId=bc-7fdebca9-6d96-59a9-8280-dca6854c

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
