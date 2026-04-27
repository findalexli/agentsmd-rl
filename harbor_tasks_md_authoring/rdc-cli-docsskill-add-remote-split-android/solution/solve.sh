#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rdc-cli

# Idempotency guard
if grep -qF "Always run `rdc doctor` first. It reports status for renderdoc module, renderdoc" "src/rdc/_skills/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/src/rdc/_skills/SKILL.md b/src/rdc/_skills/SKILL.md
@@ -20,7 +20,11 @@ Check setup: `rdc doctor`.
 
 Follow this session lifecycle for any capture analysis task:
 
-1. **Open** a capture: `rdc open path/to/capture.rdc`
+1. **Open** a capture:
+   - Local: `rdc open path/to/capture.rdc`
+   - Remote replay (Proxy): `rdc open capture.rdc --proxy host:port`
+   - Split thin-client: `rdc open --connect host:port --token TOKEN`
+   - Android device: `rdc open capture.rdc --android [--serial SERIAL]`
 2. **Inspect** metadata: `rdc info`, `rdc stats`, `rdc events`
 3. **Navigate** the VFS: `rdc ls /`, `rdc ls /textures`, `rdc cat /pipelines/0`
 4. **Analyze** specifics: `rdc shaders`, `rdc pipeline`, `rdc resources`, `rdc bindings`
@@ -196,6 +200,54 @@ rdc shader-restore EID            # revert single shader
 rdc shader-restore-all            # revert all modifications
 ```
 
+## Remote Capture Workflow
+
+rdc-cli wraps `renderdoccmd remoteserver` to support PC-to-PC remote captures.
+
+- `rdc serve [--port PORT] [--allow-ips CIDR] [--no-exec] [--daemon]` — launch remoteserver on the target machine
+- `rdc remote connect <host:port>` — save remote connection state
+- `rdc remote list` — enumerate capturable apps on the remote
+- `rdc remote capture <app> -o frame.rdc [--args ...] [--frame N] [--keep-remote]` — inject, capture, and transfer back. `--keep-remote` skips the transfer and prints the remote path; replay it with `rdc open <path> --proxy host:port`. (The CLI's own `next:` hint currently still references the deprecated `--remote` alias for `--proxy`.)
+- `rdc open frame.rdc --proxy host:port` — remote-backed replay (daemon local, GPU remote)
+
+`remote_state.py` persists the last connected host so subsequent `rdc remote list` can omit `--url`.
+
+## Split Mode (thin client)
+
+Split mode decouples CLI and daemon — run the daemon where the GPU is and connect from a machine that doesn't need the renderdoc module. Useful when the analyst's laptop is macOS/Windows and the GPU is on a Linux server.
+
+- Server side: `rdc open capture.rdc --listen [ADDR[:PORT]]`
+  - Prints these four labeled lines to stdout (among other status output): `host: ADDR`, `port: PORT`, `token: TOKEN`, `connect with: rdc open --connect ADDR:PORT --token TOKEN`
+- Client side: `rdc open --connect HOST:PORT --token TOKEN`
+
+SSH tunnel tip (use the port from `--listen`, or `rdc serve`'s default `39920`): `ssh -L 39920:localhost:39920 user@server`, then connect to `localhost:39920`.
+
+Every normal command (`rdc draws`, `rdc rt`, ...) works transparently in Split mode. Binary exports use `file_read` RPC with raw binary frames — no base64 overhead.
+
+## Android Workflow
+
+- Prerequisite: the RenderDoc APK must already be installed on the host via `rdc setup-renderdoc --android` (upstream) or `--android --arm` (ARM PS fork for Mali). `rdc android setup` does not push the APK itself.
+- `rdc android setup [--serial SERIAL]` — starts remoteserver on the device via RenderDoc's Device Protocol API (`StartRemoteServer`), sets adb forward, saves remote state.
+- `rdc android capture <activity> [--serial SERIAL] [--timeout N] [--port PORT] [-o out.rdc]` — GPU debug layers based capture (works around EMUI/Mali injection limitations).
+- `rdc android stop [--serial SERIAL]` — stops the remoteserver and cleans state.
+- For remote replay: `rdc open frame.rdc --android [--serial SERIAL]` — this is the only form that rewrites the saved `adb://SERIAL` to the forwarded `localhost:PORT`. Passing `--proxy adb://SERIAL` directly bypasses the rewrite and is known to crash the daemon (see `session.py:_resolve_android_url`).
+
+Hardware matrix: Adreno is the happy path; Mali may need the ARM Performance Studio fork (see `rdc setup-renderdoc --android --arm`).
+
+## Troubleshooting
+
+Always run `rdc doctor` first. It reports status for renderdoc module, renderdoccmd, adb, Android APK, and platform-specific toolchains. Only the missing-renderdoc-module case emits a dedicated build-hint block; other checks surface inline hints in the detail column, so read each failing line rather than relying on a uniform next-step list.
+
+Common failure categories (conceptual, not literal error strings — map from the text the tool actually emits):
+
+- **network / connect failed** — remote host unreachable, firewall, wrong port. Verify `rdc serve` is running on the target.
+- **version mismatch** — host and target RenderDoc versions differ. Re-run `rdc setup-renderdoc` or `rdc setup-renderdoc --android` to align.
+- **inject failed / ident=0** — injection blocked (Android EMUI, macOS SIP, Windows privilege). Run `rdc doctor` and check the platform-specific detail.
+- **OpenCapture unsupported** — local GPU can't replay the capture's API surface; switch to `--proxy` or `--android` remote replay.
+- **not loaded / no session** — forgot `rdc open`; use `rdc status` to inspect.
+
+For long operations (large capture transfers, remote replay init), the CLI has limited progress feedback — this is a known UX gap, not a hang. Wait up to the `--timeout` value before concluding failure.
+
 ## Command Reference
 
 For the complete list of all commands with their arguments, options, types, and defaults, see [references/commands-quick-ref.md](references/commands-quick-ref.md).
PATCH

echo "Gold patch applied."
