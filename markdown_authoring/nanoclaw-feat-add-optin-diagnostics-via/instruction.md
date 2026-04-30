# feat: add opt-in diagnostics via PostHog

Source: [qwibitai/nanoclaw#1280](https://github.com/qwibitai/nanoclaw/pull/1280)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup/SKILL.md`
- `.claude/skills/setup/diagnostics.md`
- `.claude/skills/update-nanoclaw/SKILL.md`
- `.claude/skills/update-nanoclaw/diagnostics.md`

## What to add / change

## Summary

- Adds `scripts/send-diagnostics.ts` — standalone script that collects system info (version, platform, arch, node major version, container runtime), gates conflict filenames against upstream via `git ls-tree` (fail-closed), and sends anonymous events to PostHog
- Adds `.claude/skills/_shared/diagnostics.md` — shared end-of-skill instructions for Claude: handles sub-skill delegation (skip if invoked from parent), builds event data, shows exact payload via `--dry-run`, asks consent (Yes / No / Never ask again)
- Appends a "Diagnostics (Optional)" pointer to all 23 SKILL.md files, referencing the shared instructions

### Privacy safeguards
- No persistent install ID — ephemeral UUID per event, never stored
- Node major version only (no patch)
- Conflict filenames gated against upstream (private files excluded, fail-closed)
- Custom/private skill names masked as `"custom"`
- `$process_person_profile: false` — no PostHog person profiles
- "Never ask again" opt-out persisted in `.nanoclaw/state.yaml`

### Events
- `setup_complete` — platform, channels selected, failed step/exit code on failure
- `skill_applied` — skill name, conflicts, success
- `update_complete` — version age, update method, conflicts, breaking changes

## Test plan
- [ ] `npx tsx scripts/send-diagnostics.ts --event skill_applied --data '{"skill_name":"test","error_count":0}' --success --dry-run` → valid JSON with gated fields
- [ ] Same without `--dry-run` → sends to PostHog
- [ ] Set `neverAsk: true`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
