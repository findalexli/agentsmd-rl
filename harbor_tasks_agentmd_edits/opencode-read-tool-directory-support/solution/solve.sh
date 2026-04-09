#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opencode

# Idempotent: skip if already applied
if grep -q '<type>directory</type>' packages/opencode/src/tool/read.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.opencode/skill/bun-file-io/SKILL.md b/.opencode/skill/bun-file-io/SKILL.md
index ea39507d2690..f78de330943e 100644
--- a/.opencode/skill/bun-file-io/SKILL.md
+++ b/.opencode/skill/bun-file-io/SKILL.md
@@ -32,6 +32,9 @@ description: Use this when you are working on file operations like reading, writ
 - Decode tool stderr with `Bun.readableStreamToText`.
 - For large writes, use `Bun.write(Bun.file(path), text)`.

+NOTE: Bun.file(...).exists() will return `false` if the value is a directory.
+Use Filesystem.exists(...) instead if path can be file or directory
+
 ## Quick checklist

 - Use Bun APIs first.
diff --git a/packages/opencode/src/tool/edit.txt b/packages/opencode/src/tool/edit.txt
index 863efb8409c0..618fd5ad1ef8 100644
--- a/packages/opencode/src/tool/edit.txt
+++ b/packages/opencode/src/tool/edit.txt
@@ -2,9 +2,9 @@ Performs exact string replacements in files.

 Usage:
 - You must use your `Read` tool at least once in the conversation before editing. This tool will error if you attempt an edit without reading the file.
-- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: spaces + line number + tab. Everything after that tab is the actual file content to match. Never include any part of the line number prefix in the oldString or newString.
+- When editing text from Read tool output, ensure you preserve the exact indentation (tabs/spaces) as it appears AFTER the line number prefix. The line number prefix format is: line number + colon + space (e.g., `1: `). Everything after that space is the actual file content to match. Never include any part of the line number prefix in the oldString or newString.
 - ALWAYS prefer editing existing files in the codebase. NEVER write new files unless explicitly required.
 - Only use emojis if the user explicitly requests it. Avoid adding emojis to files unless asked.
 - The edit will FAIL if `oldString` is not found in the file with an error "oldString not found in content".
-- The edit will FAIL if `oldString` is found multiple times in the file with an error "oldString found multiple times and requires more code context to uniquely identify the intended match". Either provide a larger string with more surrounding context to make it unique or use `replaceAll` to change every instance of `oldString`.
+- The edit will FAIL if `oldString` is found multiple times in the file with an error "Found multiple matches for oldString. Provide more surrounding lines in oldString to identify the correct match." Either provide a larger string with more surrounding context to make it unique or use `replaceAll` to change every instance of `oldString`.
 - Use `replaceAll` for replacing and renaming strings across the file. This parameter is useful if you want to rename a variable for instance.
