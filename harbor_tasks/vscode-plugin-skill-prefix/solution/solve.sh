#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotent: skip if already applied
if grep -q 'getCanonicalPluginCommandId({ uri: promptPath.pluginUri }' src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts b/src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts
index 99dc65416b122..bc52f6a253269 100644
--- a/src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts
+++ b/src/vs/workbench/contrib/chat/common/plugins/agentPluginService.ts
@@ -58,7 +58,7 @@ export interface IAgentPluginDiscovery extends IDisposable {
 	start(enablementModel: IEnablementModel): void;
 }

-export function getCanonicalPluginCommandId(plugin: IAgentPlugin, commandName: string): string {
+export function getCanonicalPluginCommandId(plugin: { readonly uri: URI }, commandName: string): string {
 	const pluginSegment = basename(plugin.uri);
 	const prefix = normalizePluginToken(pluginSegment);
 	const normalizedCommand = normalizePluginToken(commandName);
diff --git a/src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts b/src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts
index 77933eb32274c..e035e7a3e2b65 100644
--- a/src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts
+++ b/src/vs/workbench/contrib/chat/common/promptSyntax/service/promptsServiceImpl.ts
@@ -610,7 +610,12 @@ export class PromptsService extends Disposable implements IPromptsService {
 		const parseResults = await Promise.all(slashCommandFiles.map(async promptPath => {
 			try {
 				const parsedPromptFile = await this.parseNew(promptPath.uri, token);
-				const name = parsedPromptFile?.header?.name ?? promptPath.name ?? getCleanPromptName(promptPath.uri);
+				const rawName = parsedPromptFile?.header?.name ?? promptPath.name ?? getCleanPromptName(promptPath.uri);
+				// For plugin resources, ensure the canonical plugin prefix is always preserved even when the
+				// file's frontmatter overrides the name.
+				const name = promptPath.source === PromptFileSource.Plugin && promptPath.pluginUri
+					? getCanonicalPluginCommandId({ uri: promptPath.pluginUri }, rawName)
+					: rawName;
 				const description = parsedPromptFile?.header?.description ?? promptPath.description;
 				const argumentHint = parsedPromptFile?.header?.argumentHint;
 				const userInvocable = parsedPromptFile?.header?.userInvocable;

PATCH

echo "Patch applied successfully."
