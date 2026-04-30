# feat(agents): codify Pipeline Authority & Forkability Model (#10372)

Source: [neomjs/neo#10373](https://github.com/neomjs/neo/pull/10373)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## 🤖 Agent Origin
**Agent:** Gemini 3.1 Pro (Antigravity)
**Origin Session ID:** 27016011-8ae9-48bb-af87-9479dd5b0fd0

## 📖 What & Why
Resolves #10372

This PR explicitly codifies the 'Pipeline Authority' inside `AGENTS.md`. It explains the 'Forkability Model', distinguishing between the generic abstraction 'Human Commander' needed for downstream forks and the reality that inside the `neomjs/neo` repository, agents answer directly to `@tobiu`. This addresses MX (Model Experience) by clarifying reporting lines and eliminating excessive generic deference without breaking downstream forks.

## 🏗️ Architectural Changes
- Modified `AGENTS.md` to introduce Section 1.1 'The Forkability Model'.
- Explicitly stated the official maintainer relationship with `@tobiu` for Gemini and Claude.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
