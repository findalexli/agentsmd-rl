# Add handwritten AI outbound voice Python skill

Source: [team-telnyx/ai#108](https://github.com/team-telnyx/ai/pull/108)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `telnyx-python/skills/telnyx-ai-outbound-voice-python/SKILL.md`

## What to add / change

Summary
- add a handwritten telnyx-ai-outbound-voice-python skill under the telnyx-python plugin
- keep this skill outside generator output so future publishes preserve it as manual content

Notes
- this skill intentionally has no generated_by marker, so publish.sh will preserve it
- a companion generator PR registers it under telnyx-python marketplace metadata

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
