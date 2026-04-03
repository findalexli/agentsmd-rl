#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if grep -q 'getSkillUIIntegrations' src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/src/vs/sessions/AI_CUSTOMIZATIONS.md b/src/vs/sessions/AI_CUSTOMIZATIONS.md
index acb2203f9af97..2a7bddb5a7a37 100644
--- a/src/vs/sessions/AI_CUSTOMIZATIONS.md
+++ b/src/vs/sessions/AI_CUSTOMIZATIONS.md
@@ -172,20 +172,24 @@ The underlying `storage` remains `PromptsStorage.extension` — the grouping is
 Sessions overrides `PromptsService` via `AgenticPromptsService` (in `promptsService.ts`):
 
 - **Discovery**: `AgenticPromptFilesLocator` scopes workspace folders to the active session's worktree
-- **Built-in prompts**: Discovers bundled `.prompt.md` files from `vs/sessions/prompts/` and surfaces them with `PromptsStorage.builtin` storage type
-- **User override**: Built-in prompts are omitted when a user or workspace prompt with the same name exists
+- **Built-in skills**: Discovers bundled `SKILL.md` files from `vs/sessions/skills/{name}/` and surfaces them with `PromptsStorage.builtin` storage type
+- **User override**: Built-in skills are omitted when a user or workspace skill with the same name exists
 - **Creation targets**: `getSourceFolders()` override replaces VS Code profile user roots with `~/.copilot/{subfolder}` for CLI compatibility
 - **Hook folders**: Falls back to `.github/hooks` in the active worktree
 
-### Built-in Prompts
+### Built-in Skills
 
-Prompt files bundled with the Sessions app live in `src/vs/sessions/prompts/`. They are:
+All built-in customizations bundled with the Sessions app are skills, living in `src/vs/sessions/skills/{name}/SKILL.md`. They are:
 
-- Discovered at runtime via `FileAccess.asFileUri('vs/sessions/prompts')`
+- Discovered at runtime via `FileAccess.asFileUri('vs/sessions/skills')`
 - Tagged with `PromptsStorage.builtin` storage type
 - Shown in a "Built-in" group in the AI Customization tree view and management editor
-- Filtered out when a user/workspace prompt shares the same clean name (override behavior)
-- Included in storage filters for prompts and CLI-user types
+- Filtered out when a user/workspace skill shares the same name (override behavior)
+- Skills with UI integrations (e.g. `act-on-feedback`, `generate-run-commands`) display a "UI Integration" badge in the management editor
+
+### UI Integration Badges
+
+Skills that are directly invoked by UI elements (toolbar buttons, menu items) are annotated with a "UI Integration" badge in the management editor. The mapping is provided by `IAICustomizationWorkspaceService.getSkillUIIntegrations()`, which the Sessions implementation populates with the relevant skill names and tooltip descriptions. The badge appears on both the built-in skill and any user/workspace override, ensuring users understand that overriding the skill affects a UI surface.
 
 ### Count Consistency
 
@@ -201,7 +205,7 @@ Prompt files bundled with the Sessions app live in `src/vs/sessions/prompts/`. T
 
 ### Item Badges
 
-`IAICustomizationListItem.badge` is an optional string that renders as a small inline tag next to the item name (same visual style as the MCP "Bridged" badge). For context instructions, this badge shows the raw `applyTo` pattern (e.g. a glob like `**/*.ts`), while the tooltip (`badgeTooltip`) explains the behavior. The badge text is also included in search filtering.
+`IAICustomizationListItem.badge` is an optional string that renders as a small inline tag next to the item name (same visual style as the MCP "Bridged" badge). For context instructions, this badge shows the raw `applyTo` pattern (e.g. a glob like `**/*.ts`), while the tooltip (`badgeTooltip`) explains the behavior. For skills with UI integrations, the badge reads "UI Integration" with a tooltip describing which UI surface invokes the skill. The badge text is also included in search filtering.
 
 ### Debug Panel
 
