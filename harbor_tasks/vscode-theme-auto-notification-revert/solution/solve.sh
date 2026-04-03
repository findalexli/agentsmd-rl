#!/bin/bash
set -euo pipefail

# This script removes the showThemeAutoUpdatedNotification method and its call
# Reverts the notification added in PR #306341

THEME_SERVICE_FILE="src/vs/workbench/services/themes/browser/workbenchThemeService.ts"

cd /workspace/vscode

# Check if already applied (idempotency check)
if ! grep -q "showThemeAutoUpdatedNotification" "$THEME_SERVICE_FILE"; then
    echo "Fix already applied (showThemeAutoUpdatedNotification not found)"
    exit 0
fi

# Remove the call to showThemeAutoUpdatedNotification() from initialize()
sed -i '/this\.showThemeAutoUpdatedNotification()/d' "$THEME_SERVICE_FILE"

# Remove the THEME_AUTO_UPDATED_NOTIFICATION_KEY constant and the entire
# showThemeAutoUpdatedNotification method (from the constant declaration
# through to the closing of the method, ending before the next method)
# Strategy: delete from the THEME_AUTO_UPDATED_NOTIFICATION_KEY line
# to the blank line before the next JSDoc comment (/** ... */)
python3 -c "
import re

with open('$THEME_SERVICE_FILE', 'r') as f:
    content = f.read()

# Remove the block: from 'private static readonly THEME_AUTO_UPDATED_NOTIFICATION_KEY'
# through to the blank line before the next method/comment
# The block ends with '}));' then a tab+'}' then a blank line
pattern = (
    r'\n\tprivate static readonly THEME_AUTO_UPDATED_NOTIFICATION_KEY.*?'
    r'\n\t\}\n(?=\n\t/\*\*)'
)
content = re.sub(pattern, '\n', content, flags=re.DOTALL)

with open('$THEME_SERVICE_FILE', 'w') as f:
    f.write(content)
"

echo "Applied fix: removed showThemeAutoUpdatedNotification method and its call"
