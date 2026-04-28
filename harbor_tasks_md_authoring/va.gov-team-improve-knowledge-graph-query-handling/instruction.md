# Improve knowledge graph query handling and tool-calling instructions in copilot-instructions.md

Source: [department-of-veterans-affairs/va.gov-team#139069](https://github.com/department-of-veterans-affairs/va.gov-team/pull/139069)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Claude (especially Sonnet 4.5) was silently stalling after repeated failed `getfile` attempts on `knowledge-graph.json` (35k+ lines, truncated every time), never synthesizing an answer until the user asked again. Three fixes to `.github/copilot-instructions.md`:

## Changes

- **`<critical_tool_calling_instructions>` block** — replaces the overly strict "no output until all tool calls complete" rule with guidance to synthesize answers once sufficient information is gathered, and to immediately switch to code search when `getfile` truncates

- **`<knowledge_graph_usage>` section** — explicit guidance that `knowledge-graph.json` must never be read via `getfile`; includes a query pattern table (lexical vs. semantic vs. targeted getfile by question type) and a multi-step workflow example for complex queries

- **Expanded troubleshooting section** — adds four knowledge-graph-specific issues with root causes and solutions: first-try failures, missing/outdated graph data, truncation warnings, and 404 path errors (including URL-encoded space handling and non-standard path fallbacks like `products/ask-va/design/User research/`)

No changes to `scripts/build-knowledge-graph.js` or `copilot-setup-steps.yml` were needed — recursive research directory scanning and non-standard path notes were already in place from a prior PR.

<!-- START COPILOT ORIGINAL PROMPT -->



<details>

<summary>Original prompt</summary>

# Improve Knowledge Graph Query Handling and Tool-Calling Instructions

## 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