diff --git a/src/vs/sessions/contrib/chat/browser/aiCustomizationWorkspaceService.ts b/src/vs/sessions/contrib/chat/browser/aiCustomizationWorkspaceService.ts
index 169051def86aa..3756ed8a8efdf 100644
--- a/src/vs/sessions/contrib/chat/browser/aiCustomizationWorkspaceService.ts
+++ b/src/vs/sessions/contrib/chat/browser/aiCustomizationWorkspaceService.ts
@@ -261,4 +261,18 @@ export class SessionsAICustomizationWorkspaceService implements IAICustomization
 			return applyStorageSourceFilter([cmd.promptPath], filter).length > 0;
 		});
 	}
+
+	private static readonly _skillUIIntegrations: ReadonlyMap<string, string> = new Map([
+		['act-on-feedback', localize('skillUI.actOnFeedback', "Used by the Submit Feedback button in the Changes toolbar")],
+		['generate-run-commands', localize('skillUI.generateRunCommands', "Used by the Run button in the title bar")],
+		['create-pr', localize('skillUI.createPr', "Used by the Create Pull Request button in the Changes toolbar")],
+		['create-draft-pr', localize('skillUI.createDraftPr', "Used by the Create Draft Pull Request button in the Changes toolbar")],
+		['update-pr', localize('skillUI.updatePr', "Used by the Update Pull Request button in the Changes toolbar")],
+		['merge-changes', localize('skillUI.mergeChanges', "Used by the Merge button in the Changes toolbar")],
+		['commit', localize('skillUI.commit', "Used by the Commit button in the Changes toolbar")],
+	]);
+
+	getSkillUIIntegrations(): ReadonlyMap<string, string> {
+		return SessionsAICustomizationWorkspaceService._skillUIIntegrations;
+	}
 }
diff --git a/src/vs/sessions/contrib/chat/browser/promptsService.ts b/src/vs/sessions/contrib/chat/browser/promptsService.ts
index 22c9e661fb679..bcce55f35dc19 100644
--- a/src/vs/sessions/contrib/chat/browser/promptsService.ts
+++ b/src/vs/sessions/contrib/chat/browser/promptsService.ts
@@ -14,7 +14,7 @@ import { IConfigurationService } from '../../../../platform/configuration/common
 import { IFileService } from '../../../../platform/files/common/files.js';
 import { ILogService } from '../../../../platform/log/common/log.js';
 import { IWorkspaceContextService, IWorkspaceFolder } from '../../../../platform/workspace/common/workspace.js';
-import { HOOKS_SOURCE_FOLDER, SKILL_FILENAME, getCleanPromptName } from '../../../../workbench/contrib/chat/common/promptSyntax/config/promptFileLocations.js';
+import { HOOKS_SOURCE_FOLDER, SKILL_FILENAME } from '../../../../workbench/contrib/chat/common/promptSyntax/config/promptFileLocations.js';
 import { PromptsType } from '../../../../workbench/contrib/chat/common/promptSyntax/promptTypes.js';
 import { IAgentSkill, IPromptPath, PromptsStorage } from '../../../../workbench/contrib/chat/common/promptSyntax/service/promptsService.js';
 import { BUILTIN_STORAGE, IBuiltinPromptPath } from '../../chat/common/builtinPromptsStorage.js';
@@ -25,15 +25,11 @@ import { IUserDataProfileService } from '../../../../workbench/services/userData
 import { IAICustomizationWorkspaceService } from '../../../../workbench/contrib/chat/common/aiCustomizationWorkspaceService.js';
 import { IWorkspaceTrustManagementService } from '../../../../platform/workspace/common/workspaceTrust.js';
 
