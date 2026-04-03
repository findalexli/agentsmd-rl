#!/bin/bash
# Gold patch for VS Code Changes View root folder rendering
set -euo pipefail

echo "Applying VS Code changes view fix..."

REPO_DIR="${1:-/workspace/vscode}"
cd "$REPO_DIR"

# Check if already applied
if grep -q "type: 'root'" src/vs/sessions/contrib/changes/browser/changesView.ts 2>/dev/null; then
    echo "Fix already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/src/vs/sessions/contrib/changes/browser/changesView.ts b/src/vs/sessions/contrib/changes/browser/changesView.ts
index f18935e68c23a..4bd912b23ed0a 100644
--- a/src/vs/sessions/contrib/changes/browser/changesView.ts
+++ b/src/vs/sessions/contrib/changes/browser/changesView.ts
@@ -32,7 +32,7 @@ import { IActionWidgetDropdownActionProvider } from '../../../../platform/action
 import { IConfigurationService } from '../../../../platform/configuration/common/configuration.js';
 import { IContextKeyService, RawContextKey } from '../../../../platform/contextkey/common/contextkey.js';
 import { IContextMenuService } from '../../../../platform/contextview/browser/contextView.js';
-import { FileKind } from '../../../../platform/files/common/files.js';
+import { FileKind, IFileService } from '../../../../platform/files/common/files.js';
 import { IHoverService } from '../../../../platform/hover/browser/hover.js';
 import { IInstantiationService, ServicesAccessor } from '../../../../platform/instantiation/common/instantiation.js';
 import { IKeybindingService } from '../../../../platform/keybinding/common/keybinding.js';
