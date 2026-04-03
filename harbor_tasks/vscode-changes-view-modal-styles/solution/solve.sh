#!/bin/bash
set -euo pipefail

cd /workspace/vscode

# Check if already applied (idempotency check)
# The fix changes a hardcoded `true` to `items.length > 1` in changesView.ts
if grep -q "openFileItem(e.element, items, e.sideBySide, !!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, items.length > 1);" src/vs/sessions/contrib/changes/browser/changesView.ts 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the fix using sed for the TypeScript change
sed -i 's/openFileItem(e\.element, items, e\.sideBySide, !!e\.editorOptions?\.preserveFocus, !!e\.editorOptions?\.pinned, true);/openFileItem(e.element, items, e.sideBySide, !!e.editorOptions?.preserveFocus, !!e.editorOptions?.pinned, items.length > 1);/' \
    src/vs/sessions/contrib/changes/browser/changesView.ts

# Apply the CSS selector changes: replace .changes-view-body with .chat-editing-session-list
# in the action bar and diff stats sections (lines 246-262)
sed -i '/\.monaco-list-row.*\.chat-collapsible-list-action-bar/s/\.changes-view-body/.chat-editing-session-list/g' \
    src/vs/sessions/contrib/changes/browser/media/changesView.css
sed -i '/\.monaco-list-row.*\.working-set-line-counts/s/\.changes-view-body/.chat-editing-session-list/g' \
    src/vs/sessions/contrib/changes/browser/media/changesView.css

echo "Patch applied successfully!"
