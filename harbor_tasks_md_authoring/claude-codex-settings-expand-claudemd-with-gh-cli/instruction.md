# Expand CLAUDE.md with gh CLI reference, Python guidance, and citation rules

Source: [fcakyon/claude-codex-settings#107](https://github.com/fcakyon/claude-codex-settings/pull/107)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Expand CLAUDE.md with detailed tool usage and verification rules.

- Split MCP Tools into structured subsections: Tavily, MongoDB, and GitHub CLI with 9 `gh` command examples for common repo operations
- Add Python coding guidance for plan mode verification (`python -c` before exiting plan) and `uv` as the package manager
- Add Citation Verification Rules section covering author names, publication venues, paper titles, cited claims, and BibTeX key consistency

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
