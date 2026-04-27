# fix(skills): clarify Vibe Remote DM auth guidance

Source: [cyhhao/vibe-remote#85](https://github.com/cyhhao/vibe-remote/pull/85)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/use-vibe-remote/SKILL.md`

## What to add / change

## Summary
- clarify that DM access is currently enforced by bind state rather than `scopes.user.*.enabled`, so the skill no longer presents `enabled=false` as a reliable DM revoke path
- update the JSON validation example to validate the actual edited target file under `VIBE_REMOTE_HOME` instead of always checking the default `settings.json` path
- keep the follow-up narrowly scoped to the two post-merge Codex review findings from #81

## Testing
- `askill validate ./skills/use-vibe-remote/SKILL.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
