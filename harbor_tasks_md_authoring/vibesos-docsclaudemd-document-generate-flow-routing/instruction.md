# docs(CLAUDE.md): document generate flow routing landmine

Source: [popmechanic/VibesOS#74](https://github.com/popmechanic/VibesOS/pull/74)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

PR #73 fixed a real architectural gotcha that should never have taken as long as it did to spot. The editor's generate flow does NOT go through \`scripts/server/handlers/generate.ts:handleGenerate\` — that handler has zero call sites. The real flow is in \`ws.ts\` at \`case 'generate':\`, using the persistent bridge so brainstorm Q&A and the actual write can happen in one conversation.

CLAUDE.md didn't say this. A grep for \`handleGenerate\` / \`runOneShot\` / \`persistent bridge\` / \`ws.ts\` returned zero hits in the doc. This PR fixes that.

## What's added

1. **New "Generate Flow Routing" section** explaining:
   - \`handleGenerate\` is dead code; the real flow is \`ws.ts:case 'generate':\`
   - Why the persistent bridge is used (multi-turn brainstorm → generate continuity)
   - The two parallel stream-event translators and which one emits which UI event names
   - Where Direction D staged-preview events fire and why
   - **The manual verification rule:** unit tests of \`runOneShot\` / \`dispatchStreamEvent\` do NOT exercise the editor path — confirm via DevTools \`[WS-IN]\` logs before claiming a generate-flow feature works end-to-end
2. **Agent Quick Reference row** pointing future work at the new section before anyone edits the dead handler
3. **Non-Obvious Files entries** for \`ws.ts\`, \`claude-bridge.ts\`, \`event-translator.ts\`, and \`generate.ts\` (flagged as unused)

## Test plan

- [x] Docs-only change — no code. No test regressions possible.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
