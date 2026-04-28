# docs: enhance CLAUDE.md with detailed architecture and development notes

Source: [narumiruna/yfinance-mcp#78](https://github.com/narumiruna/yfinance-mcp/pull/78)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `CLAUDE.md`

## What to add / change

- Add comprehensive details about async/await patterns and asyncio.to_thread usage
- Document chart.py module with WebP encoding strategy
- Expand demo chatbot architecture with dual backend support details
- Add Testing section documenting integration test patterns
- Add Development Notes section covering:
  - Async/await patterns for wrapping blocking yfinance calls
  - Chart generation using WebP format for token efficiency
  - Tool naming convention with yfinance_ prefix
  - Error handling patterns using _error() helper

These additions provide future developers with critical context about architectural decisions and patterns that aren't immediately obvious from reading individual source files.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
