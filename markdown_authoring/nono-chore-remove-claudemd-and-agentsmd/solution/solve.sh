#!/usr/bin/env bash
set -euo pipefail

cd /workspace/nono

# Idempotency guard
if grep -qF "- **Environment variables in tests**: Tests that modify `HOME`, `TMPDIR`, `XDG_C" "AGENTS.md" && grep -qF "nono is a capability-based sandboxing system for running untrusted AI agents wit" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,131 +1,213 @@
-# Agent Guide: nono
+# nono - Development Guide
 
-This repository contains the `nono` project, a capability-based sandboxing system for running untrusted AI agents.
-It is a Cargo workspace with three members:
-- `crates/nono` (core library): Pure sandbox primitive.
-- `crates/nono-cli` (CLI binary): Owns security policy, profiles, and UX.
-- `bindings/c` (C FFI): C bindings.
+## Project Overview
 
-## Build, Test, and Lint Commands
+nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes, and then layers on top a policy system, diagnostic tools, and a rollback mechanism for recovery. The library is designed to be a pure sandbox primitive with no built-in policy, while the CLI implements all security policy and UX.
 
-### Primary Commands
-Use the `Makefile` for standard workflows:
+The project is a Cargo workspace with three members:
+- **nono** (`crates/nono/`) - Core library. Pure sandbox primitive with no built-in security policy.
+- **nono-cli** (`crates/nono-cli/`) - CLI binary. Owns all security policy, profiles, hooks, and UX.
+- **nono-ffi** (`bindings/c/`) - C FFI bindings. Exposes the library via `extern "C"` functions and auto-generated `nono.h` header.
+- **nono-proxy** - Proxy that provides network filtering and credential injection
 
-- **Build All**: `make build`
-- **Test All**: `make test`
-- **Lint & Format**: `make check` (runs clippy + fmt check)
-- **CI Simulation**: `make ci` (runs check + test)
+### Library vs CLI Boundary
 
-### Component-Specific Targets
-- **Library**: `make build-lib` / `make test-lib`
-- **CLI**: `make build-cli` / `make test-cli`
-- **FFI**: `make build-ffi` / `make test-ffi`
+The library is a **pure sandbox primitive**. It applies ONLY what clients explicitly add to `CapabilitySet`:
 
-### Running a Single Test
-To run a specific test case, use `cargo test` directly:
+| In Library | In CLI |
+|------------|--------|
+| `CapabilitySet` builder | Policy groups (deny rules, dangerous commands, system paths) |
+| `Sandbox::apply()` | Group resolver (`policy.rs`) and platform-aware deny handling |
+| `SandboxState` | `ExecStrategy` (Direct/Monitor/Supervised) |
+| `DiagnosticFormatter` | Profile loading and hooks |
+| `QueryContext` | All output and UX |
+| `keystore` | `learn` mode |
+| `undo` module (ObjectStore, SnapshotManager, MerkleTree, ExclusionFilter) | Rollback lifecycle, exclusion policy, rollback UI |
+
+## Build & Test
+
+After every session, run these commands to verify correctness:
 
 ```bash
-# Run a specific test in the library
-cargo test -p nono -- test_function_name
+# Build everything
+make build
 
-# Run a specific test in the CLI
-cargo test -p nono-cli -- test_function_name
+# Run all tests
+make test
+
+# Full CI check (clippy + fmt + tests)
+make ci
+```
 
-# Run a test and show stdout (useful for debugging)
-cargo test -p nono -- test_function_name --nocapture
+Individual targets:
+```bash
+make build-lib       # Library only
+make build-cli       # CLI only
+make test-lib        # Library tests only
+make test-cli        # CLI tests only
+make test-doc        # Doc tests only
+make clippy          # Lint (strict: -D warnings -D clippy::unwrap_used)
+make fmt-check       # Format check
+make fmt             # Auto-format
 ```
 
