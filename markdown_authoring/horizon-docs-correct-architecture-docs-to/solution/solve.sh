#!/usr/bin/env bash
set -euo pipefail

cd /workspace/horizon

# Idempotency guard
if grep -qF "- **Per-panel event loop thread:** alacritty_terminal `EventLoop` reads PTY outp" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -55,7 +55,7 @@ If any step fails, read the error, fix the prerequisite, and retry. On Linux, mi
 **Horizon** is a GPU-accelerated terminal board — a visual workspace for managing
 multiple terminal sessions as freely positioned, resizable panels on a canvas.
 
-**Stack:** Rust (edition 2024) · eframe/egui (wgpu backend) · vt100 · portable-pty
+**Stack:** Rust (edition 2024) · eframe/egui (wgpu backend) · alacritty_terminal (VT parsing, PTY, event loop)
 
 ## Workspace Layout
 
@@ -68,7 +68,7 @@ crates/
 ### horizon-core
 
 - `error.rs` — Typed error enum via thiserror
-- `terminal.rs` — vt100 parser wrapper (screen buffer, resize)
+- `terminal.rs` — alacritty_terminal wrapper (VT parsing, PTY spawn, event loop, resize)
 - `panel.rs` — Panel = terminal + PTY session + identity
 - `board.rs` — Board = collection of panels + focus management
 
@@ -250,20 +250,20 @@ git push origin v0.1.0
 ### Threading Model
 
 - **Main thread:** egui event loop + rendering
-- **Per-panel reader thread:** reads PTY output, sends via `mpsc::channel`
-- **Input:** main thread writes directly to PTY stdin
+- **Per-panel event loop thread:** alacritty_terminal `EventLoop` reads PTY output, parses VT sequences, and sends events via `mpsc::channel`
+- **Input:** main thread writes to PTY via `EventLoopSender`
 
 ### Data Flow
 
 ```
-Shell → PTY slave → PTY master reader → [thread] → channel → main thread → vt100 → egui
-Keyboard → main thread → PTY master writer → PTY slave → Shell
+Shell → PTY slave → PTY master → [alacritty EventLoop thread] → Term (VT parse) → channel → main thread → egui
+Keyboard → main thread → EventLoopSender → PTY master → PTY slave → Shell
 ```
 
 ### Panel Lifecycle
 
-1. `Board::create_panel()` opens a PTY, spawns `$SHELL`
-2. Reader thread continuously sends output chunks to main thread
-3. Each frame: drain channel → feed vt100 parser → render grid
-4. On resize: recalculate rows/cols → resize vt100 + PTY
+1. `Board::create_panel()` opens a PTY via `alacritty_terminal::tty`, spawns `$SHELL`
+2. alacritty `EventLoop` thread continuously reads PTY output and updates the `Term` grid
+3. Each frame: drain event channel → render from `Term` state → egui
+4. On resize: recalculate rows/cols → resize `Term` + PTY
 5. On close: drop Panel (PTY handles cleaned up automatically)
PATCH

echo "Gold patch applied."
