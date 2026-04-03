#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if grep -q 'inferStorageFromUri' src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/skills/chat-customizations-editor/SKILL.md b/.github/skills/chat-customizations-editor/SKILL.md
index 8d4ce8edda10a..ed3cf72b74193 100644
--- a/.github/skills/chat-customizations-editor/SKILL.md
+++ b/.github/skills/chat-customizations-editor/SKILL.md
@@ -27,9 +27,24 @@ When changing harness descriptor interfaces or factory functions, verify both co
 - **`IHarnessDescriptor`** — drives all UI behavior declaratively (hidden sections, button overrides, file filters, agent gating). See spec for full field reference.
 - **`ISectionOverride`** — per-section button customization (command invocation, root file creation, type labels, file extensions).
 - **`IStorageSourceFilter`** — controls which storage sources and user roots are visible per harness/type.
+- **`IExternalCustomizationItemProvider`** / **`IExternalCustomizationItem`** — internal interfaces (in `customizationHarnessService.ts`) for extension-contributed providers that supply items directly. These mirror the proposed extension API types.

 Principle: the UI widgets read everything from the descriptor — no harness-specific conditionals in widget code.

+## Extension API (`chatSessionCustomizationProvider`)
+
+The proposed API in `src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts` lets extensions register customization providers. Changes to `IExternalCustomizationItem` or `IExternalCustomizationItemProvider` must be kept in sync across the full chain:
+
+| Layer | File | Type |
+|-------|------|------|
+| Extension API | `vscode.proposed.chatSessionCustomizationProvider.d.ts` | `ChatSessionCustomizationItem` |
+| IPC DTO | `extHost.protocol.ts` | `IChatSessionCustomizationItemDto` |
+| ExtHost mapping | `extHostChatAgents2.ts` | `$provideChatSessionCustomizations()` |
+| MainThread mapping | `mainThreadChatAgents2.ts` | `provideChatSessionCustomizations` callback |
+| Internal interface | `customizationHarnessService.ts` | `IExternalCustomizationItem` |
+
+When adding fields to `IExternalCustomizationItem`, update all five layers. The proposed API `.d.ts` is additive-only (new optional fields are backward-compatible and do not require a version bump).
+
 ## Testing

 Component explorer fixtures (see `component-fixtures` skill): `aiCustomizationListWidget.fixture.ts`, `aiCustomizationManagementEditor.fixture.ts` under `src/vs/workbench/test/browser/componentFixtures/`.
diff --git a/src/vs/workbench/api/browser/mainThreadChatAgents2.ts b/src/vs/workbench/api/browser/mainThreadChatAgents2.ts
index 4aaba46c6915b..a015f5e970e33 100644
--- a/src/vs/workbench/api/browser/mainThreadChatAgents2.ts
+++ b/src/vs/workbench/api/browser/mainThreadChatAgents2.ts
@@ -632,6 +632,9 @@ export class MainThreadChatAgents2 extends Disposable implements MainThreadChatA
 					type: item.type,
 					name: item.name,
 					description: item.description,
+					groupKey: item.groupKey,
+					badge: item.badge,
+					badgeTooltip: item.badgeTooltip,
 				}));
 			},
 		};
