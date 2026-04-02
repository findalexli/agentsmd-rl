#!/bin/bash
set -euo pipefail

# Apply the gold patch for fault tolerance test fixture
cd /workspace/react

# Check if already applied (look for distinctive file)
if [ -f "compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.fault-tolerance-reports-multiple-errors.js" ]; then
    echo "Patch already applied"
    exit 0
fi

# Create the fixture directory
mkdir -p compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler

cat > compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.fault-tolerance-reports-multiple-errors.js << 'EOF'
// @validateRefAccessDuringRender
/**
 * This fixture tests fault tolerance: the compiler should report
 * multiple independent errors rather than stopping at the first one.
 *
 * Error 1: Ref access during render (ref.current)
 * Error 2: Mutation of frozen value (props)
 */
function Component(props) {
  const ref = useRef(null);

  // Error: reading ref during render
  const value = ref.current;

  // Error: mutating frozen value (props, which is frozen after hook call)
  props.items = [];

  return <div>{value}</div>;
}
EOF

cat > compiler/packages/babel-plugin-react-compiler/src/__tests__/fixtures/compiler/error.fault-tolerance-reports-multiple-errors.expect.md << 'EOF'

## Input

```javascript
// @validateRefAccessDuringRender
/**
 * This fixture tests fault tolerance: the compiler should report
 * multiple independent errors rather than stopping at the first one.
 *
 * Error 1: Ref access during render (ref.current)
 * Error 2: Mutation of frozen value (props)
 */
function Component(props) {
  const ref = useRef(null);

  // Error: reading ref during render
  const value = ref.current;

  // Error: mutating frozen value (props, which is frozen after hook call)
  props.items = [];

  return <div>{value}</div>;
}

```


## Error

```
Found 2 errors:

Error: This value cannot be modified

Modifying component props or hook arguments is not allowed. Consider using a local variable instead.

error.fault-tolerance-reports-multiple-errors.ts:16:2
  14 |
  15 |   // Error: mutating frozen value (props, which is frozen after hook call)
> 16 |   props.items = [];
     |   ^^^^^ value cannot be modified
  17 |
  18 |   return <div>{value}</div>;
  19 | }

Error: Cannot access refs during render

React refs are values that are not needed for rendering. Refs should only be accessed outside of render, such as in event handlers or effects. Accessing a ref value (the `current` property) during render can cause your component not to update as expected (https://react.dev/reference/react/useRef).

error.fault-tolerance-reports-multiple-errors.ts:13:16
  11 |
  12 |   // Error: reading ref during render
> 13 |   const value = ref.current;
     |                 ^^^^^^^^^^^ Cannot access ref value during render
  14 |
  15 |   // Error: mutating frozen value (props, which is frozen after hook call)
  16 |   props.items = [];
```


EOF

echo "Patch applied successfully"
