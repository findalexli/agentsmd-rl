#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/crates/sui-http/src/config.rs b/crates/sui-http/src/config.rs
index d3c995c91b33..54f48d4d3e29 100644
--- a/crates/sui-http/src/config.rs
+++ b/crates/sui-http/src/config.rs
@@ -4,6 +4,8 @@
 use std::time::Duration;

 const DEFAULT_HTTP2_KEEPALIVE_TIMEOUT_SECS: u64 = 20;
+const DEFAULT_TLS_HANDSHAKE_TIMEOUT: Duration = Duration::from_secs(5);
+const DEFAULT_MAX_PENDING_CONNECTIONS: usize = 4096;

 #[derive(Debug, Clone)]
 pub struct Config {
@@ -20,7 +22,8 @@ pub struct Config {
     pub(crate) accept_http1: bool,
     enable_connect_protocol: bool,
     pub(crate) max_connection_age: Option<Duration>,
-    pub(crate) allow_insecure: bool,
+    pub(crate) tls_handshake_timeout: Duration,
+    pub(crate) max_pending_connections: usize,
 }

 impl Default for Config {
@@ -39,7 +42,8 @@ impl Default for Config {
             accept_http1: true,
             enable_connect_protocol: true,
             max_connection_age: None,
-            allow_insecure: false,
+            tls_handshake_timeout: DEFAULT_TLS_HANDSHAKE_TIMEOUT,
+            max_pending_connections: DEFAULT_MAX_PENDING_CONNECTIONS,
         }
     }
 }
@@ -187,17 +191,27 @@ impl Config {
         }
     }

-    /// Allow accepting insecure connections when a tls_config is provided.
+    /// Sets the timeout for TLS handshakes on incoming connections.
     ///
-    /// This will allow clients to connect both using TLS as well as without TLS on the same
-    /// network interface.
+    /// Connections that do not complete the TLS handshake within this duration are dropped.
     ///
-    /// Default is `false`.
+    /// Default is 5 seconds.
+    pub fn tls_handshake_timeout(self, timeout: Duration) -> Self {
+        Config {
+            tls_handshake_timeout: timeout,
+            ..self
+        }
+    }
+
+    /// Sets the maximum number of pending TLS handshakes.
+    ///
+    /// When this limit is reached, new incoming connections are dropped until existing
+    /// handshakes complete or time out.
     ///
