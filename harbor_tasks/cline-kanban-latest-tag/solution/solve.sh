#!/bin/bash
set -e

cd /workspace/cline

# Apply the gold patch for kanban@latest fix - index.ts
cat <<'PATCH' | git apply -
diff --git a/cli/src/index.ts b/cli/src/index.ts
index 1cce9152aa6..49063718023 100644
--- a/cli/src/index.ts
+++ b/cli/src/index.ts
@@ -256,12 +256,12 @@ function getNpxCommand(): string {
 }

 function runKanbanAlias(): void {
-	const child = spawn(getNpxCommand(), ["-y", "kanban", "--agent", "cline"], {
+	const child = spawn(getNpxCommand(), ["-y", "kanban@latest", "--agent", "cline"], {
 		stdio: "inherit",
 	})

 	child.on("error", () => {
-		printWarning("Failed to run 'npx kanban --agent cline'. Make sure npx is installed and available in PATH.")
+		printWarning("Failed to run 'npx kanban@latest --agent cline'. Make sure npx is installed and available in PATH.")
 		exit(1)
 	})

@@ -899,7 +899,7 @@ program
 	.option("-v, --verbose", "Show verbose output")
 	.action(() => checkForUpdates(CLI_VERSION))

-program.command("kanban").description("Run npx kanban --agent cline").action(runKanbanAlias)
+program.command("kanban").description("Run npx kanban@latest --agent cline").action(runKanbanAlias)

 // Dev command with subcommands
 const devCommand = program.command("dev").description("Developer tools and utilities")
@@ -1050,7 +1050,7 @@ program
 	.option("--auto-condense", "Enable AI-powered context compaction instead of mechanical truncation")
 	.option("--hooks-dir <path>", "Path to additional hooks directory for runtime hook injection")
 	.option("--acp", "Run in ACP (Agent Client Protocol) mode for editor integration")
-	.option("--kanban", "Run npx kanban --agent cline")
+	.option("--kanban", "Run npx kanban@latest --agent cline")
 	.option("-T, --taskId <id>", "Resume an existing task by ID")
 	.option("--continue", "Resume the most recent task from the current working directory")
 	.action(async (prompt, options) => {
PATCH

# Update the test file using sed
sed -i 's/Run npx kanban --agent cline/Run npx kanban@latest --agent cline/g' cli/src/index.test.ts

# Verify the patches were applied
if ! grep -q "kanban@latest" cli/src/index.ts; then
    echo "ERROR: index.ts patch was not applied successfully"
    exit 1
fi

if ! grep -q "kanban@latest" cli/src/index.test.ts; then
    echo "ERROR: index.test.ts patch was not applied successfully"
    exit 1
fi

echo "Patches applied successfully"
