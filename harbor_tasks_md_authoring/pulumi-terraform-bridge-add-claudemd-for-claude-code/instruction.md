# Add CLAUDE.md for Claude Code assistance

Source: [pulumi/pulumi-terraform-bridge#3192](https://github.com/pulumi/pulumi-terraform-bridge/pull/3192)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary
• Add CLAUDE.md file to provide guidance for Claude Code when working with this repository
• Documents common commands (build, test, lint) using the project's Makefile
• Includes architecture overview of the Pulumi Terraform Bridge
• Details key environment variables and testing structure

## Test plan
- [x] File is properly formatted and contains accurate project information
- [ ] Review content for completeness and accuracy

🤖 Generated with [Claude Code](https://claude.ai/code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
