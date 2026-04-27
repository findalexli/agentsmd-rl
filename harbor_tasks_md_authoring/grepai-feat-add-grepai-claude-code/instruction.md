# feat: add grepai Claude Code skill

Source: [yoanbernabeu/grepai#31](https://github.com/yoanbernabeu/grepai/pull/31)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.claude/skills/grepai/SKILL.md`

## What to add / change

## Description

This PR adds the grepai skill to the repository.

The purpose of this skill is to override intent-based code exploration by requiring contributors (and agents) to use grepai for semantic search and call graph tracing, instead of relying on built-in Grep/Glob for “search by meaning”.

## Type of Change


- [ ] Bug fix (non-breaking change that fixes an issue)
- [x] New feature (non-breaking change that adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to change)
- [ ] Documentation update
- [ ] Refactoring (no functional changes)
- [ ] Performance improvement
- [ ] Test update

## How Has This Been Tested?

- [x] Manual testing

**Test Configuration:**
- OS: MacOS
- Embedding provider: nomic-embed-text

## Checklist

- [ ] My code follows the project's code style
- [ ] I have run `golangci-lint run` and fixed any issues
- [ ] I have added tests that prove my fix/feature works
- [ ] I have updated the documentation if needed
- [ ] I have added an entry to CHANGELOG.md (if applicable)
- [ ] My changes generate no new warnings
- [ ] All new and existing tests pass

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
