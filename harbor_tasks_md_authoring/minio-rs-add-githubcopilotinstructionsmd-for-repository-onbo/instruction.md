# Add .github/copilot-instructions.md for repository onboarding

Source: [minio/minio-rs#191](https://github.com/minio/minio-rs/pull/191)

This task is a **markdown_authoring** task. The repository's agent-instruction file(s)
need to be updated. Read the existing content and add or modify the rules so that
the file matches the intent described below.

## Files to update

- `.github/copilot-instructions.md`

## What to add / change

Adds comprehensive onboarding instructions to reduce agent exploration time and CI failures when working on this repository.

## Content

**Repository Overview**
- Rust SDK for MinIO/S3-compatible storage
- Stack: Rust 1.88.0, edition 2024, async-first with tokio
- Structure: ~160 source files across library, examples, tests, benchmarks

**Build &amp; Validation Commands** (all validated with timing)
- Format: `cargo fmt --all -- --check` (~1s)
- Lint: `cargo clippy --all-targets --all-features --workspace -- -D warnings` (~45-70s)
- Build: `cargo build --bins --examples --tests --benches` (~90s full, ~20s incremental)
- Unit tests: `cargo test --lib` (&lt;1s, no server required)
- Integration tests: Requires MinIO server via `./tests/start-server.sh` + environment variables
- Docs: `cargo doc --no-deps` (~8-10s)

**Project Architecture**
- Directory structure with file counts and purposes
- CI/CD pipeline: 6 jobs (format, clippy, test-multi-thread, test-current-thread, build, label-checker)
- **PR Requirements**: All PRs must have at least one label from: `highlight`, `breaking-change`, `security-fix`, `enhancement`, `bug`, `cleanup-rewrite`, `regression-fix`, `codex`
- Workspace members: minio (main), minio-common (test utils), minio-macros (proc macros)
- Design patterns: Builder pattern, S3Api trait, typed responses

**Common Pitfalls**
- Integration tests fail without MinIO server + env vars
- `--no-default-features` build fails (requires crypto + TLS backends)
- 13 doc 

## Acceptance

The grader runs `pytest /tests/test_outputs.py` which checks that distinctive
literal strings from the intended update are present in the target file(s).
You do not need to write any code outside of the markdown file(s).
