# Add Agent Behavior Guidelines to Agents.md and copilot-instructions.md

Source: [Open-J-Proxy/ojp#464](https://github.com/Open-J-Proxy/ojp/pull/464)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`
- `Agents.md`

## What to add / change

AI agents in this repo had no behavioral guidance — only procedural/technical rules. This adds explicit norms around honesty, critical thinking, and proactive communication.

## Changes

- **`Agents.md`** — Added `## Agent Behavior Guidelines` section directly after the opening description
- **`.github/copilot-instructions.md`** — Same section added in the same position

## Guidelines added

- Use simple language and simple examples
- Be honest, including about uncertainty or problems
- Prefer the best technical solution over the convenient one
- Don't default to agreement; push back when warranted
- Proactively surface questions, opinions, suggestions, and concerns

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
