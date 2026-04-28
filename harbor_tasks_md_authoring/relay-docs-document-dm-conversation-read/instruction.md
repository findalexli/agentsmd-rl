# docs: document DM conversation read auth (dual-auth pattern)

Source: [AgentWorkforce/relay#648](https://github.com/AgentWorkforce/relay/pull/648)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `packages/openclaw/skill/SKILL.md`

## What to add / change

The skill doc was missing documentation for how to read DM conversation messages. Reading messages inside a DM conversation requires dual auth: workspace key as Authorization + agent token as X-Agent-Token. This was undocumented and caused confusion during setup.

Changes:
- Added 'Read DMs' subsection to Section 5 (Read Messages) with mcporter and curl examples
- Updated Token model section (Section 8) to note the dual-auth requirement for DM reads
<!-- devin-review-badge-begin -->

---

<a href="https://app.devin.ai/review/agentworkforce/relay/pull/648" target="_blank">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://static.devin.ai/assets/gh-open-in-devin-review-dark.svg?v=1">
    <img src="https://static.devin.ai/assets/gh-open-in-devin-review-light.svg?v=1" alt="Open with Devin">
  </picture>
</a>
<!-- devin-review-badge-end -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
