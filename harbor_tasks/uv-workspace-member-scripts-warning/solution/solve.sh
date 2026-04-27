#!/bin/bash
# Apply the gold patch for astral-sh/uv PR #18389:
# "Warn when workspace member scripts are skipped due to missing build system"
set -euo pipefail

cd /workspace/uv

# Idempotency guard: distinctive line introduced by the patch.
if grep -q 'for package `{}` because this project is not packaged' \
        crates/uv/src/commands/project/sync.rs 2>/dev/null; then
    echo "Patch already applied — skipping."
    exit 0
fi

# Apply the gold diff (PR #18389 vs its merge base 5dc986d).
git apply --whitespace=nowarn <<'PATCH'
diff --git a/crates/uv/src/commands/project/sync.rs b/crates/uv/src/commands/project/sync.rs
index 8d56869666701..5777a9dc837f0 100644
--- a/crates/uv/src/commands/project/sync.rs
+++ b/crates/uv/src/commands/project/sync.rs
@@ -6,6 +6,7 @@ use std::sync::Arc;
 use anyhow::Result;
 use itertools::Itertools;
 use owo_colors::OwoColorize;
+use rustc_hash::FxHashSet;
 use serde::Serialize;
 use tracing::warn;
 use uv_cache::Cache;
@@ -133,16 +134,6 @@ pub(crate) async fn sync(
             project
         };

-        // TODO(lucab): improve warning content
-        // <https://github.com/astral-sh/uv/issues/7428>
-        if project.workspace().pyproject_toml().has_scripts()
-            && !project.workspace().pyproject_toml().is_package(true)
-        {
-            warn_user!(
-                "Skipping installation of entry points (`project.scripts`) because this project is not packaged; to install entry points, set `tool.uv.package = true` or define a `build-system`"
-            );
-        }
-
         SyncTarget::Project(project)
     };

@@ -394,6 +385,23 @@ pub(crate) async fn sync(
     // Identify the installation target.
     let sync_target = identify_installation_target(&target, outcome.lock(), all_packages, &package);

+    // TODO(lucab): improve warning content
+    // <https://github.com/astral-sh/uv/issues/7428>
+    if let SyncTarget::Project(project) = &target {
+        let roots = sync_target.roots().collect::<FxHashSet<_>>();
+        for (name, member) in project.workspace().packages() {
+            if roots.contains(name)
+                && member.pyproject_toml().has_scripts()
+                && !member.pyproject_toml().is_package(true)
+            {
+                warn_user!(
+                    "Skipping installation of entry points (`project.scripts`) for package `{}` because this project is not packaged; to install entry points, set `tool.uv.package = true` or define a `build-system`",
+                    name
+                );
+            }
+        }
+    }
+
     let state = state.fork();

     // Perform the sync operation.
PATCH

echo "Patch applied. Rebuilding uv binary..."
cargo build -p uv --bin uv 2>&1 | tail -5
echo "Done."
