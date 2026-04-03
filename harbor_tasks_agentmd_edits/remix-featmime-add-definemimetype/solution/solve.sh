#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'defineMimeType' packages/mime/src/lib/define-mime-type.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create define-mime-type.ts
cat > packages/mime/src/lib/define-mime-type.ts << 'NEWFILE'
export interface MimeTypeDefinition {
  /** The file extension(s) to register (e.g., ['x-myformat']) */
  extensions: string | string[]
  /** The MIME type for these extensions (e.g., 'application/x-myformat') */
  mimeType: string
  /**
   * Whether this MIME type is compressible.
   * If omitted, falls back to default heuristics (text/*, +json, +text, +xml).
   */
  compressible?: boolean
  /**
   * Charset to include in Content-Type header.
   * - `'utf-8'` or other string → '; charset={value}'
   * - `undefined` → falls back to default heuristics (`'utf-8'` for `text/*`, `application/json`, `+json`)
   */
  charset?: string
}

// Custom registries - only created when defineMimeType is called.
// Exported for direct access to avoid function call overhead in hot paths.
export let customMimeTypeByExtension: Map<string, string> | undefined
export let customCompressibleByMimeType: Map<string, boolean> | undefined
export let customCharsetByMimeType: Map<string, string> | undefined

/**
 * Registers a custom MIME type for one or more file extensions.
 *
 * Use this to add support for file extensions not included in the defaults,
 * or to override the behavior of existing extensions.
 *
 * @param definition The MIME type definition to register
 *
 * @example
 * defineMimeType({
 *   extensions: ['x-myformat'],
 *   mimeType: 'application/x-myformat',
 * })
 *
 * @example
 * // Configure compressibility and charset
 * defineMimeType({
 *   extensions: ['x-myformat'],
 *   mimeType: 'application/x-myformat',
 *   compressible: true, // Optional
 *   charset: 'utf-8', // Optional
 * })
 */
export function defineMimeType(definition: MimeTypeDefinition): void {
  let extensions = Array.isArray(definition.extensions)
    ? definition.extensions
    : [definition.extensions]

  customMimeTypeByExtension ??= new Map()
  for (let ext of extensions) {
    ext = ext.trim().toLowerCase()
    // Remove leading dot if present
    if (ext.startsWith('.')) {
      ext = ext.slice(1)
    }
    customMimeTypeByExtension.set(ext, definition.mimeType)
  }

  if (definition.compressible !== undefined) {
    customCompressibleByMimeType ??= new Map()
    customCompressibleByMimeType.set(definition.mimeType, definition.compressible)
  }

  if (definition.charset !== undefined) {
    customCharsetByMimeType ??= new Map()
    customCharsetByMimeType.set(definition.mimeType, definition.charset)
  }
}

// @internal - Resets all custom registrations. Used in tests for isolation.
export function resetMimeTypes(): void {
  customMimeTypeByExtension = undefined
  customCompressibleByMimeType = undefined
  customCharsetByMimeType = undefined
}
NEWFILE

# Update index.ts to export defineMimeType
cat > packages/mime/src/index.ts << 'NEWFILE'
export { detectContentType } from './lib/detect-content-type.ts'
export { detectMimeType } from './lib/detect-mime-type.ts'
export { isCompressibleMimeType } from './lib/is-compressible-mime-type.ts'
export { mimeTypeToContentType } from './lib/mime-type-to-content-type.ts'
export { defineMimeType } from './lib/define-mime-type.ts'
export type { MimeTypeDefinition } from './lib/define-mime-type.ts'
NEWFILE

# Update detect-mime-type.ts to check custom registry
cat > packages/mime/src/lib/detect-mime-type.ts << 'NEWFILE'
import { mimeTypes } from '../generated/mime-types.ts'
import { customMimeTypeByExtension } from './define-mime-type.ts'

/**
 * Detects the MIME type for a given file extension or filename.
 *
 * Custom MIME types registered via `defineMimeType()` take precedence over built-in types.
 *
 * @param extension The file extension (e.g. "txt", ".txt") or filename (e.g. "file.txt")
 * @returns The MIME type string, or undefined if not found
 *
 * @example
 * detectMimeType('txt')           // 'text/plain'
 * detectMimeType('.txt')          // 'text/plain'
 * detectMimeType('file.txt')      // 'text/plain'
 * detectMimeType('unknown')       // undefined
 */
export function detectMimeType(extension: string): string | undefined {
  let ext = extension.trim().toLowerCase()
  let idx = ext.lastIndexOf('.')
  // If no dot found (~idx === -1, so !~idx === true), use ext as-is.
  // Otherwise, skip past the dot (++idx) and extract the extension.
  // Credit to mrmime for this technique.
  ext = !~idx ? ext : ext.substring(++idx)
  return customMimeTypeByExtension?.get(ext) ?? mimeTypes[ext]
}
NEWFILE

# Update is-compressible-mime-type.ts to check custom registry
cat > packages/mime/src/lib/is-compressible-mime-type.ts << 'NEWFILE'
import { compressibleMimeTypes } from '../generated/compressible-mime-types.ts'
import { customCompressibleByMimeType } from './define-mime-type.ts'

