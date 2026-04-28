#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vortex

# Idempotency guard
if grep -qF "- If `gh` commands fail with `error connecting to api.github.com` in sandbox, im" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,26 +2,27 @@
 
 ## Development Guidelines
 
-- project is a monorepo Rust workspace, java bindings in `/java`, python bindings in
+- Project is a monorepo Rust workspace, java bindings in `/java`, python bindings in
   `/vortex-python`
-- run `cargo build -p` to build a specific crate
-- use `cargo clippy --all-targets --all-features` to make sure a project is free of lint issues.
+- Run `cargo build -p` to build a specific crate
+- Use `cargo clippy --all-targets --all-features` to make sure a project is free of lint issues.
   Please do this every time you reach a stopping point or think you've finished work.
-- run `cargo +nightly fmt --all` to format Rust source files. Please do this every time you reach a
+- Run `cargo +nightly fmt --all` to format Rust source files. Please do this every time you reach a
   stopping point or think you've finished work.
-- run `./scripts/public-api.sh` to re-generate the public API lock files. Please do this every time
+- Run `./scripts/public-api.sh` to re-generate the public API lock files. Please do this every time
   you reach a stopping point or think you've finished work.
-- you can try running
+- You can try running
   `cargo fix --lib --allow-dirty --allow-staged && cargo clippy --fix --lib --allow-dirty --allow-staged`
   to automatically many fix minor errors.
-- when iterating on CI failures, fetch only failed job logs first
+- When iterating on CI failures, fetch only failed job logs first
   (`gh run view <run-id> --job <job-id> --log-failed`) and run narrow local repro commands for the
   affected crate/tests before running workspace-wide checks.
-- if `gh` commands fail with `error connecting to api.github.com` in sandbox, immediately rerun with
+- If `gh` commands fail with `error connecting to api.github.com` in sandbox, immediately rerun with
   escalated network permissions instead of retrying in sandbox.
-- if cargo fails with `sccache: error: Operation not permitted`, rerun the command with
-  `RUSTC_WRAPPER=` so rustc runs directly.
-- run docs doctests from the docs directory (`make -C docs doctest`) so the correct Sphinx Makefile
+- If cargo fails with `sccache: error: Operation not permitted`, rerun the command with
+  `RUSTC_WRAPPER=` so rustc runs directly. You should ONLY do this if you get this exact error, as
+  this is only a concern when you are running on our CI.
+- Run docs doctests from the docs directory (`make -C docs doctest`) so the correct Sphinx Makefile
   target is used.
 
 ## Architecture
PATCH

echo "Gold patch applied."
