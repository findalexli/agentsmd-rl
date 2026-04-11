#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cline

# Idempotent: skip if already applied
if grep -q 'marginTop: -8' webview-ui/src/components/history/HistoryView.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Fix 1: Update CLAUDE.md - add Miscellaneous section after "What NOT to add" paragraph
sed -i '/What NOT to add.*standard practices.*comprehensive./a\
\
## Miscellaneous\
- This is a VS Code extension—check `package.json` for available scripts before trying to verify builds (e.g., `npm run compile`, not `npm run build`).' CLAUDE.md

# Fix 2: Modify HistoryView.tsx using Python for complex multi-line edits
cat > /tmp/fix_history_view.py << 'PYEOF'
filepath = 'webview-ui/src/components/history/HistoryView.tsx'
with open(filepath, 'r') as f:
    content = f.read()

lines = content.split('\n')
new_lines = []
i = 0
while i < len(lines):
    line = lines[i]

    # Find "Most Relevant" line (the VSCodeRadio line containing "Most Relevant")
    if 'Most Relevant' in line and '<VSCodeRadio' in line:
        new_lines.append(line)
        i += 1
        continue

    # Find the closing VSCodeRadio after Most Relevant
    if line.strip() == '</VSCodeRadio>' and i > 0 and 'Most Relevant' in lines[i-1]:
        new_lines.append(line)
        # Add closing VSCodeRadioGroup
        new_lines.append('\t\t\t\t\t\t</VSCodeRadioGroup>')
        # Add new div with marginTop
        new_lines.append('\t\t\t\t\t\t<div className="flex flex-wrap" style={{ marginTop: -8 }}>')
        i += 1
        continue

    # Skip the original closing </VSCodeRadioGroup> (we'll replace it with </div>)
    if line.strip() == '</VSCodeRadioGroup>':
        # Check context - if this is after Favorites, replace with </div>
        prev_content = '\n'.join(new_lines[-10:])
        if 'Favorites' in prev_content:
            new_lines.append('\t\t\t\t\t\t</div>')
            i += 1
            continue

    # Reformat the Workspace VSCodeRadio (one-liner to multi-line)
    if 'showCurrentWorkspaceOnly' in line and 'onClick' in line and line.strip().startswith('<VSCodeRadio'):
        new_lines.append('\t\t\t\t\t\t\t<VSCodeRadio')
        new_lines.append('\t\t\t\t\t\t\t\tchecked={showCurrentWorkspaceOnly}')
        new_lines.append('\t\t\t\t\t\t\t\tonClick={() => setShowCurrentWorkspaceOnly(!showCurrentWorkspaceOnly)}>')
        i += 1
        continue

    # Reformat the Favorites VSCodeRadio (one-liner to multi-line)
    if 'showFavoritesOnly' in line and 'onClick' in line and line.strip().startswith('<VSCodeRadio'):
        new_lines.append('\t\t\t\t\t\t\t<VSCodeRadio')
        new_lines.append('\t\t\t\t\t\t\t\tchecked={showFavoritesOnly}')
        new_lines.append('\t\t\t\t\t\t\t\tonClick={() => setShowFavoritesOnly(!showFavoritesOnly)}>')
        i += 1
        continue

    new_lines.append(line)
    i += 1

with open(filepath, 'w') as f:
    f.write('\n'.join(new_lines))

print("HistoryView.tsx updated successfully")
PYEOF

python3 /tmp/fix_history_view.py

echo "Patch applied successfully."
