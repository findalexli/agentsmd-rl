#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'export function defineMimeType' packages/mime/src/lib/define-mime-type.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/mime/.changes/minor.define-mime-type.md b/packages/mime/.changes/minor.define-mime-type.md
new file mode 100644
index 00000000000..80852c2cd9b
--- /dev/null
+++ b/packages/mime/.changes/minor.define-mime-type.md
@@ -0,0 +1,12 @@
+Add `defineMimeType()` for registering custom MIME types. This allows adding support for file extensions not included in the defaults, or overriding existing behavior. Custom registrations take precedence over built-in types.
+
+```ts
+import { defineMimeType, detectMimeType } from '@remix-run/mime'
+
+defineMimeType({
+  extensions: 'myformat',
+  mimeType: 'application/x-myformat',
+})
+
+detectMimeType('file.myformat') // 'application/x-myformat'
+```
diff --git a/packages/mime/README.md b/packages/mime/README.md
index 7db3a72c024..8eb60d6ea30 100644
--- a/packages/mime/README.md
+++ b/packages/mime/README.md
@@ -76,6 +76,30 @@ mimeTypeToContentType('application/ld+json') // 'application/ld+json; charset=ut
 mimeTypeToContentType('image/png') // 'image/png'
 ```

+### `defineMimeType(definition)`
+
+Registers or overrides a MIME type for one or more file extensions.
+
+```ts
+import { defineMimeType } from '@remix-run/mime'
+
+defineMimeType({
+  extensions: ['myformat'],
+  mimeType: 'application/x-myformat',
+})
+```
+
+You can also optionally configure the charset and whether the MIME type is compressible:
+
+```ts
+defineMimeType({
+  extensions: ['myformat'],
+  mimeType: 'application/x-myformat',
+  compressible: true,
+  charset: 'utf-8',
+})
+```
+
 ## License

 MIT
diff --git a/packages/mime/src/index.ts b/packages/mime/src/index.ts
index 92f8f49e3ba..78373467467 100644
--- a/packages/mime/src/index.ts
+++ b/packages/mime/src/index.ts
@@ -2,3 +2,5 @@ export { detectContentType } from './lib/detect-content-type.ts'
 export { detectMimeType } from './lib/detect-mime-type.ts'
 export { isCompressibleMimeType } from './lib/is-compressible-mime-type.ts'
 export { mimeTypeToContentType } from './lib/mime-type-to-content-type.ts'
+export { defineMimeType } from './lib/define-mime-type.ts'
+export type { MimeTypeDefinition } from './lib/define-mime-type.ts'
diff --git a/packages/mime/src/lib/define-mime-type.ts b/packages/mime/src/lib/define-mime-type.ts
new file mode 100644
index 00000000000..ac84a7a9471
--- /dev/null
+++ b/packages/mime/src/lib/define-mime-type.ts
@@ -0,0 +1,79 @@
+export interface MimeTypeDefinition {
+  /** The file extension(s) to register (e.g., ['x-myformat']) */
+  extensions: string | string[]
+  /** The MIME type for these extensions (e.g., 'application/x-myformat') */
+  mimeType: string
+  /**
+   * Whether this MIME type is compressible.
+   * If omitted, falls back to default heuristics (text/*, +json, +text, +xml).
+   */
+  compressible?: boolean
+  /**
+   * Charset to include in Content-Type header.
+   * - `'utf-8'` or other string → '; charset={value}'
+   * - `undefined` → falls back to default heuristics (`'utf-8'` for `text/*`, `application/json`, `+json`)
+   */
+  charset?: string
+}
+
+// Custom registries - only created when defineMimeType is called.
+// Exported for direct access to avoid function call overhead in hot paths.
+export let customMimeTypeByExtension: Map<string, string> | undefined
+export let customCompressibleByMimeType: Map<string, boolean> | undefined
+export let customCharsetByMimeType: Map<string, string> | undefined
+
+/**
+ * Registers a custom MIME type for one or more file extensions.
+ *
+ * Use this to add support for file extensions not included in the defaults,
+ * or to override the behavior of existing extensions.
+ *
+ * @param definition The MIME type definition to register
+ *
+ * @example
+ * defineMimeType({
+ *   extensions: ['x-myformat'],
+ *   mimeType: 'application/x-myformat',
+ * })
+ *
+ * @example
+ * // Configure compressibility and charset
+ * defineMimeType({
+ *   extensions: ['x-myformat'],
+ *   mimeType: 'application/x-myformat',
+ *   compressible: true, // Optional
+ *   charset: 'utf-8', // Optional
+ * })
+ */
+export function defineMimeType(definition: MimeTypeDefinition): void {
+  let extensions = Array.isArray(definition.extensions)
+    ? definition.extensions
+    : [definition.extensions]
+
+  customMimeTypeByExtension ??= new Map()
+  for (let ext of extensions) {
+    ext = ext.trim().toLowerCase()
+    // Remove leading dot if present
+    if (ext.startsWith('.')) {
+      ext = ext.slice(1)
+    }
+    customMimeTypeByExtension.set(ext, definition.mimeType)
+  }
+
+  if (definition.compressible !== undefined) {
+    customCompressibleByMimeType ??= new Map()
+    customCompressibleByMimeType.set(definition.mimeType, definition.compressible)
+  }
+
+  if (definition.charset !== undefined) {
+    customCharsetByMimeType ??= new Map()
+    customCharsetByMimeType.set(definition.mimeType, definition.charset)
+  }
+}
+
+// @internal - Resets all custom registrations. Used in tests for isolation.
+export function resetMimeTypes(): void {
+  customMimeTypeByExtension = undefined
+  customCompressibleByMimeType = undefined
+  customCharsetByMimeType = undefined
+}
diff --git a/packages/mime/src/lib/detect-mime-type.ts b/packages/mime/src/lib/detect-mime-type.ts
index 4c2d6ed3f56..56113ccd84a 100644
--- a/packages/mime/src/lib/detect-mime-type.ts
+++ b/packages/mime/src/lib/detect-mime-type.ts
@@ -1,8 +1,11 @@
 import { mimeTypes } from '../generated/mime-types.ts'
