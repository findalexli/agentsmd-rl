# docs(skill): add Peer (Root) Sessions vs Sub-Agents guidance to agent-deck skill

Source: [asheshgoplani/agent-deck#631](https://github.com/asheshgoplani/agent-deck/pull/631)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/agent-deck/SKILL.md`

## What to add / change

## Summary

- Adds a Peer (Root) Sessions vs Sub-Agents section to the agent-deck skill documenting when to use \`-no-parent\` vs default parent-linkage.
- Includes a decision table, symptoms of unintended sub-agent creation, and the fix for an already-misparented session.
- Source: 2026-04-17 incident where a peer conductor was repeatedly spawned as a sub-agent until \`-no-parent\` was found via --help.

## Test plan

- [x] Skill is symlinked into ~/.agent-deck/skills/pool/agent-deck/ — change is picked up immediately by any future session that Read-s the SKILL.md
- [x] Content kept generic (no user-specific paths / names) — this skill ships to all agent-deck users
- [x] Verified on host: spawning with \`-no-parent\` produces \`parent_session_id: null\` in \`list --json\`

Docs-only, no code changes.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
