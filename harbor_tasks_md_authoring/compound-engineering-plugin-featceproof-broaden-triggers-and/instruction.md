# feat(ce-proof): broaden triggers and surface markdown viewing

Source: [EveryInc/compound-engineering-plugin#618](https://github.com/EveryInc/compound-engineering-plugin/pull/618)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/ce-proof/SKILL.md`

## What to add / change

The `ce-proof` skill now reliably triggers on direct user requests to share, view, iterate on, or HITL a markdown file via Proof, not just upstream-caller handoffs from `ce-brainstorm` / `ce-ideate` / `ce-plan`. Markdown viewing (upload a local `.md`, get a rendered shareable URL) is surfaced as a first-class use case alongside the HITL review workflow the description previously led with.

Under the hood, the HITL Review Mode section now names "Direct user request" as a first-class entry point next to the upstream-handoff path, so a bare user phrase like "share this to proof so we can iterate" no longer needs a caller. The description itself drops prose decision trees and meta-commentary in favor of intent-first trigger phrasings, with one compact negative clause that excludes evidence, mathematical/logical proofs, burden of proof, proof-of-concept, and bare "proofread this" senses of the word.

---

[![Compound Engineering](https://img.shields.io/badge/Built_with-Compound_Engineering-6366f1)](https://github.com/EveryInc/compound-engineering-plugin)
![Claude Code](https://img.shields.io/badge/Opus_4.7_(1M)-D97757?logo=claude&logoColor=white)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
