#!/bin/bash
set -e

cd /workspace/ui

# Apply the fix for packageManager handling in monorepos
cat <<'PATCH' | git apply -
diff --git a/packages/shadcn/src/templates/create-template.ts b/packages/shadcn/src/templates/create-template.ts
index 5a438b58ab1..602c20d96d6 100644
--- a/packages/shadcn/src/templates/create-template.ts
+++ b/packages/shadcn/src/templates/create-template.ts
@@ -124,12 +124,20 @@ async function adaptWorkspaceConfig(

   const isMonorepo = fs.existsSync(pnpmWorkspacePath)

-  // Update root package.json: strip "packageManager" field to avoid
-  // triggering Corepack, and add "workspaces" for npm/bun/yarn.
+  // Update root package.json: update "packageManager" field for the
+  // target package manager, and add "workspaces" for npm/bun/yarn.
   if (fs.existsSync(packageJsonPath)) {
     const packageJsonContent = await fs.readFile(packageJsonPath, "utf8")
     const packageJson = JSON.parse(packageJsonContent)
-    delete packageJson.packageManager
+
+    if (isMonorepo) {
+      // Monorepo templates use turbo which requires packageManager.
+      // Replace the pnpm value with the target package manager.
+      packageJson.packageManager =
+        await getPackageManagerVersion(packageManager)
+    } else {
+      delete packageJson.packageManager
+    }

     if (isMonorepo) {
       // Read workspace patterns from pnpm-workspace.yaml.
@@ -160,6 +168,16 @@ async function adaptWorkspaceConfig(
   }
 }

+// Get the package manager name and version string (e.g. "bun@1.2.0").
+async function getPackageManagerVersion(packageManager: string) {
+  try {
+    const { stdout } = await execa(packageManager, ["--version"])
+    return `${packageManager}@${stdout.trim()}`
+  } catch {
+    return `${packageManager}@*`
+  }
+}
+
 // Recursively find all package.json files and replace workspace: protocol
 // version specifiers with "*", which npm understands.
 async function rewriteWorkspaceProtocol(dir: string) {
PATCH

# Apply the test updates for scaffold.test.ts
cat <<'PATCH' | git apply -
diff --git a/packages/shadcn/src/utils/scaffold.test.ts b/packages/shadcn/src/utils/scaffold.test.ts
index 77f93466..72705694 100644
--- a/packages/shadcn/src/utils/scaffold.test.ts
+++ b/packages/shadcn/src/utils/scaffold.test.ts
@@ -234,7 +234,7 @@ describe("defaultScaffold", () => {
     )
   })

-  it("should strip packageManager field from package.json for non-pnpm", async () => {
+  it("should strip packageManager field from package.json for non-pnpm non-monorepo", async () => {
     vi.mocked(fs.existsSync).mockImplementation((p: any) =>
       p.toString().includes("package.json")
     )
@@ -279,6 +279,14 @@ describe("defaultScaffold", () => {
       )
     }) as any)

+    // Mock execa to return a version for bun --version.
+    vi.mocked(execa).mockImplementation(((cmd: string, args: string[]) => {
+      if (cmd === "bun" && args[0] === "--version") {
+        return Promise.resolve({ stdout: "1.2.0" } as any)
+      }
+      return Promise.resolve({ stdout: "", exitCode: 0 } as any)
+    }) as any)
+
     const template = createTestTemplate()

     await template.scaffold({
@@ -300,7 +308,7 @@ describe("defaultScaffold", () => {
     expect(adaptCall).toBeDefined()
     const written = JSON.parse(adaptCall![1] as string)
     expect(written.workspaces).toEqual(["apps/*", "packages/*"])
-    expect(written.packageManager).toBeUndefined()
+    expect(written.packageManager).toBe("bun@1.2.0")
   })

   it("should rewrite workspace: protocol refs to * for npm monorepo", async () => {
PATCH

# Idempotency check - distinctive line from the patch
grep -q "Monorepo templates use turbo which requires packageManager" packages/shadcn/src/templates/create-template.ts && echo "Patch applied successfully"
