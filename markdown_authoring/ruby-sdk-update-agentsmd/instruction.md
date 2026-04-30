# Update AGENTS.md

Source: [modelcontextprotocol/ruby-sdk#182](https://github.com/modelcontextprotocol/ruby-sdk/pull/182)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Motivation and Context

Follow-up to #175.

Since `json_rpc_handler` was merged in #175, it has been removed from AGENTS.md.

The "Dependencies" section was also removed because the information there would have become redundant.

## Types of changes
<!-- What types of changes does your code introduce? Put an `x` in all the boxes that apply: -->
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [x] Documentation update

## Checklist
<!-- Go over all the following points, and put an `x` in all the boxes that apply. -->
- [x] I have read the [MCP Documentation](https://modelcontextprotocol.io)
- [x] My code follows the repository's style guidelines
- [x] New and existing tests pass locally
- [x] I have added appropriate error handling
- [x] I have added or updated documentation as needed

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
