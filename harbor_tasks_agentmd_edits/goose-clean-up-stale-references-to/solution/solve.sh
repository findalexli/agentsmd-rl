#!/usr/bin/env bash
set -euo pipefail

cd /workspace/goose

# Idempotent: skip if already applied (check for one of the key changes)
if ! grep -q "tracing::warn!" crates/goose/src/config/extensions.rs 2>/dev/null; then
    echo "Patch not yet applied."
else
    echo "Patch already applied."
    exit 0
fi

# Apply the patch using git apply
git apply - <<'PATCH'
diff --git a/crates/goose/src/config/experiments.rs b/crates/goose/src/config/experiments.rs
index c60802e2bc04..4a2cdfab528a 100644
--- a/crates/goose/src/config/experiments.rs
+++ b/crates/goose/src/config/experiments.rs
@@ -5,7 +5,6 @@ use std::collections::HashMap;
 /// It is the ground truth for init experiments. The experiment names in users' experiment list but not
 /// in the list will be remove from user list; The experiment names in the ground-truth list but not
 /// in users' experiment list will be added to user list with default value false;
-/// TODO: keep this up to date with the experimental-features.md documentation page
 const ALL_EXPERIMENTS: &[(&str, bool)] = &[];

 /// Experiment configuration management
diff --git a/crates/goose/src/config/extensions.rs b/crates/goose/src/config/extensions.rs
index 2f51c412c85f..460a6e93ebf5 100644
--- a/crates/goose/src/config/extensions.rs
+++ b/crates/goose/src/config/extensions.rs
@@ -81,8 +81,7 @@ fn get_extensions_map() -> IndexMap<String, ExtensionEntry> {
 fn save_extensions_map(extensions: IndexMap<String, ExtensionEntry>) {
     let config = Config::global();
     if let Err(e) = config.set_param(EXTENSIONS_CONFIG_KEY, &extensions) {
-        // TODO(jack) why is this just a debug statement?
-        tracing::debug!("Failed to save extensions config: {}", e);
+        tracing::warn!("Failed to save extensions config: {}", e);
     }
 }

PATCH

# Remove dead code files
rm -f ui/desktop/src/components/InterruptionHandler.tsx
rm -f ui/desktop/src/hooks/useRecipeManager.ts
rm -f ui/desktop/src/components/WaveformVisualizer.tsx
rm -f ui/desktop/src/components/schedule/ScheduleFromRecipeModal.tsx
rm -f ui/desktop/src/utils/sessionCache.ts
rm -f ui/desktop/src/components/recipes/RecipeExpandableInfo.tsx
rm -f ui/desktop/src/components/recipes/RecipeInfoModal.tsx
rm -f ui/desktop/src/components/ui/CustomRadio.tsx

# Remove console.log statements from App.tsx (using sed)
sed -i "/console.log('Sending reactReady signal to Electron')/d" ui/desktop/src/App.tsx
sed -i "/console.log('Setting up keyboard shortcuts')/d" ui/desktop/src/App.tsx

echo "Patch applied successfully."
