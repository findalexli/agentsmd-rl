#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied
distinctive_line='if (isEqual(current, parent) || current.path'"'"'/'"'"' || isEqual(userHome, parent) || seen.has(parent))'
if grep -q "$distinctive_line" src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

echo "Applying fix for findParentRepoFolders infinite loop..."

git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts b/src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts
index f0a166cfa9159..74b474f82a026 100644
--- a/src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts
+++ b/src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts
@@ -111,8 +111,7 @@ export class PromptFilesLocator {
 	private async findParentRepoFolders(folderUri: URI, userHome: URI, seen: ResourceSet, logger?: Logger): Promise<URI[]> {
 		const candidates: URI[] = [];
 		let current = folderUri;
-		let parent = dirname(current);
-		do {
+		while (true) {
 			try {
 				const isRepoRoot = await this.fileService.exists(joinPath(current, '.git'));
 				if (isRepoRoot) {
@@ -129,9 +128,15 @@ export class PromptFilesLocator {
 				return []; // if we can't access the folder, return an empty list to avoid treating it as a non-repository when we might just have a permission issue
 			}
 			candidates.push(current);
+			const parent = dirname(current);
+			// Stop walking up when we reach a filesystem root (fixed-point
+			// of dirname, e.g. '/' or a Windows drive root like 'D:\'),
+			// the user home directory, or an already-seen folder.
+			if (isEqual(current, parent) || current.path === '/' || isEqual(userHome, parent) || seen.has(parent)) {
+				break;
+			}
 			current = parent;
-			parent = dirname(current);
-		} while (!seen.has(current) && current.path !== '/' && !isEqual(userHome, current));
+		}
 		// no repo found
 		logger?.logInfo(`No repository root found for folder ${folderUri.toString()}.`);
 		return [];
PATCH

echo "Patch applied successfully"
