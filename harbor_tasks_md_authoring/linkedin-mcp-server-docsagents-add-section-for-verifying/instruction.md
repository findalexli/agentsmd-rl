# docs(AGENTS): add section for verifying bug reports with detailed curl commands

Source: [stickerdaniel/linkedin-mcp-server#202](https://github.com/stickerdaniel/linkedin-mcp-server/pull/202)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `AGENTS.md`

## What to add / change

<!-- greptile_comment -->

<h3>Greptile Summary</h3>

This PR adds a "Verifying Bug Reports" section to `AGENTS.md` with step-by-step `curl` commands for testing the MCP server end-to-end via HTTP transport. The `SESSION_ID` extraction via `grep`/`awk`/`tr -d '\r'` is correct and properly handles Windows-style line endings in curl header output.

However, the **server startup command blocks the terminal** — without `&` or an explicit note to use a separate shell, developers or agents following the script linearly will never reach the `curl` commands.

<h3>Confidence Score: 4/5</h3>

- Safe to merge once the server startup command is backgrounded or explicit terminal-switching instructions are added.
- The change is documentation-only and does not affect runtime code. The session-ID extraction logic is correct. The primary issue is a usability blocker: the server startup command blocks the terminal, preventing the documented workflow from executing end-to-end in a single shell. This is straightforward to fix with `&` or an explicit note.
- AGENTS.md — specifically the server startup command (line 138) needs to either background the process or include explicit instructions to use a separate terminal.

<sub>Last reviewed commit: e8e8eb9</sub>

> Greptile also left **1 inline comment** on this PR.

<!-- /greptile_comment -->

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