-## Code Style & Standards
+## Coding Standards
+
+- **Error Handling**: Use `NonoError` for all errors; propagation via `?` only.
+- **Unwrap Policy**: Strictly forbid `.unwrap()` and `.expect()`; enforced by `clippy::unwrap_used`.
+- **Libraries should almost never panic**: Panics are for unrecoverable bugs, not expected error conditions. Use `Result` instead.
+- **Unsafe Code**: Restrict to FFI; must be wrapped in safe APIs with `// SAFETY:` docs.
+- **Path Security**: Validate and canonicalize all paths before applying capabilities.
+- **Arithmetic**: Use `checked_`, `saturating_`, or `overflowing_` methods for security-critical math.
+- **Memory**: Use the `zeroize` crate for sensitive data (keys/passwords) in memory.
+- **Testing**: Write unit tests for all new capability types and sandbox logic.
+- **Environment variables in tests**: Tests that modify `HOME`, `TMPDIR`, `XDG_CONFIG_HOME`, or other env vars must save and restore the original value. Rust runs unit tests in parallel within the same process, so an unrestored env var causes flaky failures in unrelated tests (e.g. `config::check_sensitive_path` fails when another test temporarily sets `HOME` to a fake path). Always use save/restore pattern and keep the modified window as short as possible.
+- **Attributes**: Apply `#[must_use]` to functions returning critical Results.
+- **Lazy use of dead code**: Avoid `#[allow(dead_code)]`. If code is unused, either remove it or write tests that use it.
+- **Commits**: All commits must include a DCO sign-off line (`Signed-off-by: Name <email>`).
+
+## Key Design Decisions
+
+1. **No escape hatch**: Once sandbox is applied via `restrict_self()` (Landlock) or `sandbox_init()` (Seatbelt), there is no API to expand permissions.
 
-### Formatting & Linting
-- **Strict Clippy**: We enforce `clippy::unwrap_used`. **NEVER** use `.unwrap()` or `.expect()`.
-- **Formatting**: Run `make fmt` to apply standard Rust formatting.
-- **Imports**: Group imports by crate (std, external, internal).
+2. **Fork+wait process model**: nono stays alive as a parent process. On child failure, prints a diagnostic footer to stderr. Three execution strategies: `Direct` (exec, backward compat), `Monitor` (sandbox-then-fork, default), `Supervised` (fork-then-sandbox, for rollbacks/expansion).
 
-### Error Handling
-- **No Panics**: Libraries should almost never panic. Use `Result` for all error conditions.
-- **Error Type**: Use `NonoError` for all errors. Propagate using `?`.
-- **Must Use**: Apply `#[must_use]` to functions returning critical `Result`s.
+3. **Capability resolution**: All paths are canonicalized at grant time to prevent symlink escapes.
 
-### Naming Conventions
-- **Types/Traits**: `PascalCase` (e.g., `SandboxState`, `CapabilitySet`).
-- **Functions/Variables**: `snake_case` (e.g., `apply_sandbox`, `is_supported`).
-- **Constants**: `SCREAMING_SNAKE_CASE` (e.g., `MAX_PATH_LENGTH`).
+4. **Library is policy-free**: The library applies ONLY what's in `CapabilitySet`. No built-in sensitive paths, dangerous commands, or system paths. Clients define all policy.
 
-## Security Mandates (CRITICAL)
+## Platform-Specific Notes
 
-**SECURITY IS NON-NEGOTIABLE.** Every change must be evaluated through a security lens.
+### macOS (Seatbelt)
+- Uses `sandbox_init()` FFI with raw profile strings
+- Profile is Scheme-like DSL: `(allow file-read* (subpath "/path"))`
+- Network denied by default with `(deny network*)`
 
-### Path Handling
-- **Canonicalization**: Always canonicalize paths at the enforcement boundary.
-- **Comparison**: Use `Path::components()` or `Path::starts_with()`.
-  - **NEVER** use string operations like `str::starts_with()` for paths (vulnerable to `/home` vs `/homeevil`).
-- **Symlinks**: Be aware of TOCTOU (Time-of-Check Time-of-Use) race conditions.
+### Linux (Landlock)
+- Uses landlock crate for safe Rust bindings
+- Detects highest available ABI (v1-v5)
+- ABI v4+ includes TCP network filtering
+- Strictly allow-list: cannot express deny-within-allow. `deny.access`, `deny.unlink`, and `symlink_pairs` are macOS-only. Avoid broad allow groups that cover deny paths.
 
-### Memory & Arithmetic
-- **Secrets**: Use the `zeroize` crate for sensitive data (keys/passwords) in memory.
-- **Math**: Use `checked_`, `saturating_`, or `overflowing_` methods for security-critical arithmetic.
+## Security Considerations
 
