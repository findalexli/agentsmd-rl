#!/usr/bin/env bash
set -e

cd /workspace/sui

# Check if already applied (idempotency check)
if grep -q "SymbolicationStart" external-crates/move/crates/move-analyzer/src/symbols/runner.rs 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/external-crates/move/crates/move-analyzer/editors/code/.eslintrc.json b/external-crates/move/crates/move-analyzer/editors/code/.eslintrc.json
index 3de7bd2697..b78aa66d96 100644
--- a/external-crates/move/crates/move-analyzer/editors/code/.eslintrc.json
+++ b/external-crates/move/crates/move-analyzer/editors/code/.eslintrc.json
@@ -2,7 +2,6 @@
     // Don't bother looking for eslint configuration files in parent
     // directories; this is the root configuration.
     "root": true,
-
     // Instruct eslint to use a parser that can parse TypeScript.
     "parser": "@typescript-eslint/parser",
     "parserOptions": {
@@ -18,13 +17,11 @@
             "**/tsconfig.json"
         ]
     },
-
     // Specify the environment in which our JavaScript will run.
     "env": {
         // The Node.js runtime environment provides globals such as `__dirname`.
         "node": true
     },
-
     // Plug-in eslint rules from @typescript-eslint.
     "plugins": [
         "@typescript-eslint",
@@ -46,7 +43,6 @@
         "no-unsafe-optional-chaining": "warn",
         "no-useless-backreference": "warn",
         "require-atomic-updates": "warn",
-
         // The following are in the "best practices" category of eslint rules.
         "array-callback-return": "warn",
         "block-scoped-var": "warn",
@@ -85,7 +81,6 @@
         "no-useless-return": "warn",
         "prefer-promise-reject-errors": "warn",
         "radix": "warn",
-
         // The following are in the "stylistic issues" category of eslint rules.
         "array-bracket-spacing": "warn",
         "array-element-newline": [
@@ -103,8 +98,14 @@
         "comma-style": "warn",
         "computed-property-spacing": "warn",
         "eol-last": "warn",
-        "function-call-argument-newline": ["warn", "consistent"],
-        "function-paren-newline": ["warn", "consistent"],
+        "function-call-argument-newline": [
+            "warn",
+            "consistent"
+        ],
+        "function-paren-newline": [
+            "warn",
+            "consistent"
+        ],
         "key-spacing": "warn",
         "linebreak-style": "off", // We use different linebreak styles. ref https://eslint.org/docs/latest/rules/linebreak-style
         "max-len": [
@@ -134,7 +135,6 @@
         "spaced-comment": "warn",
         "switch-colon-spacing": "warn",
         "unicode-bom": "warn",
-
         // The following are @typescript-eslint rules. For more information, see:
         // * All @typescript-eslint rules: https://github.com/typescript-eslint/typescript-eslint/tree/v4.31.1/packages/eslint-plugin/docs/rules
         // * The rules included in @typescript-eslint/recommended: https://github.com/typescript-eslint/typescript-eslint/blob/v4.31.1/packages/eslint-plugin/src/configs/recommended.ts
@@ -179,7 +179,10 @@
         "@typescript-eslint/no-unused-vars": "warn",
         "@typescript-eslint/no-use-before-define": "warn",
         "@typescript-eslint/non-nullable-type-assertion-style": "warn",
-        "@typescript-eslint/object-curly-spacing": ["warn", "always"],
+        "@typescript-eslint/object-curly-spacing": [
+            "warn",
+            "always"
+        ],
         "@typescript-eslint/prefer-for-of": "warn",
         "@typescript-eslint/prefer-function-type": "warn",
         "@typescript-eslint/prefer-includes": "warn",
@@ -190,25 +193,18 @@
         "@typescript-eslint/prefer-reduce-type-parameter": "warn",
         "@typescript-eslint/prefer-string-starts-ends-with": "warn",
         "@typescript-eslint/promise-function-async": "warn",
-        "@typescript-eslint/quotes": ["warn", "single"],
+        "@typescript-eslint/quotes": [
+            "warn",
+            "single"
+        ],
         "@typescript-eslint/require-array-sort-compare": "warn",
         "@typescript-eslint/return-await": "warn",
         "@typescript-eslint/semi": "warn",
-        "@typescript-eslint/space-before-function-paren": [
-            "warn",
-            {
-                "anonymous": "never",
-                "named": "never",
-                "asyncArrow": "always"
-            }
-        ],
         "@typescript-eslint/strict-boolean-expressions": "warn",
         "@typescript-eslint/switch-exhaustiveness-check": "warn",
         "@typescript-eslint/unified-signatures": "warn",
-
         // The following are eslint-plugin-tsdoc rules:
         "tsdoc/syntax": "warn",
-
         "@typescript-eslint/no-unsafe-return": "off",
         "@typescript-eslint/type-annotation-spacing": "off",
         "@typescript-eslint/no-explicit-any": "off",
@@ -218,4 +214,4 @@
         "@typescript-eslint/restrict-template-expressions": "off",
         "@typescript-eslint/array-type": "off"
     }
-}
+}
\ No newline at end of file
diff --git a/external-crates/move/crates/move-analyzer/editors/code/package-lock.json b/external-crates/move/crates/move-analyzer/editors/code/package-lock.json
index 30653b6736..2b235e59d3 100644
--- a/external-crates/move/crates/move-analyzer/editors/code/package-lock.json
+++ b/external-crates/move/crates/move-analyzer/editors/code/package-lock.json
@@ -1,12 +1,12 @@
 {
   "name": "move",
-  "version": "1.0.40",
+  "version": "1.0.41",
   "lockfileVersion": 3,
   "requires": true,
   "packages": {
     "": {
       "name": "move",
-      "version": "1.0.40",
+      "version": "1.0.41",
       "license": "Apache-2.0",
       "dependencies": {
         "command-exists": "^1.2.9",
diff --git a/external-crates/move/crates/move-analyzer/editors/code/package.json b/external-crates/move/crates/move-analyzer/editors/code/package.json
index 6bb15ff92a..30fd1f8d80 100644
--- a/external-crates/move/crates/move-analyzer/editors/code/package.json
+++ b/external-crates/move/crates/move-analyzer/editors/code/package.json
@@ -5,7 +5,7 @@
   "publisher": "mysten",
   "icon": "images/move.png",
   "license": "Apache-2.0",
-  "version": "1.0.40",
+  "version": "1.0.41",
   "preview": true,
   "repository": {
     "url": "https://github.com/MystenLabs/sui.git",
diff --git a/external-crates/move/crates/move-analyzer/editors/code/src/activity_monitor.ts b/external-crates/move/crates/move-analyzer/editors/code/src/activity_monitor.ts
new file mode 100644
index 0000000000..647bb9c2e5
--- /dev/null
+++ b/external-crates/move/crates/move-analyzer/editors/code/src/activity_monitor.ts
@@ -0,0 +1,216 @@
+// Copyright (c) Mysten Labs, Inc.
+// SPDX-License-Identifier: Apache-2.0
+
+import * as vscode from 'vscode';
+import * as lc from 'vscode-languageclient/node';
+
+type ServerState = 'starting' | 'idle' | 'busy' | 'slow' | 'stopped';
+
+// How often the dot animation advances (. → .. → ...)
+const ANIMATION_INTERVAL_MS = 500;
+// How often pending requests are checked for exceeding the slow threshold
+const SLOW_CHECK_INTERVAL_MS = 2000;
+// Time after which a busy/starting state is promoted to slow (yellow)
+const SLOW_THRESHOLD_MS = 10000;
+const DOT_FRAMES = ['.', '..', '...'];
+const BASE_LABEL = 'move-analyzer';
+
+/**
+ * Activity monitor: displays server health in the VS Code status bar.
+ * Driven by a state machine:
+ *
+ *   starting ──► idle ◄──► busy ──► slow
+ *                  ▲                  │
+ *                  └──────────────────┘
+ *   stopped (terminal until client restarts)
+ *
+ * Starting/idle/stopped come from LanguageClient.onDidChangeState
+ * (maps Starting→starting, Running→idle, Stopped→stopped).
+ *
+ * Busy/slow detection uses two complementary signals:
+ * - Server-sent $/progress notifications (compilation start/end)
+ * - Client-side sendRequest wrapper (individual request latency)
+ * Either source can trigger busy; idle requires both to be quiet.
+ *
+ * Slow promotion: on entering starting or busy, a one-shot timer
+ * (compilationSlowTimer) is scheduled at SLOW_THRESHOLD_MS. If the
+ * state hasn't changed by the time it fires, it promotes to slow
+ * (yellow). Any state transition calls stopTimers(), cancelling the
+ * pending timer — so a quick busy→idle round-trip never turns yellow.
+ * A separate interval (slowCheckTimer) periodically scans pending
+ * requests for individually slow responses.
+ */
+export class ServerActivityMonitor implements vscode.Disposable {
+    private readonly item: vscode.StatusBarItem;
+
+    private readonly extensionVersion: string;
+
+    private readonly serverVersion: string;
+
+    private state: ServerState = 'starting';
+
+    // Tracks whether server is currently compiling (from $/progress)
+    private compilationInProgress = false;
+
+    // Maps tracking IDs → request-sent timestamps for slow request detection
+    private readonly pendingRequests: Map<string, number> = new Map();
+
+    private animationTimer: ReturnType<typeof setInterval> | undefined;
+
+    private slowCheckTimer: ReturnType<typeof setInterval> | undefined;
+
+    // Fires once after SLOW_THRESHOLD_MS to promote starting/busy → slow
+    private compilationSlowTimer: ReturnType<typeof setTimeout> | undefined;
+
+    private animationStep = 0;
+
+    constructor(extensionVersion: string, serverVersion: string, command?: string) {
+        this.extensionVersion = extensionVersion;
+        this.serverVersion = serverVersion;
+        this.item = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left, 0);
+        this.item.name = 'Move Analyzer';
+        if (command !== undefined && command.length > 0) {
+            this.item.command = command;
+        }
+        this.render();
+        this.item.show();
+    }
+
+    // Called from client.onDidChangeState; resets all tracking on transitions
+    // since a stopped/restarted server won't respond to old requests.
+    onClientStateChange(_oldState: lc.State, newState: lc.State): void {
+        if (newState === lc.State.Running) {
+            this.pendingRequests.clear();
+            this.compilationInProgress = false;
+            this.transitionTo('idle');
+        } else if (newState === lc.State.Stopped) {
+            this.pendingRequests.clear();
+            this.compilationInProgress = false;
+            this.transitionTo('stopped');
+        } else {
+            this.transitionTo('starting');
+        }
+    }
+
+    onCompilationStart(): void {
+        this.compilationInProgress = true;
+        if (this.state === 'idle') {
+            this.transitionTo('busy');
+        }
+    }
+
+    onCompilationEnd(): void {
+        this.compilationInProgress = false;
+        if (this.pendingRequests.size === 0 && (this.state === 'busy' || this.state === 'slow')) {
+            this.transitionTo('idle');
+        }
+    }
+
+    onRequestSent(trackingId: string): void {
+        this.pendingRequests.set(trackingId, Date.now());
+        if (this.state === 'idle') {
+            this.transitionTo('busy');
+        }
+    }
+
+    onResponseReceived(trackingId: string): void {
+        this.pendingRequests.delete(trackingId);
+        if (!this.compilationInProgress
+            && this.pendingRequests.size === 0
+            && (this.state === 'busy' || this.state === 'slow')) {
+            this.transitionTo('idle');
+        }
+    }
+
+    dispose(): void {
+        this.stopTimers();
+        this.item.dispose();
+    }
+
+    private transitionTo(newState: ServerState): void {
+        this.state = newState;
+        this.stopTimers();
+
+        const needsAnimation = newState === 'starting' || newState === 'busy' || newState === 'slow';
+        if (needsAnimation) {
+            this.animationStep = 0;
+            this.animationTimer = setInterval(() => {
+                this.animationStep = (this.animationStep + 1) % DOT_FRAMES.length;
+                this.render();
+            }, ANIMATION_INTERVAL_MS);
+        }
+
+        // Promote starting/busy → slow after SLOW_THRESHOLD_MS.
+        // For 'starting': the LSP handshake is taking too long.
+        // For 'busy': compilation or an individual request is taking too long.
+        if (newState === 'starting' || newState === 'busy') {
+            this.compilationSlowTimer = setTimeout(() => {
+                if (this.state === 'starting' || this.state === 'busy') {
+                    this.transitionTo('slow');
+                }
+            }, SLOW_THRESHOLD_MS);
+        }
+
+        if (newState === 'busy') {
+            // Also check for slow individual requests periodically
+            this.slowCheckTimer = setInterval(() => {
+                const now = Date.now();
+                for (const timestamp of this.pendingRequests.values()) {
+                    if (now - timestamp > SLOW_THRESHOLD_MS) {
+                        this.transitionTo('slow');
+                        return;
+                    }
+                }
+            }, SLOW_CHECK_INTERVAL_MS);
+        }
+
+        this.render();
+    }
+
+    private stopTimers(): void {
+        if (this.animationTimer !== undefined) {
+            clearInterval(this.animationTimer);
+            this.animationTimer = undefined;
+        }
+        if (this.slowCheckTimer !== undefined) {
+            clearInterval(this.slowCheckTimer);
+            this.slowCheckTimer = undefined;
+        }
+        if (this.compilationSlowTimer !== undefined) {
+            clearTimeout(this.compilationSlowTimer);
+            this.compilationSlowTimer = undefined;
+        }
+    }
+
+    private render(): void {
+        const needsAnimation = this.state === 'starting' || this.state === 'busy' || this.state === 'slow';
+
+        if (this.state === 'stopped') {
+            this.item.text = `$(error) ${BASE_LABEL}`;
+        } else if (needsAnimation) {
+            this.item.text = `${BASE_LABEL} ${DOT_FRAMES[this.animationStep]}`;
+        } else {
+            this.item.text = BASE_LABEL;
+        }
+
+        if (this.state === 'stopped') {
+            this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.errorBackground');
+        } else if (this.state === 'slow') {
+            this.item.backgroundColor = new vscode.ThemeColor('statusBarItem.warningBackground');
+        } else {
+            this.item.backgroundColor = undefined;
+        }
+
+        const statusText = this.state === 'stopped' ? 'Stopped' : 'Running';
+        const tooltip = new vscode.MarkdownString(undefined, true);
+        // Enables command: URIs so the restart link works
+        tooltip.isTrusted = true;
+        tooltip.appendMarkdown('**Move Analyzer**\n\n');
+        tooltip.appendMarkdown(`Extension: v${this.extensionVersion}\n\n`);
+        tooltip.appendMarkdown(`Server: ${this.serverVersion}\n\n`);
+        tooltip.appendMarkdown(`Status: ${statusText}\n\n`);
+        tooltip.appendMarkdown('---\n\n');
+        tooltip.appendMarkdown('[Restart Server](command:move.serverRestart)');
+        this.item.tooltip = tooltip;
+    }
+}
diff --git a/external-crates/move/crates/move-analyzer/editors/code/src/context.ts b/external-crates/move/crates/move-analyzer/editors/code/src/context.ts
index e7d6e4e429..932276bae3 100644
--- a/external-crates/move/crates/move-analyzer/editors/code/src/context.ts
+++ b/external-crates/move/crates/move-analyzer/editors/code/src/context.ts
@@ -12,9 +12,13 @@ import * as vscode from 'vscode';
 import * as lc from 'vscode-languageclient/node';
 import * as semver from 'semver';
 import { log } from './log';
+import { ServerActivityMonitor } from './activity_monitor';
 import { assert } from 'console';
 import { IndentAction } from 'vscode';
 
+// Must match PROGRESS_TOKEN in analyzer.rs
+const PROGRESS_TOKEN = 'symbolication';
+
 function version(path: string, args?: readonly string[]): string | null {
     const versionString = childProcess.spawnSync(
         path, args, { encoding: 'utf8' },
@@ -76,6 +80,15 @@ function shouldInstall(bundledVersionString: string | null,
 export class Context {
     private client: lc.LanguageClient | undefined;
 
+    private activityMonitor: ServerActivityMonitor | undefined;
+
+    // Create the output channel and pass it to every LanguageClient
+    // via clientOptions.outputChannel. This prevents the client from disposing and
+    // recreating the channel on each stop/start cycle — the same tab and its history
+    // persist across server restarts. (If we let the client create its own, it sets
+    // an internal _disposeOutputChannel=true flag and destroys the channel on stop().)
+    private readonly moveOutputChannel: vscode.OutputChannel;
+
     configuration: Configuration;
 
     private lintLevel: string;
@@ -113,6 +126,7 @@ export class Context {
         this.resolvedServerPath = this.configuration.serverPath;
         // Default to no additional args but may change during server installation
         this.resolvedServerArgs = [];
+        this.moveOutputChannel = vscode.window.createOutputChannel('Move');
         this.traceOutputChannel = vscode.window.createOutputChannel(
             'Move Language Server Trace',
         );
@@ -169,6 +183,29 @@ export class Context {
         this.extensionContext.subscriptions.push(disposable);
     }
 
+    /**
+     * Initialize the `move-analyzer` activity monitor in the status bar
+     * that:
+     *  - shows server status,
+     *  - when clicked, shows the `Move` output channel.
+     *  - when hovered, shows the extension and server versions, as well
+     *    additiona commands to execute.
+     *
+     * @param extensionVersion - The version of the extension.
+     * @param serverVersion - The version of the server.
+     */
+    initActivityMonitor(extensionVersion: string, serverVersion: string): void {
+        // Register a command that shows the move-analyzer (`Move`) output channel.
+        const showOutputCmd = 'move.showOutput';
+        const disposable = vscode.commands.registerCommand(showOutputCmd, () => {
+            this.moveOutputChannel.show();
+        });
+        this.extensionContext.subscriptions.push(disposable);
+
+        this.activityMonitor = new ServerActivityMonitor(extensionVersion, serverVersion, showOutputCmd);
+        this.extensionContext.subscriptions.push(this.activityMonitor);
+    }
+
     /**
      * Configures and starts the client that interacts with the language server.
      *
@@ -197,6 +234,7 @@ export class Context {
         this.traceOutputChannel.clear();
         const clientOptions: lc.LanguageClientOptions = {
             documentSelector: [{ scheme: 'file', language: 'move' }],
+            outputChannel: this.moveOutputChannel,
             traceOutputChannel: this.traceOutputChannel,
             initializationOptions: {
                 lintLevel: this.lintLevel,
@@ -204,6 +242,13 @@ export class Context {
                 inlayHintsType: this.inlayHintsType,
                 inlayHintsParam: this.inlayHintsParam,
             },
+            // Don't auto-restart on fatal errors — let the user restart manually
+            // via the activity monitor tooltip. By default, it would restart automatically
+            // a few times which is noisy and annoying.
+            errorHandler: {
+                error: () => ({ action: lc.ErrorAction.Continue }),
+                closed: () => ({ action: lc.CloseAction.DoNotRestart }),
+            },
         };
 
         const client = new lc.LanguageClient(
@@ -212,6 +257,38 @@ export class Context {
             serverOptions,
             clientOptions,
         );
+        // Wire activity monitor to the new client. The activityMonitor instance persists
+        // across client restarts; only the listeners are re-attached each time.
+        if (this.activityMonitor) {
+            const activityMonitor = this.activityMonitor;
+            client.onDidChangeState(e => {
+                activityMonitor.onClientStateChange(e.oldState, e.newState);
+            });
+            // Listen for server-sent $/progress notifications to detect compilation state.
+            // The 'begin'/'end' kind values come from the LSP spec's WorkDoneProgress wire format.
+            client.onNotification('$/progress', (params: { token: string; value: { kind: string } }) => {
+                if (params.token === PROGRESS_TOKEN) {
+                    if (params.value.kind === 'begin') {
+                        activityMonitor.onCompilationStart();
+                    } else if (params.value.kind === 'end') {
+                        activityMonitor.onCompilationEnd();
+                    }
+                }
+            });
+            // Wrap sendRequest to track individual LSP request latency (hover,
+            // completion, go-to-def, etc.) as a secondary busy/slow signal.
+            const originalSendRequest = client.sendRequest.bind(client);
+            client.sendRequest = async function (method: any, ...args: any[]) {
+                const trackingId = `${Date.now()}-${Math.random()}`;
+                activityMonitor.onRequestSent(trackingId);
+                try {
+                    return await originalSendRequest(method, ...args);
+                } finally {
+                    activityMonitor.onResponseReceived(trackingId);
+                }
+            } as any;
+        }
+
         log.info('Starting client...');
         const res = client.start();
         this.extensionContext.subscriptions.push({ dispose: async () => client.stop() });
diff --git a/external-crates/move/crates/move-analyzer/editors/code/src/main.ts b/external-crates/move/crates/move-analyzer/editors/code/src/main.ts
index 897453b6b6..430eef88d2 100644
--- a/external-crates/move/crates/move-analyzer/editors/code/src/main.ts
+++ b/external-crates/move/crates/move-analyzer/editors/code/src/main.ts
@@ -167,6 +167,15 @@ export async function activate(extensionContext: Readonly<vscode.ExtensionContex
         return;
     }
 
+    // Initialize activity monitor with version info.
+    const serverVersionResult = childProcess.spawnSync(
+        context.resolvedServerPath,
+        context.resolvedServerArgs.concat(['--version']),
+        { encoding: 'utf8' },
+    );
+    const serverVersionString = serverVersionResult.stdout.trim() || 'unknown';
+    context.initActivityMonitor(extension.version, serverVersionString);
+
     // Register handlers for VS Code commands that the user explicitly issues.
     context.registerCommand('serverVersion', serverVersion);
     context.registerCommand('serverRestart', serverRestart);
diff --git a/external-crates/move/crates/move-analyzer/src/analyzer.rs b/external-crates/move/crates/move-analyzer/src/analyzer.rs
index a4148e463e..ee3ed60012 100644
--- a/external-crates/move/crates/move-analyzer/src/analyzer.rs
+++ b/external-crates/move/crates/move-analyzer/src/analyzer.rs
@@ -2,20 +2,20 @@
 // Copyright (c) The Move Contributors
 // SPDX-License-Identifier: Apache-2.0
 
-use anyhow::Result;
 use crossbeam::channel::{bounded, select};
-use lsp_server::{Connection, Message, Notification, Request, Response};
+use lsp_server::{Connection, Message, Notification, Request, RequestId, Response};
 use lsp_types::{
-    CodeActionKind, CodeActionOptions, CodeActionProviderCapability, CompletionOptions, Diagnostic,
-    HoverProviderCapability, InlayHintOptions, InlayHintServerCapabilities, OneOf, SaveOptions,
-    TextDocumentSyncCapability, TextDocumentSyncKind, TextDocumentSyncOptions,
-    TypeDefinitionProviderCapability, WorkDoneProgressOptions, notification::Notification as _,
-    request::Request as _,
+    CodeActionKind, CodeActionOptions, CodeActionProviderCapability, CompletionOptions,
+    HoverProviderCapability, InlayHintOptions, InlayHintServerCapabilities, NumberOrString, OneOf,
+    ProgressParams, SaveOptions, TextDocumentSyncCapability, TextDocumentSyncKind,
+    TextDocumentSyncOptions, TypeDefinitionProviderCapability, WorkDoneProgress,
+    WorkDoneProgressBegin, WorkDoneProgressEnd, WorkDoneProgressOptions,
+    notification::Notification as _,
+    request::{Request as _, WorkDoneProgressCreate},
 };
 use move_compiler::{editions::Flavor, linters::LintLevel};
 use std::{
     collections::BTreeMap,
-    path::PathBuf,
     sync::{Arc, Mutex},
 };
 
@@ -30,7 +30,7 @@ use crate::{
             on_document_symbol_request, on_go_to_def_request, on_go_to_type_def_request,
             on_hover_request, on_references_request,
         },
-        runner::SymbolicatorRunner,
+        runner::{SymbolicatorMessage, SymbolicatorRunner},
     },
     vfs::on_text_document_sync_notification,
 };
@@ -42,6 +42,10 @@ const LINT_NONE: &str = "none";
 const LINT_DEFAULT: &str = "default";
 const LINT_ALL: &str = "all";
 
+/// Token shared between server and client to correlate $/progress
+/// notifications with the compilation activity.
+const PROGRESS_TOKEN: &str = "symbolication";
+
 #[allow(deprecated)]
 pub fn run<F: MoveFlavor>(flavor: Option<Flavor>) {
     // stdio is used to communicate Language Server Protocol requests and responses.
@@ -129,7 +133,7 @@ pub fn run<F: MoveFlavor>(flavor: Option<Flavor>) {
     })
     .expect("could not serialize server capabilities");
 
-    let (diag_sender, diag_receiver) = bounded::<Result<BTreeMap<PathBuf, Vec<Diagnostic>>>>(0);
+    let (diag_sender, diag_receiver) = bounded::<SymbolicatorMessage>(0);
     let initialize_params: lsp_types::InitializeParams =
         serde_json::from_value(client_response).expect("could not deserialize client capabilities");
 
@@ -201,14 +205,33 @@ pub fn run<F: MoveFlavor>(flavor: Option<Flavor>) {
         )
         .expect("could not finish connection initialization");
 
+    // Ask the client to create a progress token for symbolication. The client
+    // uses this token to match subsequent $/progress begin/end notifications
+    // to the compilation activity.
+    let create_progress = Request::new(
+        RequestId::from(1),
+        WorkDoneProgressCreate::METHOD.to_string(),
+        serde_json::json!({ "token": PROGRESS_TOKEN }),
+    );
+    if let Err(err) = context
+        .connection
+        .sender
+        .send(Message::Request(create_progress))
+    {
+        eprintln!("could not send progress token create request: {:?}", err);
+    }
+
+    let progress_token = NumberOrString::String(PROGRESS_TOKEN.to_string());
+
     let mut shutdown_req_received = false;
     loop {
         select! {
             recv(diag_receiver) -> message => {
                 match message {
-                    Ok(result) => {
-                        match result {
-                            Ok(diags) => {
+                    Ok(msg) => {
+                        match msg {
+                            // Forward compilation diagnostics to the client
+                            SymbolicatorMessage::Diagnostics(diags) => {
                                 for (k, v) in diags {
                                     let url = Url::from_file_path(k).unwrap();
                                     let params = lsp_types::PublishDiagnosticsParams::new(url, v, None);
@@ -221,23 +244,94 @@ pub fn run<F: MoveFlavor>(flavor: Option<Flavor>) {
                                         };
                                 }
                             },
-                            Err(err) => {
-                                let typ = lsp_types::MessageType::ERROR;
-                                let message = format!("{err}");
-                                    // report missing manifest only once to avoid re-generating
-                                    // user-visible error in cases when the developer decides to
-                                    // keep editing a file that does not belong to a packages
-                                    let params = lsp_types::ShowMessageParams { typ, message };
-                                let notification = Notification::new(lsp_types::notification::ShowMessage::METHOD.to_string(), params);
+                            // Non-fatal error (e.g. missing manifest) — show to user, server continues
+                            SymbolicatorMessage::Error(err) => {
+                                let params = lsp_types::ShowMessageParams {
+                                    typ: lsp_types::MessageType::ERROR,
+                                    message: format!("{err}"),
+                                };
+                                let notification = Notification::new(
+                                    lsp_types::notification::ShowMessage::METHOD.to_string(),
+                                    params,
+                                );
+                                if let Err(err) = context
+                                    .connection
+                                    .sender
+                                    .send(lsp_server::Message::Notification(notification)) {
+                                        eprintln!("could not send error notification: {:?}", err);
+                                    };
+                            },
+                            // Fatal error (e.g. dep download failure) — show error and exit.
+                            // The client detects the process death as State.Stopped (red indicator).
+                            SymbolicatorMessage::FatalError(err) => {
+                                eprintln!("fatal symbolication error: {:?}", err);
+                                let params = lsp_types::ShowMessageParams {
+                                    typ: lsp_types::MessageType::ERROR,
+                                    message: format!("{err}"),
+                                };
+                                let notification = Notification::new(
+                                    lsp_types::notification::ShowMessage::METHOD.to_string(),
+                                    params,
+                                );
+                                if let Err(err) = context
+                                    .connection
+                                    .sender
+                                    .send(lsp_server::Message::Notification(notification)) {
+                                        eprintln!("could not send fatal error notification: {:?}", err);
+                                    };
+                                // Exit immediately — a clean `break` would block on
+                                // io_threads.join() since the stdin reader is still
+                                // waiting for client input.
+                                std::process::exit(1);
+                            },
+                            // Notify client that compilation started
+                            SymbolicatorMessage::SymbolicationStart => {
+                                let params = ProgressParams {
+                                    token: progress_token.clone(),
+                                    value: lsp_types::ProgressParamsValue::WorkDone(
+                                        WorkDoneProgress::Begin(WorkDoneProgressBegin {
+                                            title: "Symbolicating".to_string(),
+                                            cancellable: Some(false),
+                                            message: None,
+                                            percentage: None,
+                                        }),
+                                    ),
+                                };
+                                let notification = Notification::new(
+                                    lsp_types::notification::Progress::METHOD.to_string(),
+                                    params,
+                                );
+                                if let Err(err) = context
+                                    .connection
+                                    .sender
+                                    .send(lsp_server::Message::Notification(notification)) {
+                                        eprintln!("could not send progress begin: {:?}", err);
+                                    };
+                            },
+                            // Notify client that compilation finished (status bar → idle)
+                            SymbolicatorMessage::SymbolicationEnd => {
+                                let params = ProgressParams {
+                                    token: progress_token.clone(),
+                                    value: lsp_types::ProgressParamsValue::WorkDone(
+                                        WorkDoneProgress::End(WorkDoneProgressEnd {
+                                            message: None,
+                                        }),
+                                    ),
+                                };
+                                let notification = Notification::new(
+                                    lsp_types::notification::Progress::METHOD.to_string(),
+                                    params,
+                                );
                                 if let Err(err) = context
                                     .connection
                                     .sender
                                     .send(lsp_server::Message::Notification(notification)) {
-                                        eprintln!("could not send compiler error response: {:?}", err);
+                                        eprintln!("could not send progress end: {:?}", err);
                                     };
                             },
                         }
                     },
+                    // Channel disconnected — symbolication thread crashed
                     Err(error) => {
                         eprintln!("symbolicator message error: {:?}", error);
                         // if the analyzer crashes in a separate thread, this error will keep
diff --git a/external-crates/move/crates/move-analyzer/src/symbols/runner.rs b/external-crates/move/crates/move-analyzer/src/symbols/runner.rs
index a1387e4db5..9763a9abac 100644
--- a/external-crates/move/crates/move-analyzer/src/symbols/runner.rs
+++ b/external-crates/move/crates/move-analyzer/src/symbols/runner.rs
@@ -14,7 +14,7 @@ use crate::{
     utils::canonicalize_path,
 };
 
-use anyhow::{Result, anyhow};
+use anyhow::anyhow;
 use crossbeam::channel::Sender;
 use lsp_types::Diagnostic;
 use std::{
@@ -33,6 +33,20 @@ use move_package_alt::MoveFlavor;
 /// Interval for checking if the parent process is still alive (in seconds)
 const PARENT_LIVENESS_MONITORING_INTERVAL_SECS: u64 = 10;
 
+/// Messages sent from the symbolication runner thread to the main analyzer loop.
+pub enum SymbolicatorMessage {
+    /// Compilation diagnostics — forwarded as textDocument/publishDiagnostics
+    Diagnostics(BTreeMap<PathBuf, Vec<Diagnostic>>),
+    /// Non-fatal error (e.g. missing manifest) — shown via window/showMessage, server continues
+    Error(anyhow::Error),
+    /// Fatal error (e.g. dependency download failure) — shown via window/showMessage, server exits
+    FatalError(anyhow::Error),
+    /// Symbolication batch started — triggers $/progress Begin
+    SymbolicationStart,
+    /// Symbolication batch finished — triggers $/progress End
+    SymbolicationEnd,
+}
+
 #[derive(Debug, Clone, Eq, PartialEq, Ord, PartialOrd)]
 pub enum RunnerState {
     Run(BTreeSet<PathBuf>),
@@ -57,7 +71,7 @@ impl SymbolicatorRunner {
         ide_files_root: VfsPath,
         symbols_map: Arc<Mutex<BTreeMap<PathBuf, Symbols>>>,
         packages_info: Arc<Mutex<CachedPackages>>,
-        sender: Sender<Result<BTreeMap<PathBuf, Vec<Diagnostic>>>>,
+        sender: Sender<SymbolicatorMessage>,
         lint: LintLevel,
         flavor: Option<Flavor>,
         parent_process_id: Option<u32>,
@@ -144,6 +158,14 @@ impl SymbolicatorRunner {
                             &mut missing_manifests,
                             sender.clone(),
                         );
+                        // Progress begin/end bracket the entire batch, not individual packages.
+                        // The client sees one status change if this takes a long time. It reflects
+                        // the overall server load but is less noisy than sending this (and having
+                        // client change status for each package).
+                        if let Err(err) = sender.send(SymbolicatorMessage::SymbolicationStart) {
+                            eprintln!("could not send symbolication start: {:?}", err);
+                        }
+                        let mut fatal = false;
                         for pkg_path in pkgs_to_analyze.into_iter() {
                             eprintln!("symbolication started");
                             match get_symbols::<F>(
@@ -167,18 +189,28 @@ impl SymbolicatorRunner {
                                         old_symbols_map.insert(pkg_path.clone(), new_symbols);
                                     }
                                     // set/reset (previous) diagnostics
-                                    if let Err(err) = sender.send(Ok(lsp_diagnostics)) {
+                                    if let Err(err) = sender.send(SymbolicatorMessage::Diagnostics(lsp_diagnostics)) {
                                         eprintln!("could not pass diagnostics: {:?}", err);
                                     }
                                 }
                                 Err(err) => {
                                     eprintln!("symbolication failed: {:?}", err);
-                                    if let Err(err) = sender.send(Err(err)) {
-                                        eprintln!("could not pass compiler error: {:?}", err);
+                                    // Close progress before reporting fatal error
+                                    if let Err(err) = sender.send(SymbolicatorMessage::SymbolicationEnd) {
+                                        eprintln!("could not send symbolication end: {:?}", err);
                                     }
+                                    if let Err(err) = sender.send(SymbolicatorMessage::FatalError(err)) {
+                                        eprintln!("could not pass fatal error: {:?}", err);
+                                    }
+                                    fatal = true;
+                                    break;
                                 }
                             }
                         }
+                        if !fatal && let Err(err) = sender.send(SymbolicatorMessage::SymbolicationEnd) {
+                                eprintln!("could not send symbolication end: {:?}", err);
+
+                        }
                     }
                 }
             })
@@ -191,7 +223,7 @@ impl SymbolicatorRunner {
     fn pkgs_to_analyze(
         starting_paths: BTreeSet<PathBuf>,
         missing_manifests: &mut BTreeSet<PathBuf>,
-        sender: Sender<Result<BTreeMap<PathBuf, Vec<Diagnostic>>>>,
+        sender: Sender<SymbolicatorMessage>,
     ) -> BTreeSet<PathBuf> {
         let mut pkgs_to_analyze = BTreeSet::new();
         for starting_path in &starting_paths {
@@ -202,7 +234,7 @@ impl SymbolicatorRunner {
                     // cases when developer indeed intended to open a standalone file that was
                     // not meant to compile
                     missing_manifests.insert(starting_path.clone());
-                    if let Err(err) = sender.send(Err(anyhow!(
+                    if let Err(err) = sender.send(SymbolicatorMessage::Error(anyhow!(
                         "Unable to find package manifest. Make sure that
                     the source files are located in a sub-directory of a package containing
                     a Move.toml file. "
PATCH

echo "Patch applied successfully"
