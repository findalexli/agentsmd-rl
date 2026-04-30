# Add code-review and spec-check Claude agents

Source: [Automattic/wordpress-activitypub#2905](https://github.com/Automattic/wordpress-activitypub/pull/2905)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/agents/code-review.md`
- `.claude/agents/spec-check.md`
- `.claude/skills/pr/SKILL.md`
- `CLAUDE.md`

## What to add / change

## Proposed changes:
* Add **code-review** agent — reviews code changes for quality, WordPress coding standards, and ActivityPub conventions before PR creation
* Add **spec-check** agent — audits endpoints against the W3C ActivityPub spec, SWICG ActivityPub API spec, and supported FEPs listed in `FEDERATION.md`
* Update the **pr skill** to run code-review before creating a PR

### Other information:

- [ ] Have you written new tests for your changes, if applicable?

N/A — these are Claude Code agent configuration files, not plugin code.

## Testing instructions:

* Open Claude Code in this repo
* Ask it to "review my changes" — should delegate to the code-review agent
* Ask it to "check spec compliance for the inbox endpoint" — should delegate to the spec-check agent
* Run `/pr` — should trigger code-review before creating the PR

### Changelog entry

No changelog needed — dev tooling only.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
