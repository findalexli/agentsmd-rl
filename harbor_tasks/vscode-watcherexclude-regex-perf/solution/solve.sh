#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied - look for the specific comment added in the fix
if grep -q "Avoiding a '\*\*' pattern here which results in a very complex" src/vs/workbench/contrib/files/browser/files.contribution.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts b/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts
index 43deb1d4450ad..4ddd2c1d61b5d 100644
--- a/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts
+++ b/src/vs/sessions/contrib/configuration/browser/configuration.contribution.ts
@@ -28,12 +28,6 @@ Registry.as<IConfigurationRegistry>(Extensions.Configuration).registerDefaultCon
 		'extensions.ignoreRecommendations': true,

 		'files.autoSave': 'afterDelay',
-		'files.watcherExclude': {
-			'**/.git/objects/**': true,
-			'**/.git/subtree-cache/**': true,
-			'**/node_modules/*/**': true,
-			'**/.hg/store/**': true
-		},

 		'git.autofetch': true,
 		'git.branchRandomName.enable': true,
diff --git a/src/vs/workbench/contrib/files/browser/files.contribution.ts b/src/vs/workbench/contrib/files/browser/files.contribution.ts
index 8f36c834a3a71..c0b8db32da012 100644
--- a/src/vs/workbench/contrib/files/browser/files.contribution.ts
+++ b/src/vs/workbench/contrib/files/browser/files.contribution.ts
@@ -295,7 +295,16 @@ configurationRegistry.registerConfiguration({
 			'patternProperties': {
 				'.*': { 'type': 'boolean' }
 			},
-			'default': { '**/.git/objects/**': true, '**/.git/subtree-cache/**': true, '**/.hg/store/**': true },
+			'default': {
+				// Avoiding a '**' pattern here which results in a very complex
+				// RegExp that can slow things down significantly in large workspaces
+				'.git/objects/**': true,
+				'.git/subtree-cache/**': true,
+				'.hg/store/**': true,
+				'*/.git/objects/**': true,
+				'*/.git/subtree-cache/**': true,
+				'*/.hg/store/**': true
+			},
 			'markdownDescription': nls.localize('watcherExclude', "Configure paths or [glob patterns](https://aka.ms/vscode-glob-patterns) to exclude from file watching. Paths can either be relative to the watched folder or absolute. Glob patterns are matched relative from the watched folder. When you experience the file watcher process consuming a lot of CPU, make sure to exclude large folders that are of less interest (such as build output folders)."),
 			'scope': ConfigurationScope.RESOURCE
 		},
PATCH

echo "Patch applied successfully"
