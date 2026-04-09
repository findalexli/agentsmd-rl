#!/bin/bash
set -e

cd /workspace/continue

# Apply the gold patch from PR #11915
patch -p1 <<'PATCH'
diff --git a/core/config/ConfigHandler.ts b/core/config/ConfigHandler.ts
index 336c4b40bf1..0b20f557b04 100644
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
index 122ec2f94f6..323697f774c 100644
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

# Idempotency check: verify the distinctive line was added
grep -q "const isEmpty = exists && fs.readFileSync(p, \"utf8\").trim() === \"\";" core/util/paths.ts
echo "Patch applied successfully"
