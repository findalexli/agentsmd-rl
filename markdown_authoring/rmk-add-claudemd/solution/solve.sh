#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rmk

# Idempotency guard
if grep -qF ".claude/skills/test-changes/SKILL.md" ".claude/skills/test-changes/SKILL.md" && grep -qF "RMK is a Rust keyboard firmware library targeting embedded microcontrollers (`no" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/test-changes/SKILL.md b/.claude/skills/test-changes/SKILL.md
@@ -1,14 +0,0 @@
----
-name: test-changes
-description: Test code after changes, to ensure that all changes are good enough and don't break current examples. Use when the changes are done or when the user asks "test changes"
----
-
-When testing code, there are three steps:
-
-1. Run unit test: go to the root of the current project, then run unittests in `rmk` crate and `rmk-macro` crate: `cd rmk && cargo test --no-default-features --features "storage,std,vial,_ble"` and `cd rmk-macro && cargo test`
-2. When small changes is finished, go to the root of the current project, then check the following 4 examples: 
-    - `cd examples/use_rust/nrf52840_ble_split_dongle && cargo build --release` 
-    - `cd examples/use_rust/nrf52840_ble_split && cargo build --release` 
-    - `cd examples/use_config/nrf52840_ble_split && cargo build --release`
-    - `cd examples/use_config/nrf52840_ble_split_dongle && cargo build --release`
-3. When huge changes is finished, check all examples by running: `sh scripts/clippy_all.sh && sh scripts/check_all.sh`
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,66 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.
+
+## What This Project Is
+
+RMK is a Rust keyboard firmware library targeting embedded microcontrollers (`no_std` by default). It supports USB and BLE keyboards, split keyboards, on-the-fly keymap configuration(Vial), and advanced key behaviors (combos, tap-hold, macros, morse, etc). The repo is a Cargo monorepo with four crates():
+
+- **`rmk`** — core firmware logic
+- **`rmk-config`** — TOML configuration parsing (for `keyboard.toml`-based users)
+- **`rmk-macro`** — procedural macros (`#[rmk_keyboard]`, `#[derive(Event)]`, etc.)
+- **`rmk-types`** — shared types (`KeyAction`, `EncoderAction`, etc.)
+
+Note that there's no `Cargo.toml` in the project root.
+
+The `examples/` directory shows two usage patterns: `use_config/` (driven by `keyboard.toml`) and `use_rust/` (pure Rust API).
+The `docs` directory contains multi-version documentation
+The `scripts` directory contains useful scripts for checking/formatting code
+
+## Commands
+
+### Testing
+Run from the `rmk/` directory:
+
+```bash
+cargo test --no-default-features --features=split,vial,storage,async_matrix,_ble
+```
+
+Run macro tests from `rmk-macro/` (requires `cargo-expand`):
+```bash
+cargo test
+```
+
+### Building examples
+Examples target specific MCUs; build from an example directory, e.g.:
+```bash
+cd examples/use_config/nrf52840_ble
+cargo build --release
+```
+
+### Checks
+```bash
+# Format all Rust files
+sh scripts/format_all.sh
+# Run clippy for all examples and crates
+sh scripts/clippy_all.sh
+# Build all examples to check
+sh scripts/check_all.sh
+```
+
+## Architecture
+
+### Basic Data flow
+```
+Matrix / InputDevices → Events (pub/sub channels) -> InputProcessors/Keyboard(keyboard.rs) -> KEYBOARD_REPORT_CHANNEL -> HidWriter (USB or BLE) -> Host
+```
+
+### `keyboard.toml` and compile-time constants
+
+`keyboard.toml` is parsed by `rmk-config` (`KeyboardTomlConfig`) at two points: by `rmk/build.rs` at build time, and by `rmk-macro` at macro-expansion time. The path defaults to `keyboard.toml` next to `Cargo.toml` and can be overridden with `KEYBOARD_TOML_PATH` in user space's `.cargo/config.toml`.
+
+Config is loaded in three layers (later overrides earlier): `event_default.toml` → chip-specific default (from `rmk-config/src/default_config/<chip>.toml`, selected via `[keyboard].chip`) → user `keyboard.toml`.
+
+`build.rs` reads only the `[rmk]` and `[event]` sections, then emits `constants.rs` as Rust `const` items. The full `KeyboardTomlConfig` struct in `rmk-config/src/lib.rs` is the authoritative reference for all available fields and their defaults.
+
+`[event]` tunes per-event pub/sub channel sizes (`channel_size`, `pubs`, `subs`). All event names and their defaults live in `rmk-config/src/default_config/event_default.toml`.
PATCH

echo "Gold patch applied."
