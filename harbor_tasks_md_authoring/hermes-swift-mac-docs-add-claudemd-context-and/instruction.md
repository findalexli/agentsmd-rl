# docs: add CLAUDE.md — context and rules for Claude Code

Source: [hermes-webui/hermes-swift-mac#26](https://github.com/hermes-webui/hermes-swift-mac/pull/26)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

Adds CLAUDE.md to give Claude Code full context on this repo: WKWebView/ATS rules, plist key parity requirement, Sparkle 2 signing order, SSH tunnel security, known issues (#25), opus mentor integration, and common gotchas. .claude/ is already gitignored so local settings stay local.

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
