#!/bin/bash
set -euo pipefail

cd /workspace/effect

# Apply the fix patch
git apply <<'PATCH'
diff --git a/packages/platform/src/internal/httpClientRequest.ts b/packages/platform/src/internal/httpClientRequest.ts
index 73d0132ce2a..14fb718c526 100644
--- a/packages/platform/src/internal/httpClientRequest.ts
+++ b/packages/platform/src/internal/httpClientRequest.ts
@@ -250,17 +250,21 @@ export const setUrl = dual<
 export const appendUrl = dual<
   (path: string) => (self: ClientRequest.HttpClientRequest) => ClientRequest.HttpClientRequest,
   (self: ClientRequest.HttpClientRequest, path: string) => ClientRequest.HttpClientRequest
->(2, (self, url) =>
-  makeInternal(
+>(2, (self, path) => {
+  if (path === "") {
+    return self
+  }
+  const baseUrl = self.url.endsWith("/") ? self.url : self.url + "/"
+  const pathSegment = path.startsWith("/") ? path.slice(1) : path
+  return makeInternal(
     self.method,
-    self.url.endsWith("/") && url.startsWith("/") ?
-      self.url + url.slice(1) :
-      self.url + url,
+    baseUrl + pathSegment,
     self.urlParams,
     self.hash,
     self.headers,
     self.body
-  ))
+  )
+})

 /** @internal */
 export const prependUrl = dual<
PATCH

# No build needed - tests run via tsx directly on TypeScript source
# The pnpm exec tsx resolves @effect/platform from the monorepo source
