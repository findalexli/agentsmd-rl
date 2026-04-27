# docs(skills): refresh Vibe Remote routing guidance

Source: [cyhhao/vibe-remote#88](https://github.com/cyhhao/vibe-remote/pull/88)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/use-vibe-remote/SKILL.md`

## What to add / change

## Summary
- update the `use-vibe-remote` skill to match the latest Claude backend routing behavior, including per-scope `claude_reasoning_effort`
- replace outdated wording that said Claude reasoning was not applied by Vibe Remote and add a concrete Claude routing recipe
- keep the skill aligned with the current configuration surface for channel/user routing and backend capability notes

## Testing
- `askill validate ./skills/use-vibe-remote/SKILL.md`

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
