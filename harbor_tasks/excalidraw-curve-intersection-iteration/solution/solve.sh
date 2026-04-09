#!/bin/bash
set -e

cd /workspace/excalidraw

# Check if patch is already applied (idempotency check)
if grep -q "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 4)" packages/math/src/curve.ts; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch using Python for reliable multi-line edits
python3 << 'PYTHON_SCRIPT'
import re

filepath = "packages/math/src/curve.ts"
with open(filepath, "r") as f:
    lines = f.readlines()

# 1. Remove the lineSegment import line (line 4, 0-indexed line 3)
lines = [line for line in lines if 'import { lineSegment, lineSegmentIntersectionPoints } from "./segment";' not in line]

# Re-read content after line removal
content = "".join(lines)

# 2. Change iteration count from 3 to 4
content = content.replace(
    "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 3)",
    "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 4)"
)

# 3. Remove the fallback code block
# Match from "// Fallback:" comment through the two if blocks
fallback_pattern = r'''  // Fallback: approximate the curve with short segments to catch near-endpoint hits\.
  const startHit = lineSegmentIntersectionPoints\(
    lineSegment\(bezierEquation\(c, 0\), bezierEquation\(c, 1 / 20\)\),
    l,
  \);
  if \(startHit\) \{
    return \[startHit\];
  \}

  const endHit = lineSegmentIntersectionPoints\(
    lineSegment\(bezierEquation\(c, 19 / 20\), bezierEquation\(c, 1\)\),
    l,
  \);
  if \(endHit\) \{
    return \[endHit\];
  \}

'''
content = re.sub(fallback_pattern, "", content)

with open(filepath, "w") as f:
    f.write(content)

print("Changes applied successfully")
PYTHON_SCRIPT

# Verify the patch was applied
if ! grep -q "solveWithAnalyticalJacobian(c, l, t0, s0, 1e-2, 4)" packages/math/src/curve.ts; then
    echo "ERROR: Failed to apply patch"
    exit 1
fi

echo "Patch applied successfully!"
