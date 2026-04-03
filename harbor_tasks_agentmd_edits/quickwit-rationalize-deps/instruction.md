# Remove Unused Default Features from Dependencies

## Problem

The workspace `quickwit/Cargo.toml` has several dependencies that pull in unnecessary default features, increasing compile times and binary size. Specifically, crates like `hyper-util` and `tokio-util` use `features = ["full"]` when only a subset of features is actually needed. Other dependencies like `dialoguer`, `env_logger`, `prometheus`, and `zstd` use their full default feature sets despite the project only using a fraction of their functionality.

## Expected Behavior

Each dependency should only enable the features that are actually used by the project. Dependencies that don't need all their defaults should set `default-features = false` and explicitly list only the required features. This reduces compile times and binary size without changing runtime behavior.

## What Needs to Change

1. **Audit `quickwit/Cargo.toml`** — identify workspace dependencies that enable unnecessary default features
2. **Disable defaults and specify minimal features** — for each identified dependency, set `default-features = false` and add back only the features the project actually uses
3. **Document the process** — since this is a repeatable optimization task, create a Claude skill (`.claude/skills/rationalize-deps/SKILL.md`) that documents the workflow for analyzing and trimming dependency features in this project. Look at the existing skills in `.claude/skills/` for the expected format and structure.

## Files to Look At

- `quickwit/Cargo.toml` — workspace dependency declarations (the `[workspace.dependencies]` section)
- `.claude/skills/` — existing skills for reference on format and structure
