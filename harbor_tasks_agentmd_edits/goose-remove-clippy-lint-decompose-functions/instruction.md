# Remove Custom Clippy Infrastructure and Refactor Long Functions

## Problem

The project uses a custom `too_many_lines` clippy lint enforcement system that adds unnecessary complexity:
- `scripts/clippy-lint.sh` wraps clippy with custom baseline checking
- `scripts/clippy-baseline.sh` tracks allowed violations against a baseline
- `clippy-baselines/too_many_lines.txt` lists functions exempt from the line limit

This custom infrastructure is hard to maintain and produces verbose output that's difficult for LLMs working on this codebase to interpret. Standard `cargo clippy` with a `clippy.toml` configuration would be simpler and more conventional.

Additionally, `crates/goose-cli/src/session/builder.rs` contains a very long `build_session` function that should be decomposed into smaller, focused helper functions.

## Expected Behavior

1. Replace the custom clippy lint infrastructure with standard `cargo clippy` using a `clippy.toml` configuration
2. Decompose the long `build_session` function into focused helper functions with clear responsibilities
3. Update all documentation and configuration files that reference the old clippy scripts to use the new standard approach

## Files to Look At

- `crates/goose-cli/src/session/builder.rs` — contains the long `build_session` function that needs decomposing
- `scripts/clippy-lint.sh` and `scripts/clippy-baseline.sh` — custom scripts to remove
- `clippy.toml` — should be created with clippy configuration
- `AGENTS.md` — lint/format section and development loop reference the old scripts
- `.github/copilot-instructions.md` — CI pipeline section references the old scripts
- `HOWTOAI.md` — AI coding guide references the old clippy approach
- `CONTRIBUTING.md` — developer instructions reference the old script
- `Justfile` — check-everything recipe uses the old script

After making the code changes, update all configuration and documentation files to reference the new standard `cargo clippy` approach instead of the removed custom scripts.
