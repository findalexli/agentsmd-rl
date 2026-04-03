#!/bin/bash
set -euo pipefail

cd /workspace/react

TARGET="packages/shared/ReactPerformanceTrackProperties.js"

# Check if already applied
if grep -q "^const REMOVED = '-\\\\xa0';" "$TARGET" 2>/dev/null; then
    echo "Fix already applied"
    exit 0
fi

# Replace en dash (\u2013) with ASCII minus (-) in the REMOVED constant
# Before: const REMOVED = '\u2013\xa0';
# After:  const REMOVED = '-\xa0';
sed -i "s/const REMOVED = '\\\\u2013\\\\xa0';/const REMOVED = '-\\\\xa0';/" "$TARGET"

# Also update the test expectations to match
TEST_FILE="packages/react-reconciler/src/__tests__/ReactPerformanceTrack-test.js"
if [ -f "$TEST_FILE" ]; then
    # Replace literal en dash (UTF-8: e2 80 93) with minus in test expectations
    python3 -c "
import pathlib
p = pathlib.Path('$TEST_FILE')
content = p.read_text()
content = content.replace('\u2013', '-')
p.write_text(content)
"
fi

echo "Fix applied successfully"
