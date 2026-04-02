#!/bin/bash
set -euo pipefail

# Apply the gold patch to add the Sessions Window chat tip

FILE="src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts"

# Idempotency check: check if the tip.openSessionsWindow entry already exists
if grep -q "tip.openSessionsWindow" "$FILE"; then
    echo "Patch already applied (tip.openSessionsWindow found)"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts b/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts
index f424b4692e747..0134980d2c068 100644
--- a/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts
+++ b/src/vs/workbench/contrib/chat/browser/chatTipCatalog.ts
@@ -8,8 +8,10 @@ import { localize } from '../../../../nls.js';
 import { ContextKeyExpr, ContextKeyExpression } from '../../../../platform/contextkey/common/contextkey.js';
 import { IKeybindingService } from '../../../../platform/keybinding/common/keybinding.js';
 import { MenuRegistry } from '../../../../platform/actions/common/actions.js';
+import { ProductQualityContext } from '../../../../platform/contextkey/common/contextkeys.js';
 import { ChatContextKeys } from '../common/actions/chatContextKeys.js';
 import { ChatConfiguration, ChatModeKind } from '../common/constants.js';
+import { IsSessionsWindowContext } from '../../../common/contextkeys.js';
 import { localChatSessionType } from '../common/chatSessionsService.js';
 import { ITipExclusionConfig } from './chatTipEligibilityTracker.js';
 import { TipTrackingCommands } from './chatTipStorageKeys.js';
@@ -410,4 +412,23 @@ export const TIP_CATALOG: readonly ITipDefinition[] = [
 		when: ChatContextKeys.chatSessionType.isEqualTo(localChatSessionType),
 		excludeWhenToolsInvoked: ['listDebugEvents'],
 	},
+	{
+		id: 'tip.openSessionsWindow',
+		tier: ChatTipTier.Qol,
+		buildMessage() {
+			return new MarkdownString(
+				localize(
+					'tip.openSessionsWindow',
+					"Try the [Sessions Window](command:workbench.action.openSessionsWindow \"Open Sessions Window\") to run multiple agents simultaneously and manage your coding sessions."
+				)
+			);
+		},
+		when: ContextKeyExpr.and(
+			ProductQualityContext.notEqualsTo('stable'),
+			IsSessionsWindowContext.negate(),
+			ChatContextKeys.chatModeKind.isEqualTo(ChatModeKind.Agent),
+		),
+		excludeWhenCommandsExecuted: ['workbench.action.openSessionsWindow'],
+		dismissWhenCommandsClicked: ['workbench.action.openSessionsWindow'],
+	},
 ];
PATCH

echo "Gold patch applied successfully"
