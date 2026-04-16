#!/bin/bash
set -e

# Apply the gold patch for cline/cline PR #9773
# This adds MCP server shortcuts to the CLI

cd /workspace/cline

# Apply the patch using git apply
git apply <<'PATCH'
diff --git a/cli/src/index.test.ts b/cli/src/index.test.ts
index c5dfec6b771..dd33c6a328c 100644
--- a/cli/src/index.test.ts
+++ b/cli/src/index.test.ts
@@ -67,6 +67,17 @@ describe("CLI Commands", () => {
 			.option("--config <path>", "Configuration directory")
 			.action(() => {})

+		const mcpCommand = program.command("mcp").description("Manage MCP servers")
+		mcpCommand
+			.command("add")
+			.description("Add an MCP server shortcut")
+			.argument("<name>", "MCP server name")
+			.argument("[targetOrCommand...]", "Command args for stdio, or URL for remote")
+			.option("--type <type>", "Transport type", "stdio")
+			.option("-c, --cwd <path>", "Working directory")
+			.option("--config <path>", "Configuration directory")
+			.action(() => {})
+
 		program
 			.command("kanban")
 			.description("Run npx kanban --agent cline")
@@ -331,6 +342,32 @@ describe("CLI Commands", () => {
 		})
 	})

+	describe("mcp command", () => {
+		it("should parse mcp add stdio syntax", () => {
+			const args = ["node", "cli", "mcp", "add", "kanban", "--", "kanban", "mcp"]
+			program.parse(args)
+		})
+
+		it("should parse mcp add remote http syntax", () => {
+			const args = ["node", "cli", "mcp", "add", "linear", "https://mcp.linear.app/mcp", "--type", "http"]
+			program.parse(args)
+		})
+
+		it("should default mcp add type to stdio", () => {
+			const mcpCmd = program.commands.find((c) => c.name() === "mcp")!
+			const addCmd = mcpCmd.commands.find((c) => c.name() === "add")!
+			addCmd.parse(["kanban", "--", "kanban", "mcp"], { from: "user" })
+			expect(addCmd.opts().type).toBe("stdio")
+		})
+
+		it("should parse mcp add type option", () => {
+			const mcpCmd = program.commands.find((c) => c.name() === "mcp")!
+			const addCmd = mcpCmd.commands.find((c) => c.name() === "add")!
+			addCmd.parse(["linear", "https://mcp.linear.app/mcp", "--type", "http"], { from: "user" })
+			expect(addCmd.opts().type).toBe("http")
+		})
+	})
+
 	describe("default command (interactive mode)", () => {
 		it("should parse optional prompt argument", () => {
 			const args = ["node", "cli", "do something"]
@@ -395,6 +432,7 @@ describe("CLI Commands", () => {
 			expect(commandNames).toContain("history")
 			expect(commandNames).toContain("config")
 			expect(commandNames).toContain("auth")
+			expect(commandNames).toContain("mcp")
 			expect(commandNames).toContain("kanban")
 		})


diff --git a/cli/src/index.ts b/cli/src/index.ts
index 0fc423cbba8..def6245435f 100644
--- a/cli/src/index.ts
+++ b/cli/src/index.ts
@@ -35,6 +35,7 @@ import { CliWebviewProvider } from "./controllers/CliWebviewProvider"
 import { isAuthConfigured } from "./utils/auth"
 import { restoreConsole, suppressConsoleUnlessVerbose } from "./utils/console"
 import { printInfo, printWarning } from "./utils/display"
+import { addMcpServerShortcut, type McpAddOptions } from "./utils/mcp"
 import { selectOutputMode } from "./utils/mode-selection"
 import { parseImagesFromInput, processImagePaths } from "./utils/parser"
 import { CLINE_CLI_DIR, getCliBinaryPath } from "./utils/path"
@@ -269,6 +270,17 @@ function runKanbanAlias(): void {
 	})
 }

+async function addMcpServer(name: string, targetOrCommand: string[] = [], options: McpAddOptions): Promise<void> {
+	try {
+		const result = await addMcpServerShortcut(name, targetOrCommand, options)
+		const transportLabel = result.transportType === "streamableHttp" ? "http" : result.transportType
+		printInfo(`Added MCP server '${result.serverName}' (${transportLabel}) to ${result.settingsPath}`)
+	} catch (error) {
+		printWarning(error instanceof Error ? error.message : "Failed to add MCP server.")
+		exit(1)
+	}
+}
+
 /**
  * Run a task in plain text mode (no Ink UI).
  * Handles auth check, task execution, cleanup, and exit.
@@ -864,6 +876,18 @@ program
 	.option("--config <path>", "Path to Cline configuration directory")
 	.action(runAuth)

+const mcpCommand = program.command("mcp").description("Manage MCP servers")
+
+mcpCommand
+	.command("add")
+	.description("Add an MCP server shortcut to cline_mcp_settings.json")
+	.argument("<name>", "MCP server name")
+	.argument("[targetOrCommand...]", "For stdio: use -- <command> [args]. For http/sse: provide <url>.")
+	.option("--type <type>", "Transport type: stdio (default), http, or sse", "stdio")
+	.option("-c, --cwd <path>", "Working directory for config resolution")
+	.option("--config <path>", "Path to Cline configuration directory")
+	.action(addMcpServer)
+
 program
 	.command("version")
 	.description("Show Cline CLI version number")
diff --git a/cli/src/utils/mcp.test.ts b/cli/src/utils/mcp.test.ts
new file mode 100644
index 00000000000..bf1b8da76c3
--- /dev/null
+++ b/cli/src/utils/mcp.test.ts
@@ -0,0 +1,63 @@
+import * as fs from "node:fs/promises"
+import os from "node:os"
+import path from "node:path"
+import { afterEach, describe, expect, it } from "vitest"
+import { addMcpServerShortcut } from "./mcp"
+
+const tempDirs: string[] = []
+
+async function createTempConfigDir(): Promise<string> {
+	const dir = await fs.mkdtemp(path.join(os.tmpdir(), "cline-mcp-test-"))
+	tempDirs.push(dir)
+	return dir
+}
+
+type McpSettingsFile = {
+	mcpServers: Record<string, Record<string, unknown>>
+}
+
+async function readMcpSettings(configDir: string): Promise<McpSettingsFile> {
+	const settingsPath = path.join(configDir, "data", "settings", "cline_mcp_settings.json")
+	return JSON.parse(await fs.readFile(settingsPath, "utf-8")) as McpSettingsFile
+}
+
+afterEach(async () => {
+	for (const dir of tempDirs.splice(0, tempDirs.length)) {
+		await fs.rm(dir, { recursive: true, force: true })
+	}
+})
+
+describe("addMcpServerShortcut", () => {
+	it("writes stdio servers with type=stdio", async () => {
+		const configDir = await createTempConfigDir()
+
+		await addMcpServerShortcut("kanban", ["kanban", "mcp"], { config: configDir })
+		const settings = await readMcpSettings(configDir)
+
+		expect(settings.mcpServers.kanban).toEqual({
+			command: "kanban",
+			args: ["mcp"],
+			type: "stdio",
+		})
+	})
+
+	it("maps --type http to streamableHttp", async () => {
+		const configDir = await createTempConfigDir()
+
+		await addMcpServerShortcut("linear", ["https://mcp.linear.app/mcp"], { config: configDir, type: "http" })
+		const settings = await readMcpSettings(configDir)
+
+		expect(settings.mcpServers.linear).toEqual({
+			url: "https://mcp.linear.app/mcp",
+			type: "streamableHttp",
+		})
+	})
+
+	it("errors when URL is provided without --type http", async () => {
+		const configDir = await createTempConfigDir()
+
+		await expect(addMcpServerShortcut("linear", ["https://mcp.linear.app/mcp"], { config: configDir })).rejects.toThrow(
+			"Use --type http",
+		)
+	})
+})
diff --git a/cli/src/utils/mcp.ts b/cli/src/utils/mcp.ts
new file mode 100644
index 00000000000..67710a09efe
--- /dev/null
+++ b/cli/src/utils/mcp.ts
@@ -0,0 +1,159 @@
+import * as fs from "node:fs/promises"
+import path from "node:path"
+import { getMcpSettingsFilePath } from "@/core/storage/disk"
+import { ServerConfigSchema } from "@/services/mcp/schemas"
+import { initializeCliContext } from "../vscode-context"
+
+export interface McpAddOptions {
+	type?: string
+	config?: string
+	cwd?: string
+}
+
+export type McpAddTransportType = "stdio" | "streamableHttp" | "sse"
+
+export interface AddMcpServerResult {
+	serverName: string
+	transportType: McpAddTransportType
+	settingsPath: string
+}
+
+function normalizeMcpTransportType(value?: string): McpAddTransportType {
+	const normalized = (value || "stdio").trim().toLowerCase()
+
+	switch (normalized) {
+		case "stdio":
+			return "stdio"
+		case "http":
+		case "streamable-http":
+		case "streamablehttp":
+			return "streamableHttp"
+		case "sse":
+			return "sse"
+		default:
+			throw new Error(`Invalid MCP transport type '${value}'. Valid values: stdio, http, sse.`)
+	}
+}
+
+function parseMcpSettings(content: string, settingsPath: string): Record<string, unknown> {
+	const trimmedContent = content.trim()
+	if (!trimmedContent) {
+		return { mcpServers: {} }
+	}
+
+	let parsed: unknown
+	try {
+		parsed = JSON.parse(content)
+	} catch {
+		throw new Error(`Invalid JSON in ${settingsPath}. Please fix the file and try again.`)
+	}
+
+	if (!parsed || typeof parsed !== "object" || Array.isArray(parsed)) {
+		throw new Error(`Invalid MCP settings file at ${settingsPath}. Expected a JSON object.`)
+	}
+
+	const settings = parsed as Record<string, unknown>
+	if (settings.mcpServers === undefined) {
+		settings.mcpServers = {}
+	}
+
+	if (!settings.mcpServers || typeof settings.mcpServers !== "object" || Array.isArray(settings.mcpServers)) {
+		throw new Error(`Invalid MCP settings file at ${settingsPath}. Expected 'mcpServers' to be an object.`)
+	}
+
+	return settings
+}
+
+function createMcpServerConfig(targetOrCommand: string[], transportType: McpAddTransportType): Record<string, unknown> {
+	if (transportType === "stdio") {
+		if (targetOrCommand.length < 1) {
+			throw new Error("Missing stdio command. Example: cline mcp add kanban -- kanban mcp")
+		}
+
+		// Guard against common mistake:
+		// `cline mcp add <name> <url>` without `--type http`
+		if (targetOrCommand.length === 1) {
+			const [value] = targetOrCommand
+			try {
+				const parsedUrl = new URL(value)
+				if (parsedUrl.protocol === "http:" || parsedUrl.protocol === "https:") {
+					throw new Error(
+						`Looks like you provided a URL for '${value}'. Use --type http, for example: cline mcp add <name> ${value} --type http`,
+					)
+				}
+			} catch (error) {
+				if (error instanceof Error && error.message.startsWith("Looks like you provided a URL")) {
+					throw error
+				}
+			}
+		}
+
+		const [command, ...args] = targetOrCommand
+		const config: Record<string, unknown> = {
+			command,
+			type: "stdio",
+		}
+
+		if (args.length > 0) {
+			config.args = args
+		}
+
+		ServerConfigSchema.parse(config)
+		return config
+	}
+
+	if (targetOrCommand.length !== 1) {
+		throw new Error(
+			"HTTP/SSE MCP servers require exactly one URL. Example: cline mcp add linear https://mcp.linear.app/mcp --type http",
+		)
+	}
+
+	const config = {
+		url: targetOrCommand[0],
+		type: transportType,
+	}
+
+	ServerConfigSchema.parse(config)
+	return config
+}
+
+export async function addMcpServerShortcut(
+	name: string,
+	targetOrCommand: string[] = [],
+	options: McpAddOptions,
+): Promise<AddMcpServerResult> {
+	const trimmedName = name.trim()
+	if (!trimmedName) {
+		throw new Error("Server name is required.")
+	}
+
+	const transportType = normalizeMcpTransportType(options.type)
+
+	const { DATA_DIR } = initializeCliContext({
+		clineDir: options.config,
+		workspaceDir: options.cwd || process.cwd(),
+	})
+
+	const settingsDirectoryPath = path.join(DATA_DIR, "settings")
+	await fs.mkdir(settingsDirectoryPath, { recursive: true })
+	const settingsPath = await getMcpSettingsFilePath(settingsDirectoryPath)
+
+	const content = await fs.readFile(settingsPath, "utf-8")
+	const settings = parseMcpSettings(content, settingsPath)
+	const mcpServers = settings.mcpServers as Record<string, unknown>
+
+	if (mcpServers[trimmedName]) {
+		throw new Error(`An MCP server named '${trimmedName}' already exists.`)
+	}
+
+	const serverConfig = createMcpServerConfig(targetOrCommand, transportType)
+	mcpServers[trimmedName] = serverConfig
+
+	await fs.writeFile(settingsPath, `${JSON.stringify(settings, null, 2)}\n`, "utf-8")
+
+	return {
+		serverName: trimmedName,
+		transportType,
+		settingsPath,
+	}
+}
diff --git a/docs/cline-cli/configuration.mdx b/docs/cline-cli/configuration.mdx
index d33f1a78828..57c0b1c9571 100644
--- a/docs/cline-cli/configuration.mdx
+++ b/docs/cline-cli/configuration.mdx
@@ -180,13 +180,23 @@ Cline CLI supports [MCP (Model Context Protocol)](/mcp/mcp-overview) servers, gi

 ### Setting Up MCP Servers

-To configure MCP servers for the CLI, create or edit the settings file at:
+You can add MCP servers from the CLI:
+
+```bash
+# STDIO server
+cline mcp add kanban -- kanban mcp
+
+# Remote HTTP server
+cline mcp add linear https://mcp.linear.app/mcp --type http
+```
+
+These commands update:

 ```
 ~/.cline/data/settings/cline_mcp_settings.json
 ```

-The file uses the same JSON format as the VS Code extension:
+You can still edit this file directly. It uses the same JSON format as the VS Code extension:

 ```json
 {
@@ -207,7 +217,7 @@ The file uses the same JSON format as the VS Code extension:
 For the full configuration reference including STDIO and SSE transport types, see [Adding and Configuring MCP Servers](/mcp/adding-and-configuring-servers).

 <Note>
-The CLI does not yet have a `/mcp` slash command for managing MCP servers interactively. For now, you'll need to edit the `cline_mcp_settings.json` file directly.
+The CLI does not yet have a `/mcp` slash command for interactive management inside the terminal UI. Use `cline mcp add` or edit `cline_mcp_settings.json` directly.
 </Note>

 ### Custom Config Directory
PATCH

# Verify the patch was applied
if grep -q "addMcpServerShortcut" cli/src/index.ts; then
    echo "Patch applied successfully - addMcpServerShortcut found in index.ts"
else
    echo "ERROR: Patch may not have been applied correctly"
    exit 1
fi

# Note: Typecheck is skipped because the base commit has pre-existing type errors
# (missing dependencies like @anthropic-ai/sdk, vscode, etc.) that are unrelated
# to our changes. The pytest tests validate file structure and syntax.

echo "Solve script completed successfully"
