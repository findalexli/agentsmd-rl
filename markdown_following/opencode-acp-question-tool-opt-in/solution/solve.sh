#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q 'OPENCODE_ENABLE_QUESTION_TOOL' packages/opencode/src/flag/flag.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply - <<'PATCH'
diff --git a/.opencode/agent/translator.md b/.opencode/agent/translator.md
index dec6fa6c4fc3..e2f2784e91fc 100644
--- a/.opencode/agent/translator.md
+++ b/.opencode/agent/translator.md
@@ -598,6 +598,7 @@ OPENCODE_EXPERIMENTAL_MARKDOWN
 OPENCODE_EXPERIMENTAL_OUTPUT_TOKEN_MAX
 OPENCODE_EXPERIMENTAL_OXFMT
 OPENCODE_EXPERIMENTAL_PLAN_MODE
+OPENCODE_ENABLE_QUESTION_TOOL
 OPENCODE_FAKE_VCS
 OPENCODE_GIT_BASH_PATH
 OPENCODE_MODEL
diff --git a/packages/opencode/src/acp/README.md b/packages/opencode/src/acp/README.md
index d998cb22da8d..aab33259bb18 100644
--- a/packages/opencode/src/acp/README.md
+++ b/packages/opencode/src/acp/README.md
@@ -44,6 +44,16 @@ opencode acp
 opencode acp --cwd /path/to/project
 ```

+### Question Tool Opt-In
+
+ACP excludes `QuestionTool` by default.
+
+```bash
+OPENCODE_ENABLE_QUESTION_TOOL=1 opencode acp
+```
+
+Enable this only for ACP clients that support interactive question prompts.
+
 ### Programmatic

 ```typescript
diff --git a/packages/opencode/src/flag/flag.ts b/packages/opencode/src/flag/flag.ts
index dfcb88bc51a5..4c7c716d095 100644
--- a/packages/opencode/src/flag/flag.ts
+++ b/packages/opencode/src/flag/flag.ts
@@ -30,6 +30,7 @@ export namespace Flag {
   export declare const OPENCODE_CLIENT: string
   export const OPENCODE_SERVER_PASSWORD = process.env["OPENCODE_SERVER_PASSWORD"]
   export const OPENCODE_SERVER_USERNAME = process.env["OPENCODE_SERVER_USERNAME"]
+  export const OPENCODE_ENABLE_QUESTION_TOOL = truthy("OPENCODE_ENABLE_QUESTION_TOOL")

   // Experimental
   export const OPENCODE_EXPERIMENTAL = truthy("OPENCODE_EXPERIMENTAL")
diff --git a/packages/opencode/src/tool/registry.ts b/packages/opencode/src/tool/registry.ts
index 9a06cb59937b..3ff9cce8990f 100644
--- a/packages/opencode/src/tool/registry.ts
+++ b/packages/opencode/src/tool/registry.ts
@@ -94,10 +94,11 @@ export namespace ToolRegistry {
   async function all(): Promise<Tool.Info[]> {
     const custom = await state().then((x) => x.custom)
     const config = await Config.get()
+    const question = ["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) || Flag.OPENCODE_ENABLE_QUESTION_TOOL

     return [
       InvalidTool,
-      ...(["app", "cli", "desktop"].includes(Flag.OPENCODE_CLIENT) ? [QuestionTool] : []),
+      ...(question ? [QuestionTool] : []),
       BashTool,
       ReadTool,
       GlobTool,

PATCH

echo "Patch applied successfully."
