# chore: Add .cursorrules file for AI contributor guidance

Source: [calimero-network/core#1792](https://github.com/calimero-network/core/pull/1792)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.cursorrules`

## What to add / change

# chore: Add .cursorrules file for AI contributor guidance

## Description

This PR introduces a new `.cursorrules` file at the repository root. This file provides comprehensive guidance for AI tools, helping them understand project conventions, Rust style preferences, test expectations, commit format, crate organization, and common patterns used in the codebase.

This addresses the bounty to provide AI contributor guidance and improve consistency for AI-assisted development.

## Test plan

This change introduces a new configuration file for AI tools and does not alter any existing code functionality. Therefore, no specific tests are required. The content of the file can be reviewed for accuracy and completeness against the project's established conventions.

## Documentation update

This `.cursorrules` file itself serves as documentation for AI tools. No other public or internal documentation updates are required as a direct result of this PR.

---
<a href="https://cursor.com/background-agent?bcId=bc-d93a6345-b181-49cb-9075-d2c3a97b20b5"><picture><source media="(prefers-color-scheme: dark)" srcset="https://cursor.com/assets/images/open-in-cursor-dark.png"><source media="(prefers-color-scheme: light)" srcset="https://cursor.com/assets/images/open-in-cursor-light.png"><img alt="Open in Cursor" width="131" height="28" src="https://cursor.com/assets/images/open-in-cursor-dark.png"></picture></a>&nbsp;<a href="https://cursor.com/agents?id=bc-d93a6345-b181-49cb-9075-d2c3a97b20b5">

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
