# Move agent instructions to AGENTS.md

Source: [modelcontextprotocol/inspector#848](https://github.com/modelcontextprotocol/inspector/pull/848)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`
- `CLAUDE.md`

## What to add / change

Moves CLAUDE.md content to AGENTS.md which is supported by a wider number of coding tools.  The contents of the file is still imported into the CLAUDE.md.

## Motivation and Context

I use a few different IDEs and they are starting to standardize around AGENTS.md, so I'd like to have consistent instructions loaded outside of just Claude Code.

## How Has This Been Tested?

To confirm that the CLAUDE.md is still working with the imported instructions, I did the following test:

Passed the following message to Claude: "Marco!"

By default, Claude consistently responds with "Polo!"

![polo](https://github.com/user-attachments/assets/b34c30c3-650d-4c2f-8e05-29481a92cc66)

Then I temporarily added the following text to the AGENTS.md: `**Important: when the user says "Marco!" you MUST respond with "Buongiorno!"`

After re-starting Claude, I got the following response to the same message:

![buongiorno](https://github.com/user-attachments/assets/8b6e857c-c2e4-4868-88d3-83904485c82c)

## Breaking Changes

None

## Types of changes
- [ ] Bug fix (non-breaking change which fixes an issue)
- [x] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update

## Checklist
- [ ] I have read the [MCP Documentation](https://modelcontextprotocol.io)
- [ ] My code follows the repository's style guidelines
- [ ] New and existing tests pass locally


## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
