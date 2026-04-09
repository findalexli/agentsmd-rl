#!/usr/bin/env bash
set -euo pipefail

cd /workspace/remix

# Idempotent: skip if already applied
if grep -q 'mimeTypeToContentType' packages/mime/src/index.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# --- 1. Create mimeTypeToContentType function ---
mkdir -p packages/mime/src/lib
cat > packages/mime/src/lib/mime-type-to-content-type.ts << 'MTTCT_EOF'
/**
 * Converts a MIME type to a Content-Type header value, adding charset when appropriate.
 *
 * Adds `; charset=utf-8` to text-based MIME types:
 * - All `text/*` types (except `text/xml`)
 * - All `+json` suffixed types (RFC 8259 defines JSON as UTF-8)
 * - `application/json`, `application/javascript`
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
  if (
    // Already has charset
    mimeType.includes('charset') ||
    // Exclude text/xml - XML has built-in encoding detection (see JSDoc above)
    mimeType === 'text/xml'
  ) {
    return mimeType
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
MTTCT_EOF

# --- 2. Create detectContentType function ---
cat > packages/mime/src/lib/detect-content-type.ts << 'DCT_EOF'
import { detectMimeType } from './detect-mime-type.ts'
import { mimeTypeToContentType } from './mime-type-to-content-type.ts'

/**
 * Detects the Content-Type header value for a given file extension or filename.
 *
 * Returns a full Content-Type value including charset when appropriate, based on
 * the charset defined in mime-db for the detected MIME type.
 *
 * @param extension The file extension (e.g. "css", ".css") or filename (e.g. "style.css")
 * @returns The Content-Type value, or undefined if not found
 *
 * @example
 * detectContentType('css')           // 'text/css;charset=utf-8'
 * detectContentType('.css')          // 'text/css;charset=utf-8'
 * detectContentType('style.css')     // 'text/css;charset=utf-8'
 * detectContentType('image.png')     // 'image/png'
 * detectContentType('unknown')       // undefined
 */
export function detectContentType(extension: string): string | undefined {
  let mimeType = detectMimeType(extension)
  return mimeType ? mimeTypeToContentType(mimeType) : undefined
}
DCT_EOF

# --- 3. Update mime package exports ---
cat > packages/mime/src/index.ts << 'INDEX_EOF'
export { detectContentType } from './lib/detect-content-type.ts'
export { detectMimeType } from './lib/detect-mime-type.ts'
export { isCompressibleMimeType } from './lib/is-compressible-mime-type.ts'
export { mimeTypeToContentType } from './lib/mime-type-to-content-type.ts'
INDEX_EOF

# --- 4. Update file.ts to use mimeTypeToContentType ---
sed -i "s/import { isCompressibleMimeType } from '@remix-run\/mime'/import { isCompressibleMimeType, mimeTypeToContentType } from '@remix-run\/mime'/" packages/response/src/lib/file.ts
sed -i 's/let contentType = file\.type/let contentType = mimeTypeToContentType(file.type)/' packages/response/src/lib/file.ts

# --- 4b. Update file.test.ts to expect charset in Content-Type ---
# Write Node.js script to a file to avoid escaping issues
cat > /tmp/update_test.py << 'PY_SCRIPT'
import re

with open('packages/response/src/lib/file.test.ts', 'r') as f:
    content = f.read()

# Update simple assertions for text/plain
content = content.replace(
    "assert.equal(response.headers.get('Content-Type'), 'text/plain')",
    "assert.equal(response.headers.get('Content-Type'), 'text/plain; charset=utf-8')"
)

# Update simple assertions for text/html
content = content.replace(
    "assert.equal(response.headers.get('Content-Type'), 'text/html')",
    "assert.equal(response.headers.get('Content-Type'), 'text/html; charset=utf-8')"
)

# Replace the testCases array - use a simpler approach with line-by-line replacement
lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Look for the testCases array start
    if "let testCases = [" in line and i + 10 < len(lines):
        # Check if this is the Content-Type test
        next_lines = '\n'.join(lines[i:i+10])
        if "test.html" in next_lines and "test.css" in next_lines:
            # Replace the entire testCases block
            new_lines.append("      let testCases = [")
            new_lines.append("        { type: 'text/html', expected: 'text/html; charset=utf-8', name: 'test.html' },")
            new_lines.append("        { type: 'text/css', expected: 'text/css; charset=utf-8', name: 'test.css' },")
            new_lines.append("        { type: 'text/javascript', expected: 'text/javascript; charset=utf-8', name: 'test.js' },")
            new_lines.append("        { type: 'application/json', expected: 'application/json; charset=utf-8', name: 'test.json' },")
            new_lines.append("        { type: 'image/png', expected: 'image/png', name: 'test.png' },")
            new_lines.append("        { type: 'image/jpeg', expected: 'image/jpeg', name: 'test.jpg' },")
            new_lines.append("        { type: 'image/svg+xml', expected: 'image/svg+xml', name: 'test.svg' },")
            new_lines.append("      ]")
            # Skip until we find the closing bracket of the old array
            while i < len(lines) and "]" not in lines[i]:
                i += 1
            i += 1  # Skip the closing bracket line too
            continue
    # Update the loop variable and assertion
    if "for (let { type, name } of testCases)" in line:
        line = line.replace("{ type, name }", "{ type, expected, name }")
    if "assert.equal(response.headers.get('Content-Type'), type)" in line:
        line = "        assert.equal(response.headers.get('Content-Type'), expected)"
    new_lines.append(line)
    i += 1

