#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency check)
if grep -q "workspaceGroupCappedContextKey: IContextKey<boolean>" src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix for IsWorkspaceGroupCappedContext synchronization
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts
index a92f893eb35ed..1d84b792353e1 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsView.ts
@@ -53,6 +53,7 @@ export class SessionsView extends ViewPane {
 	private currentSorting: SessionsSorting = SessionsSorting.Created;
 	private groupingContextKey: IContextKey | undefined;
 	private sortingContextKey: IContextKey | undefined;
+	private workspaceGroupCappedContextKey: IContextKey<boolean> | undefined;
 	private readonly filterContextKeys = new Map<string, { key: IContextKey<boolean>; getDefault: () => boolean }>();

 	constructor(
@@ -89,6 +90,9 @@ export class SessionsView extends ViewPane {
 		this.groupingContextKey.set(this.currentGrouping);
 		this.sortingContextKey = SessionsViewSortingContext.bindTo(contextKeyService);
 		this.sortingContextKey.set(this.currentSorting);
+
+		// Bind workspace group capped context key (will be synced with persisted state in renderBody)
+		this.workspaceGroupCappedContextKey = IsWorkspaceGroupCappedContext.bindTo(contextKeyService);
 	}

 	protected override renderBody(parent: HTMLElement): void {
@@ -187,6 +191,9 @@ export class SessionsView extends ViewPane {
 		})); this._register(this.onDidChangeBodyVisibility(visible => sessionsControl.setVisible(visible)));
+		// Sync workspace group capped context key with persisted state
+		this.workspaceGroupCappedContextKey?.set(sessionsControl.isWorkspaceGroupCapped());
+
 		// Register session type filter actions (re-register when session types change)
 		this.registerSessionTypeFilters(sessionsControl);
 		this._register(this.sessionsManagementService.onDidChangeSessionTypes(() => {
@@ -365,6 +372,7 @@ export class SessionsView extends ViewPane {

 		// Reset filter action
 		const filterContextKeys = this.filterContextKeys;
+		const workspaceGroupCappedContextKey = this.workspaceGroupCappedContextKey;
 		this._register(registerAction2(class extends Action2 {
 			constructor() {
 				super({
@@ -382,6 +390,7 @@ export class SessionsView extends ViewPane {
 				for (const { key, getDefault } of filterContextKeys.values()) {
 					key.set(getDefault());
 				}
+				workspaceGroupCappedContextKey?.set(sessionsControl.isWorkspaceGroupCapped());
 			}
 		}));
 	}
PATCH

echo "Patch applied successfully"