-### Safe Code
-- **Unsafe**: Restrict `unsafe` code to FFI modules only.
-- **Documentation**: All `unsafe` blocks must be wrapped in `// SAFETY:` comments explaining why it is safe.
+**SECURITY IS NON-NEGOTIABLE.** This is a security-critical codebase. Every change must be evaluated through a security lens first. When in doubt, choose the more restrictive option.
 
-### Principles
-- **Least Privilege**: Only grant the minimum necessary capabilities.
+### Core Principles
+- **Principle of Least Privilege**: Only grant the minimum necessary capabilities.
+- **Defense in Depth**: Combine OS-level sandboxing with application-level checks.
 - **Fail Secure**: On any error, deny access. Never silently degrade to a less secure state.
 - **Explicit Over Implicit**: Security-relevant behavior must be explicit and auditable.
 
-## Usage Example (Library)
+### Path Handling (CRITICAL)
+- Always use path component comparison, not string operations. String `starts_with()` on paths is a vulnerability.
+- Canonicalize paths at the enforcement boundary. Be aware of TOCTOU race conditions with symlinks.
+- Validate environment variables before use. Never assume `HOME`, `TMPDIR`, etc. are trustworthy.
+- Escape and validate all data used in Seatbelt profile generation.
 
-The core library (`crates/nono`) provides the sandbox primitive. Clients must construct a `CapabilitySet` and apply it.
+### Permission Scope (CRITICAL)
+- Never grant access to entire directories when specific paths suffice.
+- Separate read and write permissions explicitly.
+- Configuration load failures must be fatal. If security lists fail to load, abort.
 
-```rust
-use nono::{CapabilitySet, AccessMode, Sandbox};
+### Common Footguns
+1. **String comparison for paths**: `path.starts_with("/home")` matches `/homeevil`. Use `Path::starts_with()`.
+2. **Silent fallbacks**: `unwrap_or_default()` on security config returns empty permissions = no protection.
+3. **Trusting resolved paths**: Symlinks can change between resolution and use.
+4. **Platform differences**: macOS `/etc` is a symlink to `/private/etc`. Both must be considered.
+5. **Overly broad permissions**: Granting `/tmp` read/write when only `/tmp/specific-file` is needed.
+6. **Solving for one architecture**: Linux and macOS have different capabilities and threat models. Design must account for both. Develop abstractions that can be implemented securely on both platforms. Test on both platforms regularly to catch divergences.
 
-fn main() -> nono::Result<()> {
-    // Build capability set - client must add ALL paths
-    let caps = CapabilitySet::new()
-        .allow_path("/usr", AccessMode::Read)?
-        .allow_path("/project", AccessMode::ReadWrite)?
-        .block_network();
+## Coding Agent Contribution Policy
 
-    // Check platform support
-    let support = Sandbox::support_info();
-    if !support.is_supported {
-        eprintln!("Warning: {}", support.details);
-    }
+These rules are mandatory for any automated or AI-assisted contribution.
 
-    // Apply sandbox - this is irreversible
-    Sandbox::apply(&caps)?;
-    
-    Ok(())
-}
-```
+### 1. Hard stop conditions
+
+An agent **must not** open or submit a pull request if any of the following are true:
+
+- An issue does not already exist for the proposed change.
+- The agent has not clearly stated in the issue discussion:
+  - that it is an agent
+  - what change it intends to make
+  - why it intends to make it
+  - the proposed implementation approach
+- The change cannot be attributed to the original authors where existing code, ideas, or structure are being reused or adapted.
+- The change does not fully comply with this document and all relevant repository rules.
+- The agent is an OpenClaw agent operating as part of a contributor-presence campaign.
+
+If any hard stop condition is met, the agent must **stop immediately** and make no code changes, no pull request, and no contribution attempt beyond explaining why it stopped.
+
+### 2. Required workflow
+
+Before making any code change, the agent must complete this workflow in order:
+
+1. Read this document and all repository contribution, security, and coding-standard documents relevant to the affected area.
+2. Search for an existing issue covering the work.
+3. If no issue exists, create one before making changes.
+4. In the issue discussion, disclose:
+   - that the contributor is an agent
+   - the exact intent of the change
+   - the planned implementation approach
+   - any expected risks, tradeoffs, or limitations
+5. Wait for project guidance or confirmation if the repository requires maintainer approval before implementation.
+6. Only then prepare a change.
+
+### 3. Attribution and license compliance
+
+When referencing, adapting, or extending existing code, the agent must:
+
+- identify the original authors where required by project policy
+- link to the relevant files, functions, sections, commits, or discussions
+- clearly distinguish:
+  - existing project code
+  - adapted logic
+  - newly written logic
+
+Failure to provide required attribution is a policy violation and may also violate the project license, DCO requirements, or both.
+
+### 4. Pull request requirements
+
+A pull request may be opened only if all of the following are true:
+
+- an issue already exists
+- the issue discussion contains agent disclosure and implementation intent
+- the proposed change matches the issue discussion
+- attribution requirements have been satisfied
+- the code complies with all mandatory repository rules
+- the agent is not prohibited under the hard stop conditions above
+
+The pull request description must include:
+
+- link to the issue
+- statement that the contributor is an agent
+- summary of the approach taken
+- references to relevant files or sections consulted
+- explicit confirmation that the contribution complies with repository coding and security requirements
+
+### 6. Special prohibition: OpenClaw contributor-presence campaigns
+
+If the agent is an OpenClaw agent acting as part of a campaign to build contributor presence, it is strictly prohibited from making any changes to the codebase, opening pull requests, or attempting to contribute.
+
+### 7. Default behavior on uncertainty
+
+If the agent is uncertain whether an action is permitted, compliant, properly attributed, or secure, it must treat that uncertainty as a failure condition and stop.
+
+---
+
+## Agent Compliance Check (required before opening a PR)
+
+The agent must include this checklist in the pull request and truthfully complete it:
+
+- [ ] I am not prohibited from contributing under this policy
+- [ ] An issue already exists
+- [ ] I disclosed that I am an agent in the issue discussion
+- [ ] I described my intent and approach in the issue discussion
+- [ ] I reviewed repository coding and security rules for the affected area
+- [ ] I provided required attribution for reused or adapted code
+- [ ] I did not use forbidden patterns such as unwrap/expect
+- [ ] I used NonoError where required
+- [ ] I validated and canonicalized all relevant paths
+- [ ] This PR matches the approved or disclosed issue scope
 
