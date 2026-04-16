#!/bin/bash
set -e

cd /workspace/router

# Idempotency check: if distinctive line already exists, skip patching
if grep -q "yargs(hideBin(process.argv))" packages/router-cli/src/index.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
From e5d23ecd5c28aa592100e7344b408d67fd261c61 Mon Sep 17 00:00:00 2001
From: Birk Skyum <74932975+birkskyum@users.noreply.github.com>
Date: Thu, 19 Mar 2026 14:49:29 +0100
Subject: [PATCH] fix(router-cli): pass process.argv to yargs to fix silent CLI
 failure (#6981)

---
 .changeset/eighty-chairs-write.md | 5 +++++
 packages/router-cli/src/index.ts  | 3 ++-
 2 files changed, 7 insertions(+), 1 deletion(-)
 create mode 100644 .changeset/eighty-chairs-write.md

diff --git a/.changeset/eighty-chairs-write.md b/.changeset/eighty-chairs-write.md
new file mode 100644
index 00000000000..d2332f78518
--- /dev/null
+++ b/.changeset/eighty-chairs-write.md
@@ -0,0 +1,5 @@
+---
+'@tanstack/router-cli': patch
+---
+
+fix(router-cli): pass process.argv to yargs to fix silent CLI failure
diff --git a/packages/router-cli/src/index.ts b/packages/router-cli/src/index.ts
index c164f4f8800..eca5a9ff0ef 100644
--- a/packages/router-cli/src/index.ts
+++ b/packages/router-cli/src/index.ts
@@ -1,4 +1,5 @@
 import yargs from 'yargs'
+import { hideBin } from 'yargs/helpers'
 import { getConfig } from '@tanstack/router-generator'
 import { generate } from './generate'
 import { watch } from './watch'
@@ -6,7 +7,7 @@ import { watch } from './watch'
 main()

 export function main() {
-  yargs()
+  yargs(hideBin(process.argv))
     .scriptName('tsr')
     .usage('$0 <cmd> [args]')
     .command('generate', 'Generate the routes for a project', async () => {
PATCH

echo "Patch applied successfully"

# Rebuild the affected package
pnpm nx run @tanstack/router-cli:build

echo "Build completed"
