#!/usr/bin/env bash
set -euo pipefail

cd /workspace/pulumi

# Idempotency: if the patch is already applied, exit cleanly.
if grep -q "Signals the provider to gracefully shut down" sdk/nodejs/provider/provider.ts 2>/dev/null; then
    echo "Patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/changelog/pending/20260408--sdk-nodejs-python--add-cancel-handler-to-python-and-node-js-providers.yaml b/changelog/pending/20260408--sdk-nodejs-python--add-cancel-handler-to-python-and-node-js-providers.yaml
new file mode 100644
index 000000000000..2a2998ff8a9c
--- /dev/null
+++ b/changelog/pending/20260408--sdk-nodejs-python--add-cancel-handler-to-python-and-node-js-providers.yaml
@@ -0,0 +1,4 @@
+changes:
+- type: feat
+  scope: sdk/nodejs,python
+  description: Add Cancel handler to Python & Node.js providers
diff --git a/sdk/nodejs/provider/provider.ts b/sdk/nodejs/provider/provider.ts
index 2205812ed59d..718e56d1c669 100644
--- a/sdk/nodejs/provider/provider.ts
+++ b/sdk/nodejs/provider/provider.ts
@@ -317,4 +317,9 @@ export interface Provider {
      *   The embedded value from the sub-package.
      */
     parameterizeValue?: (name: string, version: string, value: string) => Promise<ParameterizeResult>;
+
+    /**
+     * Signals the provider to gracefully shut down and abort any ongoing operations.
+     */
+    cancel?: () => Promise<void>;
 }
diff --git a/sdk/nodejs/provider/server.ts b/sdk/nodejs/provider/server.ts
index 63d98bde2115..70302d50482d 100644
--- a/sdk/nodejs/provider/server.ts
+++ b/sdk/nodejs/provider/server.ts
@@ -69,7 +69,14 @@ class Server implements grpc.UntypedServiceImplementation {
     // Misc. methods

     public cancel(call: any, callback: any): void {
-        callback(undefined, new emptyproto.Empty());
+        if (this.provider.cancel) {
+            this.provider.cancel().then(
+                () => callback(undefined, new emptyproto.Empty()),
+                (e: any) => callback(e),
+            );
+        } else {
+            callback(undefined, new emptyproto.Empty());
+        }
     }

     public attach(call: any, callback: any): void {
diff --git a/sdk/python/lib/pulumi/provider/experimental/provider.py b/sdk/python/lib/pulumi/provider/experimental/provider.py
index 26d9f0535042..7fd5e51eecc8 100644
--- a/sdk/python/lib/pulumi/provider/experimental/provider.py
+++ b/sdk/python/lib/pulumi/provider/experimental/provider.py
@@ -736,3 +736,6 @@ async def call(self, request: CallRequest) -> CallResponse:
         Handle the call request.
         """
         raise NotImplementedError("The method 'call' is not implemented")
+
+    async def cancel(self) -> None:
+        """Cancel signals the provider to gracefully shut down and abort any ongoing operations."""
diff --git a/sdk/python/lib/pulumi/provider/experimental/server.py b/sdk/python/lib/pulumi/provider/experimental/server.py
index 313fcc6bbab6..eedc83b5ad5f 100644
--- a/sdk/python/lib/pulumi/provider/experimental/server.py
+++ b/sdk/python/lib/pulumi/provider/experimental/server.py
@@ -103,6 +103,10 @@ def __init__(
     async def GetPluginInfo(self, request, context) -> proto.PluginInfo:
         return proto.PluginInfo(version=self._version)

+    async def Cancel(self, request, context):
+        await self._provider.cancel()
+        return empty_pb2.Empty()
+
     def create_grpc_invalid_properties_status(
         self, message: str, errors: Optional[list[InputPropertyErrorDetails]]
     ) -> grpc.Status:
diff --git a/sdk/python/lib/pulumi/provider/provider.py b/sdk/python/lib/pulumi/provider/provider.py
index 121f822cb35d..cb0496cfe4ae 100644
--- a/sdk/python/lib/pulumi/provider/provider.py
+++ b/sdk/python/lib/pulumi/provider/provider.py
@@ -134,3 +134,6 @@ def invoke(self, token: str, args: Mapping[str, Any]) -> InvokeResult:
         """

         raise Exception(f"Unknown function {token}")
+
+    def cancel(self) -> None:
+        """Cancel signals the provider to gracefully shut down and abort any ongoing operations."""
diff --git a/sdk/python/lib/pulumi/provider/server.py b/sdk/python/lib/pulumi/provider/server.py
index 3d4f0bcbf62e..dd32561724ff 100644
--- a/sdk/python/lib/pulumi/provider/server.py
+++ b/sdk/python/lib/pulumi/provider/server.py
@@ -27,7 +27,7 @@
 import grpc
 import grpc.aio

-from google.protobuf import struct_pb2
+from google.protobuf import empty_pb2, struct_pb2
 from pulumi.provider.provider import InvokeResult, Provider, CallResult, ConstructResult
 from pulumi.resource import (
     ProviderResource,
@@ -479,6 +479,10 @@ async def Configure(self, request, context) -> proto.ConfigureResponse:
             acceptSecrets=True, acceptResources=True, acceptOutputs=True
         )

+    async def Cancel(self, request, context):
+        self.provider.cancel()
+        return empty_pb2.Empty()
+
     async def GetPluginInfo(self, request, context) -> proto.PluginInfo:
         if self.provider.version is None:
             return proto.PluginInfo(version="")
PATCH

echo "Patch applied successfully."
