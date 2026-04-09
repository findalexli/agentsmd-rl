#!/usr/bin/env bash
set -euo pipefail

cd /workspace/deno

# Idempotent: skip if already applied
if grep -q 'buf.length >= 2 \*\* 31 - 1' ext/node/polyfills/internal/crypto/cipher.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/ext/node/polyfills/internal/crypto/cipher.ts b/ext/node/polyfills/internal/crypto/cipher.ts
index 9bffb0b85daba1..11404d8b7324ac 100644
--- a/ext/node/polyfills/internal/crypto/cipher.ts
+++ b/ext/node/polyfills/internal/crypto/cipher.ts
@@ -321,6 +321,12 @@ Cipheriv.prototype.update = function (
   if (typeof data === "string") {
     buf = Buffer.from(data, inputEncoding);
   }
+
+  // Match Node.js/OpenSSL behavior: reject inputs >= INT_MAX bytes
+  if (buf.length >= 2 ** 31 - 1) {
+    throw new Error("Trying to add data in unsupported state");
+  }
+
   _lazyInitCipherDecoder(this, outputEncoding);

   let output: Buffer;
@@ -573,6 +579,12 @@ Decipheriv.prototype.update = function (
   if (typeof data === "string") {
     buf = Buffer.from(data, inputEncoding);
   }
+
+  // Match Node.js/OpenSSL behavior: reject inputs >= INT_MAX bytes
+  if (buf.length >= 2 ** 31 - 1) {
+    throw new Error("Trying to add data in unsupported state");
+  }
+
   _lazyInitDecipherDecoder(this, outputEncoding);

   let output;

PATCH

echo "Patch applied successfully."
