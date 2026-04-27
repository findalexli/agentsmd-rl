# fix(claws): clarify openclaw ox install choice and block brew

Source: [sageox/ox#492](https://github.com/sageox/ox/pull/492)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `claws/openclaw/sageox-distill/SKILL.md`
- `claws/openclaw/sageox-summary/SKILL.md`

## What to add / change

## Summary
- **Force the agent to actually ask.** The `sageox-distill` and `sageox-summary` skills told the agent to "prompt the user to choose an install method" and labeled curl as `(recommended)` — agents were reading that as permission to silently pick curl and persist the choice to `~/.openclaw/memory/sageox-ox-install.json`. Replaced with a hard blocking gate: `STOP` / `MUST` / `wait for their response` / `Do not pick a default`, plus an explicit "Reply `1` or `2`" prompt and a follow-up rule for handling "you choose" / "whatever" answers.
- **Block Homebrew (and other package managers) for `ox`.** A `sageox/tap/ox` tap exists for general use, but it's not supported inside OpenClaw skills — the per-skill PATH / `~/.openclaw/.env` flow assumes curl or git-source installs. Added an explicit prohibition covering `brew`, `apt`, `dnf`, `pacman`.
- **Platform-agnostic framing.** Added a note that the two options work the same on macOS and Linux; the choice should be based on pinned-release vs `main` with auto-update, not OS.

No frontmatter, no schema, no skill behavior changed beyond the install setup prose. Both SKILL.md files get the same edit.

## Test plan
- [x] `python3 .claude/skills/clawhub-skill-lint/scripts/lint.py claws/openclaw/sageox-distill claws/openclaw/sageox-summary` → PASS, 0 critical, 0 warnings
- [ ] Exercise the skill flow end-to-end in OpenClaw with a fresh `~/.openclaw/memory/` (no `sageox-ox-install.json`) and confirm the agent stops and asks rather t

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
