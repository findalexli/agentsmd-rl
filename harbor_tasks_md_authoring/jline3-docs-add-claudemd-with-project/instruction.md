# docs: Add CLAUDE.md with project conventions

Source: [jline/jline3#1641](https://github.com/jline/jline3/pull/1641)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

## Summary

Add a `CLAUDE.md` file documenting project conventions for AI coding assistants (Claude Code, etc.):

- Build commands (`./mvx` wrapper usage)
- Code formatting (Spotless / Palantir Java Format)
- Module structure overview
- Java version requirements (build: 22, runtime: 11+)
- Commit message format (`<type>: <description>`)
- No AI attribution policy (no `Co-Authored-By` or "Generated with" lines)
- Copyright header format
- Testing patterns and examples

## Test plan

- [x] File is valid markdown
- [x] Build/test commands documented are accurate

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
