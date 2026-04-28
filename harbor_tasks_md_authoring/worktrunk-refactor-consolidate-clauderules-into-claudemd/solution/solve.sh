#!/usr/bin/env bash
set -euo pipefail

cd /workspace/worktrunk

# Idempotency guard
if grep -qF ".claude/rules/accessor-conventions.md" ".claude/rules/accessor-conventions.md" && grep -qF ".claude/rules/caching-strategy.md" ".claude/rules/caching-strategy.md" && grep -qF ".claude/rules/output-system-architecture.md" ".claude/rules/output-system-architecture.md" && grep -qF "description: CLI output formatting standards for worktrunk. Use when writing use" ".claude/skills/writing-user-outputs/SKILL.md" && grep -qF "`Repository` holds its cache directly via `Arc<RepoCache>`. Cloning a Repository" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/accessor-conventions.md b/.claude/rules/accessor-conventions.md
@@ -1,64 +0,0 @@
-# Accessor Function Naming Conventions
-
-Function prefixes signal return behavior and side effects.
-
-## Prefix Semantics
-
-| Prefix | Returns | Side Effects | Error Handling | Example |
-|--------|---------|--------------|----------------|---------|
-| (bare noun) | `Option<T>` or `T` | None (may cache) | Returns None/default if absent | `config()`, `switch_previous()` |
-| `set_*` | `Result<()>` | Writes state | Errors on failure | `set_switch_previous()`, `set_config()` |
-| `require_*` | `Result<T>` | None | Errors if absent | `require_branch()`, `require_target_ref()` |
-| `fetch_*` | `Result<T>` | Network I/O | Errors on failure | `fetch_pr_info()`, `fetch_mr_info()` |
-| `load_*` | `Result<T>` | File I/O | Errors on failure | `load_project_config()`, `load_template()` |
-
-## When to Use Each
-
-**Bare nouns** — Value may not exist and that's fine (Rust stdlib convention)
-```rust
-// Returns Option - caller handles None
-if let Some(prev) = repo.switch_previous() {
-    // use prev
-}
-
-// Returns Option - read from git config
-if let Some(marker) = repo.branch_marker("feature") {
-    println!("Branch marker: {marker}");
-}
-```
-
-**`set_*`** — Write state to storage
-```rust
-// Set the previous branch for wt switch -
-repo.set_switch_previous(Some(&branch))?;
-```
-
-**`require_*`** — Value must exist for operation to proceed
-```rust
-// Error propagates if branch is missing
-let branch = env.require_branch("squash")?;
-```
-
-**`fetch_*`** — Retrieve from external service (network)
-```rust
-// May fail due to network, auth, rate limits
-let pr = fetch_pr_info(123, &repo_root)?;
-```
-
-**`load_*`** — Read from filesystem
-```rust
-// May fail due to missing file, parse errors
-let config = repo.load_project_config()?;
-```
-
-## Anti-patterns
-
-Avoid mixing semantics:
-- Don't use bare nouns if the function makes network calls (use `fetch_*`)
-- Don't use bare nouns if absence is an error (use `require_*`)
-- Don't use `load_*` for computed values (use bare nouns)
-- Don't use `get_*` prefix — use bare nouns instead (Rust convention)
-
-## Related Patterns
-
-For caching behavior, see `caching-strategy.md`.
diff --git a/.claude/rules/caching-strategy.md b/.claude/rules/caching-strategy.md
@@ -1,69 +0,0 @@
-# Repository Caching Strategy
-
-## What Changes During Execution?
-
-Most data is stable for the duration of a command. The only things worktrunk modifies are:
-
-- **Worktree list** — `wt switch --create`, `wt remove` create/remove worktrees
-- **Working tree state** — `wt merge` commits, stages files
-- **Git config** — `wt config` modifies settings
-
-Everything else (remote URLs, project config, branch metadata) is read-only.
-
-## Caching Implementation
-
-`Repository` holds its cache directly via `Arc<RepoCache>`. Cloning a Repository
-shares the cache — all clones see the same cached values.
-
-**Key patterns:**
-
-- **Command entry points** create Repository via `Repository::current()` or `Repository::at(path)`
-- **Parallel tasks** (e.g., `wt list`) clone the Repository, sharing the cache
-- **Tests** naturally get isolation since each test creates its own Repository
-
-**Currently cached:**
-
-- `git_common_dir` — computed at construction, stored on struct
-- `worktree_root()` — per-worktree, keyed by path
-- `repo_path()` — derived from git_common_dir and is_bare
-- `is_bare()` — git config, doesn't change
-- `current_branch()` — per-worktree, keyed by path
-- `project_identifier()` — derived from remote URL
-- `primary_remote()` — git config, doesn't change
-- `primary_remote_url()` — derived from primary_remote, doesn't change
-- `default_branch()` — from git config or detection, doesn't change
-- `integration_target()` — effective target for integration checks (local default or upstream if ahead)
-- `merge_base()` — keyed by (commit1, commit2) pair
-- `ahead_behind` — keyed by (base_ref, branch_name), populated by `batch_ahead_behind()`
-- `project_config` — loaded from .config/wt.toml
-
-**Not cached (intentionally):**
-
-- `is_dirty()` — changes as we stage/commit
-- `list_worktrees()` — changes as we create/remove worktrees
-
-**Adding new cached methods:**
-
-1. Add field to `RepoCache` struct: `field_name: OnceCell<T>`
-2. Access via `self.cache.field_name`
-3. Return owned values (String, PathBuf, bool)
-
-```rust
-// For repo-wide values (same for all clones)
-pub fn cached_value(&self) -> anyhow::Result<String> {
-    self.cache
-        .field_name
-        .get_or_init(|| { /* compute value */ })
-        .clone()
-}
-
-// For per-worktree values (different per worktree path)
-// Use DashMap for concurrent access
-pub fn cached_per_worktree(&self, path: &Path) -> String {
-    self.cache
-        .field_name
-        .entry(path.to_path_buf())
-        .or_insert_with(|| { /* compute value */ })
-        .clone()
-}
-```
diff --git a/.claude/rules/output-system-architecture.md b/.claude/rules/output-system-architecture.md
@@ -1,115 +0,0 @@
-# Output System Architecture
-
-## Shell Integration
-
-Worktrunk uses file-based directive passing for shell integration:
-
-1. Shell wrapper creates a temp file via `mktemp`
-2. Shell wrapper sets `WORKTRUNK_DIRECTIVE_FILE` env var to the file path
-3. wt writes shell commands (like `cd '/path'`) to that file
-4. Shell wrapper sources the file after wt exits
-
-When `WORKTRUNK_DIRECTIVE_FILE` is not set (direct binary call), commands execute
-directly and shell integration hints are shown.
-
-## Output Functions
-
-The output system handles shell integration automatically. Just call output
-functions — they do the right thing regardless of whether shell integration is
-active.
-
-```rust
-// NEVER DO THIS - don't check mode in command code
-if is_shell_integration_active() {
-    // different behavior
-}
-
-// ALWAYS DO THIS - just call output functions
-output::print(success_message("Created worktree"))?;
-output::change_directory(&path)?;  // Writes to directive file if set, else no-op
-```
-
-**Output functions** (`src/output/global.rs`):
-
-| Function | Destination | Purpose |
-|----------|-------------|---------|
-| `print(message)` | stderr | Status messages (use with formatting functions) |
-| `blank()` | stderr | Visual separation |
-| `stdout(content)` | stdout | Primary output (tables, JSON, pipeable) |
-| `change_directory(path)` | directive file | Shell cd after wt exits |
-| `execute(command)` | directive file | Shell command after wt exits |
-| `flush()` | both | Flush buffers (call before interactive prompts) |
-| `terminate_output()` | stderr | Reset ANSI state on stderr |
-| `is_shell_integration_active()` | — | Check if directive file set (rarely needed) |
-
-**Message formatting functions** (`worktrunk::styling`):
-
-| Function | Symbol | Color |
-|----------|--------|-------|
-| `success_message()` | ✓ | green |
-| `progress_message()` | ◎ | cyan |
-| `info_message()` | ○ | — |
-| `warning_message()` | ▲ | yellow |
-| `hint_message()` | ↳ | dim |
-| `error_message()` | ✗ | red |
-
-## stdout vs stderr
-
-**Decision principle:** If this command is piped, what should the receiving program get?
-
-- **stdout** → Data for pipes, scripts, `eval` (tables, JSON, shell code)
-- **stderr** → Status for the human watching (progress, success, errors, hints)
-- **directive file** → Shell commands executed after wt exits (cd, exec)
-
-Examples:
-- `wt list` → table/JSON to stdout (for grep, jq, scripts)
-- `wt config shell init` → shell code to stdout (for `eval`)
-- `wt switch` → status messages only (nothing to pipe)
-
-## Security
-
-`WORKTRUNK_DIRECTIVE_FILE` is automatically removed from spawned subprocesses
-(via `shell_exec::Cmd`). This prevents hooks from writing to the directive
-file.
-
-## Windows Compatibility (Git Bash / MSYS2)
-
-On Windows with Git Bash, `mktemp` returns POSIX-style paths like `/tmp/tmp.xxx`.
-The native Windows binary (`wt.exe`) needs a Windows path to write to the
-directive file.
-
-**No explicit path conversion is needed.** MSYS2 (which Git Bash uses)
-automatically converts POSIX paths in environment variables when spawning native
-Windows binaries. When the shell wrapper sets `WORKTRUNK_DIRECTIVE_FILE=/tmp/...`
-and runs `wt.exe`, MSYS2 translates this to `C:\Users\...\Temp\...` before the
-binary sees it.
-
-See: https://www.msys2.org/docs/filesystem-paths/
-
-This means the shell wrapper templates can use `$directive_file` directly without
-calling `cygpath -w`. The conversion happens automatically in the MSYS2 runtime.
-
-## Simplification Notes
-
-The output system was originally more complex to handle shell integration
-edge cases. After consolidation, the thin wrappers (`print`, `stdout`,
-`blank`) are essentially `eprintln!`/`println!` + flush.
-
-**What still provides value:**
-
-- `change_directory()`, `execute()` — IPC with shell wrapper via directive file
-- `terminate_output()` — ANSI reset when needed
-
-**What could be further simplified:**
-
-- `print()` → `eprintln!()` + flush (callers must remember to flush)
-- `stdout()` → `println!()` + flush
-- `blank()` → `eprintln!()` + flush
-
-The abstraction cost is low, but if we wanted to reduce indirection, these
-wrappers could be removed. The main value they provide is consistency (correct
-stream, always flushing).
-
-## Related
-
-For message content and styling conventions, see `cli-output-formatting.md`.
diff --git a/.claude/skills/writing-user-outputs/SKILL.md b/.claude/skills/writing-user-outputs/SKILL.md
@@ -1,7 +1,123 @@
-# CLI Output Formatting Standards
+---
+name: writing-user-outputs
+description: CLI output formatting standards for worktrunk. Use when writing user-facing messages, error handling, progress output, hints, warnings, or working with the output system.
+---
+
+# Output System Architecture
+
+## Shell Integration
+
+Worktrunk uses file-based directive passing for shell integration:
+
+1. Shell wrapper creates a temp file via `mktemp`
+2. Shell wrapper sets `WORKTRUNK_DIRECTIVE_FILE` env var to the file path
+3. wt writes shell commands (like `cd '/path'`) to that file
+4. Shell wrapper sources the file after wt exits
+
+When `WORKTRUNK_DIRECTIVE_FILE` is not set (direct binary call), commands execute
+directly and shell integration hints are shown.
+
+## Output Functions
+
+The output system handles shell integration automatically. Just call output
+functions — they do the right thing regardless of whether shell integration is
+active.
+
+```rust
+// NEVER DO THIS - don't check mode in command code
+if is_shell_integration_active() {
+    // different behavior
+}
+
+// ALWAYS DO THIS - just call output functions
+output::print(success_message("Created worktree"))?;
+output::change_directory(&path)?;  // Writes to directive file if set, else no-op
+```
+
+**Output functions** (`src/output/global.rs`):
+
+| Function | Destination | Purpose |
+|----------|-------------|---------|
+| `print(message)` | stderr | Status messages (use with formatting functions) |
+| `blank()` | stderr | Visual separation |
+| `stdout(content)` | stdout | Primary output (tables, JSON, pipeable) |
+| `change_directory(path)` | directive file | Shell cd after wt exits |
+| `execute(command)` | directive file | Shell command after wt exits |
+| `flush()` | both | Flush buffers (call before interactive prompts) |
+| `terminate_output()` | stderr | Reset ANSI state on stderr |
+| `is_shell_integration_active()` | — | Check if directive file set (rarely needed) |
+
+**Message formatting functions** (`worktrunk::styling`):
+
+| Function | Symbol | Color |
+|----------|--------|-------|
+| `success_message()` | ✓ | green |
+| `progress_message()` | ◎ | cyan |
+| `info_message()` | ○ | — |
+| `warning_message()` | ▲ | yellow |
+| `hint_message()` | ↳ | dim |
+| `error_message()` | ✗ | red |
+
+## stdout vs stderr
+
+**Decision principle:** If this command is piped, what should the receiving program get?
 