diff --git a/src/vs/workbench/api/common/extHost.protocol.ts b/src/vs/workbench/api/common/extHost.protocol.ts
index 97241cabb6766..196e042372fd6 100644
--- a/src/vs/workbench/api/common/extHost.protocol.ts
+++ b/src/vs/workbench/api/common/extHost.protocol.ts
@@ -1690,6 +1690,9 @@ export interface IChatSessionCustomizationItemDto {
 	readonly type: string;
 	readonly name: string;
 	readonly description?: string;
+	readonly groupKey?: string;
+	readonly badge?: string;
+	readonly badgeTooltip?: string;
 }
 export interface IChatParticipantMetadata {
 	participant: string;
diff --git a/src/vs/workbench/api/common/extHostChatAgents2.ts b/src/vs/workbench/api/common/extHostChatAgents2.ts
index 9e7ac0fb7d3af..a3f5fa5619f5b 100644
--- a/src/vs/workbench/api/common/extHostChatAgents2.ts
+++ b/src/vs/workbench/api/common/extHostChatAgents2.ts
@@ -710,6 +710,9 @@ export class ExtHostChatAgents2 extends Disposable implements ExtHostChatAgentsS
 				type: typeConvert.ChatSessionCustomizationType.from(item.type),
 				name: item.name,
 				description: item.description,
+				groupKey: item.groupKey,
+				badge: item.badge,
+				badgeTooltip: item.badgeTooltip,
 			}));
 		} catch (err) {
 			return undefined;
diff --git a/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts b/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts
index 9f7c9b7a9ee72..3c9b1699a7eb9 100644
--- a/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts
+++ b/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts
@@ -59,6 +59,7 @@ import { isInClaudeRulesFolder, getCleanPromptName } from '../../common/promptSy
 import { ExtensionIdentifier } from '../../../../../platform/extensions/common/extensions.js';
 import { ICommandService } from '../../../../../platform/commands/common/commands.js';
 import { IProductService } from '../../../../../platform/product/common/productService.js';
+import { IUserDataProfileService } from '../../../../services/userDataProfile/common/userDataProfile.js';

 export { truncateToFirstLine } from './aiCustomizationListWidgetUtils.js';

@@ -556,6 +557,7 @@ export class AICustomizationListWidget extends Disposable {
 		@IAgentPluginService private readonly agentPluginService: IAgentPluginService,
 		@ICommandService private readonly commandService: ICommandService,
 		@IProductService private readonly productService: IProductService,
+		@IUserDataProfileService private readonly userDataProfileService: IUserDataProfileService,
 	) {
 		super();
 		this.element = $('.ai-customization-list-widget');
@@ -1546,18 +1548,56 @@ export class AICustomizationListWidget extends Disposable {

 		return allItems
 			.filter(item => item.type === promptType)
-			.map((item: IExternalCustomizationItem) => ({
-				id: item.uri.toString(),
-				uri: item.uri,
-				name: item.name,
-				filename: basename(item.uri),
-				description: item.description,
-				promptType,
-				disabled: false,
-			}))
+			.map((item: IExternalCustomizationItem) => {
+				const pluginUri = this.findPluginUri(item.uri);
+				const storage = pluginUri ? PromptsStorage.plugin : this.inferStorageFromUri(item.uri);
+
+				return {
+					id: item.uri.toString(),
+					uri: item.uri,
+					name: item.name,
+					filename: basename(item.uri),
+					description: item.description,
+					promptType,
+					disabled: false,
+					groupKey: item.groupKey,
+					badge: item.badge,
+					badgeTooltip: item.badgeTooltip,
+					storage,
+					pluginUri,
+				};
+			})
 			.sort((a, b) => a.name.localeCompare(b.name));
 	}

+	/**
+	 * Infers the storage source of a URI by checking workspace folders,
+	 * user data paths, and plugin locations.
+	 */
+	private inferStorageFromUri(uri: URI): PromptsStorage {
+		// Check if under a workspace folder
+		if (this.workspaceContextService.getWorkspaceFolder(uri)) {
+			return PromptsStorage.local;
+		}
+
+		// Check if under the active project root (Sessions window may use
+		// an active root that is not a workspace folder, e.g. worktree/repo)
+		const activeProjectRoot = this.workspaceService.getActiveProjectRoot();
+		if (activeProjectRoot && isEqualOrParent(uri, activeProjectRoot)) {
+			return PromptsStorage.local;
+		}
+
+		// Check if under user data prompts home
+		const promptsHome = this.userDataProfileService.currentProfile.promptsHome;
+		if (isEqualOrParent(uri, promptsHome)) {
+			return PromptsStorage.user;
+		}
+
+		// Default to user for remaining files (e.g. user-scoped files
+		// outside the recognized prompts home)
+		return PromptsStorage.user;
+	}
+
 	/**
 	 * Derives a friendly name from a filename by removing extension suffixes.
 	 */
@@ -1608,16 +1648,78 @@ export class AICustomizationListWidget extends Disposable {
 			}
 		}

-		// When items come from an external provider, skip storage-based grouping
-		// and render a flat list. The provider controls the full item set, so
-		// Workspace/User/Extension categories don't apply.
+		// When items come from an external provider, group by groupKey if
+		// any items define one; otherwise fall through to standard
+		// storage-based grouping (storage is auto-inferred from URI).
 		const activeDescriptor = this.harnessService.getActiveDescriptor();
 		if (activeDescriptor.itemProvider) {
-			matchedItems.sort((a, b) => a.name.localeCompare(b.name));
-			this.displayEntries = matchedItems.map(item => ({ type: 'file-item' as const, item }));
-			this.list.splice(0, this.list.length, this.displayEntries);
-			this.updateEmptyState();
-			return matchedItems.length;
+			const hasExplicitGroups = matchedItems.some(item => item.groupKey !== undefined);
+			if (hasExplicitGroups) {
+				// Auto-build group definitions from the items' groupKey values,
+				// preserving insertion order. Items without a groupKey are
+				// placed into a fallback "Other" group. Uses a Map for O(1)
+				// lookups instead of repeated array scans.
+				const ungroupedKey = '__ungrouped__';
+				const groupsMap = new Map<string, { groupKey: string; label: string; icon: ThemeIcon; description: string; items: IAICustomizationListItem[] }>();
+
+				for (const item of matchedItems) {
+					const key = item.groupKey ?? ungroupedKey;
+					let group = groupsMap.get(key);
+					if (!group) {
+						group = {
+							groupKey: key,
+							label: key === ungroupedKey ? localize('otherGroup', "Other") : key,
+							icon: this.getSectionIcon(),
+							description: '',
+							items: [],
+						};
+						groupsMap.set(key, group);
+					}
+					group.items.push(item);
+				}
+
+				const groups = Array.from(groupsMap.values());
+
+				// Sort items within each group
+				for (const group of groups) {
+					group.items.sort((a, b) => a.name.localeCompare(b.name));
+				}
+
+				// Build display entries with group headers
+				this.displayEntries = [];
+				let isFirstGroup = true;
+				for (const group of groups) {
+					if (group.items.length === 0) {
+						continue;
+					}
+
+					const collapsed = this.collapsedGroups.has(group.groupKey);
+
+					this.displayEntries.push({
+						type: 'group-header',
+						id: `group-${group.groupKey}`,
+						groupKey: group.groupKey,
+						label: group.label,
+						icon: group.icon,
+						count: group.items.length,
+						isFirst: isFirstGroup,
+						description: group.description,
+						collapsed,
+					});
+					isFirstGroup = false;
+
+					if (!collapsed) {
+						for (const item of group.items) {
+							this.displayEntries.push({ type: 'file-item', item });
+						}
+					}
+				}
+
+				this.list.splice(0, this.list.length, this.displayEntries);
+				this.updateEmptyState();
+				return matchedItems.length;
+			}
+			// No explicit groupKey — fall through to standard storage-based grouping below.
 		}

 		// Group items by storage
diff --git a/src/vs/workbench/contrib/chat/common/customizationHarnessService.ts b/src/vs/workbench/contrib/chat/common/customizationHarnessService.ts
index 9c5a935bc7815..812edf3eb906e 100644
--- a/src/vs/workbench/contrib/chat/common/customizationHarnessService.ts
+++ b/src/vs/workbench/contrib/chat/common/customizationHarnessService.ts
@@ -137,6 +137,12 @@ export interface IExternalCustomizationItem {
 	readonly type: string;
 	readonly name: string;
 	readonly description?: string;
+	/** When set, items with the same groupKey are displayed under a shared collapsible header. */
+	readonly groupKey?: string;
+	/** When set, shows a small inline badge next to the item name (e.g. an applyTo glob pattern). */
+	readonly badge?: string;
+	/** Tooltip shown when hovering the badge. */
+	readonly badgeTooltip?: string;
 }

 /**
diff --git a/src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts b/src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts
index ac7425f8dd867..efb2c005470e4 100644
--- a/src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts
+++ b/src/vscode-dts/vscode.proposed.chatSessionCustomizationProvider.d.ts
@@ -94,6 +94,27 @@ declare module 'vscode' {
 		 * Optional description of this customization.
 		 */
 		readonly description?: string;
+
+		/**
+		 * Optional group key for display grouping. Items sharing the same
+		 * `groupKey` are placed under a shared collapsible header in the
+		 * management UI.
+		 *
+		 * When omitted, items are grouped automatically by their storage
+		 * source (e.g. Workspace, User) based on the item's URI.
+		 */
+		readonly groupKey?: string;
+
+		/**
+		 * Optional inline badge text shown next to the item name
+		 * (e.g. a glob pattern like `src/vs/sessions/**`).
+		 */
+		readonly badge?: string;
+
+		/**
+		 * Optional tooltip text shown when hovering over the badge.
+		 */
+		readonly badgeTooltip?: string;
 	}

 	/**

PATCH

echo "Patch applied successfully."
