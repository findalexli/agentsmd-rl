#!/usr/bin/env bash
set -euo pipefail

cd /workspace/gradio

# Check if already applied (look for HTTPConnection import in node_server.py)
if grep -q 'from http.client import HTTPConnection' gradio/node_server.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/gradio/node_server.py b/gradio/node_server.py
index 22f9f28e91..06c84c292d 100644
--- a/gradio/node_server.py
+++ b/gradio/node_server.py
@@ -9,6 +9,7 @@
 import warnings
 from concurrent.futures import TimeoutError
 from contextlib import closing
+from http.client import HTTPConnection
 from pathlib import Path
 from typing import TYPE_CHECKING

@@ -166,15 +167,26 @@ def attempt_connection(host: str, port: int) -> bool:
         return False


-def verify_server_startup(host: str, port: int, timeout: float = 5.0) -> bool:
-    """Verifies if a server is up and running by attempting to connect."""
+def verify_server_startup(host: str, port: int, timeout: float = 15.0) -> bool:
+    """Verifies if a server is up and running by making an HTTP request.
+
+    A simple TCP connection check is not sufficient because the Node SSR server
+    may accept connections before it is ready to handle HTTP requests. This
+    would cause Gradio's own url_ok health check (which does HEAD /) to fail
+    intermittently.
+    """
     start_time = time.time()
     while time.time() - start_time < timeout:
         try:
-            with socket.create_connection((host, port), timeout=1):
+            conn = HTTPConnection(host, port, timeout=2)
+            conn.request("HEAD", "/")
+            resp = conn.getresponse()
+            conn.close()
+            if resp.status < 500:
                 return True
-        except (TimeoutError, OSError):
-            time.sleep(0.1)
+        except Exception:
+            pass
+        time.sleep(0.2)
     return False


diff --git a/js/tootils/src/app-launcher.ts b/js/tootils/src/app-launcher.ts
index ad3720ebfe..a320667e57 100644
--- a/js/tootils/src/app-launcher.ts
+++ b/js/tootils/src/app-launcher.ts
@@ -1,4 +1,5 @@
 import { spawn, type ChildProcess } from "node:child_process";
+import http from "http";
 import net from "net";
 import path from "path";
 import fs from "fs";
@@ -51,6 +52,49 @@ function isPortFree(port: number): Promise<boolean> {
 	});
 }

+/**
+ * Poll the server with HTTP GET requests until it returns a response.
+ * Gradio prints "Running on local URL:" before the server is fully ready,
+ * so we need to verify it actually responds to HTTP requests.
+ */
+async function waitForServerReady(
+	port: number,
+	timeoutMs: number = 15000
+): Promise<void> {
+	const start = Date.now();
+	const pollInterval = 200;
+
+	while (Date.now() - start < timeoutMs) {
+		try {
+			await new Promise<void>((resolve, reject) => {
+				// Use HEAD on /gradio_api/info to avoid triggering SSR rendering on
+				// the root URL, which could block Gradio's own startup health check.
+				const req = http.request(
+					`http://127.0.0.1:${port}/gradio_api/info`,
+					{ method: "HEAD", timeout: 2000 },
+					(res) => {
+						res.resume(); // drain the response
+						resolve();
+					}
+				);
+				req.on("error", reject);
+				req.on("timeout", () => {
+					req.destroy();
+					reject(new Error("request timeout"));
+				});
+				req.end();
+			});
+			return; // Server responded successfully
+		} catch {
+			// Server not ready yet, wait and retry
+			await new Promise((r) => setTimeout(r, pollInterval));
+		}
+	}
+	throw new Error(
+		`Server on port ${port} did not become ready within ${timeoutMs}ms`
+	);
+}
+
 export function getTestcases(demoName: string): string[] {
 	const demoDir = path.join(ROOT_DIR, "demo", demoName);
 	if (!fs.existsSync(demoDir)) {
@@ -139,16 +183,23 @@ export async function launchGradioApp(
 		}, timeout);

 		let output = "";
+		let startupDetected = false;

 		function handleOutput(data: string): void {
 			output += data;
 			// Check for Gradio's startup message
 			if (
-				data.includes("Running on local URL:") ||
-				data.includes(`Uvicorn running on`)
+				!startupDetected &&
+				(data.includes("Running on local URL:") ||
+					data.includes(`Uvicorn running on`))
 			) {
+				startupDetected = true;
 				clearTimeout(timeoutId);
-				resolve({ port, process: childProcess });
+				// The startup message is printed before the server is fully ready.
+				// Poll with HTTP requests to ensure it actually responds.
+				waitForServerReady(port)
+					.then(() => resolve({ port, process: childProcess }))
+					.catch(reject);
 			}
 		}

PATCH

echo "Patch applied successfully."
