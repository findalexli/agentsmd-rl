#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcp-devtools

# Idempotency guard
if grep -qF "**Session span parent-child relationships**: Session spans in `internal/telemetr" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -112,13 +112,17 @@ mcp-devtools/
 
 ### Adding New Tools
 
-1. Implement `tools.Tool` interface in `internal/tools/`
-2. Register tool via `registry.Register()` in tool's `init()` function
-3. Import tool in `main.go` to trigger registration
-4. Add unit tests in `tests/tools/`
-5. Add documentation in `docs/tools/`
-6. Update `docs/tools/overview.md`
-7. Integrate with security framework if accessing files/URLs
+1. Create package under `internal/tools/[category]/[toolname]/`
+2. Implement `tools.Tool` interface with `Definition()` and `Execute()` methods
+3. Register tool in `init()` function using `registry.Register(&YourTool{})`
+4. Import the package in `internal/imports/tools.go` (NOT in `main.go`)
+5. Add unit tests in `tests/tools/` directory
+6. Add documentation in `docs/tools/` with clear, concise information
+7. Update `docs/tools/overview.md`
+8. Integrate with security framework if accessing files/URLs
+9. Verify token cost with `ENABLE_ADDITIONAL_TOOLS=your_tool_name make benchmark-tokens`
+
+**Important**: Do NOT add tool imports directly to `main.go`. Use the imports registry system in `internal/imports/tools.go` instead.
 
 ## Architecture & Structure
 
@@ -247,10 +251,161 @@ The only exception is in tests, tests are allowed to write to stdout/stderr.
 - Tool registry and discovery mechanisms
 - Memory management and potential leaks
 
+## Tool Registration Checklist
+
+**CRITICAL**: Before registering a new tool, verify the following:
+
+### Default Enablement Decision
+- **By default, ALL new tools are DISABLED** - this is the secure default
+- Only add tool to `defaultTools` list in `enabledByDefault()` (registry.go) if the user has explicitly stated it should be enabled by default
+- **If tool is NOT added to defaultTools**: It will require `ENABLE_ADDITIONAL_TOOLS` to use (this is correct for most tools)
+- Tests enable the tool via `ENABLE_ADDITIONAL_TOOLS` if not in defaultTools list
+- When in Doubt - **Leave the tool disabled by default.** It's safer to require explicit enablement than to accidentally expose destructive functionality.
+
+## Go Modernisation Rules
+
+CRITICAL: Follow these rules when writing Go code to avoid outdated patterns that `modernize` would flag:
+
+### Types and Interfaces
+- Use `any` instead of `interface{}`
+- Use `comparable` for type constraints when appropriate
+
+### String Operations
+- Use `strings.CutPrefix(s, prefix)` instead of `if strings.HasPrefix(s, prefix) { s = strings.TrimPrefix(s, prefix) }`
+- Use `strings.SplitSeq()` and `strings.FieldsSeq()` in range loops instead of `strings.Split()` and `strings.Fields()`
+
+### Loops and Control Flow
+- Use `for range n` instead of `for i := 0; i < n; i++` when index isn't used
+- Use `min(a, b)` and `max(a, b)` instead of if/else conditionals
+
+### Slices and Maps
+- Use `slices.Contains(slice, element)` instead of manual loops for searching
+- Use `slices.Sort(s)` instead of `sort.Slice(s, func(i, j int) bool { return s[i] < s[j] })`
+- Use `maps.Copy(dst, src)` instead of manual `for k, v := range src { dst[k] = v }` loops
+
+### Testing
+- Use `t.Context()` instead of `context.WithCancel()` in tests
+
+### Formatting
+- Use `fmt.Appendf(nil, format, args...)` instead of `[]byte(fmt.Sprintf(format, args...))`
+
+## MCP Development Best Practices
+
+**Build for Workflows, Not Just API Endpoints:**
+- Don't simply wrap existing API endpoints - build thoughtful, high-impact workflow tools
+- Consolidate related operations (e.g., `schedule_event` that both checks availability and creates event)
+- Focus on tools that enable complete tasks, not just individual API calls
+- Consider what workflows agents actually need to accomplish
+
+**Optimise for Limited Context:**
+- Agents have constrained context windows - make every token count
+- Return high-signal information, not exhaustive data dumps
+- Provide "concise" vs "detailed" response format options where applicable
+- Default to human-readable identifiers over technical codes (names over IDs)
+- Consider the agent's context budget as a scarce resource
+
+**Design Actionable Error Messages:**
+- Error messages should guide agents toward correct usage patterns
+- Suggest specific next steps: "Try using filter='active_only' to reduce results"
+- Make errors educational, not just diagnostic
+- Help agents learn proper tool usage through clear feedback
+
+**Follow Natural Task Subdivisions:**
+- Tool names should reflect how humans think about tasks
+- Group related tools with consistent prefixes for discoverability
+- Design tools around natural workflows, not just API structure
+
+**Use Evaluation-Driven Development:**
+- Create realistic evaluation scenarios early
+- Let agent feedback drive tool improvements
+- Prototype quickly and iterate based on actual agent performance
+
+To ensure quality, review the code for:
+- **DRY Principle**: No duplicated code between tools
+- **Composability**: Shared logic extracted into functions
+- **Consistency**: Similar operations return similar formats
+- **Error Handling**: All external calls have error handling
+- **Documentation**: Every tool has comprehensive docstrings/descriptions
+
+## OpenTelemetry Tracing Patterns
+
+**Session span parent-child relationships**: Session spans in `internal/telemetry/tracer.go` must be ended immediately followed by `ForceFlush()` to ensure they export to the backend before child tool spans. Without force flush, the OTEL batch processor exports asynchronously, causing child spans to arrive before their parent, resulting in "invalid parent span IDs" warnings in Jaeger.
+
+```go
+sessionSpan.End()
+// CRITICAL: Force flush ensures parent exports before children
+if tp != nil {
+    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
+    defer cancel()
+    _ = tp.ForceFlush(ctx)
+}
+```
+
+Tool spans inherit trace context via W3C Trace Context propagation (inject→extract pattern) in `StartToolSpan()`.
+
+## Tool Development Pattern
+
+All tools follow this pattern:
+1. Define struct implementing `tools.Tool`
+2. Register in `init()` with `registry.Register()`
+3. Implement `Definition()` for MCP tool schema
+4. Implement `Execute()` for tool logic
+5. Use shared logger and cache for consistency
+
+### Tool Descriptions Best Practices
+- Tool descriptions should focus on WHAT the tool does
+- Tool descriptions should be action-oriented and concise
+- ✅ Good: "Returns source code structure by stripping function/method bodies whilst preserving signatures, types, and declarations."
+- ❌ Poor: "Transform source code by removing implementation details while preserving structure. Achieves 60-80% token reduction for optimising AI context windows"
+- The first describes what the tool does; the second explains why it's useful (which bloats the context unnecessarily)
+- Tool descriptions should aim to be under 200 characters where possible; save detailed usage information for Extended Help
+
+### Tool Response Best Practices
+- Tool responses should be limited to only include information that is actually useful
+- Don't return the information an agent provides to call the tool back to them
+- Avoid any generic information or null / empty fields - these just waste tokens
+
 ## General Guidelines
 
 - Do not use marketing terms such as 'comprehensive' or 'production-grade' in documentation or code comments.
 - Focus on clear, concise actionable technical guidance.
