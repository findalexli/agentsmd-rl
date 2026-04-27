# fix(ce-compound): explicit mode prompt and lightweight rename

Source: [EveryInc/compound-engineering-plugin#528](https://github.com/EveryInc/compound-engineering-plugin/pull/528)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-compound/SKILL.md`

## What to add / change

## Summary

The `/ce:compound` skill told the model "always run full mode by default" but models consistently ignored the directive and asked the user to choose anyway — framing it around context/compaction concerns that the model can't actually evaluate (models have no introspection into context window usage, session duration, or token counts).

Instead of fighting the behavior, this designs the ask properly: present Full vs Lightweight with clear tradeoff framing focused on what the *user* knows (problem complexity, session state) rather than what the agent can't know (context budget).

Fixes #501

**Changes:**

- Replace the "always full by default" directive with an explicit two-option prompt the model must present before proceeding
- Rename "Compact-Safe Mode" to "Lightweight Mode" throughout — clearer name, consistent with the prompt wording
- Reframe Lightweight from "context-constrained sessions" to "same documentation, single pass" with honest tradeoffs (no dedup, no cross-refs)
- Add missing knowledge-track categories (best-practices, workflow-issues, developer-experience, documentation-gaps) to the categories list — these existed in the schema but weren't surfaced in the skill

Closes #501

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Claude_Code-Opus_4.6_(1M)-D97757?logo=claude&logoColor=whi

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
