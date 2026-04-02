#!/usr/bin/env bash
set -euo pipefail

# Apply the fix for local history commands URI scheme handling

TARGET_FILE="src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts"

# Check if already applied (idempotency check)
if grep -q "LocalHistoryFileSystemProvider.SCHEMA" "$TARGET_FILE" 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts b/src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts
index 2666528ab8286..f8e6f72e9293e 100644
--- a/src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts
+++ b/src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts
@@ -655,7 +655,16 @@ export function toDiffEditorArguments(arg1: IWorkingCopyHistoryEntry, arg2: IWor
 }

 export async function findLocalHistoryEntry(workingCopyHistoryService: IWorkingCopyHistoryService, descriptor: ITimelineCommandArgument): Promise<{ entry: IWorkingCopyHistoryEntry | undefined; previous: IWorkingCopyHistoryEntry | undefined }> {
-	const entries = await workingCopyHistoryService.getEntries(descriptor.uri, CancellationToken.None);
+
+	// When the resource URI uses the `vscode-local-history` scheme (e.g.
+	// when triggered from the diff editor), map it back to the original
+	// file URI so that the history service can find matching entries.
+	let uri = descriptor.uri;
+	if (uri.scheme === LocalHistoryFileSystemProvider.SCHEMA) {
+		uri = LocalHistoryFileSystemProvider.fromLocalHistoryFileSystem(uri).associatedResource;
+	}
+
+	const entries = await workingCopyHistoryService.getEntries(uri, CancellationToken.None);

 	let currentEntry: IWorkingCopyHistoryEntry | undefined = undefined;
 	let previousEntry: IWorkingCopyHistoryEntry | undefined = undefined;
PATCH

echo "Patch applied successfully"
