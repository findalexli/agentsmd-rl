#!/bin/bash
set -e
cd /workspace/workers-sdk

# Idempotency check
if grep -q "AGENT_PROMPT_TEMPLATE" packages/local-explorer-ui/src/utils/agent-prompt.ts 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply gold patch (all files except lockfile which is auto-generated)
git apply <<'PATCH'
diff --git a/.changeset/fuzzy-years-cover.md b/.changeset/fuzzy-years-cover.md
new file mode 100644
index 0000000000..c2b8a7d3e1
--- /dev/null
+++ b/.changeset/fuzzy-years-cover.md
@@ -0,0 +1,7 @@
+---
+"@cloudflare/local-explorer-ui": patch
+---
+
+Add new "Copy prompt for agent" button.
+
+This adds a clipboard copy field to the Local Explorer homepage for sharing an agent/LLM Local Explorer API prompt.

diff --git a/.changeset/tangy-wings-feel.md b/.changeset/tangy-wings-feel.md
new file mode 100644
index 0000000000..d5e9f8a2b3
--- /dev/null
+++ b/.changeset/tangy-wings-feel.md
@@ -0,0 +1,7 @@
+---
+"@cloudflare/local-explorer-ui": patch
+---
+
+Updates the Local Explorer homepage prompt to use the current runtime origin for the Explorer API endpoint.
+
+This ensures copied prompt text points to the correct local URL instead of a placeholder localhost port.

