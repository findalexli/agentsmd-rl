# Fix Double-Escaping of Markdown in Terminal Run Tool

In VS Code's terminal run tool (`src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/runInTerminalTool.ts`), the command display in chat invocation messages is double-escaped. The code calls `escapeMarkdownSyntaxTokens(displayCommand)` to escape markdown characters, then passes the result to `new MarkdownString(localize(...))`, which also performs escaping internally.

This causes commands containing markdown-significant characters (like `*`, `_`, `#`, backticks) to appear with visible escape characters in the chat UI. For example, a command like `echo "hello_world"` might display as `echo "hello\_world"`.

Fix by removing the `escapeMarkdownSyntaxTokens` call and passing `displayCommand` directly to the `localize`/`MarkdownString` calls, since `MarkdownString` handles the escaping. Also remove the now-unused import of `escapeMarkdownSyntaxTokens`.
