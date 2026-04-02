#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sglang

# Idempotency check: if already patched, exit
if grep -q 'host = "127.0.0.1"' python/sglang/srt/utils/network.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/python/sglang/multimodal_gen/runtime/scheduler_client.py b/python/sglang/multimodal_gen/runtime/scheduler_client.py
index caec33da4365..b009071b7f5a 100644
--- a/python/sglang/multimodal_gen/runtime/scheduler_client.py
+++ b/python/sglang/multimodal_gen/runtime/scheduler_client.py
@@ -16,9 +16,8 @@ async def run_zeromq_broker(server_args: ServerArgs):
     It listens for TCP requests from offline clients (e.g., DiffGenerator).
     """
     ctx = zmq.asyncio.Context()
-    # This is the REP socket that listens for requests from DiffGenerator
     socket = ctx.socket(zmq.REP)
-    broker_endpoint = f"tcp://*:{server_args.broker_port}"
+    broker_endpoint = f"tcp://127.0.0.1:{server_args.broker_port}"
     socket.bind(broker_endpoint)
     logger.info(f"ZMQ Broker is listening for offline jobs on {broker_endpoint}")

diff --git a/python/sglang/srt/disaggregation/encode_receiver.py b/python/sglang/srt/disaggregation/encode_receiver.py
index fa1ea0d4b83b..6b70e15ef53d 100644
--- a/python/sglang/srt/disaggregation/encode_receiver.py
+++ b/python/sglang/srt/disaggregation/encode_receiver.py
@@ -399,7 +399,7 @@ def __init__(
         self.receive_count = receive_count
         self.num_items_assigned = recv_req.num_items_assigned
         self.embedding_port, self.recv_socket = get_zmq_socket_on_host(
-            zmq.Context(), zmq.PULL
+            zmq.Context(), zmq.PULL, host=host_name
         )
         logger.info(f"Waiting for input {self.embedding_port = }")
         self.recv_embedding_data = None
@@ -681,7 +681,9 @@ async def recv_mm_data(
             if len(self.encode_urls) == 0 or not need_wait_for_mm_inputs:
                 return None
             req_id = uuid.uuid4().hex
-            embedding_port, recv_socket = get_zmq_socket_on_host(self.context, zmq.PULL)
+            embedding_port, recv_socket = get_zmq_socket_on_host(
+                self.context, zmq.PULL, host=self.host
+            )
             mm_data = self._extract_url_data(request_obj)
             asyncio.create_task(
                 self.encode(req_id, mm_data, embedding_port, "encode", "send")
diff --git a/python/sglang/srt/utils/network.py b/python/sglang/srt/utils/network.py
index c374c9535524..835b06a3c57f 100644
--- a/python/sglang/srt/utils/network.py
+++ b/python/sglang/srt/utils/network.py
@@ -189,22 +189,23 @@ def get_zmq_socket_on_host(
     Args:
         context: ZeroMQ context to create the socket from.
         socket_type: Type of ZeroMQ socket to create.
-        host: Optional host to bind/connect to, without "tcp://" prefix. If None, binds to "tcp://*".
+        host: Host to bind to, without "tcp://" prefix. Defaults to
+            "127.0.0.1" (localhost-only) to avoid exposing unauthenticated
+            sockets to the network (CVE-2026-3060). Callers that need
+            cross-machine reachability must pass an explicit host.

     Returns:
         Tuple of (port, socket) where port is the randomly assigned TCP port.
     """
     socket = context.socket(socket_type)
-    # Bind to random TCP port, auto-wrapping IPv6 and setting zmq.IPV6 flag
     config_socket(socket, socket_type)
-    if host:
-        if is_valid_ipv6_address(host):
-            socket.setsockopt(zmq.IPV6, 1)
-            bind_host = f"tcp://[{host}]"
-        else:
-            bind_host = f"tcp://{host}"
+    if host is None:
+        host = "127.0.0.1"
+    if is_valid_ipv6_address(host):
+        socket.setsockopt(zmq.IPV6, 1)
+        bind_host = f"tcp://[{host}]"
     else:
-        bind_host = "tcp://*"
+        bind_host = f"tcp://{host}"
     port = socket.bind_to_random_port(bind_host)
     return port, socket

PATCH

echo "Patch applied successfully."
