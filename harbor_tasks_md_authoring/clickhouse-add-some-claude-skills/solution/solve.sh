#!/usr/bin/env bash
set -euo pipefail

cd /workspace/clickhouse

# Idempotency guard
if grep -qF "Always load and apply the following skills:" ".claude/CLAUDE.md" && grep -qF "- **CRITICAL:** Build output is redirected to a unique log file created with `mk" ".claude/skills/build/SKILL.md" && grep -qF "description: Configure and customize skills for your workspace by asking questio" ".claude/skills/install-skills/SKILL.md" && grep -qF "- **CRITICAL:** Test output is redirected to a unique log file created with `mkt" ".claude/skills/test/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/CLAUDE.md b/.claude/CLAUDE.md
@@ -40,3 +40,9 @@ You can run integration tests as in `tests/integration/README.md` using: `python
 When writing tests, do not add "no-*" tags (like "no-parallel") unless strictly necessarily.
 
 When writing tests in tests/queries, prefer adding a new test instead of extending existing ones.
+
+Always load and apply the following skills:
+
+- .claude/skills/install-skills
+- .claude/skills/build
+- .claude/skills/test
\ No newline at end of file
diff --git a/.claude/skills/build/SKILL.md b/.claude/skills/build/SKILL.md
@@ -0,0 +1,217 @@
+---
+name: build
+description: Build ClickHouse with various configurations (Release, Debug, ASAN, TSAN, etc.). Use when the user wants to compile ClickHouse.
+argument-hint: [build-type] [target] [options]
+disable-model-invocation: false
+allowed-tools: Task, Bash(ninja:*), Bash(cd:*), Bash(ls:*), Bash(pgrep:*), Bash(ps:*), Bash(pkill:*), Bash(mktemp:*), Bash(sleep:*)
+---
+
+# ClickHouse Build Skill
+
+Build ClickHouse in `build/${buildType}` directory (e.g., `build/Debug`, `build/ASAN`, `build/RelWithDebInfo`).
+
+## Arguments
+
+- `$0` (optional): Build type - one of: `Release`, `Debug`, `RelWithDebInfo`, `ASAN`, `TSAN`, `MSAN`, `UBSAN`. Default: `RelWithDebInfo`
+- `$1` (optional): Target - specific target to build (e.g., `clickhouse-server`, `clickhouse-client`, `clickhouse`). Default: `clickhouse`
+- `$2+` (optional): Additional cmake/ninja options
+
+## Build Types
+
+| Type | Description | CMake Flags |
+|------|-------------|-------------|
+| `Release` | Optimized production build | `-DCMAKE_BUILD_TYPE=Release` |
+| `Debug` | Debug build with symbols | `-DCMAKE_BUILD_TYPE=Debug` |
+| `RelWithDebInfo` | Optimized with debug info | `-DCMAKE_BUILD_TYPE=RelWithDebInfo` |
+| `ASAN` | AddressSanitizer (memory errors) | `-DCMAKE_BUILD_TYPE=Debug -DSANITIZE=address` |
+| `TSAN` | ThreadSanitizer (data races) | `-DCMAKE_BUILD_TYPE=Debug -DSANITIZE=thread` |
+| `MSAN` | MemorySanitizer (uninitialized reads) | `-DCMAKE_BUILD_TYPE=Debug -DSANITIZE=memory` |
+| `UBSAN` | UndefinedBehaviorSanitizer | `-DCMAKE_BUILD_TYPE=Debug -DSANITIZE=undefined` |
+
+## Common Targets
+
+- `clickhouse` - Main all-in-one binary
+- `clickhouse-server` - Server component
+- `clickhouse-client` - Client component
+- `clickhouse-local` - Local query processor
+- `clickhouse-benchmark` - Benchmarking tool
+
+## Build Process
+
+**IMPORTANT:** This skill assumes the build directory is already configured with CMake. Do NOT run `cmake` or create build directories - only run `ninja`.
+
+1. **Determine build configuration:**
+   - Build type: `$0` or `RelWithDebInfo` if not specified
+   - Target: `$1` or `clickhouse` if not specified
+   - Build directory: `build/${buildType}` (e.g., `build/RelWithDebInfo`, `build/Debug`, `build/ASAN`)
+
+2. **Create log file and start the build:**
+
+   **Step 2a: Create temporary log file first:**
+   ```bash
+   mktemp /tmp/build_clickhouse_XXXXXX.log
+   ```
+   - This will print the log file path
+   - **IMMEDIATELY report to the user:**
+     - "Build logs will be written to: [log file path]"
+     - Then display in a copyable code block:
+       ```bash
+       tail -f [log file path]
+       ```
+     - Example: "You can monitor the build in real-time with:" followed by the tail command in a code block
+
+   **Step 2b: Start the ninja build:**
+   ```bash
+   cd build/${buildType} && ninja [target] > [log file path] 2>&1
+   ```
+
+   **Important:**
+   - Do NOT create build directories or run `cmake` configuration
+   - The build directory must already exist and be configured
+   - Use the log file path from step 2a
+   - Redirect both stdout and stderr to the log file using `> "$logfile" 2>&1`
+   - Run the build in the background using `run_in_background: true`
+   - **After starting the build**, report: "Build started in the background. Waiting for completion..."
+
+3. **Wait for build completion:**
+   - Use TaskOutput with `block=true` to wait for the background task to finish
+   - The log file path is already known from step 2a
+   - Pass the log file path to the Task agent in step 4
+
+4. **Report results:**
+
+   **ALWAYS use Task tool to analyze results** (both success and failure):
+   - Use Task tool with `subagent_type=general-purpose` to analyze the build output
+   - **Pass the log file path from step 2a** to the Task agent - let it read the file directly
+   - Example Task prompt: "Read and analyze the build output from: /tmp/build_clickhouse_abc123.log"
+   - The Task agent should read the file and provide:
+
+     **If build succeeds:**
+     - Confirm build completed successfully
+     - Report binary location: `build/${buildType}/programs/[target]`
+     - Mention any warnings if present
+     - Report build time if available
+     - Keep response concise
+
+     **If build fails:**
+     - Parse the build output to identify what failed (compilation, linking, etc.)
+     - Extract and highlight the specific error messages with file paths and line numbers
+     - Identify compilation errors with the exact error text
+     - For linker errors, identify missing symbols or libraries
+     - For template errors, simplify and extract the core issue from verbose C++ template error messages
+     - Provide the root cause if identifiable
+     - Provide a concise summary with:
+       - What component/file failed to build
+       - The specific error type (syntax error, undefined symbol, etc.)
+       - File path and line number where error occurred
+       - The actual error message
+       - Brief explanation of likely cause if identifiable
+     - Filter out excessive verbose compiler output and focus on the actual errors
+
+   - Return ONLY the Task agent's summary to the user
+   - Do NOT return the full raw build output
+
+   **After receiving the summary:**
+   - If build succeeded: Proceed to step 5 to check for running server
+   - If build failed:
+     - Present the summary to the user first
+     - **MANDATORY:** Use `AskUserQuestion` to prompt: "Do you want deeper analysis of this build failure?"
+       - Option 1: "Yes, investigate further" - Description: "Launch a subagent to investigate the root cause across the codebase"
+       - Option 2: "No, I'll fix it myself" - Description: "Skip deeper analysis and proceed without investigation"
+     - If user chooses "Yes, investigate further":
+       - **CRITICAL: DO NOT read files, edit code, or fix the issue yourself**
+       - **MANDATORY: Use Task tool to launch a subagent for deep analysis only (NO FIXES)**
+       - Use Task tool with `subagent_type=Explore` to search for related code patterns, similar errors, or find where symbols/functions are defined
+       - For complex errors involving multiple files or dependencies, use Task tool with `subagent_type=general-purpose` to investigate missing symbols, headers, or dependencies
+       - Provide specific prompts to the agent based on the error type:
+         - Compilation errors: "Analyze the compilation error in [file:line]. Find where [symbol/class/function] is defined in the codebase and explain the root cause. Do NOT fix the code."
+         - Linker errors: "Investigate why [symbol] is undefined and find its implementation. Explain what's causing the linker error. Do NOT fix the code."
+         - Header errors: "Find which header file provides [missing declaration] and explain what's missing. Do NOT fix the code."
+         - Template errors: "Investigate the template instantiation issue with [template name] and explain the root cause. Do NOT fix the code."
+       - The subagent should only investigate and analyze, NOT edit or fix code
+       - **CRITICAL: Return ONLY the agent's summary of findings to the user**
+       - **DO NOT return full investigation details, raw file contents, or excessive verbose output**
+       - **Present findings in a well-organized summary format**
+     - If user chooses "No, I'll fix it myself":
+       - Skip deeper analysis
+     - Skip step 5 (no need to check for running server if build failed)
+
+5. **MANDATORY: Check for running server and offer to stop it (only after successful build):**
+
+   **IMPORTANT:** This step MUST be performed after every successful build. Do not skip this step.
+
+   **Use Task tool with `subagent_type=general-purpose` to handle server checking and stopping:**
+
+   ```
+   Task tool with subagent_type=general-purpose
+   Prompt: "Check if a ClickHouse server is currently running and handle it.
+
+   Steps:
+   1. Check for running ClickHouse server:
+      pgrep -f \"clickhouse[- ]server\" | xargs -I {} ps -p {} -o pid,cmd --no-headers 2>/dev/null | grep -v \"cmake|ninja|Building\"
+
+   2. If a server is running:
+      - Report the PID and explain it's using the old binary
+      - Use AskUserQuestion to ask: \"A ClickHouse server is currently running. Do you want to stop it so the new build can be used?\"
+        - Option 1: \"Yes, stop the server\" - Description: \"Stop the running server (you'll need to start it manually later)\"
+        - Option 2: \"No, keep it running\" - Description: \"Keep the old server running (won't use the new build)\"
+      - If user chooses \"Yes, stop the server\":
+        - Run: pkill -f \"clickhouse[- ]server\"
+        - Wait 1 second: sleep 1
+        - Verify stopped: pgrep -f \"clickhouse[- ]server\" should return nothing
+        - Report: \"Server stopped. To start the new version, run: ./build/${buildType}/programs/clickhouse server --config-file ./programs/server/config.xml\"
+      - If user chooses \"No, keep it running\":
+        - Report: \"Server remains running with the old binary. You'll need to manually restart it to use the new build.\"
+
+   3. If no server is running:
+      - Report: \"No ClickHouse server is currently running.\"
+
+   Keep the response concise and only report the outcome to the user."
+   ```
+
+   - Wait for the Task agent to complete
+   - Return the Task agent's summary to the user
+
+6. **MANDATORY: Provide final summary to user:**
+
+   After completing all steps, always provide a concise final summary to the user:
+
+   **For successful builds:**
+   - Confirm the build completed successfully
+   - Report the binary location: `build/${buildType}/programs/[target]`
+   - Report the server status outcome from step 5
+
+   **For failed builds:**
+   - Already handled in step 4 with error analysis and optional investigation
+
+   **Example final summary for successful build:**
+   ```
+   Build completed successfully!
+
+   Binary: build/RelWithDebInfo/programs/clickhouse
+   Server status: No ClickHouse server is currently running.
+   ```
+
+   Keep the summary brief and clear.
+
+## Examples
+
+- `/build` - Build `clickhouse` target in RelWithDebInfo mode (default)
+- `/build Debug clickhouse-server` - Build server in Debug mode
+- `/build ASAN` - Build with AddressSanitizer
+- `/build Release clickhouse-client` - Build only the client in Release mode
+
+## Notes
+
+- Always run from repository root
+- **NEVER** create build directories or run `cmake` - the build directory must already be configured
+- Build directories follow pattern: `build/${buildType}` (e.g., `build/Debug`, `build/ASAN`)
+- Binaries are located in: `build/${buildType}/programs/`
+- This skill only runs incremental builds with `ninja`
+- To configure a new build directory, the user must manually run CMake first
+- For a clean build, the user should remove `build/${buildType}` and reconfigure manually
+- **MANDATORY:** After successful builds, this skill MUST check for running ClickHouse servers and ask the user if they want to stop them to use the new build
+- **MANDATORY:** ALL build output (success or failure) MUST be analyzed by a Task agent with `subagent_type=general-purpose`
+- **MANDATORY:** ALWAYS provide a final summary to the user at the end of the skill execution (step 6)
+- **CRITICAL:** Build output is redirected to a unique log file created with `mktemp`. The log file path is reported to the user in a copyable format BEFORE starting the build, allowing real-time monitoring with `tail -f`. The log file path is saved from step 2a and passed to the Task agent for analysis. This keeps large build logs out of the main context.
+- **Subagents available:** Task tool is used to analyze all build output (by reading from output file) and provide concise summaries. Additional agents (Explore or general-purpose) can be used for deeper investigation of complex build errors
diff --git a/.claude/skills/install-skills/SKILL.md b/.claude/skills/install-skills/SKILL.md
@@ -0,0 +1,183 @@
+---
+name: install-skills
+description: Configure and customize skills for your workspace by asking questions and updating skill files with your preferences.
+argument-hint: [skill-name]
+disable-model-invocation: false
+allowed-tools: Read, Edit, AskUserQuestion
+---
+
+# Install Skills Configuration Tool
+
+Configure skills by asking the user for their preferences and updating the skill files accordingly.
+
+## Arguments
+
+- `$0` (optional): Skill name to configure. If not provided, configure all available skills that need setup.
+
+## Supported Skills
+
+### Build Skill
+
+The `build` skill can be configured with:
+
+1. **Build directory pattern**: Where builds are stored relative to workspace
+   - **Always prompt with at least these options:**
+     - `build/${buildType}` (e.g., `build/Debug`, `build/Release`) - Recommended
+     - `build` (single build directory)
+   - Additional optional patterns:
+     - `cmake-build-${buildType}` (CLion style)
+     - Custom pattern
+
+2. **Default build type**: What build type to use when not specified
+   - Options: `Release`, `Debug`, `RelWithDebInfo`, `ASAN`, `TSAN`, `MSAN`, `UBSAN`
+
+3. **Default target**: What to build by default
+   - Common targets: `clickhouse`, `clickhouse-server`, `clickhouse-client`, or build all
+
+### Test Skill
+
+The `test` skill can be configured with:
+
+1. **Build directory pattern**: Where to find the clickhouse binary for testing
+   - Should match the build skill configuration
+   - Used to set PATH for test runner
+   - **Always prompt with at least:** `build/${buildType}` and `build`
+
+2. **Default build type for testing**: Which build to use when running tests
+   - Options: `Release`, `Debug`, `RelWithDebInfo`, `ASAN`, `TSAN`, etc.
+   - Typically the same as the build skill default
+
+## Configuration Process
+
+1. **Identify the skill to configure:**
+   - If `$ARGUMENTS` is provided, configure that specific skill
+   - Otherwise, configure all available skills that need setup (build and test together)
+
+2. **When configuring both build and test skills together:**
+   - Ask all questions upfront (build directory, default build type, default target)
+   - Use the same answers to configure both skills
+   - The test skill will use the same build directory and default build type as the build skill
+   - After configuration, update CLAUDE.md to load both skills
+
+3. **For the build skill:**
+
+   a. **Ask about build directory structure:**
+   - Use `AskUserQuestion` to ask: "What is your build directory structure?"
+   - **MANDATORY:** Always include at least these two options:
+     - `build/${buildType}` - Separate directory per build type (e.g., build/Debug, build/Release)
+     - `build` - Single build directory for all build types
+   - Additional optional options:
+     - `cmake-build-${buildType}` - CLion/JetBrains style
+     - Custom - Let user specify their own pattern
+
+   b. **Ask about default build type:**
+   - Use `AskUserQuestion` to ask: "What should be the default build type?"
+   - Options (with descriptions):
+     - `RelWithDebInfo` - Optimized with debug info (recommended for development)
+     - `Debug` - Full debug symbols, no optimization
+     - `Release` - Fully optimized, no debug info
+     - `ASAN` - AddressSanitizer build
+     - `TSAN` - ThreadSanitizer build
+     - Other sanitizers as options
+
+   c. **Ask about default target:**
+   - Use `AskUserQuestion` to ask: "What should be the default build target?"
+   - Options:
+     - `clickhouse` - Main binary (recommended)
+     - `clickhouse-server` - Server only
+     - `clickhouse-client` - Client only
+     - `all` - Build everything
+     - Custom - Let user specify
+
+   d. **Update the build skill file:**
+   - Read `.claude/skills/build/SKILL.md`
+   - Use `Edit` tool to update:
+     - Build directory path pattern
+     - Default build type in the arguments section
+     - Default target in the arguments section
+     - Update examples to reflect new defaults
+     - Update the "Build Process" section with the actual paths
+
+3. **For the test skill:**
+
+   a. **Ask about build directory structure:**
+   - Use the same build directory structure selected for the build skill
+   - Or ask separately if configuring test skill independently
+   - **MANDATORY:** When asking, always include at least these two options:
+     - `build/${buildType}` - Separate directory per build type
+     - `build` - Single build directory
+
+   b. **Ask about default build type for testing:**
+   - Use `AskUserQuestion` to ask: "Which build should be used for running tests?"
+   - Options (with descriptions):
+     - `RelWithDebInfo` - Optimized with debug info (recommended, same as build default)
+     - `Debug` - Full debug build
+     - `Release` - Optimized build
+     - `ASAN` - AddressSanitizer build (for memory testing)
+     - `TSAN` - ThreadSanitizer build (for concurrency testing)
+
+   c. **Update the test skill file:**
+   - Read `.claude/skills/test/SKILL.md`
+   - Use `Edit` tool to update:
+     - Binary path in step 3 (verify server) to match build directory pattern
+     - Binary path in step 4 (PATH export) to match build directory pattern
+     - Update examples and notes with correct paths
+
+4. **Confirm configuration:**
+   - Show summary of changes made
+   - Confirm the skill is now configured for their workspace
+   - Provide example commands they can use
+
+5. **Update CLAUDE.md to load configured skills:**
+
+   After configuring skills, update `.claude/CLAUDE.md` to include them in the "Always load and apply" section:
+
+   a. **Read the current CLAUDE.md:**
+   - Use `Read` tool to read `.claude/CLAUDE.md`
+
+   b. **Update the skills list:**
+   - Find the section that starts with "Always load and apply the following skills:"
+   - The section currently lists only `.claude/skills/install-skills`
+   - Add entries for all configured skills:
+     - `.claude/skills/build` - if build skill was configured
+     - `.claude/skills/test` - if test skill was configured
+
+   c. **Use Edit to update CLAUDE.md:**
+   - Replace the skills list to include all configured skills
+   - Maintain the format with one skill per line prefixed with "- "
+   - Example result:
+     ```
+     Always load and apply the following skills:
+
+     - .claude/skills/install-skills
+     - .claude/skills/build
+     - .claude/skills/test
+     ```
+
+   d. **Confirm the update:**
+   - Inform user that CLAUDE.md has been updated to load the configured skills
+   - Explain that the skills will be automatically available in future sessions
+
+## Implementation Details
+
+- Always use `AskUserQuestion` to gather preferences before making changes
+- Use `Read` to read the current skill files and CLAUDE.md
+- Use `Edit` to make precise updates to skill files and CLAUDE.md
+- Present clear options with descriptions to help users choose
+- **IMPORTANT:** When prompting for build directory, ALWAYS include at minimum: `build/${buildType}` and `build` as options
+- Validate user inputs before applying changes
+- Show before/after summary of what changed
+- After configuring skills, always update CLAUDE.md to include them in the load list
+
+## Example Usage
+
+- `/install-skills` - Configure all skills (build and test together)
+- `/install-skills build` - Configure only the build skill
+- `/install-skills test` - Configure only the test skill
+
+## Notes
+
+- Configuration is workspace-specific and stored in `.claude/skills/`
+- Changes are made to the local skill files
+- Users can manually edit skill files later if needed
+- The tool preserves other skill content while updating only the specified sections
diff --git a/.claude/skills/test/SKILL.md b/.claude/skills/test/SKILL.md
@@ -0,0 +1,344 @@
+---
+name: test
+description: Run ClickHouse stateless or integration tests. Use when the user wants to run or execute tests.
+argument-hint: [test-name] [--flags]
+disable-model-invocation: false
+allowed-tools: Task, Bash(./tests/clickhouse-test:*), Bash(pgrep:*), Bash(./build/*/programs/clickhouse:*), Bash(python:*), Bash(python3:*), Bash(mktemp:*), Bash(export:*)
+---
+
+# ClickHouse Test Runner Skill
+
+Run stateless tests from `tests/queries/0_stateless/` or integration tests from `tests/integration/`.
+
+## Arguments
+
+- `$0` (optional): Test name (e.g., `03312_issue_63093` for stateless or `test_keeper_three_nodes_start` for integration), or empty to prompt for selection
+- `$1+` (optional): Additional flags for test runner (e.g., `--no-random-settings`, `--record` for stateless tests)
+
+## Test Types
+
+The skill automatically detects the test type:
+- **Stateless tests**: Located in `tests/queries/0_stateless/`, named like `NNNNN_description` (e.g., `03312_issue_63093`)
+- **Integration tests**: Located in `tests/integration/`, named like `test_*` (e.g., `test_keeper_three_nodes_start`)
+
+Detection logic:
+1. If test name starts with `test_` → Integration test
+2. If test name matches pattern `\d{5}_.*` → Stateless test
+3. If currently viewing file in `tests/integration/test_*/` → Integration test
+4. If currently viewing file in `tests/queries/0_stateless/` → Stateless test
+
+## Test Selection
+
+If no test name is provided in arguments, prompt the user with `AskUserQuestion`:
+
+**Question: "Which test would you like to run?"**
+- **Option 1: "Currently viewed test"** - Extract test name from currently opened file in IDE
+  - Description: "Run the test file currently open in your editor"
+  - Only available if a test file is currently open in the IDE
+  - For stateless: Extract filename without extension from `tests/queries/0_stateless/03312_issue_63093.sh` → `03312_issue_63093`
+  - For integration: Extract directory name from `tests/integration/test_keeper_three_nodes_start/test.py` → `test_keeper_three_nodes_start`
+
+- **Option 2: "Custom test name"** - User provides test name
+  - Description: "Specify a test name manually"
+  - User can provide the test name via the "Other" field
+  - Stateless examples: `03312_issue_63093`, `00029_test_zookeeper`
+  - Integration examples: `test_keeper_three_nodes_start`, `test_access_control_on_cluster`
+
+## Test Execution Process
+
+### For Stateless Tests
+
+**IMPORTANT**: ALWAYS perform the server check at the start of EVERY stateless test execution, even for repeated runs.
+
+1. **Check if ClickHouse server is running (MANDATORY for stateless tests):**
+   - **CRITICAL**: Use Task tool with `subagent_type=general-purpose` to perform server liveness check
+   - The Task agent should:
+     - Check if any `clickhouse-server` process is running (filter out build processes like cmake/ninja)
+     - Test if server responds to a simple query: `SELECT 1`
+     - Report status: "Server is running and healthy" or "Server is not running" or "Server is running but not responding"
+
+   Example Task prompt:
+   ```
+   Check if the ClickHouse server is running and responding to queries.
+
+   Perform these checks:
+   1. Check if any clickhouse-server process is running (filter out build processes like cmake/ninja)
+      Command: pgrep -f "clickhouse[- ]server" | xargs -I {} ps -p {} -o pid,cmd --no-headers 2>/dev/null | grep -v "cmake\|ninja\|Building"
+
+   2. Test if the server responds to a simple query: SELECT 1
+      Command: ./build/RelWithDebInfo/programs/clickhouse client -q "SELECT 1" 2>/dev/null
+
+   Report:
+   - Whether a server process is running (show PID and command if found)
+   - Whether the server responds to queries
+   - Overall status: "Server is running and healthy" or "Server is not running" or "Server is running but not responding"
+   ```
+
+   - **If server is not running or not responding:**
+     - Report the Task agent's finding
+     - Provide instructions: "Start the server with: `./build/RelWithDebInfo/programs/clickhouse server --config-file ./programs/server/config.xml`"
+     - Use `AskUserQuestion` to prompt: "Did you start the ClickHouse server?"
+       - Option 1: "Yes, server is running now" - Run the liveness check Task again to verify
+       - Option 2: "No, I'll start it later" - Exit without running the test
+     - If user confirms server is running, run the liveness check Task again before proceeding
+
+   - **If server is running and healthy:**
+     - Proceed to run the test
+
+   - Note: Build directory path is configured via `/install-skills` (currently: `build/RelWithDebInfo`)
+
+2. **Determine test name and type:**
+   - If `$ARGUMENTS` is provided, use it as the test name
+   - Otherwise, use `AskUserQuestion` to prompt user for test selection
+   - Detect test type using patterns described in "Test Types" section
+   - For stateless: Test name should NOT include file extension (`.sql`, `.sh`, etc.)
+
+3. **Create log file and run the stateless test:**
+
+   **Step 3a: Create temporary log file first:**
+   ```bash
+   mktemp /tmp/test_clickhouse_XXXXXX.log
+   ```
+   - This will print the log file path
+   - **IMMEDIATELY report to the user:**
+     - "Test logs will be written to: [log file path]"
+     - Then display in a copyable code block:
+       ```bash
+       tail -f [log file path]
+       ```
+     - Example: "You can monitor the test progress in real-time with:" followed by the tail command in a code block
+
+   **Step 3b: Start the stateless test:**
+   ```bash
+   # Add clickhouse binary to PATH
+   # Configured via /install-skills (currently: build/RelWithDebInfo)
+   export PATH="./build/RelWithDebInfo/programs:$PATH" && ./tests/clickhouse-test <test_name> [flags] > [log file path] 2>&1
+   ```
+
+   **Important:**
+   - Run from repository root directory
+   - Use the log file path from step 3a
+   - Redirect both stdout and stderr to the log file using `> "$logfile" 2>&1`
+   - Run in the background using `run_in_background: true`
+   - **After starting the test**, report: "Test started in the background. Waiting for completion..."
+
+   Common flags to mention if user asks:
+   - `--no-random-settings` - Disable settings randomization
+   - `--no-random-merge-tree-settings` - Disable MergeTree settings randomization
+   - `--record` - Update `.reference` files when output differs
+
+4. **Wait for stateless test completion:**
+   - Use TaskOutput with `block=true` to wait for the background task to finish
+   - The log file path is already known from step 3a
+   - Pass the log file path to the Task agent in step 5
+
+### For Integration Tests
+
+**Note**: Integration tests manage their own Docker containers, so no server check is needed.
+
+1. **Determine test name:**
+   - If `$ARGUMENTS` is provided, use it as the test name
+   - Otherwise, use `AskUserQuestion` to prompt user for test selection
+   - Test name should be the directory name (e.g., `test_keeper_three_nodes_start`)
+
+2. **Create log file and run the integration test:**
+
+   **Step 2a: Create temporary log file first:**
+   ```bash
+   mktemp /tmp/test_clickhouse_XXXXXX.log
+   ```
+   - This will print the log file path
+   - **IMMEDIATELY report to the user:**
+     - "Test logs will be written to: [log file path]"
+     - Then display in a copyable code block:
+       ```bash
+       tail -f [log file path]
+       ```
+     - Example: "You can monitor the test progress in real-time with:" followed by the tail command in a code block
+
+   **Step 2b: Start the integration test with praktika:**
+   ```bash
+   python -u -m ci.praktika run "integration" --test <test_name> > [log file path] 2>&1
+   ```
+
+   **Important:**
+   - Run from repository root directory
+   - Use `python -u` flag to ensure unbuffered output (so logs stream in real-time)
+   - Use the log file path from step 2a
+   - Redirect both stdout and stderr to the log file using `> "$logfile" 2>&1`
+   - Integration tests use Docker containers (managed automatically)
+   - Tests may take longer than stateless tests (container startup time)
+   - Run in the background using `run_in_background: true`
+   - **After starting the test**, report: "Test started in the background. Waiting for completion..."
+
+3. **Wait for integration test completion:**
+   - Use TaskOutput with `block=true` to wait for the background task to finish
+   - The log file path is already known from step 2a
+   - Pass the log file path to the Task agent in step 4
+
+5. **Report results:**
+
+   **For Stateless Tests:**
+
+   **ALWAYS use Task tool to analyze results** (both pass and fail):
+   - Use Task tool with `subagent_type=general-purpose` to analyze the test output
+   - **Pass the log file path from step 3a** to the Task agent - let it read the file directly
+   - Example Task prompt: "Read and analyze the test output from: /tmp/test_clickhouse_abc123.log"
+   - The Task agent should read the file and provide:
+
+     **If tests passed:**
+     - Confirm all tests passed
+     - Report execution time from clickhouse-test output
+     - Show summary (e.g., "1 tests passed. 0 tests skipped. 3.51 s elapsed")
+     - Keep response brief
+
+     **If tests failed:**
+     - Parse the clickhouse-test output to identify which test failed
+     - Extract the relevant error messages and differences
+     - Identify the root cause if possible
+     - Provide a concise summary with:
+       - Test name that failed
+       - What assertion or comparison failed
+       - Expected vs actual output (show the diff)
+       - Any error messages or exceptions
+       - Brief explanation of the root cause
+     - Filter out excessive verbose logs and focus on the actual failure
+
+   - Return ONLY the Task agent's summary to the user
+   - Do NOT return the full raw test output
+
+   **After receiving the summary (for stateless tests):**
+   - If tests passed: Done, no further action needed
+   - If tests failed:
+     - Present the summary to the user first
+     - **MANDATORY:** Use `AskUserQuestion` to prompt: "Do you want deeper analysis of this test failure?"
+       - Option 1: "Yes, investigate further" - Description: "Launch a subagent to investigate the root cause across the codebase"
+       - Option 2: "No, I'll fix it myself" - Description: "Skip deeper analysis and proceed without investigation"
+     - If user chooses "Yes, investigate further":
+       - **CRITICAL: DO NOT read files, edit code, or fix the issue yourself**
+       - **MANDATORY: Use Task tool to launch a subagent for deep analysis only (NO FIXES)**
+       - Use Task tool with `subagent_type=Explore` to search for related code patterns, or find where functions/queries are implemented
+       - For complex failures involving multiple components, use Task tool with `subagent_type=general-purpose` to investigate root causes
+       - Provide specific prompts to the agent based on the failure type:
+         - Query failures: "Investigate why the query [query] returns [actual] instead of [expected]. Find the implementation and explain the root cause. Do NOT fix the code."
+         - Assertion failures: "Analyze why [assertion] failed in test [test_name]. Find the relevant code and explain what's happening. Do NOT fix the code."
+         - Output differences: "Investigate the difference between expected and actual output in test [test_name]. Explain why the output changed. Do NOT fix the code."
+         - Exception/error: "Investigate the error [error_message] in test [test_name]. Find where it originates and explain the cause. Do NOT fix the code."
+       - The subagent should only investigate and analyze, NOT edit or fix code
+       - **CRITICAL: Return ONLY the agent's summary of findings to the user**
+       - **DO NOT return full investigation details, raw file contents, or excessive verbose output**
+       - **Present findings in a well-organized summary format**
+     - If user chooses "No, I'll fix it myself":
+       - Skip deeper analysis
+
+   **For Integration Tests:**
+
+   **ALWAYS use Task tool to analyze results** (both pass and fail):
+   - Use Task tool with `subagent_type=general-purpose` to analyze the test output
+   - **Pass the log file path from step 2a** to the Task agent - let it read the file directly
+   - Example Task prompt: "Read and analyze the test output from: /tmp/test_clickhouse_abc123.log"
+   - The Task agent should read the file and provide:
+
+     **If tests passed:**
+     - Confirm all tests passed
+     - Report total execution time from pytest output
+     - Keep response brief: "All tests passed (XX.XXs)"
+
+     **If tests failed:**
+     - Parse the pytest output to identify which specific test cases failed
+     - Extract the relevant error messages, assertions, and stack traces
+     - Identify the root cause if possible (e.g., timeout, connection error, assertion failure)
+     - Filter out verbose Docker logs and focus on the actual test failure
+     - Provide a concise summary with:
+       - Test name that failed
+       - Line number where it failed
+       - Specific assertion or error
+       - Expected vs actual values
+       - Brief explanation of the root cause
+
+   - Return ONLY the Task agent's summary to the user
+   - Do NOT return the full raw test output
+
+   **After receiving the summary (for integration tests):**
+   - If tests passed: Done, no further action needed
+   - If tests failed:
+     - Present the summary to the user first
+     - **MANDATORY:** Use `AskUserQuestion` to prompt: "Do you want deeper analysis of this test failure?"
+       - Option 1: "Yes, investigate further" - Description: "Launch a subagent to investigate the root cause across the codebase"
+       - Option 2: "No, I'll fix it myself" - Description: "Skip deeper analysis and proceed without investigation"
+     - If user chooses "Yes, investigate further":
+       - **CRITICAL: DO NOT read files, edit code, or fix the issue yourself**
+       - **MANDATORY: Use Task tool to launch a subagent for deep analysis only (NO FIXES)**
+       - Use Task tool with `subagent_type=Explore` to search for related code patterns, or find where functions are implemented
+       - For complex failures involving multiple components, use Task tool with `subagent_type=general-purpose` to investigate root causes
+       - Provide specific prompts to the agent based on the failure type:
+         - Timeout errors: "Investigate why test [test_name] times out. Find what operation is slow and explain the cause. Do NOT fix the code."
+         - Connection errors: "Investigate the connection error [error] in test [test_name]. Find what's causing the connection issue. Do NOT fix the code."
+         - Assertion failures: "Analyze the assertion failure at [file:line] in test [test_name]. Explain why the assertion failed. Do NOT fix the code."
+         - Exception/error: "Investigate the exception [exception] in test [test_name]. Find where it originates and explain the cause. Do NOT fix the code."
+       - The subagent should only investigate and analyze, NOT edit or fix code
+       - **CRITICAL: Return ONLY the agent's summary of findings to the user**
+       - **DO NOT return full investigation details, raw file contents, or excessive verbose output**
+       - **Present findings in a well-organized summary format**
+     - If user chooses "No, I'll fix it myself":
+       - Skip deeper analysis
+
+## Test File Structure
+
+### Stateless Tests
+- **Location**: `tests/queries/0_stateless/`
+- **Extensions**: `.sql`, `.sh`, `.py`, `.sql.j2`, `.expect`
+- **Reference files**: `.reference` (expected output)
+- **Test name format**: `NNNNN_description` (e.g., `03312_issue_63093`)
+
+### Integration Tests
+- **Location**: `tests/integration/test_*/`
+- **Format**: Python pytest files (`test.py` or `test_*.py`)
+- **Directory structure**: Each test is a directory named `test_*`
+- **Test name format**: `test_*` (e.g., `test_keeper_three_nodes_start`)
+- **Dependencies**: Uses Docker containers, pytest fixtures, and helper modules
+
+## Examples
+
+### Stateless Tests
+- `/test` - Prompt to select test (currently viewed or custom name)
+- `/test 03312_issue_63093` - Run specific stateless test by name
+- `/test 00029_test_zookeeper --no-random-settings` - Run stateless test with flags
+- `/test 03312_issue_63093 --record` - Run stateless test and update reference files
+
+### Integration Tests
+- `/test test_keeper_three_nodes_start` - Run specific integration test
+- `/test test_access_control_on_cluster` - Run integration test by name
+- `/test` - If viewing `tests/integration/test_*/test.py`, automatically detect and run that integration test
+
+## Environment Variables
+
+The test runner automatically detects and sets the necessary environment variables for connecting to the server (for stateless tests).
+
+## Notes
+
+### General
+- Run from repository root directory
+- Test type is automatically detected based on name pattern or file location
+- **MANDATORY:** ALL test output (success or failure) MUST be analyzed by a Task agent with `subagent_type=general-purpose`
+- **MANDATORY:** For test failures, MUST prompt user if they want deeper analysis and use Task subagent if requested
+- **CRITICAL:** Test output is redirected to a unique log file created with `mktemp`. The log file path is reported to the user in a copyable format BEFORE starting the test, allowing real-time monitoring with `tail -f`. The log file path is saved and passed to the Task agent for analysis. This keeps large test logs out of the main context.
+- **Subagents available:** Task tool is used to analyze all test output (by reading from log file) and provide concise summaries. Additional agents (Explore or general-purpose) are used for deeper investigation of test failures when user requests it
+
+### Stateless Tests
+- Test names do NOT include extensions (use `03312_issue_63093`, not `03312_issue_63093.sh`)
+- **CRITICAL**: Always check if server is running before attempting to run stateless tests - this check MUST be performed EVERY time, even for repeated test runs
+- The server check protects against running tests when the server has crashed or been stopped
+- Test runner creates temporary database with random name for isolation
+- Reference files use `default` database name, not the random test database
+- Build directory used: `build/RelWithDebInfo` (configured with `/install-skills`)
+- Use `/install-skills test` to reconfigure which build directory to use for testing
+
+### Integration Tests
+- Test names are directory names (use `test_keeper_three_nodes_start`, not `test.py`)
+- Integration tests manage their own Docker containers - no server check needed
+- Tests may take longer due to container startup and teardown
+- Integration tests use pytest framework with fixtures
+- Docker daemon must be running and accessible
+- Requires Python dependencies from `tests/integration/` directory
+- Tests are run via praktika: `python -m ci.praktika run "integration" --test <test_name>`
PATCH

echo "Gold patch applied."
