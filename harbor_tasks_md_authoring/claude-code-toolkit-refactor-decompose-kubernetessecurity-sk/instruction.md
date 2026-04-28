# refactor: decompose kubernetes-security SKILL.md into references

Source: [notque/claude-code-toolkit#427](https://github.com/notque/claude-code-toolkit/pull/427)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `skills/kubernetes-security/SKILL.md`
- `skills/kubernetes-security/references/network-policies.md`
- `skills/kubernetes-security/references/pod-security.md`
- `skills/kubernetes-security/references/rbac-patterns.md`
- `skills/kubernetes-security/references/supply-chain.md`

## What to add / change

## Summary
- Decomposed kubernetes-security SKILL.md from 317 lines to 76 lines
- Created 4 reference files: rbac-patterns.md, pod-security.md, network-policies.md, supply-chain.md
- Added 3-phase workflow (IDENTIFY, RESPOND, VERIFY) to thin orchestrator
- All 9 YAML manifests, misconfiguration table, and Dockerfile example preserved

## Test plan
- [ ] All YAML manifests preserved in references
- [ ] Reference Loading Table maps signals correctly
- [ ] Ruff lint passes

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
