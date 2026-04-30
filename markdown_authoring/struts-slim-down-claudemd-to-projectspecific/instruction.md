# Slim down CLAUDE.md to project-specific guardrails

Source: [apache/struts#1605](https://github.com/apache/struts/pull/1605)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
- Remove generic architecture descriptions, common patterns, and technology lists that Claude already knows from training
- Keep only build commands, project-specific traps (javax.servlet, OGNL sandbox, RAT headers), and module layout
- Reduce from ~160 lines to ~35 lines

Based on [CLAUDE.md benchmark results](https://techloom.it/blog/claudemd-benchmark-results.html) showing that generic instructions degrade performance on bug-fix and code-generation tasks, while project-specific guardrails raise worst-case scores.

## Test plan
- [x] Verify Claude Code still picks up build commands and project rules from the slimmed file
- [x] Confirm no project-specific traps were lost (javax.servlet, OGNL security, RAT headers, plugin descriptors)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
