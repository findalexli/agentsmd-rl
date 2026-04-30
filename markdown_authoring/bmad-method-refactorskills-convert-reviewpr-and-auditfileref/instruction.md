# refactor(skills): convert review-pr and audit-file-refs to bmad-os skills

Source: [bmad-code-org/BMAD-METHOD#1732](https://github.com/bmad-code-org/BMAD-METHOD/pull/1732)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/bmad-os-audit-file-refs/SKILL.md`
- `.claude/skills/bmad-os-audit-file-refs/prompts/instructions.md`
- `.claude/skills/bmad-os-review-pr/README.md`
- `.claude/skills/bmad-os-review-pr/SKILL.md`
- `.claude/skills/bmad-os-review-pr/prompts/instructions.md`

## What to add / change

## Summary

- Move Raven PR Review (`tools/maintainer/review-pr.md`) and File Ref Audit (`tools/audit-file-refs.md`) into `.claude/skills/` as proper bmad-os skills
- Follow established SKILL.md + `prompts/instructions.md` split pattern with `bmad-os-` prefix naming
- Strip XML tags from Raven content and promote sections to H2 headings
- Delete originals from `tools/` including empty `maintainer/` directory

## Test plan

- [ ] Invoke `/bmad-os-review-pr` in a Claude Code session and verify it is discovered and loads correctly
- [ ] Invoke `/bmad-os-audit-file-refs` in a Claude Code session and verify it is discovered and loads correctly
- [ ] Verify `prompts/instructions.md` is read on-demand (not pre-loaded into context)
- [ ] Confirm `tools/maintainer/` directory and `tools/audit-file-refs.md` no longer exist
- [ ] Diff instructions.md against original sources to confirm no unintended content changes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
