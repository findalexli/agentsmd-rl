#!/bin/bash
set -e

cd /workspace/continue

# Apply the gold patch to fix config.yaml empty file handling
git apply <<'PATCH'
diff --git a/core/config/ConfigHandler.ts b/core/config/ConfigHandler.ts
index abc123..def456 100644
--- a/core/config/ConfigHandler.ts
+++ b/core/config/ConfigHandler.ts
@@ -10,6 +10,7 @@ import {
   ILLMLogger,
 } from "../index.js";
 import { GlobalContext } from "../util/GlobalContext.js";
+import { getConfigYamlPath } from "../util/paths.js";

 import EventEmitter from "node:events";
 import {
@@ -637,6 +638,7 @@ export class ConfigHandler {
     }

     if (profile.profileDescription.profileType === "local") {
+      getConfigYamlPath();
       const configFile = element?.sourceFile ?? profile.profileDescription.uri;
       await this.ide.openFile(configFile);
     } else {
diff --git a/core/util/paths.ts b/core/util/paths.ts
index 123abc..456def 100644
--- a/core/util/paths.ts
+++ b/core/util/paths.ts
@@ -118,15 +118,12 @@ export function getConfigJsonPath(): string {

 export function getConfigYamlPath(ideType?: IdeType): string {
   const p = path.join(getContinueGlobalPath(), "config.yaml");
-  if (!fs.existsSync(p) && !fs.existsSync(getConfigJsonPath())) {
-    if (ideType === "jetbrains") {
-      // https://github.com/continuedev/continue/pull/7224
-      // This was here because we had different context provider support between jetbrains and vs code
-      // Leaving so we could differentiate later but for now configs are the same between IDEs
-      fs.writeFileSync(p, YAML.stringify(defaultConfig));
-    } else {
-      fs.writeFileSync(p, YAML.stringify(defaultConfig));
-    }
+  const exists = fs.existsSync(p);
+  const isEmpty = exists && fs.readFileSync(p, "utf8").trim() === "";
+  const needsCreation = !exists && !fs.existsSync(getConfigJsonPath());
+
+  if (needsCreation || isEmpty) {
+    fs.writeFileSync(p, YAML.stringify(defaultConfig));
     setConfigFilePermissions(p);
   }
   return p;
PATCH

# Verify the patch was applied (idempotency check)
grep -q "const exists = fs.existsSync(p);" core/util/paths.ts
grep -q "const isEmpty = exists && fs.readFileSync(p, \"utf8\").trim() === \"\";" core/util/paths.ts
grep -q "const needsCreation = !exists && !fs.existsSync(getConfigJsonPath());" core/util/paths.ts
grep -q "getConfigYamlPath();" core/config/ConfigHandler.ts

echo "Patch applied successfully"