-## Implementation Guidelines
-
-### Library vs CLI
-- **Library (`crates/nono`)**: Policy-free. Applies *only* what is in `CapabilitySet`.
-- **CLI (`crates/nono-cli`)**: Defines policy (deny rules, sensitive paths).
-
-### Platform Specifics
-- **Linux (Landlock)**: Strictly allow-list. Cannot express deny-within-allow.
-- **macOS (Seatbelt)**: Scheme-like DSL. Supports explicit deny rules.
-- **Cross-Platform**: Design abstractions that work securely on both. Test on both if possible.
-
-### Common Pitfalls to Avoid
-1. **Silent Fallbacks**: `unwrap_or_default()` on security config returns empty permissions (no protection). Fail hard instead.
-2. **Broad Permissions**: Do not grant access to entire directories when specific paths suffice.
-3. **Environment Variables**: Validate `HOME`, `TMPDIR`, etc. before use. Do not assume they are trustworthy.
-4. **Dead Code**: Avoid `#[allow(dead_code)]`. Remove unused code or write tests for it.
-
-## Testing Strategy
-When writing tests for new capabilities:
-1.  **Unit Tests**: Verify the logic of `CapabilitySet` construction.
-2.  **Integration Tests**: Use `tests/` directory to run actual sandbox enforcement checks.
-3.  **Platform Checks**: Use `#[cfg(target_os = "linux")]` or `#[cfg(target_os = "macos")]` if the test is platform-specific.
-
-## Quick Reference
-- **Check code quality**: `make clippy`
-- **Fix formatting**: `make fmt`
-- **Run all tests**: `make test`
+If any item cannot be truthfully checked, the agent must not open a pull request. Instead, it must stop and report the issue.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -2,76 +2,13 @@
 
 ## Project Overview
 
-nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes where unauthorized operations are structurally impossible.
+nono is a capability-based sandboxing system for running untrusted AI agents with OS-enforced isolation. It uses Landlock (Linux) and Seatbelt (macOS) to create sandboxes, and then layers on top a policy system, diagnostic tools, and a rollback mechanism for recovery. The library is designed to be a pure sandbox primitive with no built-in policy, while the CLI implements all security policy and UX.
 
 The project is a Cargo workspace with three members:
 - **nono** (`crates/nono/`) - Core library. Pure sandbox primitive with no built-in security policy.
 - **nono-cli** (`crates/nono-cli/`) - CLI binary. Owns all security policy, profiles, hooks, and UX.
 - **nono-ffi** (`bindings/c/`) - C FFI bindings. Exposes the library via `extern "C"` functions and auto-generated `nono.h` header.