/**
 * Checks if a MIME type is known to be compressible.
 *
 * Returns true for:
 * - Compressible MIME types from mime-db, except for types starting with `x-` (experimental) or `vnd.` (vendor-specific).
 * - Any text/* type
 * - Types with +json, +text, or +xml suffix
 * - MIME types explicitly registered as compressible via `defineMimeType()`
 *
 * Accepts either a bare MIME type or a full Content-Type header value with parameters.
 *
 * @param mimeType The MIME type to check (e.g. "application/json" or "text/html; charset=utf-8")
 * @returns true if the MIME type is known to be compressible
 */
export function isCompressibleMimeType(mimeType: string): boolean {
  if (!mimeType) return false

  // Extract MIME type from Content-Type header if it includes parameters
  let idx = mimeType.indexOf(';')
  let type = ~idx ? mimeType.substring(0, idx).trim() : mimeType

  let customCompressible = customCompressibleByMimeType?.get(type)
  if (customCompressible !== undefined) {
    return customCompressible
  }

  if (compressibleMimeTypes.has(type)) {
    return true
  }

  return genericCompressibleRegex.test(type)
}

// Check for text/*, or anything with +json, +text, or +xml suffix
const genericCompressibleRegex = /^text\/|\+(?:json|text|xml)$/i
NEWFILE

# Update mime-type-to-content-type.ts to check custom charset
cat > packages/mime/src/lib/mime-type-to-content-type.ts << 'NEWFILE'
import { customCharsetByMimeType } from './define-mime-type.ts'

/**
 * Converts a MIME type to a Content-Type header value, adding charset when appropriate.
 *
 * By default, adds `; charset=utf-8` to text-based MIME types:
 * - All `text/*` types (except `text/xml`)
 * - All `+json` suffixed types (RFC 8259 defines JSON as UTF-8)
 * - `application/json`, `application/javascript`
 *
 * Custom charset registered via `defineMimeType()` takes precedence over built-in rules.
 *
 * Note: `text/xml` is excluded because XML has built-in encoding detection.
 * Per the XML spec, documents without an encoding declaration must be UTF-8 or
 * UTF-16, detectable from byte patterns. Adding an external charset parameter
 * is redundant and can conflict with the document's internal declaration.
 *
 * @see https://www.w3.org/TR/xml/#charencoding
 *
 * @param mimeType The MIME type (e.g. "text/css", "image/png")
 * @returns The Content-Type value with charset if appropriate
 *
 * @example
 * mimeTypeToContentType('text/html')           // 'text/html; charset=utf-8'
 * mimeTypeToContentType('application/json')    // 'application/json; charset=utf-8'
 * mimeTypeToContentType('application/ld+json') // 'application/ld+json; charset=utf-8'
 * mimeTypeToContentType('image/png')           // 'image/png'
 * mimeTypeToContentType('text/xml')            // 'text/xml'
 */
export function mimeTypeToContentType(mimeType: string): string {
  // Already has charset - return as-is
  if (mimeType.includes('charset')) {
    return mimeType
  }

  // Exclude text/xml - XML has built-in encoding detection (see JSDoc above)
  if (mimeType === 'text/xml') {
    return mimeType
  }

  // Check custom charset registry
  let customCharset = customCharsetByMimeType?.get(mimeType)
  if (customCharset !== undefined) {
    return `${mimeType}; charset=${customCharset}`
  }

  // Text-based types that should have charset=utf-8
  if (
    mimeType.startsWith('text/') ||
    mimeType.endsWith('+json') ||
    mimeType === 'application/json' ||
    mimeType === 'application/javascript'
  ) {
    return `${mimeType}; charset=utf-8`
  }

  return mimeType
}
NEWFILE

# Update README.md to document defineMimeType
cat > /tmp/readme_patch.py << 'PYSCRIPT'
import re
path = "packages/mime/README.md"
with open(path) as f:
    content = f.read()

insert_after = "mimeTypeToContentType('image/png') // 'image/png'\n```"
new_section = """

### `defineMimeType(definition)`

Registers or overrides a MIME type for one or more file extensions.

```ts
import { defineMimeType } from '@remix-run/mime'

defineMimeType({
  extensions: ['myformat'],
  mimeType: 'application/x-myformat',
})
```

You can also optionally configure the charset and whether the MIME type is compressible:

```ts
defineMimeType({
  extensions: ['myformat'],
  mimeType: 'application/x-myformat',
  compressible: true,
  charset: 'utf-8',
})
```"""

content = content.replace(insert_after, insert_after + new_section)
with open(path, 'w') as f:
    f.write(content)
PYSCRIPT
python3 /tmp/readme_patch.py

# Create changeset file
cat > packages/mime/.changes/minor.define-mime-type.md << 'NEWFILE'
Add `defineMimeType()` for registering custom MIME types. This allows adding support for file extensions not included in the defaults, or overriding existing behavior. Custom registrations take precedence over built-in types.

```ts
import { defineMimeType, detectMimeType } from '@remix-run/mime'

defineMimeType({
  extensions: 'myformat',
  mimeType: 'application/x-myformat',
})

detectMimeType('file.myformat') // 'application/x-myformat'
```
NEWFILE

echo "Patch applied successfully."
