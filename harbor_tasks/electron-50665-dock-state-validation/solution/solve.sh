#!/bin/bash
set -euo pipefail

cd /workspace/electron

# Check if already applied
if grep -q "IsValidDockState" shell/browser/ui/inspectable_web_contents.cc; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/shell/browser/ui/inspectable_web_contents.cc b/shell/browser/ui/inspectable_web_contents.cc
index c0f6e4dfc19c1..24c2e6015e606 100644
--- a/shell/browser/ui/inspectable_web_contents.cc
+++ b/shell/browser/ui/inspectable_web_contents.cc
@@ -12,6 +12,7 @@
 #include <utility>

 #include "base/base64.h"
+#include "base/containers/fixed_flat_set.h"
 #include "base/containers/span.h"
 #include "base/dcheck_is_on.h"
 #include "base/memory/raw_ptr.h"
@@ -160,6 +161,13 @@ void OnOpenItemComplete(const base::FilePath& path, const std::string& result) {
 constexpr base::TimeDelta kInitialBackoffDelay = base::Milliseconds(250);
 constexpr base::TimeDelta kMaxBackoffDelay = base::Seconds(10);

+constexpr auto kValidDockStates = base::MakeFixedFlatSet<std::string_view>(
+    {"bottom", "left", "right", "undocked"});
+
+bool IsValidDockState(const std::string& state) {
+  return kValidDockStates.contains(state);
+}
+
 }  // namespace

 class InspectableWebContents::NetworkResourceLoader
@@ -394,7 +402,7 @@ void InspectableWebContents::SetDockState(const std::string& state) {
     can_dock_ = false;
   } else {
     can_dock_ = true;
-    dock_state_ = state;
+    dock_state_ = IsValidDockState(state) ? state : "right";
   }
 }

@@ -559,7 +567,13 @@ void InspectableWebContents::LoadCompleted() {
           pref_service_->GetDict(kDevToolsPreferences);
       const std::string* current_dock_state =
           prefs.FindString("currentDockState");
-      base::RemoveChars(*current_dock_state, "\"", &dock_state_);
+      if (current_dock_state) {
+        std::string sanitized;
+        base::RemoveChars(*current_dock_state, "\"", &sanitized);
+        dock_state_ = IsValidDockState(sanitized) ? sanitized : "right";
+      } else {
+        dock_state_ = "right";
+      }
     }
 #if BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX)
     auto* api_web_contents = api::WebContents::From(GetWebContents());
PATCH

echo "Patch applied successfully"
