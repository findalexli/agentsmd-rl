#!/bin/bash
set -e

# Fix: Wrap the function call in try-catch to handle sync errors.
# The issue is that when a sync function throws, the error escapes
# because there's no try-catch. The fix is to:
# 1. Capture the return value
# 2. Wrap in try-catch
# 3. Pass sync errors to next()

cat > index.js << 'EOF'
const asyncUtil = fn => (req, res, next) => {
  try {
    const ret = fn(req, res, next)
    if (ret && typeof ret.catch === 'function') {
      ret.catch(next)
    }
    return ret
  } catch (e) {
    next(e)
  }
}

module.exports = asyncUtil
EOF

echo "Applied fix for sync error handling in asyncHandler"
