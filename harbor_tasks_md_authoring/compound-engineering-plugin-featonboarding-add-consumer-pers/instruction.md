# feat(onboarding): add consumer perspective and split architecture diagrams

Source: [EveryInc/compound-engineering-plugin#413](https://github.com/EveryInc/compound-engineering-plugin/pull/413)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `plugins/compound-engineering/skills/onboarding/SKILL.md`

## What to add / change

## Summary

The onboarding skill generates `ONBOARDING.md` to help new contributors understand a codebase. The "Where Do I Start?" section conflated two different questions — how to use the product vs. how to develop in the codebase — and the architecture diagram guidance didn't distinguish between component wiring and user interaction flows.

## Changes

**New section: "How It's Used" (Section 2)** — Sits between "What Is This?" and "How Is It Organized?" so contributors understand the product from the consumer's side before reading architecture. The output heading adapts to the project type:

| Project type | Output heading |
|---|---|
| End-user product (web app, mobile app) | User Experience |
| Developer tool (SDK, library, CLI) | Developer Experience |
| Both | User and Developer Experience |

This keeps the section relevant for all three cases — an SDK's "developer experience" (consuming the tool) is distinct from the "developer guide" (contributing to the codebase).

**Architecture diagrams: one vs. two lenses** — The skill now distinguishes between an architecture diagram (components, protocols, wiring) and a user interaction flow (logical product journey). For straightforward systems, one diagram suffices. For multi-surface products, both are generated. Both use ASCII flow diagrams, not prose lists.

**Section 5 renamed to "Developer Guide"** — Removes the ambiguity of "Where Do I Start?" which could apply to either audience. Document now has six sections with unamb

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