-
-Language bindings live in separate repositories:
-- **nono-py** (`../nono-py/`) - Python bindings via PyO3. Published to PyPI.
-- **nono-ts** (`../nono-ts/`) - TypeScript/Node bindings via napi-rs. Published to npm.
-
-## Architecture
-
-```
-crates/nono/src/                    # Library - pure sandbox primitive
-├── lib.rs                          # Public API re-exports
-├── capability.rs                   # CapabilitySet, FsCapability, AccessMode (builder pattern)
-├── error.rs                        # NonoError enum
-├── state.rs                        # SandboxState serialization
-├── diagnostic.rs                   # DiagnosticFormatter
-├── query.rs                        # QueryContext for permission checking
-├── keystore.rs                     # Secure credential loading from system keystore
-├── undo/
-│   ├── mod.rs                      # Module root, re-exports public API
-│   ├── types.rs                    # ContentHash, FileState, Change, SnapshotManifest, SessionMetadata
-│   ├── object_store.rs             # Content-addressable file storage (SHA-256, dedup, clone_or_copy)
-│   ├── merkle.rs                   # MerkleTree (cryptographic state commitment)
-│   ├── snapshot.rs                 # SnapshotManager (baseline, incremental, restore)
-│   └── exclusion.rs                # ExclusionFilter (gitignore, patterns, globs)
-└── sandbox/
-    ├── mod.rs                      # Sandbox facade: apply(), is_supported(), support_info()
-    ├── linux.rs                    # Landlock implementation
-    └── macos.rs                    # Seatbelt implementation
-
-crates/nono-cli/src/                # CLI - security policy and UX
-├── main.rs                         # Entry point, command routing
-├── cli.rs                          # Clap argument definitions
-├── capability_ext.rs               # CapabilitySetExt trait (CLI-specific construction)
-├── policy.rs                       # Group resolver: parse policy.json, filter, expand, resolve
-├── query_ext.rs                    # CLI-specific query functions
-├── sandbox_state.rs                # CLI-specific state handling
-├── exec_strategy.rs                # Fork+exec with signal forwarding (Direct/Monitor/Supervised)
-├── hooks.rs                        # Claude Code hook installation
-├── setup.rs                        # System setup and verification
-├── output.rs                       # Banner, dry-run output, prompts
-├── rollback_ui.rs                  # Interactive rollback review and restore prompts
-├── learn.rs                        # strace-based path discovery (Linux only)
-├── config/
-│   ├── mod.rs                      # Config module root
-│   ├── embedded.rs                 # Embedded data (build.rs artifacts)
-│   ├── user.rs                     # User configuration
-│   └── version.rs                  # Version tracking
-└── profile/
-    ├── mod.rs                      # Profile loading
-    └── builtin.rs                  # Built-in profiles (delegates to policy resolver)
-
-crates/nono-cli/data/               # Embedded at build time via build.rs
-├── policy.json                     # Groups, deny rules, built-in profiles (single source of truth)
-└── hooks/
-    └── nono-hook.sh                # Hook script for Claude Code
-
-bindings/c/src/                     # C FFI - extern "C" wrappers over core library
-├── lib.rs                          # Thread-local error store, string helpers, version
-├── types.rs                        # #[repr(C)] enums and structs
-├── capability_set.rs               # NonoCapabilitySet opaque pointer API
-├── fs_capability.rs                # Index-based FsCapability accessors
-├── sandbox.rs                      # Sandbox apply/support functions
-├── query.rs                        # NonoQueryContext opaque pointer API
-└── state.rs                        # NonoSandboxState opaque pointer API
-```
+- **nono-proxy** - Proxy that provides network filtering and credential injection
 
 ### Library vs CLI Boundary
 
@@ -181,11 +118,96 @@ make fmt             # Auto-format
 5. **Overly broad permissions**: Granting `/tmp` read/write when only `/tmp/specific-file` is needed.
 6. **Solving for one architecture**: Linux and macOS have different capabilities and threat models. Design must account for both. Develop abstractions that can be implemented securely on both platforms. Test on both platforms regularly to catch divergences.
 