-> For output system architecture (shell integration, stdout vs stderr, output
-> functions API), see `output-system-architecture.md`.
+- **stdout** → Data for pipes, scripts, `eval` (tables, JSON, shell code)
+- **stderr** → Status for the human watching (progress, success, errors, hints)
+- **directive file** → Shell commands executed after wt exits (cd, exec)
+
+Examples:
+- `wt list` → table/JSON to stdout (for grep, jq, scripts)
+- `wt config shell init` → shell code to stdout (for `eval`)
+- `wt switch` → status messages only (nothing to pipe)
+
+## Security
+
+`WORKTRUNK_DIRECTIVE_FILE` is automatically removed from spawned subprocesses
+(via `shell_exec::Cmd`). This prevents hooks from writing to the directive
+file.
+
+## Windows Compatibility (Git Bash / MSYS2)
+
+On Windows with Git Bash, `mktemp` returns POSIX-style paths like `/tmp/tmp.xxx`.
+The native Windows binary (`wt.exe`) needs a Windows path to write to the
+directive file.
+
+**No explicit path conversion is needed.** MSYS2 (which Git Bash uses)
+automatically converts POSIX paths in environment variables when spawning native
+Windows binaries. When the shell wrapper sets `WORKTRUNK_DIRECTIVE_FILE=/tmp/...`
+and runs `wt.exe`, MSYS2 translates this to `C:\Users\...\Temp\...` before the
+binary sees it.
+
+See: https://www.msys2.org/docs/filesystem-paths/
+
+This means the shell wrapper templates can use `$directive_file` directly without
+calling `cygpath -w`. The conversion happens automatically in the MSYS2 runtime.
+
+## Simplification Notes
+
+The output system was originally more complex to handle shell integration
+edge cases. After consolidation, the thin wrappers (`print`, `stdout`,
+`blank`) are essentially `eprintln!`/`println!` + flush.
+
+**What still provides value:**
+
+- `change_directory()`, `execute()` — IPC with shell wrapper via directive file
+- `terminate_output()` — ANSI reset when needed
+
+**What could be further simplified:**
+
+- `print()` → `eprintln!()` + flush (callers must remember to flush)
+- `stdout()` → `println!()` + flush
+- `blank()` → `eprintln!()` + flush
+
+The abstraction cost is low, but if we wanted to reduce indirection, these
+wrappers could be removed. The main value they provide is consistency (correct
+stream, always flushing).
+
+---
+
+# CLI Output Formatting Standards
 
 ## User Message Principles
 
