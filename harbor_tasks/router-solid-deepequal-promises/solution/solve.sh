#!/bin/bash
set -e

cd /workspace/router

# Idempotency check - distinctive line from the patch
if grep -q "if (isPromiseLike(a) || isPromiseLike(b)) return false" packages/solid-router/src/useRouterState.tsx; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the fix by modifying the file directly
# First, add the isPromiseLike check inside deepEqual after the Object.is check
cat > /tmp/new_content.txt << 'EOF'
function deepEqual(a: any, b: any): boolean {
  if (Object.is(a, b)) return true

  if (isPromiseLike(a) || isPromiseLike(b)) return false

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false
  }

  const keysA = Object.keys(a)
  const keysB = Object.keys(b)

  if (keysA.length !== keysB.length) return false

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false
    if (!deepEqual(a[key], b[key])) return false
  }

  return true
}

function isPromiseLike(value: unknown): value is PromiseLike<unknown> {
  return (
    !!value &&
    (typeof value === 'object' || typeof value === 'function') &&
    typeof (value as PromiseLike<unknown>).then === 'function'
  )
}
EOF

# Replace the old deepEqual function with the new one
# We need to find and replace from "function deepEqual" to the closing brace before the export types

# Read the file
SRC_FILE="packages/solid-router/src/useRouterState.tsx"

# Use node to do the replacement (more reliable than sed for multi-line replacements)
node -e "
const fs = require('fs');
const src = fs.readFileSync('$SRC_FILE', 'utf8');

// Find the deepEqual function and replace it along with adding isPromiseLike
const deepEqualStart = src.indexOf('function deepEqual(a: any, b: any): boolean {');
const exportTypeStart = src.indexOf('export type UseRouterStateOptions');

if (deepEqualStart === -1 || exportTypeStart === -1) {
  console.error('Could not find markers');
  process.exit(1);
}

const newContent = src.substring(0, deepEqualStart) +
  \`function deepEqual(a: any, b: any): boolean {
  if (Object.is(a, b)) return true

  if (isPromiseLike(a) || isPromiseLike(b)) return false

  if (
    typeof a !== 'object' ||
    a === null ||
    typeof b !== 'object' ||
    b === null
  ) {
    return false
  }

  const keysA = Object.keys(a)
  const keysB = Object.keys(b)

  if (keysA.length !== keysB.length) return false

  for (const key of keysA) {
    if (!Object.prototype.hasOwnProperty.call(b, key)) return false
    if (!deepEqual(a[key], b[key])) return false
  }

  return true
}

function isPromiseLike(value: unknown): value is PromiseLike<unknown> {
  return (
    !!value &&
    (typeof value === 'object' || typeof value === 'function') &&
    typeof (value as PromiseLike<unknown>).then === 'function'
  )
}

\` +
  src.substring(exportTypeStart);

fs.writeFileSync('$SRC_FILE', newContent);
console.log('File updated successfully');
"

# Rebuild the package to apply changes
CI=1 NX_DAEMON=false pnpm nx run @tanstack/solid-router:build

echo "Patch applied and package rebuilt successfully"