-    /// NOTE: This presently will only work for `tokio::net::TcpStream` IO connections
-    pub fn allow_insecure(self, allow_insecure: bool) -> Self {
+    /// Default is 4096.
+    pub fn max_pending_connections(self, max: usize) -> Self {
         Config {
-            allow_insecure,
+            max_pending_connections: max,
             ..self
         }
     }
diff --git a/crates/sui-http/src/lib.rs b/crates/sui-http/src/lib.rs
index 6ae3519fc94b..7720d628c5a2 100644
--- a/crates/sui-http/src/lib.rs
+++ b/crates/sui-http/src/lib.rs
@@ -290,33 +290,23 @@ where

     fn handle_incomming(&mut self, io: L::Io, remote_addr: L::Addr) {
         if let Some(tls) = self.tls_config.clone() {
+            if self.pending_connections.len() >= self.config.max_pending_connections {
+                tracing::warn!(
+                    pending = self.pending_connections.len(),
+                    "max pending connections reached, dropping new connection"
+                );
+                return;
+            }
+
             let tls_acceptor = TlsAcceptor::from(tls);
-            let allow_insecure = self.config.allow_insecure;
+            let timeout_duration = self.config.tls_handshake_timeout;
             self.pending_connections.spawn(async move {
-                if allow_insecure {
-                    // XXX: If we want to allow for supporting insecure traffic from other types of
-                    // io, we'll need to implement a generic peekable IO type
-                    if let Some(tcp) =
-                        <dyn std::any::Any>::downcast_ref::<tokio::net::TcpStream>(&io)
-                    {
-                        // Determine whether new connection is TLS.
-                        let mut buf = [0; 1];
-                        // `peek` blocks until at least some data is available, so if there is no error then
-                        // it must return the one byte we are requesting.
-                        tcp.peek(&mut buf).await?;
-                        // First byte of a TLS handshake is 0x16, so if it isn't 0x16 then its
-                        // insecure
-                        if buf != [0x16] {
-                            tracing::trace!("accepting insecure connection");
-                            return Ok((ServerIo::new_io(io), remote_addr));
-                        }
-                    } else {
-                        tracing::warn!("'allow_insecure' is configured but io type is not 'tokio::net::TcpStream'");
-                    }
-                }
-
                 tracing::trace!("accepting TLS connection");
-                let io = tls_acceptor.accept(io).await?;
+                let io = tokio::time::timeout(timeout_duration, tls_acceptor.accept(io))
+                    .await
+                    .map_err(|_| {
+                        std::io::Error::new(std::io::ErrorKind::TimedOut, "TLS handshake timed out")
+                    })??;
                 Ok((ServerIo::new_tls_io(io), remote_addr))
             });
         } else {
diff --git a/crates/sui-http/src/listener.rs b/crates/sui-http/src/listener.rs
index d3e09dffd660..330d2015d4d2 100644
--- a/crates/sui-http/src/listener.rs
+++ b/crates/sui-http/src/listener.rs
@@ -207,19 +207,11 @@ async fn handle_accept_error(e: std::io::Error) {
         return;
     }

-    // [From `hyper::Server` in 0.14](https://github.com/hyperium/hyper/blob/v0.14.27/src/server/tcp.rs#L186)
-    //
-    // > A possible scenario is that the process has hit the max open files
-    // > allowed, and so trying to accept a new connection will fail with
-    // > `EMFILE`. In some cases, it's preferable to just wait for some time, if
-    // > the application will likely close some files (or connections), and try
-    // > to accept the connection again. If this option is `true`, the error
-    // > will be logged at the `error` level, since it is still a big deal,
-    // > and then the listener will sleep for 1 second.
-    //
-    // hyper allowed customizing this but axum does not.
+    // Sleep briefly to avoid tight-looping on persistent errors (e.g., EMFILE) while
+    // not blocking the server event loop for too long — the serve loop needs to keep
+    // draining completed connections to free file descriptors.
     tracing::error!("accept error: {e}");
-    tokio::time::sleep(Duration::from_secs(1)).await;
+    tokio::time::sleep(Duration::from_millis(5)).await;
 }

 fn is_connection_error(e: &std::io::Error) -> bool {
diff --git a/crates/sui-network/src/validator/server.rs b/crates/sui-network/src/validator/server.rs
index 9eb28f89e80e..0b4f4b3b35ef8 100644
--- a/crates/sui-network/src/validator/server.rs
+++ b/crates/sui-network/src/validator/server.rs
@@ -68,13 +68,6 @@ impl<M: MetricsCallbackProvider> ServerBuilder<M> {
     }

     pub async fn bind(self, addr: &Multiaddr, tls_config: Option<ServerConfig>) -> Result<Server> {
-        let http_config = self
-            .config
-            .http_config()
-            // Temporarily continue allowing clients to connection without TLS even when the server
-            // is configured with a tls_config
-            .allow_insecure(true);
-
         let request_timeout = self
             .config
             .request_timeout
@@ -125,7 +118,7 @@ impl<M: MetricsCallbackProvider> ServerBuilder<M> {
                 mysten_network::grpc_timeout::GrpcTimeout::new(service, request_timeout)
             });

-        let mut builder = sui_http::Builder::new().config(http_config);
+        let mut builder = sui_http::Builder::new().config(self.config.http_config());

         if let Some(tls_config) = tls_config {
             builder = builder.tls_config(tls_config);
PATCH

echo "Patch applied successfully"
