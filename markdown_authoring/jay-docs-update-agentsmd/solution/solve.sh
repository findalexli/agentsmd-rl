#!/usr/bin/env bash
set -euo pipefail

cd /workspace/jay

# Idempotency guard
if grep -qF "| `src/control_center/cc_*.rs` | Control center panes: 11 sidebar panes + `cc_wi" "book/AGENTS.md" && grep -qF "book/CLAUDE.md" "book/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/book/AGENTS.md b/book/AGENTS.md
@@ -8,20 +8,34 @@ is end users, not developers. Goal is feature discoverability.
 
 ### Book files (`book/src/`)
 
-The table of contents is `SUMMARY.md`. Key chapter-to-topic mapping:
+The table of contents is `SUMMARY.md` — it is the authoritative chapter
+list and must be updated when adding a new chapter. Chapter-to-topic mapping:
 
 | File | Covers |
 |------|--------|
+| `configuration/index.md` | Config overview: replacement semantics, `jay config init`, auto-reload |
 | `configuration/shortcuts.md` | Shortcuts, actions (simple + parameterized), marks, named actions, virtual outputs, actions in window rules |
+| `configuration/startup.md` | Startup hooks (`on-graphics-initialized`, `on-idle`, `on-resume`) |
 | `configuration/outputs.md` | Monitor config, VRR, tearing, scaling, transforms |
 | `configuration/inputs.md` | Input devices, per-device settings |
+| `configuration/keymaps.md` | Keymaps, repeat rate |
+| `configuration/idle.md` | Idle timeout, screen locking |
+| `configuration/gpu.md` | GPU selection, multi-GPU |
+| `configuration/theme.md` | Theme, appearance |
+| `configuration/status-bar.md` | Status bar config |
+| `configuration/xwayland.md` | Xwayland |
+| `configuration/environment.md` | Environment variables |
 | `configuration/misc.md` | Color management, libei, floating defaults, ui-drag |
-| `window-rules.md` | Window/client rules, privileges, capabilities |
-| `control-center.md` | All 11 control center panes |
-| `cli.md` | All CLI subcommands, JSON output |
-| `input-modes.md` | Modal keybinding system (push/pop/latch/clear) |
+| `tiling.md` | i3-like tiling layout, splitting containers |
+| `workspaces.md` | Virtual desktops, workspace management, multi-monitor |
 | `floating.md` | Floating windows, window management mode |
+| `mouse.md` | All mouse-driven interactions (resize, drag, scroll) |
+| `input-modes.md` | Modal keybinding system (push/pop/latch/clear) |
+| `window-rules.md` | Window/client rules, privileges, capabilities |
+| `screen-sharing.md` | Screen sharing via xdg-desktop-portal, PipeWire |
 | `hdr.md` | HDR & color management walkthrough |
+| `control-center.md` | All control center panes (see pane list below) |
+| `cli.md` | All CLI subcommands, JSON output |
 
 ### Source-of-truth files (from repo root)
 
@@ -33,7 +47,7 @@ The table of contents is `SUMMARY.md`. Key chapter-to-topic mapping:
 | `toml-config/src/lib.rs` | Action dispatch — `window_or_seat!` macro shows which actions work in window rules |
 | `src/config/handler.rs` | Config handler; `update_capabilities` shows capability replacement semantics |
 | `src/cli/*.rs` | CLI subcommands (clap definitions) |
-| `src/control_center/cc_*.rs` | Control center pane implementations (verify field names/ordering here) |
+| `src/control_center/cc_*.rs` | Control center panes: 11 sidebar panes + `cc_window.rs` / `cc_clients.rs` detail panes + `cc_criterion.rs` shared helper. Verify field names/ordering here |
 | `toml-config/src/config/parsers/exec.rs` | Exec parser (string, array, or table forms) |
 
 ### Known spec.yaml bugs
@@ -127,6 +141,12 @@ The table of contents is `SUMMARY.md`. Key chapter-to-topic mapping:
 2. Edit `book/src/control-center.md`. Match field names, ordering, and
    conditional visibility exactly.
 
+### Adding a new book chapter
+
+1. Create the new `.md` file under `book/src/`.
+2. Add an entry in `book/src/SUMMARY.md` under the appropriate section.
+3. Update the chapter-to-topic mapping in this file and `AGENTS.md`.
+
 ## Building
 
 ```shell
diff --git a/book/CLAUDE.md b/book/CLAUDE.md
@@ -0,0 +1 @@
+AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
