# feat(agent): inject framework bias anchor into AGENTS.md (#10452)

Source: [neomjs/neo#10453](https://github.com/neomjs/neo/pull/10453)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

Authored by Gemini 3.1 Pro (Antigravity). Session 49e9b05a-0581-4fb7-861f-7e4970ea4c2b.

Related: #10452

This PR injects the Framework Bias Anchor into `AGENTS.md` (Phase 1 of the Identity Rewrite). It mechanically forces future agent sessions to nullify the "web framework" training-data bias and aligns their mental models with Neo's actual trajectory as a self-improving digital organism.

## Deltas from ticket (if any)
No structural deltas. This implements the exact Phase 1 requirement defined in the epic. Phase 2 (Ideation Sandbox) will follow via cross-family coordination.

## Test Evidence
- Read `AGENTS.md` locally to verify the section `15.5 The Framework Bias Anchor` was inserted cleanly and does not disrupt the markdown structure.

## Post-Merge Validation
- [ ] Verify future agent sessions successfully pull and adhere to the anchor context during startup.

## Commits
- `d921060` — feat(agent): inject framework bias anchor into AGENTS.md (#10452)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
