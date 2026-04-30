# docs: expose commands and skills in AGENTS.md for cross-agent parity

Source: [mastra-ai/mastra#15311](https://github.com/mastra-ai/mastra/pull/15311)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

## Description

Adds Commands and Skills sections to AGENTS.md so that non-Claude agents (e.g. OpenAI Codex) can discover and use the same reusable command prompts and domain-specific skill files that Claude agents access via `.claude/commands/` and `.claude/skills/`. This gives all coding agents parity regardless of which provider they come from.

## Related Issue(s)

N/A

## Type of Change

- [ ] Bug fix (non-breaking change that fixes an issue)
- [ ] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [x] Documentation update
- [ ] Code refactoring
- [ ] Performance improvement
- [ ] Test update

## Checklist

- [x] I have made corresponding changes to the documentation (if applicable)
- [ ] I have added tests that prove my fix is effective or that my feature works

<!-- This is an auto-generated comment: release notes by coderabbit.ai -->

## ELI5
This PR adds a helpful instruction guide to AGENTS.md that lists all the reusable command templates and skill guides that AI agents can use when working on the project. Think of it like adding a table of contents or a menu that shows agents what tools and best practices they can follow, whether they're Claude or another AI provider.

## Overview
Updates the root `AGENTS.md` file to expose Commands and Skills sections, enabling agents of any provider to discover and reference reusable command prompts and domain-specific skill document

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
