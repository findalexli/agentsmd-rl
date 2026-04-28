#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ghostty

# Idempotency guard
if grep -qF "- **Test filter (Zig)**: `zig build test -Dtest-filter=<test name>`" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,23 @@
+# Agent Development Guide
+
+A file for [guiding coding agents](https://agents.md/).
+
+## Commands
+
+- **Build:** `zig build`
+- **Test (Zig):** `zig build test`
+- **Test filter (Zig)**: `zig build test -Dtest-filter=<test name>`
+- **Formatting (Zig)**: `zig fmt .`
+- **Formatting (other)**: `prettier -w .`
+
+## Directory Structure
+
+- Shared Zig core: `src/`
+- C API: `include/ghostty.h`
+- macOS app: `macos/`
+- GTK (Linux and FreeBSD) app: `src/apprt/gtk-ng`
+
+## macOS App
+
+- Do not use `xcodebuild`
+- Use `zig build` to build the macOS app and any shared Zig code
PATCH

echo "Gold patch applied."
