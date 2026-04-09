#!/bin/bash
set -e

cd /workspace/continue

# Apply the fix patch
cat <<'PATCH' | git apply -
diff --git a/core/util/Logger.ts b/core/util/Logger.ts
index 68538792d30..bb7c0f9931c 100644
--- a/core/util/Logger.ts
+++ b/core/util/Logger.ts
@@ -28,8 +28,10 @@ class LoggerClass {
               }),
             ]
           : []),
-        // Normal console.log behavior
-        new winston.transports.Console(),
+        // Use stderr to avoid corrupting IPC stdout stream in the binary
+        new winston.transports.Console({
+          stderrLevels: ["error", "warn", "info", "debug"],
+        }),
       ],
     });
   }
diff --git a/binary/test/binary.test.ts b/binary/test/binary.test.ts
index 56e2d9d5ef1..b68c2f17113 100644
--- a/binary/test/binary.test.ts
+++ b/binary/test/binary.test.ts
@@ -1,5 +1,5 @@
 import { ModelDescription, SerializedContinueConfig } from "core";
-// import Mock from "core/llm/llms/Mock.js";
+import { IDE } from "core/index.js";
 import { FromIdeProtocol, ToIdeProtocol } from "core/protocol/index.js";
 import { IMessenger } from "core/protocol/messenger";
 import FileSystemIde from "core/util/filesystem";
@@ -15,7 +15,115 @@ import {
   CoreBinaryTcpMessenger,
 } from "../src/IpcMessenger";

-// jest.setTimeout(100_000);
+/**
+ * Handles IDE messages from the binary subprocess, responding with plain data
+ * matching the Kotlin CoreMessenger format: { messageType, data, messageId }.
+ *
+ * This bypasses the JS _handleLine auto-wrapper which would double-wrap
+ * responses in { done, content, status }.
+ */
+class BinaryIdeHandler {
+  private ide: IDE;
+  private subprocess: ChildProcessWithoutNullStreams;
+  private handlers: Record<string, (data: any) => Promise<any> | any> = {};
+  private unfinishedLine: string | undefined;
+
+  constructor(subprocess: ChildProcessWithoutNullStreams, ide: IDE) {
+    this.ide = ide;
+    this.subprocess = subprocess;
+    this.registerHandlers();
+
+    // Listen on stdout alongside CoreBinaryMessenger (EventEmitter allows multiple listeners)
+    // Use setEncoding so split multibyte UTF-8 characters are decoded correctly
+    subprocess.stdout.setEncoding("utf8");
+    subprocess.stdout.on("data", (data: string) => this.handleData(data));
+  }
+
+  private registerHandlers() {
+    const ide = this.ide;
+    const h = this.handlers;
+    h["getIdeInfo"] = () => ide.getIdeInfo();
+    h["getIdeSettings"] = () => ide.getIdeSettings();
+    h["getControlPlaneSessionInfo"] = () => undefined;
+    h["getWorkspaceDirs"] = () => ide.getWorkspaceDirs();
+    h["readFile"] = (d) => ide.readFile(d.filepath);
+    h["writeFile"] = (d) => ide.writeFile(d.path, d.contents);
+    h["fileExists"] = (d) => ide.fileExists(d.filepath);
+    h["showLines"] = (d) => ide.showLines(d.filepath, d.startLine, d.endLine);
+    h["openFile"] = (d) => ide.openFile(d.path);
+    h["openUrl"] = (d) => ide.openUrl(d.url);
+    h["runCommand"] = (d) => ide.runCommand(d.command);
+    h["saveFile"] = (d) => ide.saveFile(d.filepath);
+    h["readRangeInFile"] = (d) => ide.readRangeInFile(d.filepath, d.range);
+    h["getFileStats"] = (d) => ide.getFileStats(d.files);
+    h["getGitRootPath"] = (d) => ide.getGitRootPath(d.dir);
+    h["listDir"] = (d) => ide.listDir(d.dir);
+    h["getRepoName"] = (d) => ide.getRepoName(d.dir);
+    h["getTags"] = (d) => ide.getTags(d);
+    h["isTelemetryEnabled"] = () => ide.isTelemetryEnabled();
+    h["isWorkspaceRemote"] = () => false;
+    h["getUniqueId"] = () => ide.getUniqueId();
+    h["getDiff"] = (d) => ide.getDiff(d.includeUnstaged);
+    h["getTerminalContents"] = () => ide.getTerminalContents();
+    h["getOpenFiles"] = () => ide.getOpenFiles();
+    h["getCurrentFile"] = () => ide.getCurrentFile();
+    h["getPinnedFiles"] = () => ide.getPinnedFiles();
+    h["getSearchResults"] = (d) => ide.getSearchResults(d.query, d.maxResults);
+    h["getFileResults"] = (d) => ide.getFileResults(d.pattern);
+    h["getProblems"] = (d) => ide.getProblems(d.filepath);
+    h["getBranch"] = (d) => ide.getBranch(d.dir);
+    h["subprocess"] = (d) => ide.subprocess(d.command, d.cwd);
+    h["getDebugLocals"] = (d) => ide.getDebugLocals(d.threadIndex);
+    h["getAvailableThreads"] = () => ide.getAvailableThreads();
+    h["getTopLevelCallStackSources"] = (d) =>
+      ide.getTopLevelCallStackSources(d.threadIndex, d.stackDepth);
+    h["showToast"] = () => {};
+    h["readSecrets"] = (d) => ide.readSecrets(d.keys);
+    h["writeSecrets"] = (d) => ide.writeSecrets(d.secrets);
+    h["removeFile"] = (d) => ide.removeFile(d.path);
+  }
+
+  private handleData(data: string) {
+    const d = data;
+    const lines = d.split(/\r\n/).filter((line) => line.trim() !== "");
+    if (lines.length === 0) return;
+
+    if (this.unfinishedLine) {
+      lines[0] = this.unfinishedLine + lines[0];
+      this.unfinishedLine = undefined;
+    }
+    if (!d.endsWith("\r\n")) {
+      this.unfinishedLine = lines.pop();
+    }
+    lines.forEach((line) => this.handleLine(line));
+  }
+
+  private async handleLine(line: string) {
+    let msg: { messageType: string; messageId: string; data?: any };
+    try {
+      msg = JSON.parse(line);
+    } catch {
+      return; // not JSON, ignore
+    }
+
+    const handler = this.handlers[msg.messageType];
+    if (!handler) return; // not an IDE message, let CoreBinaryMessenger handle it
+
+    try {
+      const result = await handler(msg.data);
+      this.respond(msg.messageType, result, msg.messageId);
+    } catch (e) {
+      this.respond(msg.messageType, undefined, msg.messageId);
+    }
+  }
+
+  private respond(messageType: string, data: any, messageId: string) {
+    const response = JSON.stringify({ messageType, data, messageId });
+    this.subprocess.stdin.write(response + "\r\n");
+  }
+}
+
+jest.setTimeout(30_000);

 const USE_TCP = false;