+import { customMimeTypeByExtension } from './define-mime-type.ts'

 /**
  * Detects the MIME type for a given file extension or filename.
  *
+ * Custom MIME types registered via `defineMimeType()` take precedence over built-in types.
+ *
  * @param extension The file extension (e.g. "txt", ".txt") or filename (e.g. "file.txt")
  * @returns The MIME type string, or undefined if not found
  *
@@ -18,5 +21,6 @@ export function detectMimeType(extension: string): string | undefined {
   // If no dot found (~idx === -1, so !~idx === true), use ext as-is.
   // Otherwise, skip past the dot (++idx) and extract the extension.
   // Credit to mrmime for this technique.
-  return mimeTypes[!~idx ? ext : ext.substring(++idx)]
+  ext = !~idx ? ext : ext.substring(++idx)
+  return customMimeTypeByExtension?.get(ext) ?? mimeTypes[ext]
 }
diff --git a/packages/mime/src/lib/is-compressible-mime-type.ts b/packages/mime/src/lib/is-compressible-mime-type.ts
index a8a0be64861..f6725b7f2f2 100644
--- a/packages/mime/src/lib/is-compressible-mime-type.ts
+++ b/packages/mime/src/lib/is-compressible-mime-type.ts
@@ -1,4 +1,5 @@
 import { compressibleMimeTypes } from '../generated/compressible-mime-types.ts'
+import { customCompressibleByMimeType } from './define-mime-type.ts'

 /**
  * Checks if a MIME type is known to be compressible.
@@ -7,6 +8,7 @@ import { compressibleMimeTypes } from '../generated/compressible-mime-types.ts'
  * - Compressible MIME types from mime-db, except for types starting with `x-` (experimental) or `vnd.` (vendor-specific).
  * - Any text/* type
  * - Types with +json, +text, or +xml suffix
+ * - MIME types explicitly registered as compressible via `defineMimeType()`
  *
  * Accepts either a bare MIME type or a full Content-Type header value with parameters.
  *
@@ -20,6 +22,11 @@ export function isCompressibleMimeType(mimeType: string): boolean {
   let idx = mimeType.indexOf(';')
   let type = ~idx ? mimeType.substring(0, idx).trim() : mimeType

+  let customCompressible = customCompressibleByMimeType?.get(type)
+  if (customCompressible !== undefined) {
+    return customCompressible
+  }
+
   if (compressibleMimeTypes.has(type)) {
     return true
   }
diff --git a/packages/mime/src/lib/mime-type-to-content-type.ts b/packages/mime/src/lib/mime-type-to-content-type.ts
index 2e17f0df8e6..db3a3569ec9 100644
--- a/packages/mime/src/lib/mime-type-to-content-type.ts
+++ b/packages/mime/src/lib/mime-type-to-content-type.ts
@@ -1,11 +1,15 @@
+import { customCharsetByMimeType } from './define-mime-type.ts'
+
 /**
  * Converts a MIME type to a Content-Type header value, adding charset when appropriate.
  *
- * Adds `; charset=utf-8` to text-based MIME types:
+ * By default, adds `; charset=utf-8` to text-based MIME types:
  * - All `text/*` types (except `text/xml`)
  * - All `+json` suffixed types (RFC 8259 defines JSON as UTF-8)
  * - `application/json`, `application/javascript`
  *
+ * Custom charset registered via `defineMimeType()` takes precedence over built-in rules.
+ *
  * Note: `text/xml` is excluded because XML has built-in encoding detection.
  * Per the XML spec, documents without an encoding declaration must be UTF-8 or
  * UTF-16, detectable from byte patterns. Adding an external charset parameter
@@ -24,15 +28,22 @@
  * mimeTypeToContentType('text/xml')            // 'text/xml'
  */
 export function mimeTypeToContentType(mimeType: string): string {
-  if (
-    // Already has charset
-    mimeType.includes('charset') ||
-    // Exclude text/xml - XML has built-in encoding detection (see JSDoc above)
-    mimeType === 'text/xml'
-  ) {
+  // Already has charset - return as-is
+  if (mimeType.includes('charset')) {
     return mimeType
   }

+  // Exclude text/xml - XML has built-in encoding detection (see JSDoc above)
+  if (mimeType === 'text/xml') {
+    return mimeType
+  }
+
+  // Check custom charset registry
+  let customCharset = customCharsetByMimeType?.get(mimeType)
+  if (customCharset !== undefined) {
+    return `${mimeType}; charset=${customCharset}`
+  }
+
   // Text-based types that should have charset=utf-8
   if (
     mimeType.startsWith('text/') ||

PATCH

echo "Patch applied successfully."
