# feat(skills): create industry-friction-radar skill (#10297)

Source: [neomjs/neo#10298](https://github.com/neomjs/neo/pull/10298)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.agent/skills/industry-friction-radar/SKILL.md`
- `.agent/skills/industry-friction-radar/references/industry-friction-radar-workflow.md`

## What to add / change

Authored by Neo-Gemini-3-1-Pro (Antigravity) consuming Neo-Opus-4-7's ideation handoff — session 0b29a8fa-c6b0-42e2-ab3b-8015a99db2d8.

Resolves #10297

Implemented the `industry-friction-radar` skill, establishing a systematic SOTA innovation intake mechanism while enforcing strict engine-category architectural boundaries.

## Deltas from ticket
- Explicitly documented the `ideation-sandbox` output integration and duplicate sweep necessity in Step 3.
- Added explicit citations array to the JSON schema output in Step 2 for provenance attribution.

## Test Evidence
- Verified formatting of `SKILL.md` and `references/industry-friction-radar-workflow.md`.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
