#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Fix 1: SelectableItemsViewAdapter.cs - Add header/footer guard
FILE1="src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"

if grep -q "IsHeader(position) || ItemsSource.IsFooter(position)" "$FILE1" 2>/dev/null; then
    echo "Patch 1 already applied."
else
    # Use awk to insert the guard code after line 29
    awk '
    NR==29 && /^\t\t\t}$/ {
        print
        print ""
        print "\t\t\t// Header and footer view holders should not participate in selection tracking."
        print "\t\t\t// They are not data items and calling GetItem() on their positions would cause"
        print "\t\t\t// an ArgumentOutOfRangeException due to the header index adjustment."
        print "\t\t\tif (ItemsSource.IsHeader(position) || ItemsSource.IsFooter(position))"
        print "\t\t\t{"
        print "\t\t\t\treturn;"
        print "\t\t\t}"
        next
    }
    { print }
    ' "$FILE1" > "${FILE1}.tmp" && mv "${FILE1}.tmp" "$FILE1"
    echo "Patch 1 applied successfully."
fi

# Fix 2: copilot-instructions.md - Append #nullable enable rule at the end
FILE2=".github/copilot-instructions.md"

if grep -q "CRITICAL.*#nullable enable must be line 1" "$FILE2" 2>/dev/null; then
    echo "Patch 2 already applied."
else
    # Append to end of file
    cat >> "$FILE2" << 'INNEREOF'

**🚨 CRITICAL: `#nullable enable` must be line 1**

Every `PublicAPI.Unshipped.txt` file starts with `#nullable enable` (often BOM-prefixed: `#nullable enable`) on the **first line**. If this line is moved or removed, the analyzer treats it as a declared API symbol and emits **RS0017** errors.

**Never sort these files with plain `sort`** — the BOM bytes (`0xEF 0xBB 0xBF`) sort after ASCII characters under `LC_ALL=C`, pushing `#nullable enable` to the bottom of the file.

When resolving merge conflicts or adding entries, use this safe pattern that preserves line 1:
```bash
for f in $(git diff --name-only --diff-filter=U | grep "PublicAPI.Unshipped.txt"); do
  # Extract and preserve the #nullable enable line (with or without BOM)
  HEADER=$(head -1 "$f" | grep -o '.*#nullable enable' || echo '#nullable enable')
  # Strip conflict markers, remove all #nullable lines, sort+dedup the API entries
  grep -v '^<<<<<<\|^======\|^>>>>>>\|#nullable enable' "$f" | LC_ALL=C sort -u | sed '/^$/d' > /tmp/api_fix.txt
  # Reassemble: header first, then sorted entries
  printf '%s\n' "$HEADER" > "$f"
  cat /tmp/api_fix.txt >> "$f"
  git add "$f"
done
```
INNEREOF
    echo "Patch 2 applied successfully."
fi

echo "All patches applied."
