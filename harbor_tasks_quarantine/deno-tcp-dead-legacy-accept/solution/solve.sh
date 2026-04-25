#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q '^import { ceilPowOf2 } from "ext:deno_node/internal_binding/_listen.ts";$' ext/node/polyfills/internal_binding/tcp_wrap.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/ext/node/polyfills/internal_binding/tcp_wrap.ts b/ext/node/polyfills/internal_binding/tcp_wrap.ts
index 47df8c7cec7088..8d2f0541ab290b 100644
--- a/ext/node/polyfills/internal_binding/tcp_wrap.ts
+++ b/ext/node/polyfills/internal_binding/tcp_wrap.ts
@@ -50,13 +50,8 @@ import {
 } from "ext:deno_node/internal_binding/stream_wrap.ts";
 import { ownerSymbol } from "ext:deno_node/internal_binding/symbols.ts";
 import { codeMap } from "ext:deno_node/internal_binding/uv.ts";
-import { delay } from "ext:deno_node/_util/async.ts";
 import { getIPFamily } from "ext:deno_node/internal/net.ts";
-import {
-  ceilPowOf2,
-  INITIAL_ACCEPT_BACKOFF_DELAY,
-  MAX_ACCEPT_BACKOFF_DELAY,
-} from "ext:deno_node/internal_binding/_listen.ts";
+import { ceilPowOf2 } from "ext:deno_node/internal_binding/_listen.ts";
 import { nextTick } from "ext:deno_node/_next_tick.ts";
 import { Buffer } from "node:buffer";