+- Always use British English spelling, we are not American.
+- Follow the principle of least privileged security.
+- Use 0600 and 0700 permissions for files and directories respectively, unless otherwise specified avoid using 0644 and 0755.
+- All tools should work on both macOS and Linux unless otherwise specified (we do not need to support Windows).
+- Rather than creating lots of tools for one purpose / provider, instead favour creating a single tool with multiple functions and parameters.
+- When creating new MCP tools make sure descriptions are clear and concise as they are what is used as hints to the AI coding agent using the tool, you should also make good use of MCP's annotations.
+- The mcp-go package documentation contains useful examples of using the package which you can lookup when asked to implement specific MCP features https://mcp-go.dev/servers/tools
+
+## Important Warnings and Reminders
+
+- **CRITICAL**: Ensure that when running in stdio mode that we NEVER log to stdout or stderr, as this will break the MCP protocol.
+- When testing the docprocessing tool, unless otherwise instructed always call it with "clear_file_cache": true and do not enable return_inline_only
+- If you're wanting to call a tool you've just made changes to directly (rather than using the command line approach), you have to let the user know to restart the conversation otherwise you'll only have access to the old version of the tool functions directly.
+- When adding new tools ensure they are registered in the list of available tools in the server (within their init function), ensure they have a basic unit test, and that they have docs/tools/<toolname>.md with concise, clear information about the tool and that they're mentioned in the main README.md and docs/tools/overview.md.
+- We should be mindful of the risks of code injection and other security risks when parsing any information from external sources.
+- On occasion the user may ask you to build a new tool and provide reference code or information in a provided directory such as `tmp_repo_clones/<dirname>` unless specified otherwise this should only be used for reference and learning purposes, we don't ever want to use code that directory as part of the project's codebase.
+- After making changes and performing a build if you need to test the MCP server with the updated changes you MUST either test it from the command line - or STOP and ask the user to restart the MCP client otherwise you won't pick up the latest changes
+- **YOU MUST ALWAYS run `make lint && make test && make build` etc... to build the project rather than gofmt, go build or test directly, and you MUST always do this before stating you've completed your changes!**
+
+## Quick Debugging Tips
+
+You can debug the tool by running it in debug mode interactively, e.g.:
+
+```bash
+rm -f debug.log; pkill -f "mcp-devtools.*" ; echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "fetch_url", "arguments": {"url": "https://go.dev", "max_length": 500, "raw": false}}}' | ./bin/mcp-devtools stdio
+```
+
+Or with API key:
+
+```bash
+BRAVE_API_KEY="ask the user if you need this" ./bin/mcp-devtools stdio <<< '{"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": "brave_search", "arguments": {"type": "web", "query": "cat facts", "count": 1}}}'
+```
+
+### Lint Github Actions
+```bash
+actionlint
+```
 
 ## Review Checklist for Every PR
 
@@ -263,6 +418,10 @@ Before approving any pull request, verify:
 5. [ ] Error handling uses wrapped errors (`fmt.Errorf` with `%w`)
 6. [ ] Context cancellation handled properly
 7. [ ] Resource cleanup with defer statements
-8. [ ] Australian English spelling used throughout, No American English spelling used (unless it's a function or parameter to an upstream library)
+8. [ ] British English spelling used throughout, No American English spelling used (unless it's a function or parameter to an upstream library)
+9. [ ] New tools are disabled by default unless explicitly approved
+10. [ ] Tool imports added to `internal/imports/tools.go` (NOT `main.go`)
+11. [ ] Go modernisation rules followed (use `any`, `strings.CutPrefix`, etc.)
+12. [ ] Tool descriptions are concise and action-oriented (<200 chars where possible)
 
 If you are re-reviewing a PR you've reviewed in the past and your previous comments / suggestions have been addressed or are no longer valid please resolve those previous review comments to keep the review history clean and easy to follow.
PATCH

echo "Gold patch applied."