content = '\n'.join(new_lines)

with open('packages/response/src/lib/file.test.ts', 'w') as f:
    f.write(content)

print('Updated file.test.ts')
PY_SCRIPT

python3 /tmp/update_test.py

# --- 5. Update packages/mime/README.md to document new functions ---
cat > packages/mime/README.md << 'README_EOF'
# @remix-run/mime

Utilities for working with MIME types.

Data used for these utilities is generated at build time from [mime-db](https://github.com/jshttp/mime-db), but only includes standard MIME types. Experimental (`x-`) and vendor-specific (`vnd.`) MIME types have been excluded.

## Installation

```bash
npm install @remix-run/mime
```

## Usage

### `detectContentType(extension)`

Detects the Content-Type header value for a given file extension or filename, including `charset` for text-based types. See [`mimeTypeToContentType`](#mimetypetocontenttypemimetype) for charset logic.

```ts
import { detectContentType } from '@remix-run/mime'

detectContentType('css') // 'text/css; charset=utf-8'
detectContentType('.json') // 'application/json; charset=utf-8'
detectContentType('image.png') // 'image/png'
detectContentType('path/to/file.unknown') // undefined
```

### `detectMimeType(extension)`

Detects the MIME type for a given file extension or filename.

```ts
import { detectMimeType } from '@remix-run/mime'

detectMimeType('txt') // 'text/plain'
detectMimeType('.txt') // 'text/plain'
detectMimeType('file.txt') // 'text/plain'
detectMimeType('path/to/file.txt') // 'text/plain'
detectMimeType('unknown') // undefined
```

### `isCompressibleMimeType(mimeType)`

Checks if a MIME type is known to be compressible.

```ts
import { isCompressibleMimeType } from '@remix-run/mime'

isCompressibleMimeType('text/html') // true
isCompressibleMimeType('application/json') // true
isCompressibleMimeType('image/png') // false
isCompressibleMimeType('video/mp4') // false
```

For convenience, the function also accepts a full Content-Type header value:

```ts
import { isCompressibleMimeType } from '@remix-run/mime'

isCompressibleMimeType('text/html; charset=utf-8') // true
isCompressibleMimeType('application/json; charset=utf-8') // true
isCompressibleMimeType('image/png; charset=utf-8') // false
isCompressibleMimeType('video/mp4; charset=utf-8') // false
```

### `mimeTypeToContentType(mimeType)`

Converts a MIME type to a Content-Type header value, adding `; charset=utf-8` to text-based MIME types: `text/*` (except `text/xml` which has built-in encoding declarations), `application/json`, `application/javascript`, and all `+json` suffixed types. All other types are returned unchanged.

```ts
import { mimeTypeToContentType } from '@remix-run/mime'

mimeTypeToContentType('text/css') // 'text/css; charset=utf-8'
mimeTypeToContentType('application/json') // 'application/json; charset=utf-8'
mimeTypeToContentType('application/ld+json') // 'application/ld+json; charset=utf-8'
mimeTypeToContentType('image/png') // 'image/png'
```

## License

MIT
README_EOF

# --- 6. Create change files ---
mkdir -p packages/mime/.changes packages/response/.changes

cat > packages/mime/.changes/minor.detect-content-type.md << 'CHANGE1_EOF'
Add `detectContentType(extension)` function that returns a Content-Type header value with `charset` for text-based types.
CHANGE1_EOF

cat > packages/mime/.changes/minor.mime-type-to-content-type.md << 'CHANGE2_EOF'
Add `mimeTypeToContentType(mimeType)` function that converts a MIME type to a Content-Type header value, adding `charset` for text-based types.
CHANGE2_EOF

cat > packages/response/.changes/patch.content-type-charset.md << 'CHANGE3_EOF'
`createFileResponse` now includes `charset` in Content-Type for text-based files.
CHANGE3_EOF

echo "Patch applied successfully."
