#!/bin/bash
set -e

cd /workspace/electron

# Apply the gold patch for dock_state validation
cat << 'PATCH' | git apply -
diff --git a/shell/browser/ui/inspectable_web_contents.cc b/shell/browser/ui/inspectable_web_contents.cc
index 8b9b25e314957..a99b18c493372 100644
--- a/shell/browser/ui/inspectable_web_contents.cc
+++ b/shell/browser/ui/inspectable_web_contents.cc
@@ -12,6 +12,7 @@
 #include <utility>

 #include "base/base64.h"
+#include "base/containers/fixed_flat_set.h"
 #include "base/containers/span.h"
 #include "base/memory/raw_ptr.h"
 #include "base/metrics/histogram.h"
@@ -158,6 +159,13 @@ void OnOpenItemComplete(const base::FilePath& path, const std::string& result) {
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
@@ -392,7 +400,7 @@ void InspectableWebContents::SetDockState(const std::string& state) {
     can_dock_ = false;
   } else {
     can_dock_ = true;
-    dock_state_ = state;
+    dock_state_ = IsValidDockState(state) ? state : "right";
   }
 }

@@ -557,7 +565,13 @@ void InspectableWebContents::LoadCompleted() {
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

# Verify the patch was applied by checking for the distinctive line
grep -q "kValidDockStates.contains" shell/browser/ui/inspectable_web_contents.cc && echo "Patch applied successfully"
