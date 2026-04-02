#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if patch already applied
check_file="src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts"
if grep -q "delegate.getHeight(session)" "${check_file}"; then
    echo "Patch already applied"
    exit 0
fi

# Apply the fix
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
index 1c5f706c7c734..4f630e2fc1546 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsList.ts
@@ -689,11 +689,13 @@ export class SessionsList extends Disposable implements ISessionsList {

 		const showMoreRenderer = new SessionShowMoreRenderer();

+		const delegate = new SessionsTreeDelegate(approvalModel);
+
 		this.tree = this._register(instantiationService.createInstance(
 			WorkbenchObjectTree<SessionListItem, FuzzyScore>,
 			'SessionsListTree',
 			this.listContainer,
-			new SessionsTreeDelegate(approvalModel),
+			delegate,
 			[
 				sessionRenderer,
 				new SessionSectionRenderer(true /* hideSectionCount */, instantiationService, contextKeyService),
@@ -751,7 +753,7 @@ export class SessionsList extends Disposable implements ISessionsList {

 		this._register(sessionRenderer.onDidChangeItemHeight(session => {
 			if (this.tree.hasElement(session)) {
-				this.tree.updateElementHeight(session, undefined);
+				this.tree.updateElementHeight(session, delegate.getHeight(session));
 			}
 		}));
 PATCH

echo "Patch applied successfully"