-/** URI root for built-in prompts bundled with the Sessions app. */
-export const BUILTIN_PROMPTS_URI = FileAccess.asFileUri('vs/sessions/prompts');
-
 /** URI root for built-in skills bundled with the Sessions app. */
 export const BUILTIN_SKILLS_URI = FileAccess.asFileUri('vs/sessions/skills');
 
 export class AgenticPromptsService extends PromptsService {
 	private _copilotRoot: URI | undefined;
-	private _builtinPromptsCache: Map<PromptsType, Promise<readonly IBuiltinPromptPath[]>> | undefined;
 	private _builtinSkillsCache: Promise<readonly IAgentSkill[]> | undefined;
 
 	protected override createPromptFilesLocator(): PromptFilesLocator {
@@ -48,42 +44,6 @@ export class AgenticPromptsService extends PromptsService {
 		return this._copilotRoot;
 	}
 
-	/**
-	 * Returns built-in prompt files bundled with the Sessions app.
-	 */
-	private async getBuiltinPromptFiles(type: PromptsType): Promise<readonly IBuiltinPromptPath[]> {
-		if (type !== PromptsType.prompt) {
-			return [];
-		}
-
-		if (!this._builtinPromptsCache) {
-			this._builtinPromptsCache = new Map();
-		}
-
-		let cached = this._builtinPromptsCache.get(type);
-		if (!cached) {
-			cached = this.discoverBuiltinPrompts(type);
-			this._builtinPromptsCache.set(type, cached);
-		}
-		return cached;
-	}
-
-	private async discoverBuiltinPrompts(type: PromptsType): Promise<readonly IBuiltinPromptPath[]> {
-		const fileService = this.instantiationService.invokeFunction(accessor => accessor.get(IFileService));
-		const promptsDir = FileAccess.asFileUri('vs/sessions/prompts');
-		try {
-			const stat = await fileService.resolve(promptsDir);
-			if (!stat.children) {
-				return [];
-			}
-			return stat.children
-				.filter(child => !child.isDirectory && child.name.endsWith('.prompt.md'))
-				.map(child => ({ uri: child.resource, storage: BUILTIN_STORAGE, type }));
-		} catch {
-			return [];
-		}
-	}
-
 	//#region Built-in Skills
 
 	/**
@@ -189,18 +149,17 @@ export class AgenticPromptsService extends PromptsService {
 	//#endregion
 
 	/**
-	 * Override to include built-in prompts and built-in skills, filtering out
-	 * those overridden by user or workspace items with the same name.
+	 * Override to include built-in skills, filtering out those overridden by
+	 * user or workspace items with the same name.
 	 */
 	public override async listPromptFiles(type: PromptsType, token: CancellationToken): Promise<readonly IPromptPath[]> {
 		const baseResults = await super.listPromptFiles(type, token);
 
-		let builtinItems: readonly IBuiltinPromptPath[];
-		if (type === PromptsType.skill) {
-			builtinItems = await this.getBuiltinSkillPaths();
-		} else {
-			builtinItems = await this.getBuiltinPromptFiles(type);
+		if (type !== PromptsType.skill) {
+			return baseResults;
 		}
+
+		const builtinItems = await this.getBuiltinSkillPaths();
 		if (builtinItems.length === 0) {
 			return baseResults;
 		}
@@ -209,12 +168,12 @@ export class AgenticPromptsService extends PromptsService {
 		const overriddenNames = new Set<string>();
 		for (const p of baseResults) {
 			if (p.storage === PromptsStorage.local || p.storage === PromptsStorage.user) {
-				overriddenNames.add(type === PromptsType.skill ? basename(dirname(p.uri)) : getCleanPromptName(p.uri));
+				overriddenNames.add(basename(dirname(p.uri)));
 			}
 		}
 
 		const nonOverridden = builtinItems.filter(
-			p => !overriddenNames.has(type === PromptsType.skill ? basename(dirname(p.uri)) : getCleanPromptName(p.uri))
+			p => !overriddenNames.has(basename(dirname(p.uri)))
 		);
 		// Built-in items use BUILTIN_STORAGE ('builtin') which is not in the
 		// core IPromptPath union but is handled by the sessions UI layer.
@@ -226,7 +185,8 @@ export class AgenticPromptsService extends PromptsService {
 			if (type === PromptsType.skill) {
 				return this.getBuiltinSkillPaths() as Promise<readonly IPromptPath[]>;
 			}
-			return this.getBuiltinPromptFiles(type) as Promise<readonly IPromptPath[]>;
+			// Built-in storage is only valid for skills; for other types, there are no items.
+			return [];
 		}
 		return super.listPromptFilesForStorage(type, storage, token);
 	}
diff --git a/src/vs/sessions/prompts/act-on-feedback.prompt.md b/src/vs/sessions/skills/act-on-feedback/SKILL.md
similarity index 62%
rename from src/vs/sessions/prompts/act-on-feedback.prompt.md
rename to src/vs/sessions/skills/act-on-feedback/SKILL.md
index 29ef4622505b7..a321a21049029 100644
--- a/src/vs/sessions/prompts/act-on-feedback.prompt.md
+++ b/src/vs/sessions/skills/act-on-feedback/SKILL.md
@@ -1,7 +1,10 @@
 ---
-description: Act on user feedback attached to the current session
+name: act-on-feedback
+description: Act on user feedback attached to the current session. Use when the user submits feedback on the session's changes via the Submit Feedback button.
 ---
-<!-- Customize this prompt and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+<!-- Customize this skill and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+
+# Act on Feedback
 
 The user has provided feedback on the current session's changes. Their feedback comments have been attached to this message.
 
diff --git a/src/vs/sessions/prompts/create-draft-pr.prompt.md b/src/vs/sessions/skills/create-draft-pr/SKILL.md
similarity index 69%
rename from src/vs/sessions/prompts/create-draft-pr.prompt.md
rename to src/vs/sessions/skills/create-draft-pr/SKILL.md
index c2529a264d4aa..22f1dbbee6673 100644
--- a/src/vs/sessions/prompts/create-draft-pr.prompt.md
+++ b/src/vs/sessions/skills/create-draft-pr/SKILL.md
@@ -1,7 +1,10 @@
 ---
-description: Create a draft pull request for the current session
+name: create-draft-pr
+description: Create a draft pull request for the current session. Use when the user wants to open a draft PR with the session's changes.
 ---
-<!-- Customize this prompt and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+<!-- Customize this skill and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+
+# Create Draft Pull Request
 
 Use the GitHub MCP server to create a draft pull request — do NOT use the `gh` CLI.
 
diff --git a/src/vs/sessions/prompts/create-pr.prompt.md b/src/vs/sessions/skills/create-pr/SKILL.md
similarity index 62%
rename from src/vs/sessions/prompts/create-pr.prompt.md
rename to src/vs/sessions/skills/create-pr/SKILL.md
index 4991f4ff58216..027f8cfb63d67 100644
--- a/src/vs/sessions/prompts/create-pr.prompt.md
+++ b/src/vs/sessions/skills/create-pr/SKILL.md
@@ -1,7 +1,10 @@
 ---
-description: Create a pull request for the current session
+name: create-pr
+description: Create a pull request for the current session. Use when the user wants to open a PR with the session's changes.
 ---
-<!-- Customize this prompt and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+<!-- Customize this skill and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+
+# Create Pull Request
 
 Use the GitHub MCP server to create a pull request — do NOT use the `gh` CLI.
 
diff --git a/src/vs/sessions/prompts/generate-run-commands.prompt.md b/src/vs/sessions/skills/generate-run-commands/SKILL.md
similarity index 88%
rename from src/vs/sessions/prompts/generate-run-commands.prompt.md
rename to src/vs/sessions/skills/generate-run-commands/SKILL.md
index e1744cf92c38a..d43dcda400b98 100644
--- a/src/vs/sessions/prompts/generate-run-commands.prompt.md
+++ b/src/vs/sessions/skills/generate-run-commands/SKILL.md
@@ -1,7 +1,10 @@
 ---
-description: Generate or modify run commands for the current session
+name: generate-run-commands
+description: Generate or modify run commands for the current session. Use when the user wants to set up or update run commands that appear in the session's Run button.
 ---
-<!-- Customize this prompt and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+<!-- Customize this skill and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+
+# Generate Run Commands
 
 Help the user set up run commands for the current Agent Session workspace. Run commands appear in the session's Run button in the title bar.
 
diff --git a/src/vs/sessions/prompts/merge-changes.prompt.md b/src/vs/sessions/skills/merge-changes/SKILL.md
similarity index 67%
rename from src/vs/sessions/prompts/merge-changes.prompt.md
rename to src/vs/sessions/skills/merge-changes/SKILL.md
index 065cb18ad18eb..504268e31a28e 100644
--- a/src/vs/sessions/prompts/merge-changes.prompt.md
+++ b/src/vs/sessions/skills/merge-changes/SKILL.md
@@ -1,7 +1,10 @@
 ---
-description: Merge changes from the topic branch to the merge base branch
+name: merge-changes
+description: Merge changes from the topic branch to the merge base branch. Use when the user wants to merge their session's work back to the base branch.
 ---
-<!-- Customize this prompt and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+<!-- Customize this skill and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+
+# Merge Changes
 
 Merge changes from the topic branch to the merge base branch.
 The context block appended to the prompt contains the source and target branch information.
diff --git a/src/vs/sessions/prompts/update-pr.prompt.md b/src/vs/sessions/skills/update-pr/SKILL.md
similarity index 71%
rename from src/vs/sessions/prompts/update-pr.prompt.md
rename to src/vs/sessions/skills/update-pr/SKILL.md
index 22ecf6ccf52e0..394d906d3ead0 100644
--- a/src/vs/sessions/prompts/update-pr.prompt.md
+++ b/src/vs/sessions/skills/update-pr/SKILL.md
@@ -1,7 +1,10 @@
 ---
-description: Update the pull request for the current session
+name: update-pr
+description: Update the pull request for the current session. Use when the user wants to push new changes to an existing PR.
 ---
-<!-- Customize this prompt and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+<!-- Customize this skill and select save to override its behavior. Delete that copy to restore the built-in behavior. -->
+
+# Update Pull Request
 
 Update the existing pull request for the current session.
 The context block appended to the prompt contains the pull request information.
diff --git a/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts b/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts
index 95ce950e3dc8d..f6e6da00b6ae3 100644
--- a/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts
+++ b/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationListWidget.ts
@@ -1293,11 +1293,14 @@ export class AICustomizationListWidget extends Disposable {
 					extensionInfoByUri.set(file.uri.toString(), { id: file.extension.identifier, displayName: file.extension.displayName });
 				}
 			}
+			const uiIntegrations = this.workspaceService.getSkillUIIntegrations();
 			const seenUris = new ResourceSet();
 			for (const skill of skills || []) {
 				const filename = basename(skill.uri);
 				const skillName = skill.name || basename(dirname(skill.uri)) || filename;
 				seenUris.add(skill.uri);
+				const skillFolderName = basename(dirname(skill.uri));
+				const uiTooltip = uiIntegrations.get(skillFolderName);
 				items.push({
 					id: skill.uri.toString(),
 					uri: skill.uri,
@@ -1308,6 +1311,8 @@ export class AICustomizationListWidget extends Disposable {
 					promptType,
 					pluginUri: skill.storage === PromptsStorage.plugin ? this.findPluginUri(skill.uri) : undefined,
 					disabled: false,
+					badge: uiTooltip ? localize('uiIntegrationBadge', "UI Integration") : undefined,
+					badgeTooltip: uiTooltip,
 				});
 			}
 			// Also include disabled skills from the raw file list
@@ -1315,15 +1320,20 @@ export class AICustomizationListWidget extends Disposable {
 				for (const file of allSkillFiles) {
 					if (!seenUris.has(file.uri) && disabledUris.has(file.uri)) {
 						const filename = basename(file.uri);
+						const disabledName = file.name || basename(dirname(file.uri)) || filename;
+						const disabledFolderName = basename(dirname(file.uri));
+						const uiTooltip = uiIntegrations.get(disabledFolderName);
 						items.push({
 							id: file.uri.toString(),
 							uri: file.uri,
-							name: file.name || basename(dirname(file.uri)) || filename,
+							name: disabledName,
 							filename,
 							description: file.description,
 							storage: file.storage,
 							promptType,
 							disabled: true,
+							badge: uiTooltip ? localize('uiIntegrationBadge', "UI Integration") : undefined,
+							badgeTooltip: uiTooltip,
 						});
 					}
 				}
diff --git a/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationWorkspaceService.ts b/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationWorkspaceService.ts
index 8a64b0cddba56..a4e399195b09f 100644
--- a/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationWorkspaceService.ts
+++ b/src/vs/workbench/contrib/chat/browser/aiCustomization/aiCustomizationWorkspaceService.ts
@@ -93,6 +93,12 @@ class AICustomizationWorkspaceService implements IAICustomizationWorkspaceServic
 	async getFilteredPromptSlashCommands(token: CancellationToken): Promise<readonly IChatPromptSlashCommand[]> {
 		return this.promptsService.getPromptSlashCommands(token);
 	}
+
+	private static readonly _emptyIntegrations: ReadonlyMap<string, string> = new Map();
+
+	getSkillUIIntegrations(): ReadonlyMap<string, string> {
+		return AICustomizationWorkspaceService._emptyIntegrations;
+	}
 }
 
 registerSingleton(IAICustomizationWorkspaceService, AICustomizationWorkspaceService, InstantiationType.Delayed);
diff --git a/src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts b/src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts
index 9b2aadb806a37..799899c28a7a8 100644
--- a/src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts
+++ b/src/vs/workbench/contrib/chat/common/aiCustomizationWorkspaceService.ts
@@ -150,4 +150,13 @@ export interface IAICustomizationWorkspaceService {
 	 * customizations visible in the AI Customization views.
 	 */
 	getFilteredPromptSlashCommands(token: CancellationToken): Promise<readonly IChatPromptSlashCommand[]>;
+
+	/**
+	 * Returns a map of built-in skill names that have direct UI integrations
+	 * (toolbar buttons, menu items, etc.) to a tooltip describing the
+	 * integration. Used to display a 'UI Integration' badge in the
+	 * customizations editor, especially important when users override a
+	 * built-in skill that drives a UI surface.
+	 */
+	getSkillUIIntegrations(): ReadonlyMap<string, string>;
 }
diff --git a/src/vs/workbench/test/browser/componentFixtures/aiCustomizationManagementEditor.fixture.ts b/src/vs/workbench/test/browser/componentFixtures/aiCustomizationManagementEditor.fixture.ts
index 3837c0cd369ce..cd2ee3fc79ad0 100644
--- a/src/vs/workbench/test/browser/componentFixtures/aiCustomizationManagementEditor.fixture.ts
+++ b/src/vs/workbench/test/browser/componentFixtures/aiCustomizationManagementEditor.fixture.ts
@@ -290,6 +290,11 @@ const allFiles: IFixtureFile[] = [
 	// Skills - extension (built-in + third-party)
 	{ uri: URI.file('/extensions/github.copilot-chat/skills/workspace/SKILL.md'), storage: PromptsStorage.extension, type: PromptsType.skill, name: 'Workspace Search', description: 'Built-in workspace search skill', extensionId: 'GitHub.copilot-chat', extensionDisplayName: 'GitHub Copilot Chat' },
 	{ uri: URI.file('/extensions/acme.tools/skills/audit/SKILL.md'), storage: PromptsStorage.extension, type: PromptsType.skill, name: 'Audit', description: 'Third-party audit skill', extensionId: 'acme.tools', extensionDisplayName: 'Acme Tools' },
+	// Skills - built-in (sessions bundled skills with UI integrations)
+	{ uri: URI.file('/app/skills/act-on-feedback/SKILL.md'), storage: BUILTIN_STORAGE as PromptsStorage, type: PromptsType.skill, name: 'act-on-feedback', description: 'Act on user feedback attached to the current session' },
+	{ uri: URI.file('/app/skills/generate-run-commands/SKILL.md'), storage: BUILTIN_STORAGE as PromptsStorage, type: PromptsType.skill, name: 'generate-run-commands', description: 'Generate or modify run commands for the current session' },
+	{ uri: URI.file('/app/skills/commit/SKILL.md'), storage: BUILTIN_STORAGE as PromptsStorage, type: PromptsType.skill, name: 'commit', description: 'Commit staged or unstaged changes with an AI-generated commit message' },
+	{ uri: URI.file('/app/skills/create-pr/SKILL.md'), storage: BUILTIN_STORAGE as PromptsStorage, type: PromptsType.skill, name: 'create-pr', description: 'Create a pull request for the current session' },
 	// Prompts — workspace
 	{ uri: URI.file('/workspace/.github/prompts/explain.prompt.md'), storage: PromptsStorage.local, type: PromptsType.prompt, name: 'Explain', description: 'Explain selected code' },
 	{ uri: URI.file('/workspace/.github/prompts/review.prompt.md'), storage: PromptsStorage.local, type: PromptsType.prompt, name: 'Review', description: 'Review changes' },
@@ -353,6 +358,7 @@ interface IRenderEditorOptions {
 	readonly scrollToBottom?: boolean;
 	readonly width?: number;
 	readonly height?: number;
+	readonly skillUIIntegrations?: ReadonlyMap<string, string>;
 }
 
 async function waitForAnimationFrames(count: number): Promise<void> {
@@ -423,6 +429,7 @@ async function renderEditor(ctx: ComponentFixtureContext, options: IRenderEditor
 	ctx.container.style.height = `${height}px`;
 
 	const isSessionsWindow = options.isSessionsWindow ?? false;
+	const skillUIIntegrations = options.skillUIIntegrations ?? new Map();
 	const managementSections = options.managementSections ?? [
 		AICustomizationManagementSection.Agents,
 		AICustomizationManagementSection.Skills,
@@ -470,12 +477,14 @@ async function renderEditor(ctx: ComponentFixtureContext, options: IRenderEditor
 				override setOverrideProjectRoot() { }
 				override readonly managementSections = managementSections;
 				override async generateCustomization() { }
+				override getSkillUIIntegrations() { return skillUIIntegrations; }
 			}());
 			reg.defineInstance(ICustomizationHarnessService, harnessService);
 			reg.defineInstance(IChatSessionsService, new class extends mock<IChatSessionsService>() {
 				override readonly onDidChangeCustomizations = Event.None;
 				override async getCustomizations() { return undefined; }
 				override getRegisteredChatSessionItemProviders() { return []; }
+				override hasCustomizationsProvider() { return false; }
 			}());
 			reg.defineInstance(IWorkspaceContextService, new class extends mock<IWorkspaceContextService>() {
 				override readonly onDidChangeWorkspaceFolders = Event.None;
@@ -812,6 +821,32 @@ export default defineThemedFixtureGroup({ path: 'chat/aiCustomizations/' }, {
 		}),
 	}),
 
+	// Sessions Skills tab showing UI Integration badges on built-in skills
+	SessionsSkillsTab: defineComponentFixture({
+		labels: { kind: 'screenshot' },
+		render: ctx => renderEditor(ctx, {
+			harness: CustomizationHarness.CLI,
+			isSessionsWindow: true,
+			selectedSection: AICustomizationManagementSection.Skills,
+			availableHarnesses: [
+				createCliHarnessDescriptor(getCliUserRoots(userHome), [BUILTIN_STORAGE]),
+			],
+			managementSections: [
+				AICustomizationManagementSection.Agents,
+				AICustomizationManagementSection.Skills,
+				AICustomizationManagementSection.Instructions,
+				AICustomizationManagementSection.Prompts,
+				AICustomizationManagementSection.Hooks,
+				AICustomizationManagementSection.McpServers,
+				AICustomizationManagementSection.Plugins,
+			],
+			skillUIIntegrations: new Map([
+				['act-on-feedback', 'Used by the Submit Feedback button in the Changes toolbar'],
+				['generate-run-commands', 'Used by the Run button in the title bar'],
+			]),
+		}),
+	}),
+
 	// MCP Servers tab with many servers to verify scrollable list layout
 	McpServersTab: defineComponentFixture({
 		labels: { kind: 'screenshot', blocksCi: true },

PATCH

echo "Patch applied successfully."
