# Remove Custom Clippy Infrastructure and Refactor Long Functions

## Problem

The project uses a custom `too_many_lines` clippy lint enforcement system that adds unnecessary complexity:
- `scripts/clippy-lint.sh` wraps clippy with custom baseline checking
- `scripts/clippy-baseline.sh` tracks allowed violations against a baseline
- `clippy-baselines/too_many_lines.txt` lists functions exempt from the line limit

This custom infrastructure is hard to maintain and produces verbose output. Standard `cargo clippy` with a `clippy.toml` configuration would be simpler and more conventional.

Additionally, `crates/goose-cli/src/session/builder.rs` contains a very long `build_session` function that should be decomposed into smaller, focused helper functions.

## Expected Behavior

### 1. Replace custom clippy infrastructure with standard approach

- Delete the files `scripts/clippy-lint.sh`, `scripts/clippy-baseline.sh`, and `clippy-baselines/too_many_lines.txt`
- Create a `clippy.toml` file at the repository root containing a `too-many-lines-threshold` setting (a positive integer)
- Replace all references to `./scripts/clippy-lint.sh` with `cargo clippy --all-targets -- -D warnings`

### 2. Update documentation and config files

The following files must be updated so they no longer reference `./scripts/clippy-lint.sh` and instead use the standard clippy command. After updating:

- **AGENTS.md**: Must contain `cargo clippy --all-targets`. Its "Never" rules must include the phrase "Merge without running clippy" (not the old script path).
- **`.github/copilot-instructions.md`**: Must contain `cargo clippy --all-targets`. The comment about clippy warnings must say "CI handles this (clippy)".
- **HOWTOAI.md**: Must contain `cargo clippy --all-targets` and must reference `clippy.toml`.
- **CONTRIBUTING.md**: Must contain `cargo clippy --all-targets`.
- **Justfile**: Must contain `cargo clippy --all-targets`.

### 3. Decompose the `build_session` function

The `build_session` function in `crates/goose-cli/src/session/builder.rs` must be refactored so that its logic is delegated to smaller, focused helper functions. The decomposition should include at least five helper functions that handle:

- Resolving the provider name and model configuration from session config, saved data, and recipe settings
- Determining the session ID (for new, resumed, or hidden sessions)
- Handling working directory changes when resuming a session
- Resolving which extensions to load and loading them onto the agent
- Configuring system prompts for the session

Each helper must exist as a standalone `fn` declaration in the file, and `build_session` must call each of them. After refactoring, `builder.rs` must have at least 10 function declarations with valid syntax and balanced braces.

## Files to Look At

- `crates/goose-cli/src/session/builder.rs` — contains the `build_session` function to decompose
- `scripts/clippy-lint.sh` and `scripts/clippy-baseline.sh` — custom scripts to remove
- `clippy.toml` — should be created with clippy configuration
- `AGENTS.md`, `.github/copilot-instructions.md`, `HOWTOAI.md`, `CONTRIBUTING.md`, `Justfile` — documentation and config files to update

## Code Style Requirements

Your solution will be checked by the repository's existing linters/formatters. All modified files must pass:

- `cargo fmt (Rust formatter)`
