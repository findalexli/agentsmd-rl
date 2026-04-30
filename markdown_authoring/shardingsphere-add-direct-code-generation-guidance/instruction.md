# Add direct code generation guidance to CLAUDE.md

Source: [apache/shardingsphere#36930](https://github.com/apache/shardingsphere/pull/36930)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Add "Direct Code Generation" section to Operational Procedures
- Allow Claude to generate final code and call tools without seeking explicit user approval
- Enable automatic application of formatting tools (e.g., Spotless) when appropriate
- Support independent decision-making within task scope
- Remove tentative language requirement
- Simplify pre-execution checklist to only require change declaration when uncertainty exists

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