@@ -117,7 +117,7 @@ const hasOutgoingChangesContextKey = new RawContextKey<boolean>('sessions.hasOut

 // --- List Item

-type ChangeType = 'added' | 'modified' | 'deleted';
+type ChangeType = 'added' | 'modified' | 'deleted' | 'none';

 interface IChangesFileItem {
 	readonly type: 'file';
@@ -132,25 +132,42 @@ interface IChangesFileItem {
 	readonly agentFeedbackCount: number;
 }

-type ChangesTreeElement = IChangesFileItem | IResourceNode<IChangesFileItem, undefined>;
+interface IChangesRootItem {
+	readonly type: 'root';
+	readonly uri: URI;
+	readonly name: string;
+	description?: string;
+}
+
+interface IChangesTreeRootInfo {
+	readonly root: IChangesRootItem;
+	readonly resourceTreeRootUri: URI;
+}
+
+type ChangesTreeElement = IChangesRootItem | IChangesFileItem | IResourceNode<IChangesFileItem, undefined>;

 function isChangesFileItem(element: ChangesTreeElement): element is IChangesFileItem {
-	return !ResourceTree.isResourceNode(element);
+	return !ResourceTree.isResourceNode(element) && element.type === 'file';
+}
+
+function isChangesRootItem(element: ChangesTreeElement): element is IChangesRootItem {
+	return !ResourceTree.isResourceNode(element) && element.type === 'root';
 }

 /**
  * Builds a tree of `ICompressedTreeElement<ChangesTreeElement>` from a flat list of file items
  * using a `ResourceTree` to group files by their directory path segments.
  */
-function buildTreeChildren(items: IChangesFileItem[]): ICompressedTreeElement<ChangesTreeElement>[] {
+function buildTreeChildren(items: IChangesFileItem[], treeRootInfo?: IChangesTreeRootInfo): ICompressedTreeElement<ChangesTreeElement>[] {
 	if (items.length === 0) {
 		return [];
 	}

+	let rootUri = treeRootInfo?.resourceTreeRootUri ?? URI.file('/');
+
 	// For github-remote-file URIs, set the root to /{owner}/{repo}/{ref}
 	// so the tree shows repo-relative paths instead of internal URI segments.
-	let rootUri = URI.file('/');
-	if (items[0].uri.scheme === GITHUB_REMOTE_FILE_SCHEME) {
+	if (!treeRootInfo && items[0].uri.scheme === GITHUB_REMOTE_FILE_SCHEME) {
 		const parts = items[0].uri.path.split('/').filter(Boolean);
 		if (parts.length >= 3) {
 			rootUri = items[0].uri.with({ path: '/' + parts.slice(0, 3).join('/') });
@@ -185,7 +202,18 @@ function buildTreeChildren(items: IChangesFileItem[]): ICompressedTreeElement<Ch
 		return result;
 	}

-	return convertChildren(resourceTree.root);
+	const children = convertChildren(resourceTree.root);
+	if (!treeRootInfo) {
+		return children;
+	}
+
+	return [{
+		element: treeRootInfo.root,
+		children,
+		collapsible: true,
+		collapsed: false,
+		incompressible: true,
+	}];
 }

 function toChangesFileItem(changes: GitDiffChange[], modifiedRef: string | undefined, originalRef: string | undefined): IChangesFileItem[] {
@@ -218,6 +246,45 @@ function toChangesFileItem(changes: GitDiffChange[], modifiedRef: string | undef
 	});
 }

+async function collectWorkspaceFiles(fileService: IFileService, rootUri: URI): Promise<IChangesFileItem[]> {
+	const files: IChangesFileItem[] = [];
+
+	const collect = async (uri: URI): Promise<void> => {
+		let stat;
+		try {
+			stat = await fileService.resolve(uri);
+		} catch {
+			return;
+		}
+
+		if (!stat.children) {
+			return;
+		}
+
+		for (const child of stat.children) {
+			if (child.isDirectory) {
+				await collect(child.resource);
+				continue;
+			}
+
+			files.push({
+				type: 'file',
+				uri: child.resource,
+				state: ModifiedFileEntryState.Accepted,
+				isDeletion: false,
+				changeType: 'none',
+				linesAdded: 0,
+				linesRemoved: 0,
+				reviewCommentCount: 0,
+				agentFeedbackCount: 0,
+			});
+		}
+	};
+
+	await collect(rootUri);
+	return files;
+}
+
 // --- View Model

 class ChangesViewModel extends Disposable {
@@ -229,6 +296,7 @@ class ChangesViewModel extends Disposable {
 	readonly activeSessionIsolationModeObs: IObservable<IsolationMode>;
 	readonly activeSessionRepositoryObs: IObservableWithChange<IGitRepository | undefined>;
 	readonly activeSessionChangesObs: IObservable<readonly (IChatSessionFileChange | IChatSessionFileChange2)[]>;
+	readonly activeSessionWorkspaceFilesObs: IObservableWithChange<IObservable<readonly IChangesFileItem[] | undefined>>;
 	readonly activeSessionHasGitRepositoryObs: IObservable<boolean>;
 	readonly activeSessionFirstCheckpointRefObs: IObservable<string | undefined>;
 	readonly activeSessionLastCheckpointRefObs: IObservable<string | undefined>;
@@ -252,9 +320,11 @@ class ChangesViewModel extends Disposable {

 	constructor(
 		@IAgentSessionsService private readonly agentSessionsService: IAgentSessionsService,
+		@IFileService private readonly fileService: IFileService,
 		@IGitService private readonly gitService: IGitService,
 		@ISessionsManagementService private readonly sessionManagementService: ISessionsManagementService,
 		@IStorageService private readonly storageService: IStorageService,
+		@IWorkspaceContextService private readonly workspaceContextService: IWorkspaceContextService,
 	) {
 		super();

@@ -376,6 +446,24 @@ class ChangesViewModel extends Disposable {
 			return model?.metadata?.lastCheckpointRef as string | undefined;
 		});

+		// Active session workspace files
+		this.activeSessionWorkspaceFilesObs = derived(reader => {
+			if (!this.activeSessionResourceObs.read(reader)) {
+				return constObservable([]);
+			}
+
+			if (this.activeSessionHasGitRepositoryObs.read(reader)) {
+				return constObservable([]);
+			}
+
+			const rootUri = this.workspaceContextService.getWorkspace().folders[0]?.uri;
+			if (!rootUri) {
+				return constObservable([]);
+			}
+
+			return new ObservablePromise(collectWorkspaceFiles(this.fileService, rootUri)).resolvedValue;
+		});
+
 		// Version mode
 		this.versionModeObs = observableValue<ChangesVersionMode>(this, ChangesVersionMode.BranchChanges);

@@ -437,6 +525,7 @@ export class ChangesViewPane extends ViewPane {
 		@ICodeReviewService private readonly codeReviewService: ICodeReviewService,
 		@IGitHubService private readonly gitHubService: IGitHubService,
 		@IAgentFeedbackService private readonly agentFeedbackService: IAgentFeedbackService,
+		@IWorkspaceContextService private readonly workspaceContextService: IWorkspaceContextService,
 	) {
 		super({ ...options, titleMenuId: MenuId.ChatEditingSessionTitleToolbar }, keybindingService, contextMenuService, configurationService, contextKeyService, viewDescriptorService, instantiationService, openerService, themeService, hoverService);

@@ -721,6 +810,11 @@ export class ChangesViewPane extends ViewPane {
 		});

 		const isLoadingChangesObs = derived(reader => {
+			if (!this.viewModel.activeSessionHasGitRepositoryObs.read(reader)) {
+				const files = this.viewModel.activeSessionWorkspaceFilesObs.read(reader).read(reader);
+				return files === undefined;
+			}
+
 			const versionMode = this.viewModel.versionModeObs.read(reader);
 			if (versionMode !== ChangesVersionMode.AllChanges && versionMode !== ChangesVersionMode.LastTurn) {
 				return false;
@@ -751,8 +845,14 @@ export class ChangesViewPane extends ViewPane {

 			const sourceEntries: IChangesFileItem[] = [];
 			if (versionMode === ChangesVersionMode.BranchChanges) {
-				const sessionFiles = sessionFilesObs.read(reader);
-				sourceEntries.push(...sessionFiles);
+				const hasGitRepository = this.viewModel.activeSessionHasGitRepositoryObs.read(reader);
+				if (hasGitRepository) {
+					const sessionFiles = sessionFilesObs.read(reader);
+					sourceEntries.push(...sessionFiles);
+				} else {
+					const files = this.viewModel.activeSessionWorkspaceFilesObs.read(reader).read(reader) ?? [];
+					sourceEntries.push(...files);
+				}
 			} else if (versionMode === ChangesVersionMode.AllChanges) {
 				const allChanges = allChangesObs.read(reader).read(reader) ?? [];
 				const firstCheckpointRef = this.viewModel.activeSessionFirstCheckpointRefObs.read(reader);
@@ -1097,7 +1197,8 @@ export class ChangesViewPane extends ViewPane {

 			if (viewMode === ChangesViewMode.Tree) {
 				// Tree mode: build hierarchical tree from file entries
-				const treeChildren = buildTreeChildren(entries);
+				const treeRootInfo = this.getTreeRootInfo(entries);
+				const treeChildren = buildTreeChildren(entries, treeRootInfo);
 				this.tree.setChildren(null, treeChildren);
 			} else {
 				// List mode: flat list of file items
@@ -1147,6 +1248,39 @@ export class ChangesViewPane extends ViewPane {
 		return selection.filter(item => !!item && isChangesFileItem(item));
 	}

+	private getTreeRootInfo(items: readonly IChangesFileItem[]): IChangesTreeRootInfo | undefined {
+		if (items.length === 0) {
+			return undefined;
+		}
+
+		const workspaceFolder = this.workspaceContextService.getWorkspace().folders[0];
+		if (!workspaceFolder) {
+			return undefined;
+		}
+
+		const sampleUri = items[0].uri;
+		let resourceTreeRootUri = workspaceFolder.uri;
+
+		if (sampleUri.scheme === GITHUB_REMOTE_FILE_SCHEME) {
+			const parts = sampleUri.path.split('/').filter(Boolean);
+			if (parts.length >= 3) {
+				resourceTreeRootUri = sampleUri.with({ path: '/' + parts.slice(0, 3).join('/'), query: '', fragment: '' });
+			}
+		} else if (sampleUri.scheme !== workspaceFolder.uri.scheme || sampleUri.authority !== workspaceFolder.uri.authority) {
+			resourceTreeRootUri = sampleUri.with({ path: workspaceFolder.uri.path, authority: workspaceFolder.uri.authority, query: '', fragment: '' });
+		}
+
+		return {
+			root: {
+				type: 'root',
+				uri: workspaceFolder.uri,
+				name: workspaceFolder.name,
+				description: this.viewModel.activeSessionBranchNameObs.get(),
+			},
+			resourceTreeRootUri,
+		};
+	}
+
 	private getSessionDiscardRef(): string {
 		const versionMode = this.viewModel.versionModeObs.get();
 		const firstCheckpointRef = this.viewModel.activeSessionFirstCheckpointRefObs.get();
@@ -1187,7 +1321,7 @@ export class ChangesViewPane extends ViewPane {
 		const tree = this.createChangesTree(container, Event.None, disposables, () => tree.getSelection().filter(item => !!item && isChangesFileItem(item)));

 		if (viewMode === ChangesViewMode.Tree) {
-			tree.setChildren(null, buildTreeChildren(items));
+			tree.setChildren(null, buildTreeChildren(items, this.getTreeRootInfo(items)));
 		} else {
 			tree.setChildren(null, items.map(item => ({ element: item as ChangesTreeElement, collapsible: false })));
 		}
@@ -1345,7 +1479,13 @@ class ChangesViewActionRunner extends ActionRunner {

 		const contextIsSelected = selection.some(s => s === context);
 		const actualContext = contextIsSelected ? selection : [context];
-		const args = actualContext.map(e => ResourceTree.isResourceNode(e) ? ResourceTree.collect(e) : [e]).flat();
+		const args = actualContext.map(e => {
+			if (ResourceTree.isResourceNode(e)) {
+				return ResourceTree.collect(e);
+			}
+
+			return isChangesFileItem(e) ? [e] : [];
+		}).flat();
 		await action.run(sessionResource, discardRef, ...args.map(item => item.uri));
 	}
 }
@@ -1435,12 +1575,18 @@ class ChangesTreeRenderer implements ICompressibleTreeRenderer<ChangesTreeElemen
 	}

 	renderElement(node: ITreeNode<ChangesTreeElement, void>, _index: number, templateData: IChangesTreeTemplate): void {
+		console.log('Rendering element:', node.element);
 		const element = node.element;
 		templateData.label.element.style.display = 'flex';

-		if (ResourceTree.isResourceNode(element)) {
+		if (isChangesRootItem(element)) {
+			// Root element
+			this.renderRootElement(element, templateData);
+		} else if (ResourceTree.isResourceNode(element)) {
+			// Folder element
 			this.renderFolderElement(element, templateData);
 		} else {
+			// File element
 			this.renderFileElement(element, templateData);
 		}
 	}
@@ -1479,9 +1625,11 @@ class ChangesTreeRenderer implements ICompressibleTreeRenderer<ChangesTreeElemen
 			hidePath: false
 		});

-		// Show file-specific decorations
-		templateData.lineCountsContainer.style.display = '';
-		templateData.decorationBadge.style.display = '';
+		const showChangeDecorations = data.changeType !== 'none';
+
+		// Show file-specific decorations for changed files only
+		templateData.lineCountsContainer.style.display = showChangeDecorations ? '' : 'none';
+		templateData.decorationBadge.style.display = showChangeDecorations ? '' : 'none';

 		if (data.reviewCommentCount > 0) {
 			templateData.reviewCommentsBadge.style.display = '';
@@ -1507,30 +1655,36 @@ class ChangesTreeRenderer implements ICompressibleTreeRenderer<ChangesTreeElemen
 			templateData.agentFeedbackBadge.replaceChildren();
 		}

-		// Update decoration badge (A/M/D)
 		const badge = templateData.decorationBadge;
 		badge.className = 'changes-decoration-badge';
-		switch (data.changeType) {
-			case 'added':
-				badge.textContent = 'A';
-				badge.classList.add('added');
-				break;
-			case 'deleted':
-				badge.textContent = 'D';
-				badge.classList.add('deleted');
-				break;
-			case 'modified':
-			default:
-				badge.textContent = 'M';
-				badge.classList.add('modified');
-				break;
-		}
+		if (showChangeDecorations) {
+			// Update decoration badge (A/M/D)
+			switch (data.changeType) {
+				case 'added':
+					badge.textContent = 'A';
+					badge.classList.add('added');
+					break;
+				case 'deleted':
+					badge.textContent = 'D';
+					badge.classList.add('deleted');
+					break;
+				case 'modified':
+				default:
+					badge.textContent = 'M';
+					badge.classList.add('modified');
+					break;
+			}

-		templateData.addedSpan.textContent = `+${data.linesAdded}`;
-		templateData.removedSpan.textContent = `-${data.linesRemoved}`;
+			templateData.addedSpan.textContent = `+${data.linesAdded}`;
+			templateData.removedSpan.textContent = `-${data.linesRemoved}`;

-		// eslint-disable-next-line no-restricted-syntax
-		templateData.label.element.querySelector('.monaco-icon-name-container')?.classList.add('modified');
+			// eslint-disable-next-line no-restricted-syntax
+			templateData.label.element.querySelector('.monaco-icon-name-container')?.classList.add('modified');
+		} else {
+			badge.textContent = '';
+			// eslint-disable-next-line no-restricted-syntax
+			templateData.label.element.querySelector('.monaco-icon-name-container')?.classList.remove('modified');
+		}

 		if (templateData.toolbar) {
 			templateData.toolbar.context = data;
@@ -1540,6 +1694,28 @@ class ChangesTreeRenderer implements ICompressibleTreeRenderer<ChangesTreeElemen
 		}
 	}

+	private renderRootElement(data: IChangesRootItem, templateData: IChangesTreeTemplate): void {
+		templateData.label.setResource({
+			resource: data.uri,
+			name: data.name,
+		}, {
+			fileKind: FileKind.ROOT_FOLDER,
+			separator: this.labelService.getSeparator(data.uri.scheme, data.uri.authority),
+		});
+
+		templateData.reviewCommentsBadge.style.display = 'none';
+		templateData.agentFeedbackBadge.style.display = 'none';
+		templateData.decorationBadge.style.display = 'none';
+		templateData.lineCountsContainer.style.display = 'none';
+
+		if (templateData.toolbar) {
+			templateData.toolbar.context = data.uri;
+		}
+		if (templateData.contextKeyService) {
+			chatEditingWidgetFileStateContextKey.bindTo(templateData.contextKeyService).set(undefined!);
+		}
+	}
+
 	private renderFolderElement(node: IResourceNode<IChangesFileItem, undefined>, templateData: IChangesTreeTemplate): void {
 		templateData.label.setFile(node.uri, {
 			fileKind: FileKind.FOLDER,
@@ -1646,18 +1822,24 @@ class ChangesPickerActionItem extends ActionWidgetDropdownActionViewItem {
 		@IContextKeyService contextKeyService: IContextKeyService,
 		@ISessionsManagementService sessionManagementService: ISessionsManagementService,
 		@ITelemetryService telemetryService: ITelemetryService,
+		@IWorkspaceContextService private readonly workspaceContextService: IWorkspaceContextService,
 	) {
 		const actionProvider: IActionWidgetDropdownActionProvider = {
 			getActions: () => {
 				const branchName = viewModel.activeSessionBranchNameObs.get();
 				const baseBranchName = viewModel.activeSessionBaseBranchNameObs.get();
+				const hasGitRepository = viewModel.activeSessionHasGitRepositoryObs.get();

 				return [
 					{
 						...action,
 						id: 'chatEditing.versionsBranchChanges',
-						label: localize('chatEditing.versionsBranchChanges', 'Branch Changes'),
-						description: `${branchName} → ${baseBranchName}`,
+						label: hasGitRepository
+							? localize('chatEditing.versionsBranchChanges', 'Branch Changes')
+							: localize('chatEditing.versionsFolderChanges', 'Folder Changes'),
+						description: hasGitRepository
+							? `${branchName} → ${baseBranchName}`
+							: this.workspaceContextService.getWorkspace().folders[0]?.uri.fsPath,
 						checked: viewModel.versionModeObs.get() === ChangesVersionMode.BranchChanges,
 						category: { label: 'changes', order: 1, showHeader: false },
 						run: async () => {
@@ -1707,16 +1889,22 @@ class ChangesPickerActionItem extends ActionWidgetDropdownActionViewItem {

 		this._register(autorun(reader => {
 			viewModel.versionModeObs.read(reader);
+			viewModel.activeSessionHasGitRepositoryObs.read(reader);
+
 			if (this.element) {
 				this.renderLabel(this.element);
 			}
 		}));
 	}

-	protected override renderLabel(element: HTMLElement): null {
+	protected override renderLabel(element: HTMLElement): IDisposable | null {
 		const mode = this.viewModel.versionModeObs.get();
+		const hasGitRepository = this.viewModel.activeSessionHasGitRepositoryObs.get();
+
 		const label = mode === ChangesVersionMode.BranchChanges
-			? localize('sessionsChanges.versionsBranchChanges', "Branch Changes")
+			? hasGitRepository
+				? localize('sessionsChanges.versionsBranchChanges', "Branch Changes")
+				: localize('sessionsChanges.versionsFolderChanges', "Folder Changes")
 			: mode === ChangesVersionMode.AllChanges
 				? localize('sessionsChanges.versionsAllChanges', "All Changes")
 				: localize('sessionsChanges.versionsLastTurn', "Last Turn's Changes");
PATCH

echo "Fix applied successfully."