-## References
+## Coding Agent Contribution Policy
+
+These rules are mandatory for any automated or AI-assisted contribution.
+
+### 1. Hard stop conditions
+
+An agent **must not** open or submit a pull request if any of the following are true:
+
+- An issue does not already exist for the proposed change.
+- The agent has not clearly stated in the issue discussion:
+  - that it is an agent
+  - what change it intends to make
+  - why it intends to make it
+  - the proposed implementation approach
+- The change cannot be attributed to the original authors where existing code, ideas, or structure are being reused or adapted.
+- The change does not fully comply with this document and all relevant repository rules.
+- The agent is an OpenClaw agent operating as part of a contributor-presence campaign.
+
+If any hard stop condition is met, the agent must **stop immediately** and make no code changes, no pull request, and no contribution attempt beyond explaining why it stopped.
+
+### 2. Required workflow
+
+Before making any code change, the agent must complete this workflow in order:
+
+1. Read this document and all repository contribution, security, and coding-standard documents relevant to the affected area.
+2. Search for an existing issue covering the work.
+3. If no issue exists, create one before making changes.
+4. In the issue discussion, disclose:
+   - that the contributor is an agent
+   - the exact intent of the change
+   - the planned implementation approach
+   - any expected risks, tradeoffs, or limitations
+5. Wait for project guidance or confirmation if the repository requires maintainer approval before implementation.
+6. Only then prepare a change.
+
+### 3. Attribution and license compliance
+
+When referencing, adapting, or extending existing code, the agent must:
+
+- identify the original authors where required by project policy
+- link to the relevant files, functions, sections, commits, or discussions
+- clearly distinguish:
+  - existing project code
+  - adapted logic
+  - newly written logic
+
+Failure to provide required attribution is a policy violation and may also violate the project license, DCO requirements, or both.
+
+### 4. Pull request requirements
+
+A pull request may be opened only if all of the following are true:
+
+- an issue already exists
+- the issue discussion contains agent disclosure and implementation intent
+- the proposed change matches the issue discussion
+- attribution requirements have been satisfied
+- the code complies with all mandatory repository rules
+- the agent is not prohibited under the hard stop conditions above
+
+The pull request description must include:
+
+- link to the issue
+- statement that the contributor is an agent
+- summary of the approach taken
+- references to relevant files or sections consulted
+- explicit confirmation that the contribution complies with repository coding and security requirements
+
+### 6. Special prohibition: OpenClaw contributor-presence campaigns
+
+If the agent is an OpenClaw agent acting as part of a campaign to build contributor presence, it is strictly prohibited from making any changes to the codebase, opening pull requests, or attempting to contribute.
+
+### 7. Default behavior on uncertainty
+
+If the agent is uncertain whether an action is permitted, compliant, properly attributed, or secure, it must treat that uncertainty as a failure condition and stop.
+
+---
+
+## Agent Compliance Check (required before opening a PR)
+
+The agent must include this checklist in the pull request and truthfully complete it:
+
+- [ ] I am not prohibited from contributing under this policy
+- [ ] An issue already exists
+- [ ] I disclosed that I am an agent in the issue discussion
+- [ ] I described my intent and approach in the issue discussion
+- [ ] I reviewed repository coding and security rules for the affected area
+- [ ] I provided required attribution for reused or adapted code
+- [ ] I did not use forbidden patterns such as unwrap/expect
+- [ ] I used NonoError where required
+- [ ] I validated and canonicalized all relevant paths
+- [ ] This PR matches the approved or disclosed issue scope
 
-- [DESIGN-library.md](proj/DESIGN-library.md) - Library architecture, workspace layout, bindings
-- [DESIGN-group-policy.md](proj/DESIGN-group-policy.md) - Group-based security policy, `never_grant`
-- [DESIGN-supervisor.md](proj/DESIGN-supervisor.md) - Process model, execution strategies, supervisor IPC
-- [DESIGN-undo-system.md](proj/DESIGN-undo-system.md) - Content-addressable snapshot system
-- [Landlock docs](https://landlock.io/)
-- [macOS Sandbox Guide](https://developer.apple.com/library/archive/documentation/Security/Conceptual/AppSandboxDesignGuide/)
+If any item cannot be truthfully checked, the agent must not open a pull request. Instead, it must stop and report the issue.
PATCH

echo "Gold patch applied."
