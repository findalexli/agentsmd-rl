# docs: improve CLAUDE.md and add AGENTS.md for token efficiency

Source: [ComposioHQ/agent-orchestrator#36](https://github.com/ComposioHQ/agent-orchestrator/pull/36)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Condensed CLAUDE.md from 223 to 169 lines (24% reduction)
- Removed verbose sections (reference implementation table, redundant explanations)
- Added "Key Files" section to guide agents to types.ts and plugin examples
- Tightened tech stack, conventions, and commands sections
- Created new AGENTS.md (74 lines) specifically for orchestrated agents
- AGENTS.md covers: session awareness, metadata format, PR workflow, hooks, communication

These changes optimize documentation for AI agents, reducing token waste while improving discoverability of critical files like packages/core/src/types.ts.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
