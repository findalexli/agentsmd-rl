#!/bin/bash
set -euo pipefail

# Fix: Scope editor service in window title to own editor groups container
# This prevents the main window title from incorrectly showing editors
# that were moved to auxiliary windows.

# Check if already applied
if grep -q "const scopedEditorService = editorService.createScoped" src/vs/workbench/browser/parts/titlebar/titlebarPart.ts; then
    echo "Fix already applied"
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts b/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts
index a7b85c157ae78..1e424bd9bb862 100644
--- a/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts
+++ b/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts
@@ -55,6 +55,7 @@ import { IHoverDelegate } from '../../../../base/browser/ui/hover/hoverDelegate.
 import { CommandsRegistry } from '../../../../platform/commands/common/commands.js';
 import { safeIntl } from '../../../../base/common/date.js';
 import { IsCompactTitleBarContext, TitleBarVisibleContext } from '../../../common/contextkeys.js';
+import { ServiceCollection } from '../../../../platform/instantiation/common/serviceCollection.js';

 export interface ITitleVariable {
 	readonly name: string;
@@ -292,6 +293,8 @@ export class BrowserTitlebarPart extends Part implements ITitlebarPart {

 	private readonly windowTitle: WindowTitle;

+	protected readonly instantiationService: IInstantiationService;
+
 	constructor(
 		id: string,
 		targetWindow: CodeWindow,
@@ -299,25 +302,30 @@ export class BrowserTitlebarPart extends Part implements ITitlebarPart {
 		@IContextMenuService private readonly contextMenuService: IContextMenuService,
 		@IConfigurationService protected readonly configurationService: IConfigurationService,
 		@IBrowserWorkbenchEnvironmentService protected readonly environmentService: IBrowserWorkbenchEnvironmentService,
-		@IInstantiationService protected readonly instantiationService: IInstantiationService,
+		@IInstantiationService instantiationService: IInstantiationService,
 		@IThemeService themeService: IThemeService,
 		@IStorageService private readonly storageService: IStorageService,
 		@IWorkbenchLayoutService layoutService: IWorkbenchLayoutService,
 		@IContextKeyService protected readonly contextKeyService: IContextKeyService,
 		@IHostService private readonly hostService: IHostService,
-		@IEditorService private readonly editorService: IEditorService,
+		@IEditorService editorService: IEditorService,
 		@IMenuService private readonly menuService: IMenuService,
 		@IKeybindingService private readonly keybindingService: IKeybindingService
 	) {
 		super(id, { hasTitle: false }, themeService, storageService, layoutService);

+		const scopedEditorService = editorService.createScoped(editorGroupsContainer, this._store);
+		this.instantiationService = this._register(instantiationService.createChild(new ServiceCollection(
+			[IEditorService, scopedEditorService]
+		)));
+
 		this.isAuxiliary = targetWindow.vscodeWindowId !== mainWindow.vscodeWindowId;

 		this.isCompactContextKey = IsCompactTitleBarContext.bindTo(this.contextKeyService);

 		this.titleBarStyle = getTitleBarStyle(this.configurationService);

-		this.windowTitle = this._register(instantiationService.createInstance(WindowTitle, targetWindow));
+		this.windowTitle = this._register(this.instantiationService.createInstance(WindowTitle, targetWindow));

 		this.hoverDelegate = this._register(createInstantHoverDelegate());

@@ -713,7 +721,7 @@ export class BrowserTitlebarPart extends Part implements ITitlebarPart {

 			// The editor toolbar menu is handled by the editor group so we do not need to manage it here.
 			// However, depending on the active editor, we need to update the context and action runner of the toolbar menu.
-			if (this.editorActionsEnabled && this.editorService.activeEditor !== undefined) {
+			if (this.editorActionsEnabled && this.editorGroupsContainer.activeGroup.activeEditor !== undefined) {
 				const context: IEditorCommandsContext = { groupId: this.editorGroupsContainer.activeGroup.id };

 				this.actionToolBar.actionRunner = this.editorToolbarMenuDisposables.add(new EditorCommandsContextActionRunner(context));
PATCH

echo "Fix applied successfully"
