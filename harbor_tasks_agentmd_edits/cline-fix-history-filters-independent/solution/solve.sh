#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cline

# Idempotent: skip if already applied
if grep -q 'marginTop: -8' webview-ui/src/components/history/HistoryView.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 4e941e0709f..c898cbf1ca9 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -14,6 +14,9 @@ This file is the secret sauce for working effectively in this codebase. It captu

 **What NOT to add:** Stuff you can figure out from reading a few files, obvious patterns, or standard practices. This file should be high-signal, not comprehensive.

+## Miscellaneous
+- This is a VS Code extension—check `package.json` for available scripts before trying to verify builds (e.g., `npm run compile`, not `npm run build`).
+
 ## gRPC/Protobuf Communication
 The extension and webview communicate via gRPC-like protocol over VS Code message passing.

diff --git a/webview-ui/src/components/history/HistoryView.tsx b/webview-ui/src/components/history/HistoryView.tsx
index 97d57186ce5..b41ef613c1e 100644
--- a/webview-ui/src/components/history/HistoryView.tsx
+++ b/webview-ui/src/components/history/HistoryView.tsx
@@ -334,6 +334,8 @@ const HistoryView = ({ onDone }: HistoryViewProps) => {
 							<VSCodeRadio disabled={!searchQuery} style={{ opacity: searchQuery ? 1 : 0.5 }} value="mostRelevant">
 								Most Relevant
 							</VSCodeRadio>
+						</VSCodeRadioGroup>
+						<div className="flex flex-wrap" style={{ marginTop: -8 }}>
 							<VSCodeRadio
 								checked={showCurrentWorkspaceOnly}
 								onClick={() => setShowCurrentWorkspaceOnly(!showCurrentWorkspaceOnly)}>
@@ -342,13 +344,15 @@ const HistoryView = ({ onDone }: HistoryViewProps) => {
 									Workspace
 								</span>
 							</VSCodeRadio>
-							<VSCodeRadio checked={showFavoritesOnly} onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}>
+							<VSCodeRadio
+								checked={showFavoritesOnly}
+								onClick={() => setShowFavoritesOnly(!showFavoritesOnly)}>
 								<span className="flex items-center gap-[3px]">
 									<span className="codicon codicon-star-full text-(--vscode-button-background)" />
 									Favorites
 								</span>
 							</VSCodeRadio>
-						</VSCodeRadioGroup>
+						</div>
 						</div>
 				</div>
 				<div style={{ flexGrow: 1, overflowY: "auto", margin: 0 }}>

PATCH

echo "Patch applied successfully."