diff --git a/packages/opencode/src/tool/read.ts b/packages/opencode/src/tool/read.ts
index f230cdf44cbb..d3bff27d6331 100644
--- a/packages/opencode/src/tool/read.ts
+++ b/packages/opencode/src/tool/read.ts
@@ -17,9 +17,9 @@ const MAX_BYTES = 50 * 1024
 export const ReadTool = Tool.define("read", {
   description: DESCRIPTION,
   parameters: z.object({
-    filePath: z.string().describe("The path to the file to read"),
-    offset: z.coerce.number().describe("The line number to start reading from (0-based)").optional(),
-    limit: z.coerce.number().describe("The number of lines to read (defaults to 2000)").optional(),
+    filePath: z.string().describe("The absolute path to the file or directory to read"),
+    offset: z.coerce.number().describe("The 0-based line offset to start reading from").optional(),
+    limit: z.coerce.number().describe("The maximum number of lines to read (defaults to 2000)").optional(),
   }),
   async execute(params, ctx) {
     let filepath = params.filePath
@@ -28,8 +28,12 @@ export const ReadTool = Tool.define("read", {
     }
     const title = path.relative(Instance.worktree, filepath)

+    const file = Bun.file(filepath)
+    const stat = await file.stat().catch(() => undefined)
+
     await assertExternalDirectory(ctx, filepath, {
       bypass: Boolean(ctx.extra?.["bypassCwdCheck"]),
+      kind: stat?.isDirectory() ? "directory" : "file",
     })

     await ctx.ask({
@@ -39,8 +43,7 @@ export const ReadTool = Tool.define("read", {
       metadata: {},
     })

-    const file = Bun.file(filepath)
-    if (!(await file.exists())) {
+    if (!stat) {
       const dir = path.dirname(filepath)
       const base = path.basename(filepath)

@@ -60,6 +63,47 @@ export const ReadTool = Tool.define("read", {
       throw new Error(`File not found: ${filepath}`)
     }

+    if (stat.isDirectory()) {
+      const dirents = await fs.promises.readdir(filepath, { withFileTypes: true })
+      const entries = await Promise.all(
+        dirents.map(async (dirent) => {
+          if (dirent.isDirectory()) return dirent.name + "/"
+          if (dirent.isSymbolicLink()) {
+            const target = await fs.promises.stat(path.join(filepath, dirent.name)).catch(() => undefined)
+            if (target?.isDirectory()) return dirent.name + "/"
+          }
+          return dirent.name
+        }),
+      )
+      entries.sort((a, b) => a.localeCompare(b))
+
+      const limit = params.limit ?? DEFAULT_READ_LIMIT
+      const offset = params.offset || 0
+      const sliced = entries.slice(offset, offset + limit)
+      const truncated = offset + sliced.length < entries.length
+
+      const output = [
+        `<path>${filepath}</path>`,
+        `<type>directory</type>`,
+        `<entries>`,
+        sliced.join("\n"),
+        truncated
+          ? `\n(Showing ${sliced.length} of ${entries.length} entries. Use 'offset' parameter to read beyond entry ${offset + sliced.length})`
+          : `\n(${entries.length} entries)`,
+        `</entries>`,
+      ].join("\n")
+
+      return {
+        title,
+        output,
+        metadata: {
+          preview: sliced.slice(0, 20).join("\n"),
+          truncated,
+          loaded: [] as string[],
+        },
+      }
+    }
+
     const instructions = await InstructionPrompt.resolve(ctx.messages, filepath, ctx.messageID)

     // Exclude SVG (XML-based) and vnd.fastbidsheet (.fbs extension, commonly FlatBuffers schema files)
@@ -75,7 +119,7 @@ export const ReadTool = Tool.define("read", {
         metadata: {
           preview: msg,
           truncated: false,
-          ...(instructions.length > 0 && { loaded: instructions.map((i) => i.filepath) }),
+          loaded: instructions.map((i) => i.filepath),
         },
         attachments: [
           {
@@ -112,11 +156,11 @@ export const ReadTool = Tool.define("read", {
     }

     const content = raw.map((line, index) => {
-      return `${(index + offset + 1).toString().padStart(5, "0")}| ${line}`
+      return `${index + offset + 1}: ${line}`
     })
     const preview = raw.slice(0, 20).join("\n")

-    let output = "<file>\n"
+    let output = [`<path>${filepath}</path>`, `<type>file</type>`, "<content>"].join("\n")
     output += content.join("\n")

     const totalLines = lines.length
@@ -131,7 +175,7 @@ export const ReadTool = Tool.define("read", {
     } else {
       output += `\n\n(End of file - total ${totalLines} lines)`
     }
-    output += "\n</file>"
+    output += "\n</content>"

     // just warms the lsp client
     LSP.touchFile(filepath, false)
@@ -147,7 +191,7 @@ export const ReadTool = Tool.define("read", {
       metadata: {
         preview,
         truncated,
-        ...(instructions.length > 0 && { loaded: instructions.map((i) => i.filepath) }),
+        loaded: instructions.map((i) => i.filepath),
       },
     }
   },
diff --git a/packages/opencode/src/tool/read.txt b/packages/opencode/src/tool/read.txt
index b5bffee263e3..308aaea54952 100644
--- a/packages/opencode/src/tool/read.txt
+++ b/packages/opencode/src/tool/read.txt
@@ -1,12 +1,13 @@
-Reads a file from the local filesystem. You can access any file directly by using this tool.
-Assume this tool is able to read all files on the machine. If the User provides a path to a file assume that path is valid. It is okay to read a file that does not exist; an error will be returned.
+Read a file or directory from the local filesystem. If the path does not exist, an error is returned.

 Usage:
-- The filePath parameter must be an absolute path, not a relative path
-- By default, it reads up to 2000 lines starting from the beginning of the file
-- You can optionally specify a line offset and limit (especially handy for long files), but it's recommended to read the whole file by not providing these parameters
-- Any lines longer than 2000 characters will be truncated
-- Results are returned using cat -n format, with line numbers starting at 1
-- You have the capability to call multiple tools in a single response. It is always better to speculatively read multiple files as a batch that are potentially useful.
-- If you read a file that exists but has empty contents you will receive a system reminder warning in place of file contents.
-- You can read image files using this tool.
+- The filePath parameter should be an absolute path.
+- By default, this tool returns up to 2000 lines from the start of the file.
+- To read later sections, call this tool again with a larger offset.
+- Use the grep tool to find specific content in large files or files with long lines.
+- If you are unsure of the correct file path, use the glob tool to look up filenames by glob pattern.
+- Contents are returned with each line prefixed by its line number as `<line>: <content>`. For example, if a file has contents "foo\n", you will receive "1: foo\n". For directories, entries are returned one per line (without line numbers) with a trailing `/` for subdirectories.
+- Any line longer than 2000 characters is truncated.
+- Call this tool in parallel when you know there are multiple files you want to read.
+- Avoid tiny repeated slices (30 line chunks). If you need more context, read a larger window.
+- This tool can read image files and PDFs and return them as file attachments.
diff --git a/packages/opencode/test/tool/read.test.ts b/packages/opencode/test/tool/read.test.ts
index 187d9a9fc807..d6c5cf439258 100644
--- a/packages/opencode/test/tool/read.test.ts
+++ b/packages/opencode/test/tool/read.test.ts
@@ -78,6 +78,32 @@ describe("tool.read external_directory permission", () => {
     })
   })

+  test("asks for directory-scoped external_directory permission when reading external directory", async () => {
+    await using outerTmp = await tmpdir({
+      init: async (dir) => {
+        await Bun.write(path.join(dir, "external", "a.txt"), "a")
+      },
+    })
+    await using tmp = await tmpdir({ git: true })
+    await Instance.provide({
+      directory: tmp.path,
+      fn: async () => {
+        const read = await ReadTool.init()
+        const requests: Array<Omit<PermissionNext.Request, "id" | "sessionID" | "tool">> = []
+        const testCtx = {
+          ...ctx,
+          ask: async (req: Omit<PermissionNext.Request, "id" | "sessionID" | "tool">) => {
+            requests.push(req)
+          },
+        }
+        await read.execute({ filePath: path.join(outerTmp.path, "external") }, testCtx)
+        const extDirReq = requests.find((r) => r.permission === "external_directory")
+        expect(extDirReq).toBeDefined()
+        expect(extDirReq!.patterns).toContain(path.join(outerTmp.path, "external", "*"))
+      },
+    })
+  })
+
   test("asks for external_directory permission when reading relative path outside project", async () => {
     await using tmp = await tmpdir({ git: true })
     await Instance.provide({
@@ -249,6 +275,25 @@ describe("tool.read truncation", () => {
     })
   })

+  test("does not mark final directory page as truncated", async () => {
+    await using tmp = await tmpdir({
+      init: async (dir) => {
+        await Promise.all(
+          Array.from({ length: 10 }, (_, i) => Bun.write(path.join(dir, "dir", `file-${i}.txt`), `line${i}`)),
+        )
+      },
+    })
+    await Instance.provide({
+      directory: tmp.path,
+      fn: async () => {
+        const read = await ReadTool.init()
+        const result = await read.execute({ filePath: path.join(tmp.path, "dir"), offset: 5, limit: 5 }, ctx)
+        expect(result.metadata.truncated).toBe(false)
+        expect(result.output).not.toContain("Showing 5 of 10 entries")
+      },
+    })
+  })
+
   test("truncates long lines", async () => {
     await using tmp = await tmpdir({
       init: async (dir) => {

PATCH

echo "Patch applied successfully."
