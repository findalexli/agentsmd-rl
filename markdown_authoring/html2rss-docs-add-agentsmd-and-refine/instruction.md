# docs: add AGENTS.md and refine copilot-instructions.md

Source: [html2rss/html2rss#287](https://github.com/html2rss/html2rss/pull/287)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `AGENTS.md`

## What to add / change

This pull request updates the engineering agent guidelines for the repository, focusing on clarity, structure, and maintainability of the instructions. The main changes include a comprehensive rewrite of `.github/copilot-instructions.md` to clarify agent roles, coding and testing standards, and workflow, as well as the introduction of `AGENTS.md` to formally establish `.github/copilot-instructions.md` as the canonical source of agent instructions.

**Documentation and Guidelines Overhaul:**

* Major rewrite and restructuring of `.github/copilot-instructions.md` to clarify agent roles, mission, system pipeline, coding/testing standards, security practices, and workflow. The new version provides more actionable and organized instructions for engineering agents.
* Addition of `AGENTS.md`, which designates `.github/copilot-instructions.md` as the canonical set of agent guidelines and instructs contributors to extend it for future process changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
