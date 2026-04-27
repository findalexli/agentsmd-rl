# docs(agents): add attribution evaluation guardrails

Source: [TencentCloudBase/CloudBase-MCP#547](https://github.com/TencentCloudBase/CloudBase-MCP/pull/547)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `mcp/AGENTS.md`

## What to add / change

## Summary
- add attribution/evaluation guardrails to root and `mcp/AGENTS.md`
- tell agents to avoid grader-only fixes, internal artifact leakage, and alias-field shims
- remove `cnb` force-push guidance and keep GitHub-only push as the safe default

## Testing
- not run (documentation-only changes)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
