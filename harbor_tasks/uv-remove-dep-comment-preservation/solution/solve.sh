#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Check if already applied
if grep -q 'Transfer removed item.*prefix to the next' crates/uv-workspace/src/pyproject_mut.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-workspace/src/pyproject_mut.rs b/crates/uv-workspace/src/pyproject_mut.rs
index a9ebf3dd49399..1da387822cff6 100644
--- a/crates/uv-workspace/src/pyproject_mut.rs
+++ b/crates/uv-workspace/src/pyproject_mut.rs
@@ -1545,11 +1545,51 @@ fn update_requirement(old: &mut Requirement, new: &Requirement, has_source: bool

 /// Removes all occurrences of dependencies with the given name from the given `deps` array.
 fn remove_dependency(name: &PackageName, deps: &mut Array) -> Vec<Requirement> {
-    // Remove matching dependencies.
+    // Remove in reverse to preserve indices. Before each removal, transfer the item's
+    // prefix (which may contain end-of-line comments belonging to the previous line) to
+    // the next item or array trailing so comments are not lost.
+    //
+    // For example, in:
+    // ```toml
+    // dependencies = [
+    //     "numpy>=2.4.3", # essential comment
+    //     "requests>=2.32.5",
+    // ]
+    // ```
+    //
+    // The comment `# essential comment` is stored by `toml_edit` in the prefix of
+    // `requests`. When `requests` is removed, we transfer it so it remains on the
+    // `numpy` line.
     let removed = find_dependencies(name, None, deps)
         .into_iter()
-        .rev() // Reverse to preserve indices as we remove them.
+        .rev()
         .filter_map(|(i, _)| {
+            if let Some(prefix) = deps
+                .get(i)
+                .and_then(|item| item.decor().prefix().and_then(|s| s.as_str()))
+                .filter(|s| !s.is_empty())
+            {
+                let prefix = prefix.to_string();
+                if let Some(next) = deps.get(i + 1)
+                    && let Some(existing) = next.decor().prefix().and_then(|s| s.as_str())
+                {
+                    // Transfer removed item's prefix to the next item's prefix.
+                    let existing = existing.to_string();
+                    deps.get_mut(i + 1)
+                        .unwrap()
+                        .decor_mut()
+                        .set_prefix(format!("{prefix}{existing}"));
+                } else if let Some(next) = deps.get_mut(i + 1) {
+                    // Next item exists but has no prefix; use ours directly.
+                    next.decor_mut().set_prefix(&prefix);
+                } else if let Some(existing) = deps.trailing().as_str() {
+                    // No next item; move comments to the array trailing.
+                    deps.set_trailing(format!("{prefix}{existing}"));
+                } else {
+                    deps.set_trailing(&prefix);
+                }
+            }
+
             deps.remove(i)
                 .as_str()
                 .and_then(|req| Requirement::from_str(req).ok())

PATCH
