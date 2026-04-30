# Enhance Claude.md with CODE_OF_CONDUCT.md integration and simplification

Source: [apache/shardingsphere#36932](https://github.com/apache/shardingsphere/pull/36932)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Add specific CODE_OF_CONDUCT.md mappings instead of generic reference
- Include clean code principles, naming conventions, and AIR testing principle
- Integrate CODE_OF_CONDUCT.md test coverage requirements with Quality Assurance standards
- Add AIR (Automatic, Independent, Repeatable) and BCDE (Border, Correct, Design, Error) testing principles
- Simplify redundant descriptions while maintaining comprehensive guidance
- Add precise assertion naming conventions (actualXXX, expectedXXX)

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
