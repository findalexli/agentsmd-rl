#!/bin/bash
set -euo pipefail

# Check if patch is already applied
if grep -q "hasGitRepositoryContextKey" src/vs/sessions/contrib/changes/browser/changesView.ts; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/changes/browser/changesView.ts b/src/vs/sessions/contrib/changes/browser/changesView.ts
index 5ece08cf7fa6c..31aae8247b9a3 100644
--- a/src/vs/sessions/contrib/changes/browser/changesView.ts
+++ b/src/vs/sessions/contrib/changes/browser/changesView.ts
@@ -108,6 +108,7 @@ const enum IsolationMode {
 const changesVersionModeContextKey = new RawContextKey<ChangesVersionMode>('sessions.changesVersionMode', ChangesVersionMode.BranchChanges);
 const isMergeBaseBranchProtectedContextKey = new RawContextKey<boolean>('sessions.isMergeBaseBranchProtected', false);
 const isolationModeContextKey = new RawContextKey<IsolationMode>('sessions.isolationMode', IsolationMode.Workspace);
+const hasGitRepositoryContextKey = new RawContextKey<boolean>('sessions.hasGitRepository', true);
 const hasPullRequestContextKey = new RawContextKey<boolean>('sessions.hasPullRequest', false);
 const hasOpenPullRequestContextKey = new RawContextKey<boolean>('sessions.hasOpenPullRequest', false);
 const hasIncomingChangesContextKey = new RawContextKey<boolean>('sessions.hasIncomingChanges', false);
@@ -265,6 +266,7 @@ class ChangesViewModel extends Disposable {
 	readonly activeSessionIsolationModeObs: IObservable<IsolationMode>;
 	readonly activeSessionRepositoryObs: IObservableWithChange<IGitRepository | undefined>;
 	readonly activeSessionChangesObs: IObservable<readonly (IChatSessionFileChange | IChatSessionFileChange2)[]>;
+	readonly activeSessionHasGitRepositoryObs: IObservable<boolean>;
 	readonly activeSessionFirstCheckpointRefObs: IObservable<string | undefined>;
 	readonly activeSessionLastCheckpointRefObs: IObservable<string | undefined>;

@@ -373,6 +375,19 @@ class ChangesViewModel extends Disposable {
 			: undefined;
 	});

+		// Active session has git repository
+		this.activeSessionHasGitRepositoryObs = derived(reader => {
+			const sessionResource = this.activeSessionResourceObs.read(reader);
+			if (!sessionResource) {
+				return false;
+			}
+
+			this.sessionsChangedSignal.read(reader);
+			const model = this.agentSessionsService.getSession(sessionResource);
+
+			return model?.metadata?.repositoryPath !== undefined;
+		});
+
 		// Active session first checkpoint ref
 		this.activeSessionFirstCheckpointRefObs = derived(reader => {
 			const sessionResource = this.activeSessionResourceObs.read(reader);
@@ -834,6 +849,10 @@ export class ChangesViewPane extends ViewPane {
 				return this.viewModel.activeSessionIsolationModeObs.read(reader);
 			}));

+			this.renderDisposables.add(bindContextKey(hasGitRepositoryContextKey, this.scopedContextKeyService, reader => {
+				return this.viewModel.activeSessionHasGitRepositoryObs.read(reader);
+			}));
+
 			this.renderDisposables.add(bindContextKey(isMergeBaseBranchProtectedContextKey, this.scopedContextKeyService, reader => {
 				const activeSession = this.sessionManagementService.activeSession.read(reader);
 				return activeSession?.workspace.read(reader)?.repositories[0]?.baseBranchProtected === true;
@@ -952,6 +971,9 @@ export class ChangesViewPane extends ViewPane {
 							if (action.id === 'github.copilot.sessions.commitChanges') {
 								return { showIcon: true, showLabel: true, isSecondary: false };
 							}
+							if (action.id === 'agentSession.markAsDone') {
+								return { showIcon: true, showLabel: true, isSecondary: false };
+							}

 							return undefined;
 						}
diff --git a/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts b/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
index c409f6a06d709..c688a3d4f19cf 100644
--- a/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
+++ b/src/vs/sessions/contrib/sessions/browser/views/sessionsViewActions.ts
@@ -14,7 +14,7 @@ import { IQuickInputService } from '../../../../../platform/quickinput/common/qu
 import { IStorageService, StorageScope, StorageTarget } from '../../../../../platform/storage/common/storage.js';
 import { KeybindingsRegistry, KeybindingWeight } from '../../../../../platform/keybinding/common/keybindingsRegistry.js';
 import { IViewsService } from '../../../../../workbench/services/views/common/viewsService.js';
-import { EditorsVisibleContext, IsAuxiliaryWindowContext } from '../../../../../workbench/common/contextkeys.js';
+import { EditorsVisibleContext, IsAuxiliaryWindowContext, IsSessionsWindowContext } from '../../../../../workbench/common/contextkeys.js';
 import { IChatWidgetService } from '../../../../../workbench/contrib/chat/browser/chat.js';
 import { AUX_WINDOW_GROUP } from '../../../../../workbench/services/editor/common/editorService.js';
 import { SessionsCategories } from '../../../../common/categories.js';
@@ -634,6 +634,16 @@ registerAction2(class MarkSessionAsDoneAction extends Action2 {
 				SessionsWelcomeVisibleContext.negate(),
 				IsNewChatSessionContext.negate()
 			)
+		},
+		{
+			id: MenuId.ChatEditingSessionChangesToolbar,
+			group: 'navigation',
+			order: 1,
+			when: ContextKeyExpr.and(
+				IsSessionsWindowContext,
+				ContextKeyExpr.equals('sessions.hasPullRequest', true),
+				ContextKeyExpr.equals('sessions.hasOpenPullRequest', false),
+			)
 		}]
 	});
 }
PATCH

echo "Patch applied successfully"
