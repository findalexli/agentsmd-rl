Background server processes started via the `run_in_terminal` tool with `isBackground: true` are being killed when VS Code exits, causing long-running servers to terminate unexpectedly.

The terminal command rewriting system in `src/vs/workbench/contrib/terminalContrib/chatAgentTools/browser/tools/commandLineRewriter/` needs a new rewriter that can wrap background commands so they survive VS Code shutdown:

- On POSIX systems (Linux/macOS), commands should be wrapped with `nohup` and run in the background
- On Windows with PowerShell, commands should be wrapped with `Start-Process` to detach from the terminal process tree

The rewriter should:
1. Only activate when `isBackground` is true
2. Check a configuration setting (`chat.tools.terminal.detachBackgroundProcesses`) before applying the rewrite
3. Return `undefined` for foreground commands or when the setting is disabled
4. Return an `ICommandLineRewriterResult` with `rewritten`, `reasoning`, and `forDisplay` fields
5. Handle PowerShell detection on Windows to only apply the rewrite for PowerShell shells

Update the `ICommandLineRewriterOptions` interface to include an optional `isBackground` property, modify `runInTerminalTool.ts` to pass the `isBackground` flag to rewriters, and add the new configuration setting. The rewriter must be registered after `CommandLineSandboxRewriter` so that the wrapping applies to the entire sandbox runtime.

Add comprehensive tests in `src/vs/workbench/contrib/terminalContrib/chatAgentTools/test/electron-browser/commandLineBackgroundDetachRewriter.test.ts` covering:
- Foreground commands return `undefined`
- Setting disabled returns `undefined`
- POSIX commands wrapped with `nohup`
- PowerShell commands wrapped with `Start-Process`
- Quote escaping for PowerShell commands
- Non-PowerShell Windows shells return `undefined`
