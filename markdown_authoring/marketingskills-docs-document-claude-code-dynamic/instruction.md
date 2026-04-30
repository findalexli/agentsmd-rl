# docs: document Claude Code dynamic content injection for skills

Source: [coreyhaines31/marketingskills#189](https://github.com/coreyhaines31/marketingskills/pull/189)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Summary

- Documents the backtick-command syntax in AGENTS.md as a Claude Code-specific enhancement pattern for skills
- Explains the most impactful use case: auto-injecting .agents/product-marketing-context.md at skill invocation time so the model gets context immediately without a file-reading step
- Includes examples for other useful injections (date, git branch, recent commits)
- Clearly marks this as Claude Code-only to preserve cross-agent compatibility of SKILL.md files

Prompted by a tip from @lydiahallie on X.

## Test plan

- [ ] Verify the new section appears in AGENTS.md under "Claude Code-Specific Enhancements"
- [ ] Verify the cross-agent compatibility warning is present
- [ ] Verify code examples are syntactically correct

Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
