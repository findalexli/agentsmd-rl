# Add GitHub Copilot instructions

Source: [arsfeld/reel#18](https://github.com/arsfeld/reel/pull/18)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Configures GitHub Copilot coding agent for the repository per [best practices](https://docs.github.com/en/copilot/tutorials/coding-agent/get-the-best-results).

## Changes

Created `.github/copilot-instructions.md` covering:

- **Environment**: Nix flakes requirement (critical for builds)
- **Build/Test/Lint**: `cargo check`, `cargo build`, `cargo fmt`, `cargo clippy`, `cargo test` workflows
- **Architecture**: Relm4 reactive patterns (AsyncComponents, Factory, Worker, MessageBroker), offline-first design, three-tier caching
- **Platform specifics**: Linux (MPV/GStreamer), macOS (GStreamer only, use `--no-default-features --features gstreamer`)
- **Code standards**: No backward compatibility layers, no fallbacks, fix Clippy warnings
- **Common tasks**: Step-by-step guides for adding UI components, backend features, database entities

## Key Rules for Copilot

- All development commands require `nix develop` shell
- Backend abstraction via `MediaBackend` trait—no hardcoded backend logic
- Use SeaORM repository pattern for data access
- Follow existing Relm4 component patterns

<!-- START COPILOT CODING AGENT SUFFIX -->



<details>

<summary>Original prompt</summary>

> 
> ----
> 
> *This section details on the original issue you should resolve*
> 
> <issue_title>✨ Set up Copilot instructions</issue_title>
> <issue_description>Configure instructions for this repository as documented in [Best practices for Copilot coding agent in your repository](https://gh.io/copilot-coding-ag

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
