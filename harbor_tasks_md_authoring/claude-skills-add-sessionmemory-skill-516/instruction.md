# Add session-memory skill (#516)

Source: [oaustegard/claude-skills#555](https://github.com/oaustegard/claude-skills/pull/555)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `session-memory/SKILL.md`

## What to add / change

## Summary

Implements #516 — a new \`session-memory\` skill that maintains a
structured running-notes document during work sessions. Adapted from
Claude Code's \`services/SessionMemory/\` pattern.

Notes persist as a \`procedure\` memory tagged \`[session-memory, active]\`
via the \`remembering\` skill, so they survive container death within a
session thread. Manual-only invocation, inline (no background subagent).
Fixed template sections; updates use \`supersede()\` to keep exactly one
active note per session.

### Deviation from the issue spec

The issue proposed a ~2K-token budget for the note document. I relaxed
this to ~12K (matching CC's upstream design) because Muninn runs on
200K–1M context models — the original constraint was over-tight for this
environment. Rationale is captured in the skill's \`## Budget\` section.

## Test plan

- [ ] Trigger on "session notes" / "update notes" and confirm skill
      activates from description
- [ ] First invocation creates a memory tagged \`[session-memory, active]\`
      with the template structure
- [ ] Subsequent invocation finds the active memory via \`recall\` and
      supersedes it in place
- [ ] User correction during a session lands in \`## Errors & Corrections\`
      with priority over routine worklog entries
- [ ] "End session" transition retags \`active\` → \`archived\`
- [ ] Only one \`active\` note exists at a time across the session
- [ ] Note body stays under ~12K tokens for a typical session; worklog
      co

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
