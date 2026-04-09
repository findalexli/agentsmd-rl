#!/usr/bin/env bash
set -euo pipefail

cd /workspace/next.js

# Idempotent: skip if already applied
if grep -q "os.cpus().some" packages/next/src/bin/next.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/packages/next/src/bin/next.ts b/packages/next/src/bin/next.ts
index ecd0456ab628f8..781d7b303630eb 100755
--- a/packages/next/src/bin/next.ts
+++ b/packages/next/src/bin/next.ts
@@ -2,6 +2,7 @@

 import '../server/require-hook'

+import os from 'os'
 import {
   Argument,
   Command,
@@ -89,6 +90,16 @@ class NextRootCommand extends Command {
       ;(process.env as any).NODE_ENV = process.env.NODE_ENV || defaultEnv
       ;(process.env as any).NEXT_RUNTIME = 'nodejs'

+      if (
+        process.platform === 'darwin' &&
+        process.arch === 'x64' &&
+        os.cpus().some((cpu) => cpu.model.includes('Apple'))
+      ) {
+        warn(
+          'You are running Next.js on an Apple Silicon Mac with Rosetta 2 translation, which may cause degraded performance.'
+        )
+      }
+
       if (
         commandName !== 'dev' &&
         commandName !== 'start' &&

PATCH

echo "Patch applied successfully."