diff --git a/packages/local-explorer-ui/package.json b/packages/local-explorer-ui/package.json
index e3f2c1a0b4..d4a5b6c7e8 100644
--- a/packages/local-explorer-ui/package.json
+++ b/packages/local-explorer-ui/package.json
@@ -22,7 +22,7 @@
 	},
 	"dependencies": {
 		"@base-ui/react": "^1.1.0",
-		"@cloudflare/kumo": "^1.17.0",
+		"@cloudflare/kumo": "^1.18.0",
 		"@cloudflare/workers-editor-shared": "^0.1.1",
 		"@codemirror/autocomplete": "^6.20.0",
 		"@codemirror/commands": "^6.10.2",

diff --git a/packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts b/packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts
new file mode 100644
index 0000000000..a1b2c3d4e5
--- /dev/null
+++ b/packages/local-explorer-ui/src/__tests__/utils/agent-prompt.test.ts
@@ -0,0 +1,39 @@
+import { describe, test, vi } from "vitest";
+import {
+	copyTextToClipboard,
+	createLocalExplorerPrompt,
+	getLocalExplorerApiEndpoint,
+} from "../../utils/agent-prompt";
+
+describe("llm-prompt utils", () => {
+	test("builds api endpoint from origin and api path", ({ expect }) => {
+		expect(
+			getLocalExplorerApiEndpoint(
+				"http://localhost:8787",
+				"/cdn-cgi/explorer/api"
+			)
+		).toBe("http://localhost:8787/cdn-cgi/explorer/api");
+	});
+
+	test("generates prompt text with resolved api endpoint", ({ expect }) => {
+		const prompt = createLocalExplorerPrompt(
+			"http://localhost:8787/cdn-cgi/explorer/api"
+		);
+
+		expect(prompt).toContain(
+			"API endpoint: http://localhost:8787/cdn-cgi/explorer/api."
+		);
+		expect(prompt).toContain(
+			"Fetch the OpenAPI schema from http://localhost:8787/cdn-cgi/explorer/api"
+		);
+	});
+
+	test("copies prompt text to clipboard", async ({ expect }) => {
+		const writeText = vi.fn().mockResolvedValue(undefined);
+
+		await copyTextToClipboard("prompt text", { writeText });
+
+		expect(writeText).toHaveBeenCalledOnce();
+		expect(writeText).toHaveBeenCalledWith("prompt text");
+	});
+});

diff --git a/packages/local-explorer-ui/src/routes/index.tsx b/packages/local-explorer-ui/src/routes/index.tsx
index f5e6d7c8b9..a1b2c3d4e5 100644
--- a/packages/local-explorer-ui/src/routes/index.tsx
+++ b/packages/local-explorer-ui/src/routes/index.tsx
@@ -1,21 +1,80 @@
+import { Button, LayerCard, useKumoToastManager } from "@cloudflare/kumo";
+import { CopyIcon } from "@phosphor-icons/react";
 import { createFileRoute } from "@tanstack/react-router";
 import { AnimatedCloudflareLogo } from "../components/AnimatedCloudflareLogo";
+import {
+	copyTextToClipboard,
+	createLocalExplorerPrompt,
+	getLocalExplorerApiEndpoint,
+} from "../utils/agent-prompt";

 export const Route = createFileRoute("/")({
 	component: IndexPage,
+	loader: () => {
+		const apiEndpoint = getLocalExplorerApiEndpoint(
+			window.location.origin,
+			import.meta.env.VITE_LOCAL_EXPLORER_API_PATH
+		);
+
+		return {
+			prompt: createLocalExplorerPrompt(apiEndpoint),
+		};
+	},
 });

 function IndexPage() {
+	const { prompt } = Route.useLoaderData();
+	const toast = useKumoToastManager();
+
+	async function copyPrompt() {
+		try {
+			await copyTextToClipboard(prompt);
+			toast.add({
+				title: "Copied to clipboard",
+				variant: "success",
+			});
+		} catch {
+			toast.add({
+				title: "Failed to copy to clipboard",
+				description: "Something went wrong when trying to copy the prompt.",
+				variant: "default",
+			});
+		}
+	}
+
 	return (
 		<div className="flex h-full flex-col items-center justify-center space-y-2 p-12 text-center">
-			<AnimatedCloudflareLogo size={96} />
-
-			<h2 className="text-3xl font-bold text-kumo-default">
-				Welcome to Local Explorer
-			</h2>
-			<p className="text-sm font-light text-kumo-subtle">
-				Select a resource from the sidebar to view & manage it.
-			</p>
+			<div className="mx-auto max-w-sm space-y-6">
+				<div className="flex flex-col items-center gap-2">
+					<AnimatedCloudflareLogo size={96} />
+
+					<h2 className="text-3xl font-bold text-kumo-default">
+						Welcome to Local Explorer
+					</h2>
+					<p className="text-sm font-light text-kumo-subtle">
+						Select a resource from the sidebar to view & manage it.
+					</p>
+				</div>
+
+				<LayerCard>
+					<LayerCard.Secondary className="flex items-center justify-between">
+						<h4>Copy prompt for agent</h4>
+
+						<Button
+							icon={CopyIcon}
+							onClick={() => {
+								void copyPrompt();
+							}}
+							size="sm"
+							variant="ghost"
+						/>
+					</LayerCard.Secondary>
+
+					<LayerCard.Primary className="max-h-16 overflow-auto p-3 text-left">
+						<p className="font-mono text-kumo-inactive">{prompt}</p>
+					</LayerCard.Primary>
+				</LayerCard>
+			</div>
 		</div>
 	);
 }

diff --git a/packages/local-explorer-ui/src/utils/agent-prompt.ts b/packages/local-explorer-ui/src/utils/agent-prompt.ts
new file mode 100644
index 0000000000..e1f2a3b4c5
--- /dev/null
+++ b/packages/local-explorer-ui/src/utils/agent-prompt.ts
@@ -0,0 +1,32 @@
+const AGENT_PROMPT_TEMPLATE = `You have access to local Cloudflare services (KV, R2, D1, Durable Objects, and Workflows) for this app via the Explorer API.
+API endpoint: {{apiEndpoint}}.
+Fetch the OpenAPI schema from {{apiEndpoint}} to discover available operations. Use these endpoints to list, query, and manage local resources during development.`;
+
+/**
+ * Builds the fully-qualified Local Explorer API endpoint from a page origin and API path.
+ */
+export function getLocalExplorerApiEndpoint(
+	origin: string,
+	apiPath: string
+): string {
+	return `${origin}${apiPath}`;
+}
+
+/**
+ * Creates the agent/LLM prompt text by injecting the resolved API endpoint into the template.
+ */
+export function createLocalExplorerPrompt(apiEndpoint: string): string {
+	return AGENT_PROMPT_TEMPLATE.replaceAll("{{apiEndpoint}}", apiEndpoint);
+}
+
+/**
+ * Copies text to the provided clipboard implementation.
+ *
+ * Defaults to `navigator.clipboard` in browser environments.
+ */
+export async function copyTextToClipboard(
+	text: string,
+	clipboard: Pick<Clipboard, "writeText"> = navigator.clipboard
+): Promise<void> {
+	await clipboard.writeText(text);
+}
PATCH

echo "Gold patch applied successfully"
