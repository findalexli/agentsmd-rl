# fix(security): add collaborator filter to all agent prompts

Source: [OpenRouterTeam/spawn#3351](https://github.com/OpenRouterTeam/spawn/pull/3351)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/setup-agent-team/_shared-rules.md`
- `.claude/skills/setup-agent-team/refactor-issue-prompt.md`
- `.claude/skills/setup-agent-team/refactor-team-prompt.md`
- `.claude/skills/setup-agent-team/security-review-all-prompt.md`
- `.claude/skills/setup-agent-team/security-scan-prompt.md`
- `.claude/skills/setup-agent-team/security-team-building-prompt.md`
- `.claude/skills/setup-agent-team/teammates/qa-record-keeper.md`
- `.claude/skills/setup-agent-team/teammates/refactor-community-coordinator.md`
- `.claude/skills/setup-agent-team/teammates/refactor-pr-maintainer.md`
- `.claude/skills/setup-agent-team/teammates/security-issue-checker.md`
- `.claude/skills/setup-agent-team/teammates/security-scanner.md`

## What to add / change

## Summary
- The bash collaborator gate (`exit 0` before Claude spawns) only blocks issue-triggered runs. Schedule-triggered agents run Claude freely, and prompts told it to run raw `gh issue list` — bypassing the gate entirely.
- Non-collaborator issue bodies could contain prompt injection that Claude would read and act on.
- All 10 prompt files with `gh issue list` or `gh pr list` now pipe through a jq filter using the cached collaborator list at `/tmp/spawn-collaborators-cache`.
- Added a mandatory "Collaborator Gate" section to `_shared-rules.md` with the reusable filter snippet.

## Files changed
- `_shared-rules.md` — new collaborator gate section + updated dedup rule
- 6 issue-list prompts (high risk): `refactor-team-prompt.md`, `refactor-community-coordinator.md`, `security-issue-checker.md`, `qa-record-keeper.md`, `security-scan-prompt.md`, `security-scanner.md`
- 4 PR-list prompts (lower risk): `refactor-issue-prompt.md`, `security-review-all-prompt.md`, `security-team-building-prompt.md`, `refactor-pr-maintainer.md`

## Test plan
- [ ] Run a refactor cycle and verify only collaborator issues appear
- [ ] File a test issue from a non-collaborator account and confirm agents don't see it

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
