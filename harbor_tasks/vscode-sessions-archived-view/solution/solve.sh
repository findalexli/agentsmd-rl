#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied
if grep -q "_activeSessionDisposables = this._register(new DisposableStore())" src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts b/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts
index 76fa40d2767e8..aa03bb62d53cb 100644
--- a/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts
+++ b/src/vs/sessions/contrib/sessions/browser/sessionsManagementService.ts
@@ -4,8 +4,8 @@
  *--------------------------------------------------------------------------------------------*/

 import { Emitter, Event } from '../../../../base/common/event.js';
-import { Disposable } from '../../../../base/common/lifecycle.js';
-import { IObservable, IReader, observableFromEvent, observableValue } from '../../../../base/common/observable.js';
+import { Disposable, DisposableStore } from '../../../../base/common/lifecycle.js';
+import { IObservable, IReader, autorun, observableFromEvent, observableValue } from '../../../../base/common/observable.js';
 import { URI } from '../../../../base/common/uri.js';
 import { localize } from '../../../../nls.js';
 import { createDecorator } from '../../../../platform/instantiation/common/instantiation.js';
@@ -243,6 +243,7 @@ export class SessionsManagementService extends Disposable implements ISessionsMa
 	private readonly _isBackgroundProvider: IContextKey<boolean>;
 	private readonly _groupModel: SessionsGroupModel;
 	private readonly _sessionDataCache = new Map<string, ISession>();
+	private _activeSessionDisposables = this._register(new DisposableStore());

 	constructor(
 		@IStorageService private readonly storageService: IStorageService,
@@ -394,24 +395,6 @@ export class SessionsManagementService extends Disposable implements ISessionsMa
 				return;
 			}
 		}
-
-		if (e.changed.length) {
-			const updated = e.changed.find(s => currentActive.chats.get().find(c => c.chatId === s.id));
-			if (updated?.isArchived.get()) {
-				// Only open new session view if all chats in the group are archived
-				const groupId = this._groupModel.getSessionIdForChat(currentActive.sessionId);
-				const chatIds = groupId ? this._groupModel.getChatIds(groupId) : [];
-				const allChats = this.sessionsProvidersService.getSessions();
-				const allArchived = chatIds.length === 0 || chatIds.every(id => {
-					const chat = allChats.find(c => c.id === id);
-					return !chat || chat.isArchived.get();
-				});
-				if (allArchived) {
-					this.openNewSessionView();
-				}
-				return;
-			}
-		}
 	}

 	getSessions(): ISession[] {
@@ -609,6 +592,10 @@ export class SessionsManagementService extends Disposable implements ISessionsMa
 	}

 	private setActiveSession(session: ISession | undefined): void {
+		if (this._activeSession.get()?.sessionId === session?.sessionId) {
+			return;
+		}
+
 		// Update context keys from session data
 		this._activeSessionProviderId.set(session?.providerId ?? '');
 		this._activeSessionType.set(session?.sessionType ?? '');
@@ -625,6 +612,16 @@ export class SessionsManagementService extends Disposable implements ISessionsMa
 		}

 		this._activeSession.set(session, undefined);
+
+		this._activeSessionDisposables.clear();
+		// Listen for the active session becoming archived
+		if (session && !session.isArchived.get()) {
+			this._activeSessionDisposables.add(autorun(reader => {
+				if (session.isArchived.read(reader)) {
+					this.openNewSessionView();
+				}
+			}));
+		}
 	}

 	/**
PATCH

echo "Patch applied successfully"
