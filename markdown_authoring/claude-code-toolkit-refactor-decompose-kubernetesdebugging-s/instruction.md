# refactor: decompose kubernetes-debugging SKILL.md into references

Source: [notque/claude-code-toolkit#426](https://github.com/notque/claude-code-toolkit/pull/426)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/kubernetes-debugging/SKILL.md`
- `skills/kubernetes-debugging/references/crash-diagnosis.md`
- `skills/kubernetes-debugging/references/network-debugging.md`
- `skills/kubernetes-debugging/references/resource-debugging.md`

## What to add / change

## Summary
- Decomposed kubernetes-debugging SKILL.md from 355 lines to 83 lines
- Created 3 reference files: crash-diagnosis.md, network-debugging.md, resource-debugging.md
- Triage workflow (6-step describe/logs/events/exec sequence) preserved in SKILL.md
- All 15 key terms and 46 code fence markers verified present

## Test plan
- [ ] kubectl commands and YAML preserved in references
- [ ] Triage workflow logic intact in SKILL.md
- [ ] Ruff lint passes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
