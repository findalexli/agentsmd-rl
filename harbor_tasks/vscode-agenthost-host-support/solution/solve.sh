#!/usr/bin/env bash
set -euo pipefail

cd /workspace/vscode

# Idempotency check: look for the new serverUrls.ts file which doesn't exist in the buggy version
if [[ -f "src/vs/platform/agentHost/node/serverUrls.ts" ]]; then
    echo "Patch already applied (serverUrls.ts exists)"
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/scripts/code-agent-host.js b/scripts/code-agent-host.js
index ecd162a0a24c3..578b655b3beff 100644
--- a/scripts/code-agent-host.js
+++ b/scripts/code-agent-host.js
@@ -12,7 +12,7 @@ const minimist = require('minimist');
 async function main() {
 	const args = minimist(process.argv.slice(2), {
 		boolean: ['help', 'enable-mock-agent', 'quiet', 'without-connection-token'],
-		string: ['port', 'log', 'connection-token', 'connection-token-file'],
+		string: ['port', 'host', 'log', 'connection-token', 'connection-token-file'],
 	});

 	if (args.help) {
@@ -21,6 +21,7 @@ async function main() {
 			'\n' +
 			'Options:\n' +
 			'  --port <number>                Port to listen on (default: 8081, or VSCODE_AGENT_HOST_PORT env)\n' +
+			'  --host <host>                  Host/IP to bind to (default: 127.0.0.1, use 0.0.0.0 for all interfaces)\n' +
 			'  --connection-token <token>      A secret that must be included with all requests\n' +
 			'  --connection-token-file <path>  Path to a file containing the connection token\n' +
 			'  --without-connection-token      Run without a connection token\n' +
@@ -36,6 +37,9 @@ async function main() {

 	/** @type {string[]} */
 	const serverArgs = ['--port', String(port)];
+	if (args.host) {
+		serverArgs.push('--host', String(args.host));
+	}
 	if (args['enable-mock-agent']) {
 		serverArgs.push('--enable-mock-agent');
 	}
@@ -55,12 +59,15 @@ async function main() {
 		serverArgs.push('--without-connection-token');
 	}

-	const addr = await startServer(serverArgs);
-	console.log(`Agent Host server listening on ${addr}`);
+	await startServer(serverArgs);
 }

+/**
+ * @param {string[]} programArgs
+ * @returns {Promise<void>}
+ */
 function startServer(programArgs) {
-	return new Promise((resolve, reject) => {
+	return new Promise((resolve) => {
 		const env = { ...process.env };
 		const entryPoint = path.join(
 			__dirname,
@@ -85,7 +92,7 @@ function startServer(programArgs) {
 			process.stdout.write(text);
 			const m = text.match(/READY:(\d+)/);
 			if (m) {
-				resolve(`ws://127.0.0.1:${m[1]}`);
+				resolve();
 			}
 		});

diff --git a/src/vs/platform/agentHost/node/agentHostServerMain.ts b/src/vs/platform/agentHost/node/agentHostServerMain.ts
index a0b3487b79cdd..35fdcc8661c6b 100644
--- a/src/vs/platform/agentHost/node/agentHostServerMain.ts
+++ b/src/vs/platform/agentHost/node/agentHostServerMain.ts
@@ -4,7 +4,7 @@
  *--------------------------------------------------------------------------------------------*/

 // Standalone agent host server with WebSocket protocol transport.
-// Start with: node out/vs/platform/agentHost/node/agentHostServerMain.js [--port <port>] [--connection-token <token>] [--connection-token-file <path>] [--without-connection-token] [--enable-mock-agent] [--quiet] [--log <level>]
+// Start with: node out/vs/platform/agentHost/node/agentHostServerMain.js [--port <port>] [--host <host>] [--connection-token <token>] [--connection-token-file <path>] [--without-connection-token] [--enable-mock-agent] [--quiet] [--log <level>]

 import { fileURLToPath } from 'url';

@@ -39,6 +39,7 @@ import { DiskFileSystemProvider } from '../../files/node/diskFileSystemProvider.
 import { Schemas } from '../../../base/common/network.js';
 import { ISessionDataService } from '../common/sessionDataService.js';
 import { SessionDataService } from './sessionDataService.js';
+import { resolveServerUrls } from './serverUrls.js';

 /** Log to stderr so messages appear in the terminal alongside the process. */
 function log(msg: string): void {
@@ -51,6 +52,7 @@ const connectionTokenRegex = /^[0-9A-Za-z_-]+$/;

 interface IServerOptions {
 	readonly port: number;
+	readonly host: string | undefined;
 	readonly enableMockAgent: boolean;
 	readonly quiet: boolean;
 	/** Connection token string, or `undefined` when `--without-connection-token`. */
@@ -62,6 +64,8 @@ function parseServerOptions(): IServerOptions {
 	const envPort = parseInt(process.env['VSCODE_AGENT_HOST_PORT'] ?? '8081', 10);
 	const portIdx = argv.indexOf('--port');
 	const port = portIdx >= 0 ? parseInt(argv[portIdx + 1], 10) : envPort;
+	const hostIdx = argv.indexOf('--host');
+	const host = hostIdx >= 0 ? argv[hostIdx + 1] : undefined;
 	const enableMockAgent = argv.includes('--enable-mock-agent');
 	const quiet = argv.includes('--quiet');

@@ -105,7 +109,7 @@ function parseServerOptions(): IServerOptions {
 		connectionToken = generateUuid();
 	}

-	return { port, enableMockAgent, quiet, connectionToken };
+	return { port, host, enableMockAgent, quiet, connectionToken };
 }

 // ---- Main -------------------------------------------------------------------
@@ -177,6 +181,7 @@ async function main(): Promise<void> {
 	// WebSocket server
 	const wsServer = disposables.add(await WebSocketProtocolServer.create({
 		port: options.port,
+		host: options.host,
 		connectionTokenValidate: options.connectionToken
 			? token => token === options.connectionToken
 			: undefined,
@@ -193,14 +198,22 @@ async function main(): Promise<void> {

 	// Report ready
 	function reportReady(addr: string): void {
-		const listeningPort = addr.split(':').pop();
-		let wsUrl = `ws://${addr}`;
-		if (options.connectionToken) {
-			wsUrl += `?tkn=${options.connectionToken}`;
-		}
+		const listeningPort = Number(addr.split(':').pop());
 		process.stdout.write(`READY:${listeningPort}\n`);
-		log(`WebSocket server listening on ${wsUrl}`);
-		logService.info(`[AgentHostServer] WebSocket server listening on ${wsUrl}`);
+
+		const urls = resolveServerUrls(options.host, listeningPort);
+		for (const url of urls.local) {
+			log(`  Local:   ${url}`);
+			logService.info(`[AgentHostServer] Local:   ${url}`);
+		}
+		for (const url of urls.network) {
+			log(`  Network: ${url}`);
+			logService.info(`[AgentHostServer] Network: ${url}`);
+		}
+		if (urls.network.length === 0 && options.host === undefined) {
+			log('  Network: use --host to expose');
+			logService.info('[AgentHostServer] Network: use --host to expose');
+		}
 	}

 	const address = wsServer.address;
diff --git a/src/vs/platform/agentHost/node/serverUrls.ts b/src/vs/platform/agentHost/node/serverUrls.ts
new file mode 100644
index 0000000000000..7112746bc929a
--- /dev/null
+++ b/src/vs/platform/agentHost/node/serverUrls.ts
@@ -0,0 +1,48 @@
+/*---------------------------------------------------------------------------------------------
+ *  Copyright (c) Microsoft Corporation. All rights reserved.
+ *  Licensed under the MIT License. See License.txt in the project root for license information.
+ *--------------------------------------------------------------------------------------------*/
+
+import * as os from 'os';
+
+export interface IResolvedServerUrls {
+	readonly local: readonly string[];
+	readonly network: readonly string[];
+}
+
+const loopbackHosts = new Set(['localhost', '127.0.0.1', '::1', '0000:0000:0000:0000:0000:0000:0000:0001']);
+const wildcardHosts = new Set(['0.0.0.0', '::', '0000:0000:0000:0000:0000:0000:0000:0000']);
+
+export function resolveServerUrls(host: string | undefined, port: number, networkInterfaces: ReturnType<typeof os.networkInterfaces> = os.networkInterfaces()): IResolvedServerUrls {
+	if (host === undefined) {
+		return { local: [formatWebSocketUrl('localhost', port)], network: [] };
+	}
+
+	if (!wildcardHosts.has(host)) {
+		const url = formatWebSocketUrl(host, port);
+		return loopbackHosts.has(host)
+			? { local: [url], network: [] }
+			: { local: [], network: [url] };
+	}
+
+	const network = new Set<string>();
+	for (const netInterface of Object.values(networkInterfaces)) {
+		for (const detail of netInterface ?? []) {
+			if (detail.family !== 'IPv4' || detail.internal) {
+				continue;
+			}
+
+			network.add(formatWebSocketUrl(detail.address, port));
+		}
+	}
+
+	return {
+		local: [formatWebSocketUrl('localhost', port)],
+		network: [...network],
+	};
+}
+
+export function formatWebSocketUrl(host: string, port: number): string {
+	const normalizedHost = host.includes(':') ? `[${host}]` : host;
+	return `ws://${normalizedHost}:${port}`;
+}
diff --git a/src/vs/platform/agentHost/test/node/serverUrls.test.ts b/src/vs/platform/agentHost/test/node/serverUrls.test.ts
new file mode 100644
index 0000000000000..61394085c53a9
--- /dev/null
+++ b/src/vs/platform/agentHost/test/node/serverUrls.test.ts
@@ -0,0 +1,65 @@
+/*---------------------------------------------------------------------------------------------
+ *  Copyright (c) Microsoft Corporation. All rights reserved.
+ *  Licensed under the MIT License. See License.txt in the project root for license information.
+ *--------------------------------------------------------------------------------------------*/
+
+import assert from 'assert';
+import { ensureNoDisposablesAreLeakedInTestSuite } from '../../../../base/test/common/utils.js';
+import { formatWebSocketUrl, resolveServerUrls } from '../../node/serverUrls.js';
+
+suite('serverUrls', () => {
+	ensureNoDisposablesAreLeakedInTestSuite();
+
+	test('uses localhost for default local-only binding', () => {
+		assert.deepStrictEqual(resolveServerUrls(undefined, 8081), {
+			local: ['ws://localhost:8081'],
+			network: [],
+		});
+	});
+
+	test('formats IPv6 websocket URLs with brackets', () => {
+		assert.strictEqual(formatWebSocketUrl('::1', 8081), 'ws://[::1]:8081');
+		assert.deepStrictEqual(resolveServerUrls('::1', 8081), {
+			local: ['ws://[::1]:8081'],
+			network: [],
+		});
+		assert.deepStrictEqual(resolveServerUrls('0000:0000:0000:0000:0000:0000:0000:0001', 8081), {
+			local: ['ws://[0000:0000:0000:0000:0000:0000:0000:0001]:8081'],
+			network: [],
+		});
+	});
+
+	test('treats wildcard binding as localhost plus network urls', () => {
+		assert.deepStrictEqual(resolveServerUrls('0.0.0.0', 8081, {
+			lo0: [
+				{ address: '127.0.0.1', netmask: '255.0.0.0', family: 'IPv4', mac: '00:00:00:00:00:00', internal: true, cidr: '127.0.0.1/8' },
+			],
+			en0: [
+				{ address: '192.168.1.20', netmask: '255.255.255.0', family: 'IPv4', mac: '11:22:33:44:55:66', internal: false, cidr: '192.168.1.20/24' },
+				{ address: 'fe80::1', netmask: 'ffff:ffff:ffff:ffff::', family: 'IPv6', mac: '11:22:33:44:55:66', internal: false, cidr: 'fe80::1/64', scopeid: 0 },
+			],
+		}), {
+			local: ['ws://localhost:8081'],
+			network: ['ws://192.168.1.20:8081'],
+		});
+
+		assert.deepStrictEqual(resolveServerUrls('0000:0000:0000:0000:0000:0000:0000:0000', 8081, {
+			lo0: [
+				{ address: '127.0.0.1', netmask: '255.0.0.0', family: 'IPv4', mac: '00:00:00:00:00:00', internal: true, cidr: '127.0.0.1/8' },
+			],
+			en0: [
+				{ address: '192.168.1.20', netmask: '255.255.255.0', family: 'IPv4', mac: '11:22:33:44:55:66', internal: false, cidr: '192.168.1.20/24' },
+			],
+		}), {
+			local: ['ws://localhost:8081'],
+			network: ['ws://192.168.1.20:8081'],
+		});
+	});
+
+	test('treats explicit non-loopback host as a network url', () => {
+		assert.deepStrictEqual(resolveServerUrls('example.test', 8081), {
+			local: [],
+			network: ['ws://example.test:8081'],
+		});
+	});
+});
PATCH

echo "Patch applied successfully"
