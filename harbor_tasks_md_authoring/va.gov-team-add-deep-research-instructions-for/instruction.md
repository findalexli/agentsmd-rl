# Add deep research instructions for analyzing research findings

Source: [department-of-veterans-affairs/va.gov-team#139263](https://github.com/department-of-veterans-affairs/va.gov-team/pull/139263)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Summary files answer "what research exists?" but provide no guidance for "what did we learn?" queries that require reading actual findings. This adds instructions to `.github/copilot-instructions.md` so Copilot knows when and how to trigger deep research vs. use summary files.

### Changes to `.github/copilot-instructions.md`

New "Deep Research Analysis for Research Findings" section inserted between Research Data Integrity Rules and Critical Setup Requirements:

- **Decision matrix** — table mapping question types to the right tool (summary files for metadata, deep research for analysis)
- **7 query patterns with prompt templates** — pain points, thematic analysis, journey mapping, impact tracing, pre-research discovery, cross-product synthesis, stakeholder briefings
- **2 example conversations** — shows expected Copilot behavior for pain point analysis and pre-research discovery
- **Decision logic** — 3-step flowchart: metadata → findings/themes → multiple files
- **Best practices** — specificity, structured output, citations, expectation-setting
- **Output format template** — consistent structure for presenting deep research results
- **Performance notes** — summary queries <5s, deep research 2-4min

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
