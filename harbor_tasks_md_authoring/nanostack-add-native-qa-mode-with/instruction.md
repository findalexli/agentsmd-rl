# Add Native QA mode with computer use support

Source: [garagon/nanostack#57](https://github.com/garagon/nanostack/pull/57)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `qa/SKILL.md`

## What to add / change

## Summary
- Add **Native QA** mode to `/qa` for testing macOS apps, iOS Simulator, Electron apps, and GUI-only tools
- Uses Claude Code's [computer use](https://code.claude.com/docs/en/computer-use) MCP server
- Playwright remains preferred for web apps; computer use is the fallback for anything without a CLI, API, or browser interface
- Adds tool selection guidance: MCP > Bash > Playwright > computer use
- Prompt injection boundary applies to native app content
- Graceful fallback when computer use is not available (Linux, Windows, no Pro/Max)

## Changes
- `qa/SKILL.md`: new Native QA section, updated mode table, updated Visual QA to cover native apps, updated output format

## Test plan
- [ ] Enable `computer-use` via `/mcp` in Claude Code
- [ ] Build a simple macOS app (e.g. Swift window with button)
- [ ] Run `/qa` and verify it detects Native QA mode
- [ ] Verify it launches app, clicks through, takes screenshots
- [ ] Run `/qa` on a web app and verify it still uses Playwright (not computer use)
- [ ] Test on Linux/Windows: verify "computer use not available" message

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
