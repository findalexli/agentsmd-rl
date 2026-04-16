#!/bin/bash
set -e

cd /workspace/excalidraw
CURVE_FILE="packages/math/src/curve.ts"

# Idempotency check: verify if fix is already applied
if grep -q "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 4)" "$CURVE_FILE"; then
    echo "Fix already applied, skipping"
    exit 0
fi

python3 << 'EOF'
import re

CURVE_FILE = "packages/math/src/curve.ts"

with open(CURVE_FILE, "r") as f:
    content = f.read()

# Step 1: Change iteration count from 3 to 4
content = content.replace(
    "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 3)",
    "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 4)"
)

# Step 2: Remove unused import
content = content.replace(
    'import { lineSegment, lineSegmentIntersectionPoints } from "./segment";\n',
    ""
)

# Step 3: Remove the fallback code block
# Match from "// Fallback:" through the end of the second if block
fallback_pattern = r'''  // Fallback: approximate the curve with short segments to catch near-endpoint hits\.
  const startHit = lineSegmentIntersectionPoints\(
    lineSegment\(bezierEquation\(c, 0\), bezierEquation\(c, 1 / 20\)\),
    l,
  \);
  if \(startHit\) {
    return \[startHit\];
  }

  const endHit = lineSegmentIntersectionPoints\(
    lineSegment\(bezierEquation\(c, 19 / 20\), bezierEquation\(c, 1\)\),
    l,
  \);
  if \(endHit\) {
    return \[endHit\];
  }

'''

content = re.sub(fallback_pattern, "", content)

with open(CURVE_FILE, "w") as f:
    f.write(content)

print("Fix applied successfully")
EOF