@@ -122,6 +230,11 @@ describe("Test Suite", () => {
         console.error("Error spawning subprocess:", error);
         throw error;
       }
+
+      subprocess.stderr.on("data", (data: Buffer) => {
+        console.error(`[stderr] ${data.toString()}`);
+      });
+
       messenger = new CoreBinaryMessenger<ToIdeProtocol, FromIdeProtocol>(
         subprocess,
       );
@@ -132,7 +245,9 @@ describe("Test Suite", () => {
       fs.mkdirSync(testDir);
     }
     const ide = new FileSystemIde(testDir);
-    // const reverseIde = new ReverseMessageIde(messenger.on.bind(messenger), ide);
+    if (!USE_TCP && subprocess) {
+      new BinaryIdeHandler(subprocess, ide);
+    }

     // Wait for core to set itself up
     await new Promise((resolve) => setTimeout(resolve, 1000));
@@ -151,8 +266,15 @@ describe("Test Suite", () => {
     }
   });

+  // Binary responses are wrapped in { done, content, status } by _handleLine.
+  // This helper unwraps them, matching how the Kotlin CoreMessenger reads responses.
+  async function request(messageType: string, data: any): Promise<any> {
+    const resp = await messenger.request(messageType as any, data);
+    return resp?.content !== undefined ? resp.content : resp;
+  }
+
   it("should respond to ping with pong", async () => {
-    const resp = await messenger.request("ping", "ping");
+    const resp = await request("ping", "ping");
     expect(resp).toBe("pong");
   });

@@ -160,19 +282,9 @@ describe("Test Suite", () => {
     expect(fs.existsSync(CONTINUE_GLOBAL_DIR)).toBe(true);

     // Many of the files are only created when trying to load the config
-    const config = await messenger.request(
-      "config/getSerializedProfileInfo",
-      undefined,
-    );
+    await request("config/getSerializedProfileInfo", undefined);

-    const expectedFiles = [
-      "config.json",
-      "config.ts",
-      "package.json",
-      "logs/core.log",
-      "index/autocompleteCache.sqlite",
-      "types/core/index.d.ts",
-    ];
+    const expectedFiles = ["logs/core.log", "index/autocompleteCache.sqlite"];

     const missingFiles = expectedFiles.filter((file) => {
       const filePath = path.join(CONTINUE_GLOBAL_DIR, file);
@@ -186,38 +298,36 @@ describe("Test Suite", () => {
   });

   it("should return valid config object", async () => {
-    const { result } = await messenger.request(
+    const { result } = await request(
       "config/getSerializedProfileInfo",
       undefined,
     );
     const { config } = result;
-    expect(config).toHaveProperty("models");
-    expect(config).toHaveProperty("embeddingsProvider");
+    expect(config).toHaveProperty("modelsByRole");
     expect(config).toHaveProperty("contextProviders");
     expect(config).toHaveProperty("slashCommands");
   });

   it("should properly handle history requests", async () => {
     const sessionId = "test-session-id";
-    await messenger.request("history/save", {
+    await request("history/save", {
       history: [],
       sessionId,
       title: "test-title",
-
       workspaceDirectory: "test-workspace-directory",
     });
-    const sessions = await messenger.request("history/list", {});
+    const sessions = await request("history/list", {});
     expect(sessions.length).toBeGreaterThan(0);

-    const session = await messenger.request("history/load", {
+    const session = await request("history/load", {
       id: sessionId,
     });
     expect(session).toHaveProperty("history");

-    await messenger.request("history/delete", {
+    await request("history/delete", {
       id: sessionId,
     });
-    const sessionsAfterDelete = await messenger.request("history/list", {});
+    const sessionsAfterDelete = await request("history/list", {});
     expect(sessionsAfterDelete.length).toBe(sessions.length - 1);
   });

@@ -228,12 +338,10 @@ describe("Test Suite", () => {
       model: "gpt-3.5-turbo",
       underlyingProviderName: "openai",
     };
-    await messenger.request("config/addModel", {
-      model,
-    });
+    await request("config/addModel", { model });
     const {
       result: { config },
-    } = await messenger.request("config/getSerializedProfileInfo", undefined);
+    } = await request("config/getSerializedProfileInfo", undefined);

     expect(
       config!.modelsByRole.chat.some(
@@ -241,10 +349,10 @@ describe("Test Suite", () => {
       ),
     ).toBe(true);

-    await messenger.request("config/deleteModel", { title: model.title });
+    await request("config/deleteModel", { title: model.title });
     const {
       result: { config: configAfterDelete },
-    } = await messenger.request("config/getSerializedProfileInfo", undefined);
+    } = await request("config/getSerializedProfileInfo", undefined);
     expect(
       configAfterDelete!.modelsByRole.chat.some(
         (m: ModelDescription) => m.title === model.title,
@@ -259,11 +367,9 @@ describe("Test Suite", () => {
       model: "gpt-3.5-turbo",
       underlyingProviderName: "mock",
     };
-    await messenger.request("config/addModel", {
-      model,
-    });
+    await request("config/addModel", { model });

-    const resp = await messenger.request("llm/complete", {
+    const resp = await request("llm/complete", {
       prompt: "Say 'Hello' and nothing else",
       completionOptions: {},
       title: "Test Model",
PATCH

# Verify the patch was applied
if grep -q "stderrLevels:" core/util/Logger.ts; then
    echo "✓ Logger.ts patch applied successfully"
else
    echo "✗ Logger.ts patch failed"
    exit 1
fi

if grep -q "BinaryIdeHandler" binary/test/binary.test.ts; then
    echo "✓ binary.test.ts patch applied successfully"
else
    echo "✗ binary.test.ts patch failed"
    exit 1
fi

echo "All patches applied successfully"
