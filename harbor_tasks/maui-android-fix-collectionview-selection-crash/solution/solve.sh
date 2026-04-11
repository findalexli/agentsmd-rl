#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Fix 1: SelectableItemsViewAdapter.cs - Add header/footer guard
FILE1="src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs"

if grep -q "IsHeader(position) || ItemsSource.IsFooter(position)" "$FILE1" 2>/dev/null; then
    echo "Patch 1 already applied."
else
    git apply - <<'PATCH1'
diff --git a/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs b/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs
index 41f5619c3ea7..55579ae57324 100644
--- a/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs
+++ b/src/Controls/src/Core/Handlers/Items/Android/Adapters/SelectableItemsViewAdapter.cs
@@ -28,6 +28,14 @@ public override void OnBindViewHolder(RecyclerView.ViewHolder holder, int posi
 			return;
 		}

+		// Header and footer view holders should not participate in selection tracking.
+		// They are not data items and calling GetItem() on their positions would cause
+		// an ArgumentOutOfRangeException due to the header index adjustment.
+		if (ItemsSource.IsHeader(position) || ItemsSource.IsFooter(position))
+		{
+			return;
+		}
+
 		// Watch for clicks so the user can select the item held by this ViewHolder
 		selectable.Clicked += SelectableClicked;

PATCH1
    echo "Patch 1 applied successfully."
fi

# Fix 2: copilot-instructions.md - Add #nullable enable rule
FILE2=".github/copilot-instructions.md"

if grep -q "CRITICAL.*#nullable enable must be line 1" "$FILE2" 2>/dev/null; then
    echo "Patch 2 already applied."
else
    git apply - <<'PATCH2'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index b8f6e9a890a0..6b39e8adc893 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -138,6 +138,26 @@ When working with public API changes:
 - **Use `dotnet format analyzers`** if having trouble
 - **If files are incorrect**: Revert all changes, then add only the necessary new API entries

+**🚨 CRITICAL: `#nullable enable` must be line 1**
+
+Every `PublicAPI.Unshipped.txt` file starts with `#nullable enable` (often BOM-prefixed: `﻿#nullable enable`) on the **first line**. If this line is moved or removed, the analyzer treats it as a declared API symbol and emits **RS0017** errors.
+
+**Never sort these files with plain `sort`** — the BOM bytes (`0xEF 0xBB 0xBF`) sort after ASCII characters under `LC_ALL=C`, pushing `#nullable enable` to the bottom of the file.
+
+When resolving merge conflicts or adding entries, use this safe pattern that preserves line 1:
+```bash
+for f in $(git diff --name-only --diff-filter=U | grep "PublicAPI.Unshipped.txt"); do
+  # Extract and preserve the #nullable enable line (with or without BOM)
+  HEADER=$(head -1 "$f" | grep -o '.*#nullable enable' || echo '#nullable enable')
+  # Strip conflict markers, remove all #nullable lines, sort+dedup the API entries
+  grep -v '^<<<<<<\|^======\|^>>>>>>\|#nullable enable' "$f" | LC_ALL=C sort -u | sed '/^$/d' > /tmp/api_fix.txt
+  # Reassemble: header first, then sorted entries
+  printf '%s\n' "$HEADER" > "$f"
+  cat /tmp/api_fix.txt >> "$f"
+  git add "$f"
+done
+```
+
 ### Branching
 - `main` - For bug fixes without API changes
 - `net10.0` - For new features and API changes
PATCH2
    echo "Patch 2 applied successfully."
fi

echo "All patches applied."
