#!/usr/bin/env bash
set -euo pipefail

cd /workspace/detekt

# Idempotency guard
if grep -qF "- Android SDK must be installed to execute certain tests. They will be skipped i" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -14,8 +14,10 @@ This document provides guidance for AI coding agents (Claude, Codex, Copilot, et
 ## Development Environment
 
 ### Prerequisites
-- JDK 11+ (JDK 17+ recommended)
-- Gradle (wrapper included)
+- JDK 17+ required for the build
+  - Note that some detekt-gradle-plugin tests only run on JDK 19 or lower
+  - JDK 17 must be available for build-logic JVM toolchain
+- Android SDK must be installed to execute certain tests. They will be skipped if the SDK is not installed. This is only an issue if making changes to detekt-gradle-plugin.
 
 ### Initial Setup
 ```bash
PATCH

echo "Gold patch applied."