@@ -255,9 +371,6 @@ naturally come after the action.
 
 ## Message Types
 
-See `output-system-architecture.md` for the API. This section covers when to use
-each type.
-
 **Success vs Info:** Success (✓) means something was created or changed. Info
 (○) acknowledges state without changing anything.
 
@@ -403,8 +516,7 @@ Specific rules:
 
 ## Output System
 
-Use `output::` functions for consistency. See `output-system-architecture.md`
-for stdout vs stderr decisions and simplification notes.
+Use `output::` functions for consistency.
 
 ```rust
 // Preferred - consistent routing and flushing
@@ -415,8 +527,7 @@ eprintln!("{}", success_message("Branch created"));
 ```
 
 **Note:** The output wrappers are thin (`eprintln!` + flush). The main value is
-consistency, not complex logic. See "Simplification Notes" in
-`output-system-architecture.md`.
+consistency, not complex logic.
 
 **Interactive prompts** must flush stderr before blocking on stdin:
 
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -315,3 +315,97 @@ fn validate_config() { ... }
 ### No Test Code in Library Code
 
 Never use `#[cfg(test)]` to add test-only convenience methods to library code. Tests should call the real API directly. If tests need helpers, define them in the test module.
+
+## Accessor Function Naming Conventions
+
+Function prefixes signal return behavior and side effects.
+
+| Prefix | Returns | Side Effects | Error Handling | Example |
+|--------|---------|--------------|----------------|---------|
+| (bare noun) | `Option<T>` or `T` | None (may cache) | Returns None/default if absent | `config()`, `switch_previous()` |
+| `set_*` | `Result<()>` | Writes state | Errors on failure | `set_switch_previous()`, `set_config()` |
+| `require_*` | `Result<T>` | None | Errors if absent | `require_branch()`, `require_target_ref()` |
+| `fetch_*` | `Result<T>` | Network I/O | Errors on failure | `fetch_pr_info()`, `fetch_mr_info()` |
+| `load_*` | `Result<T>` | File I/O | Errors on failure | `load_project_config()`, `load_template()` |
+
+**When to use each:**
+
+- **Bare nouns** — Value may not exist and that's fine (Rust stdlib convention)
+- **`set_*`** — Write state to storage
+- **`require_*`** — Value must exist for operation to proceed
+- **`fetch_*`** — Retrieve from external service (network)
+- **`load_*`** — Read from filesystem
+
+**Anti-patterns:**
+
+- Don't use bare nouns if the function makes network calls (use `fetch_*`)
+- Don't use bare nouns if absence is an error (use `require_*`)
+- Don't use `load_*` for computed values (use bare nouns)
+- Don't use `get_*` prefix — use bare nouns instead (Rust convention)
+
+## Repository Caching Strategy
+
+Most data is stable for the duration of a command. The only things worktrunk modifies are:
+
+- **Worktree list** — `wt switch --create`, `wt remove` create/remove worktrees
+- **Working tree state** — `wt merge` commits, stages files
+- **Git config** — `wt config` modifies settings
+
+Everything else (remote URLs, project config, branch metadata) is read-only.
+
+### Caching Implementation
+
+`Repository` holds its cache directly via `Arc<RepoCache>`. Cloning a Repository shares the cache — all clones see the same cached values.
+
+**Key patterns:**
+
+- **Command entry points** create Repository via `Repository::current()` or `Repository::at(path)`
+- **Parallel tasks** (e.g., `wt list`) clone the Repository, sharing the cache
+- **Tests** naturally get isolation since each test creates its own Repository
+
+**Currently cached:**
+
+- `git_common_dir` — computed at construction, stored on struct
+- `worktree_root()` — per-worktree, keyed by path
+- `repo_path()` — derived from git_common_dir and is_bare
+- `is_bare()` — git config, doesn't change
+- `current_branch()` — per-worktree, keyed by path
+- `project_identifier()` — derived from remote URL
+- `primary_remote()` — git config, doesn't change
+- `primary_remote_url()` — derived from primary_remote, doesn't change
+- `default_branch()` — from git config or detection, doesn't change
+- `integration_target()` — effective target for integration checks (local default or upstream if ahead)
+- `merge_base()` — keyed by (commit1, commit2) pair
+- `ahead_behind` — keyed by (base_ref, branch_name), populated by `batch_ahead_behind()`
+- `project_config` — loaded from .config/wt.toml
+
+**Not cached (intentionally):**
+
+- `is_dirty()` — changes as we stage/commit
+- `list_worktrees()` — changes as we create/remove worktrees
+
+### Adding New Cached Methods
+
+1. Add field to `RepoCache` struct: `field_name: OnceCell<T>`
+2. Access via `self.cache.field_name`
+3. Return owned values (String, PathBuf, bool)
+
+```rust
+// For repo-wide values (same for all clones)
+pub fn cached_value(&self) -> anyhow::Result<String> {
+    self.cache
+        .field_name
+        .get_or_init(|| { /* compute value */ })
+        .clone()
+}
+
+// For per-worktree values (different per worktree path)
+// Use DashMap for concurrent access
+pub fn cached_per_worktree(&self, path: &Path) -> String {
+    self.cache
+        .field_name
+        .entry(path.to_path_buf())
+        .or_insert_with(|| { /* compute value */ })
+        .clone()
+}
+```
PATCH

echo "Gold patch applied."
