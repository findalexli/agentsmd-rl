# feat(agents): codify §22 turn-start mailbox-check + §23 sibling-file-lift (#10380)

Source: [neomjs/neo#10394](https://github.com/neomjs/neo/pull/10394)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Authored by Claude Opus 4.7 (Claude Code). Session a0abd010-e4fc-4e79-92e7-11ec5a074b2f.

Resolves #10380
Resolves #10383

Adds two per-turn AGENTS.md hardening sections, parallel in shape to the proven §3 Pre-Commit and §4.2 Consolidate-Then-Save reflex primitives. Both fire as Pre-Flight Check reasoning-statements at specific lifecycle points, designed to survive context-pruning to their application moment.

## What ships

### §22 Mailbox Check Protocol (Pre-Flight at Turn Start)

Symmetric companion to §4.2 (Consolidate-Then-Save at turn end). Codifies the \`list_messages({status: 'unread'})\` reflex at turn start so agents stop proceeding on stale cross-family coordination state.

- Pre-Flight Check reasoning-statement template (mirrors §3 / §4.2 proven shape)
- Conditional-skip clause for direct-continuation turns (cheap to check; cost of missed signal compounds)
- Explicit relationship to Phase 3 wake substrate (#10357): the mandate is *not* obsoleted by auto-wakeup — it becomes the verification primitive for wake-substrate transport (catches subscriber-filter exclusions, transport failures, cold-cache, in-flight-turn arrivals)
- Empirical anchor: session \`aaf22f06-cc5c-4dff-aa2f-7d5efb3a6343\` (this session) — 6+ instances of inbound A2A messages requiring explicit human-prompted nudges

### §23 Authoring Discipline (Sibling-File Lift)

Per-turn reflex companion to \`AGENTS_STARTUP.md §1 Steps 2-3\` (one-time boot read of \`src/Neo.mjs\` + \`src/core/Base.mjs\`). Boot

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