@@ -108,11 +103,9 @@ export class TCP extends ConnectionWrap {
   #remotePort?: number;

   #backlog?: number;
-  #listener!: Deno.Listener;
   #connections = 0;

   #closed = false;
-  #acceptBackoffDelay?: number;

   #netPermToken?: object | undefined;

@@ -240,10 +233,6 @@ export class TCP extends ConnectionWrap {
    * @return An error status code.
    */
   listen(backlog: number): number {
-    if (!this[kUseNativeWrap]) {
-      return this.#listenLegacy(backlog);
-    }
-
     this.#backlog = ceilPowOf2(backlog + 1);

     // deno-lint-ignore no-this-alias
@@ -397,10 +386,6 @@ export class TCP extends ConnectionWrap {
       return;
     }

-    if (this.#listener) {
-      this.#listener.ref();
-    }
-
     if (this[kStreamBaseField]) {
       this[kStreamBaseField].ref();
     }
@@ -413,10 +398,6 @@ export class TCP extends ConnectionWrap {
       return;
     }

-    if (this.#listener) {
-      this.#listener.unref();
-    }
-
     if (this[kStreamBaseField]) {
       this[kStreamBaseField].unref();
     }
@@ -524,39 +505,6 @@ export class TCP extends ConnectionWrap {
     notImplemented("TCP.prototype.setSimultaneousAccepts");
   }

-  /**
-   * Legacy listen using Deno.listen.
-   */
-  #listenLegacy(backlog: number): number {
-    this.#backlog = ceilPowOf2(backlog + 1);
-
-    const listenOptions = {
-      hostname: this.#address!,
-      port: this.#port!,
-      transport: "tcp" as const,
-    };
-
-    let listener;
-
-    try {
-      listener = Deno.listen(listenOptions);
-    } catch (e) {
-      if (e instanceof Deno.errors.NotCapable) {
-        throw e;
-      }
-      return codeMap.get(e.code ?? "UNKNOWN") ?? codeMap.get("UNKNOWN")!;
-    }
-
-    const address = listener.addr as Deno.NetAddr;
-    this.#address = address.hostname;
-    this.#port = address.port;
-    this.#listener = listener;
-
-    nextTick(nextTick, () => this.#accept());
-
-    return 0;
-  }
-
   #nativeConnect(req: TCPConnectWrap, address: string, port: number) {
     // deno-lint-ignore no-this-alias
     const self = this;
@@ -656,74 +604,6 @@ export class TCP extends ConnectionWrap {
     }
   }

-  /** Handle backoff delays following an unsuccessful accept. */
-  async #acceptBackoff() {
-    // Backoff after transient errors to allow time for the system to
-    // recover, and avoid blocking up the event loop with a continuously
-    // running loop.
-    if (!this.#acceptBackoffDelay) {
-      this.#acceptBackoffDelay = INITIAL_ACCEPT_BACKOFF_DELAY;
-    } else {
-      this.#acceptBackoffDelay *= 2;
-    }
-
-    if (this.#acceptBackoffDelay >= MAX_ACCEPT_BACKOFF_DELAY) {
-      this.#acceptBackoffDelay = MAX_ACCEPT_BACKOFF_DELAY;
-    }
-
-    await delay(this.#acceptBackoffDelay);
-
-    this.#accept();
-  }
-
-  /** Accept new connections (legacy path). */
-  async #accept(): Promise<void> {
-    if (this.#closed) {
-      return;
-    }
-
-    if (this.#connections > this.#backlog!) {
-      this.#acceptBackoff();
-
-      return;
-    }
-
-    let connection: Deno.Conn;
-
-    try {
-      connection = await this.#listener.accept();
-    } catch (e) {
-      if (e instanceof Deno.errors.BadResource && this.#closed) {
-        // Listener and server has closed.
-        return;
-      }
-
-      try {
-        // TODO(cmorten): map errors to appropriate error codes.
-        this.onconnection!(codeMap.get("UNKNOWN")!, undefined);
-      } catch {
-        // swallow callback errors.
-      }
-
-      this.#acceptBackoff();
-
-      return;
-    }
-
-    // Reset the backoff delay upon successful accept.
-    this.#acceptBackoffDelay = undefined;
-    const connectionHandle = new TCP(socketType.SOCKET, connection);
-    this.#connections++;
-
-    try {
-      this.onconnection!(0, connectionHandle);
-    } catch {
-      // swallow callback errors.
-    }
-
-    return this.#accept();
-  }
-
   /** Handle server closure. */
   override _onClose(): number {
     this.#closed = true;
@@ -738,7 +618,6 @@ export class TCP extends ConnectionWrap {

     this.#backlog = undefined;
     this.#connections = 0;
-    this.#acceptBackoffDelay = undefined;

     // Close native libuv handle. uv_close is safe to call at any time -
     // it cancels pending writes and defers the actual handle free to the
@@ -748,14 +627,6 @@ export class TCP extends ConnectionWrap {
       this.#native = null;
     }

-    if (!this[kUseNativeWrap] && this.provider === providerType.TCPSERVERWRAP) {
-      try {
-        this.#listener.close();
-      } catch {
-        // listener already closed
-      }
-    }
-
     return LibuvStreamWrap.prototype._onClose.call(this);
   }

diff --git a/tools/lint_plugins/no_deno_api_in_polyfills.ts b/tools/lint_plugins/no_deno_api_in_polyfills.ts
index 3afa562e187702..50eab3a848f4a5 100644
--- a/tools/lint_plugins/no_deno_api_in_polyfills.ts
+++ b/tools/lint_plugins/no_deno_api_in_polyfills.ts
@@ -32,7 +32,6 @@ export const EXPECTED_VIOLATIONS: Record<string, number> = {
   "ext/node/polyfills/internal/readline/interface.mjs": 3,
   "ext/node/polyfills/internal/errors.ts": 3,
   "ext/node/polyfills/internal/buffer.mjs": 3,
-  "ext/node/polyfills/internal_binding/tcp_wrap.ts": 3,
   "ext/node/polyfills/_fs/_fs_lstat.ts": 3,
   "ext/node/polyfills/testing.ts": 2,
   "ext/node/polyfills/internal/util/inspect.mjs": 2,

PATCH

echo "Patch applied successfully."
