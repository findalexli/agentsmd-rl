#!/bin/bash
set -e

cd /workspace/router

# Idempotency check: verify if fix is already applied
if grep -q "useLayoutEffect" packages/react-router/src/Match.tsx && grep -q "return null" packages/react-router/src/Match.tsx; then
    echo "Fix already applied, skipping..."
    exit 0
fi

# Use Python for complex replacements
python3 << 'PYTHON_SCRIPT'
import re

# Read the file
with open('packages/react-router/src/Match.tsx', 'r') as f:
    content = f.read()

# 1. Update imports - replace the multi-line type import
old_import = '''import type {
  AnyRoute,
  ParsedLocation,
  RootRouteOptions,
} from '@tanstack/router-core'
'''

new_import = '''import { useLayoutEffect } from './utils'
import type { AnyRoute, RootRouteOptions } from '@tanstack/router-core'
'''

content = content.replace(old_import, new_import)

# 2. Update OnRendered call to pass resetKey
content = content.replace('<OnRendered />', '<OnRendered resetKey={resetKey} />')

# 3. Find and replace the OnRendered function
# Look for the function signature and its body
lines = content.split('\n')
start_idx = None
end_idx = None
brace_count = 0
in_function = False

for i, line in enumerate(lines):
    # Find the comment block before OnRendered
    if '// On Rendered can' in line and start_idx is None:
        # This is the start of the comment
        start_idx = i

    if start_idx is not None and not in_function:
        # Look for the function signature
        if 'function OnRendered()' in line:
            in_function = True
            brace_count = 0

    if in_function:
        # Count braces to find end of function
        for c in line:
            if c == '{':
                brace_count += 1
            elif c == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        if end_idx is not None:
            break

if start_idx is None or end_idx is None:
    print("ERROR: Could not find OnRendered function!")
    print(f"start_idx={start_idx}, end_idx={end_idx}")
    exit(1)

new_function = '''// On Rendered can't happen above the root layout because it needs to run after
// the route subtree has committed below the root layout. Keeping it here lets
// us fire onRendered even after a hydration mismatch above the root layout
// (like bad head/link tags, which is common).
function OnRendered({ resetKey }: { resetKey: number }) {
  const router = useRouter()

  if (isServer ?? router.isServer) {
    return null
  }

  // eslint-disable-next-line react-hooks/rules-of-hooks
  const prevHrefRef = React.useRef<string | undefined>(undefined)

  // eslint-disable-next-line react-hooks/rules-of-hooks
  useLayoutEffect(() => {
    const currentHref = router.latestLocation.href

    if (
      prevHrefRef.current === undefined ||
      prevHrefRef.current !== currentHref
    ) {
      router.emit({
        type: 'onRendered',
        ...getLocationChangeInfo(
          router.stores.location.state,
          router.stores.resolvedLocation.state,
        ),
      })
      prevHrefRef.current = currentHref
    }
  }, [router.latestLocation.state.__TSR_key, resetKey, router])

  return null
}'''

# Replace the old function with the new one
new_lines = lines[:start_idx] + new_function.split('\n') + lines[end_idx+1:]
content = '\n'.join(new_lines)

# Write back
with open('packages/react-router/src/Match.tsx', 'w') as f:
    f.write(content)

print("Match.tsx updated successfully")
PYTHON_SCRIPT

# Update the test expectation to remove the sentinel script tag
python3 << 'PYTHON_SCRIPT'
with open('packages/react-router/tests/Scripts.test.tsx', 'r') as f:
    content = f.read()

# Remove the sentinel script tag from the expected output
content = content.replace('<script></script><script src="script.js">', '<script src="script.js">')

with open('packages/react-router/tests/Scripts.test.tsx', 'w') as f:
    f.write(content)

print("Scripts.test.tsx updated successfully")
PYTHON_SCRIPT

# Update the solid-router comment for consistency
if [ -f packages/solid-router/src/Match.tsx ]; then
    python3 << 'PYTHON_SCRIPT'
with open('packages/solid-router/src/Match.tsx', 'r') as f:
    content = f.read()

# Update the comment to match the new pattern
old_comment = '''// On Rendered can't happen above the root layout because it actually
// renders a dummy dom element to track the rendered state of the app.
// We render a script tag with a key that changes based on the current
// location state.__TSR_key. Also, because it's below the root layout, it
// allows us to fire onRendered events even after a hydration mismatch
// error that occurred above the root layout (like bad head/link tags,
// which is common).'''

new_comment = '''// On Rendered can't happen above the root layout because it needs to run after
// the route subtree has committed below the root layout. Keeping it here lets
// us fire onRendered even after a hydration mismatch above the root layout
// (like bad head/link tags, which is common).'''

content = content.replace(old_comment, new_comment)

with open('packages/solid-router/src/Match.tsx', 'w') as f:
    f.write(content)

print("solid-router Match.tsx updated successfully")
PYTHON_SCRIPT
fi

# Rebuild the react-router package
pnpm nx run @tanstack/react-router:build

echo "Fix applied successfully"
