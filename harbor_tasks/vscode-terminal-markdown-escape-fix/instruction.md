# Bug Report: Terminal command display double-escapes markdown in chat invocation messages

## Problem

When a chat agent runs a command in the VS Code integrated terminal, the invocation message displayed in the chat UI (e.g., "Running `command` in sandbox") shows mangled output for commands containing markdown-special characters like underscores, asterisks, or brackets. Characters that are part of normal shell commands get double-escaped — for example, a command containing underscores may render with visible backslashes before them.

This happens because the command string is being pre-escaped for markdown syntax before being passed into a `MarkdownString` via the `localize` template, but the `localize` substitution within backtick-delimited code spans already handles these characters correctly. The pre-escaping is redundant and causes the escape characters themselves to appear in the rendered output.

## Expected Behavior

Commands displayed in the chat invocation message should render cleanly inside their inline code spans, with no spurious backslash escaping of characters like `_`, `*`, `[`, etc.

## Actual Behavior

Commands containing markdown-significant characters display with visible escape backslashes in the chat UI invocation message (e.g., `some\_command` instead of `some_command`).

## Files to Look At

- `src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts`
