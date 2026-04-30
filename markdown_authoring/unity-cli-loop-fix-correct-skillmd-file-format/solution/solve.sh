#!/usr/bin/env bash
set -euo pipefail

cd /workspace/unity-cli-loop

# Idempotency guard
if grep -qF "description: \"Get Unity project information via uloop CLI. Use when you need to:" "Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-project-info/SKILL.md" && grep -qF "description: \"Get Unity and project information via uloop CLI. Use when you need" "Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-version/SKILL.md" && grep -qF "description: \"Take a screenshot of Unity Editor windows and save as PNG image. U" "Packages/src/Editor/Api/McpTools/CaptureWindow/SKILL.md" && grep -qF "description: \"Clear Unity console logs via uloop CLI. Use when you need to: (1) " "Packages/src/Editor/Api/McpTools/ClearConsole/SKILL.md" && grep -qF "description: \"Compile Unity project via uloop CLI. Use when you need to: (1) Ver" "Packages/src/Editor/Api/McpTools/Compile/SKILL.md" && grep -qF "description: \"Control Unity Editor play mode via uloop CLI. Use when you need to" "Packages/src/Editor/Api/McpTools/ControlPlayMode/SKILL.md" && grep -qF "description: \"Execute C# code dynamically in Unity Editor via uloop CLI. Use for" "Packages/src/Editor/Api/McpTools/ExecuteDynamicCode/SKILL.md" && grep -qF "description: \"Execute Unity MenuItem via uloop CLI. Use when you need to: (1) Tr" "Packages/src/Editor/Api/McpTools/ExecuteMenuItem/SKILL.md" && grep -qF "description: \"Find GameObjects with search criteria via uloop CLI. Use when you " "Packages/src/Editor/Api/McpTools/FindGameObjects/SKILL.md" && grep -qF "description: \"Bring Unity Editor window to front via uloop CLI. Use when you nee" "Packages/src/Editor/Api/McpTools/FocusUnityWindow/SKILL.md" && grep -qF "description: \"Get Unity Hierarchy structure via uloop CLI. Use when you need to:" "Packages/src/Editor/Api/McpTools/GetHierarchy/SKILL.md" && grep -qF "description: \"Get Unity Console output including errors, warnings, and Debug.Log" "Packages/src/Editor/Api/McpTools/GetLogs/SKILL.md" && grep -qF "description: \"Retrieve Unity MenuItems via uloop CLI. Use when you need to: (1) " "Packages/src/Editor/Api/McpTools/GetMenuItems/SKILL.md" && grep -qF "description: \"Execute Unity Test Runner via uloop CLI. Use when you need to: (1)" "Packages/src/Editor/Api/McpTools/RunTests/SKILL.md" && grep -qF "description: \"Search Unity project via uloop CLI. Use when you need to: (1) Find" "Packages/src/Editor/Api/McpTools/UnitySearch/SKILL.md" && grep -qF "description: \"Get Unity Search provider details via uloop CLI. Use when you need" "Packages/src/Editor/Api/McpTools/UnitySearchProviderDetails/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-project-info/SKILL.md b/Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-project-info/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-project-info
-description: Get Unity project information via uloop CLI. Use when you need to: (1) Check Unity Editor version, (2) Get project settings and platform info, (3) Retrieve project metadata for diagnostics.
+description: "Get Unity project information via uloop CLI. Use when you need to: (1) Check Unity Editor version, (2) Get project settings and platform info, (3) Retrieve project metadata for diagnostics."
 internal: true
 ---
 
diff --git a/Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-version/SKILL.md b/Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-version/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-version
-description: Get Unity and project information via uloop CLI. Use when you need to verify Unity version, check project settings (ProductName, CompanyName, Version), or troubleshoot environment issues.
+description: "Get Unity and project information via uloop CLI. Use when you need to verify Unity version, check project settings (ProductName, CompanyName, Version), or troubleshoot environment issues."
 internal: true
 ---
 
diff --git a/Packages/src/Editor/Api/McpTools/CaptureWindow/SKILL.md b/Packages/src/Editor/Api/McpTools/CaptureWindow/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-screenshot
-description: Take a screenshot of Unity Editor windows and save as PNG image. Use when you need to: (1) Screenshot the Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual state for debugging or documentation, (3) Save what the Editor looks like as an image file.
+description: "Take a screenshot of Unity Editor windows and save as PNG image. Use when you need to: (1) Screenshot the Game View, Scene View, Console, Inspector, or other windows, (2) Capture current visual state for debugging or documentation, (3) Save what the Editor looks like as an image file."
 ---
 
 # uloop capture-window
diff --git a/Packages/src/Editor/Api/McpTools/ClearConsole/SKILL.md b/Packages/src/Editor/Api/McpTools/ClearConsole/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-clear-console
-description: Clear Unity console logs via uloop CLI. Use when you need to: (1) Clear the console before running tests, (2) Start a fresh debugging session, (3) Clean up log output for better readability.
+description: "Clear Unity console logs via uloop CLI. Use when you need to: (1) Clear the console before running tests, (2) Start a fresh debugging session, (3) Clean up log output for better readability."
 ---
 
 # uloop clear-console
diff --git a/Packages/src/Editor/Api/McpTools/Compile/SKILL.md b/Packages/src/Editor/Api/McpTools/Compile/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-compile
-description: Compile Unity project via uloop CLI. Use when you need to: (1) Verify C# code compiles successfully after editing scripts, (2) Check for compile errors or warnings, (3) Validate script changes before running tests.
+description: "Compile Unity project via uloop CLI. Use when you need to: (1) Verify C# code compiles successfully after editing scripts, (2) Check for compile errors or warnings, (3) Validate script changes before running tests."
 ---
 
 # uloop compile
diff --git a/Packages/src/Editor/Api/McpTools/ControlPlayMode/SKILL.md b/Packages/src/Editor/Api/McpTools/ControlPlayMode/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-control-play-mode
-description: Control Unity Editor play mode via uloop CLI. Use when you need to: (1) Start play mode for testing, (2) Stop play mode after testing, (3) Pause play mode for debugging.
+description: "Control Unity Editor play mode via uloop CLI. Use when you need to: (1) Start play mode for testing, (2) Stop play mode after testing, (3) Pause play mode for debugging."
 ---
 
 # uloop control-play-mode
diff --git a/Packages/src/Editor/Api/McpTools/ExecuteDynamicCode/SKILL.md b/Packages/src/Editor/Api/McpTools/ExecuteDynamicCode/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-execute-dynamic-code
-description: Execute C# code dynamically in Unity Editor via uloop CLI. Use for editor automation: (1) Prefab/material wiring and AddComponent operations, (2) Reference wiring with SerializedObject, (3) Scene/hierarchy edits and batch operations. NOT for file I/O or script authoring.
+description: "Execute C# code dynamically in Unity Editor via uloop CLI. Use for editor automation: (1) Prefab/material wiring and AddComponent operations, (2) Reference wiring with SerializedObject, (3) Scene/hierarchy edits and batch operations. NOT for file I/O or script authoring."
 ---
 
 # uloop execute-dynamic-code
diff --git a/Packages/src/Editor/Api/McpTools/ExecuteMenuItem/SKILL.md b/Packages/src/Editor/Api/McpTools/ExecuteMenuItem/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-execute-menu-item
-description: Execute Unity MenuItem via uloop CLI. Use when you need to: (1) Trigger menu commands programmatically, (2) Automate editor actions (save, build, refresh), (3) Run custom menu items defined in scripts.
+description: "Execute Unity MenuItem via uloop CLI. Use when you need to: (1) Trigger menu commands programmatically, (2) Automate editor actions (save, build, refresh), (3) Run custom menu items defined in scripts."
 ---
 
 # uloop execute-menu-item
diff --git a/Packages/src/Editor/Api/McpTools/FindGameObjects/SKILL.md b/Packages/src/Editor/Api/McpTools/FindGameObjects/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-find-game-objects
-description: Find GameObjects with search criteria via uloop CLI. Use when you need to: (1) Locate GameObjects by name pattern, (2) Find objects by tag or layer, (3) Search for objects with specific component types.
+description: "Find GameObjects with search criteria via uloop CLI. Use when you need to: (1) Locate GameObjects by name pattern, (2) Find objects by tag or layer, (3) Search for objects with specific component types."
 ---
 
 # uloop find-game-objects
diff --git a/Packages/src/Editor/Api/McpTools/FocusUnityWindow/SKILL.md b/Packages/src/Editor/Api/McpTools/FocusUnityWindow/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-focus-window
-description: Bring Unity Editor window to front via uloop CLI. Use when you need to: (1) Focus Unity Editor before capturing screenshots, (2) Ensure Unity window is visible for visual checks, (3) Bring Unity to foreground for user interaction.
+description: "Bring Unity Editor window to front via uloop CLI. Use when you need to: (1) Focus Unity Editor before capturing screenshots, (2) Ensure Unity window is visible for visual checks, (3) Bring Unity to foreground for user interaction."
 ---
 
 # uloop focus-window
diff --git a/Packages/src/Editor/Api/McpTools/GetHierarchy/SKILL.md b/Packages/src/Editor/Api/McpTools/GetHierarchy/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-hierarchy
-description: Get Unity Hierarchy structure via uloop CLI. Use when you need to: (1) Inspect scene structure and GameObject tree, (2) Find GameObjects and their parent-child relationships, (3) Check component attachments on objects.
+description: "Get Unity Hierarchy structure via uloop CLI. Use when you need to: (1) Inspect scene structure and GameObject tree, (2) Find GameObjects and their parent-child relationships, (3) Check component attachments on objects."
 ---
 
 # uloop get-hierarchy
diff --git a/Packages/src/Editor/Api/McpTools/GetLogs/SKILL.md b/Packages/src/Editor/Api/McpTools/GetLogs/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-logs
-description: Get Unity Console output including errors, warnings, and Debug.Log messages. Use when you need to: (1) Check for compile errors or runtime exceptions after code changes, (2) See what Debug.Log printed during execution, (3) Find NullReferenceException, MissingComponentException, or other error messages, (4) Investigate why something failed in Unity Editor.
+description: "Get Unity Console output including errors, warnings, and Debug.Log messages. Use when you need to: (1) Check for compile errors or runtime exceptions after code changes, (2) See what Debug.Log printed during execution, (3) Find NullReferenceException, MissingComponentException, or other error messages, (4) Investigate why something failed in Unity Editor."
 ---
 
 # uloop get-logs
diff --git a/Packages/src/Editor/Api/McpTools/GetMenuItems/SKILL.md b/Packages/src/Editor/Api/McpTools/GetMenuItems/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-menu-items
-description: Retrieve Unity MenuItems via uloop CLI. Use when you need to: (1) Discover available menu commands in Unity Editor, (2) Find menu paths for automation, (3) Prepare for executing menu items programmatically.
+description: "Retrieve Unity MenuItems via uloop CLI. Use when you need to: (1) Discover available menu commands in Unity Editor, (2) Find menu paths for automation, (3) Prepare for executing menu items programmatically."
 ---
 
 # uloop get-menu-items
diff --git a/Packages/src/Editor/Api/McpTools/RunTests/SKILL.md b/Packages/src/Editor/Api/McpTools/RunTests/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-run-tests
-description: Execute Unity Test Runner via uloop CLI. Use when you need to: (1) Run unit tests (EditMode tests), (2) Run integration tests (PlayMode tests), (3) Verify code changes don't break existing functionality.
+description: "Execute Unity Test Runner via uloop CLI. Use when you need to: (1) Run unit tests (EditMode tests), (2) Run integration tests (PlayMode tests), (3) Verify code changes don't break existing functionality."
 ---
 
 # uloop run-tests
diff --git a/Packages/src/Editor/Api/McpTools/UnitySearch/SKILL.md b/Packages/src/Editor/Api/McpTools/UnitySearch/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-unity-search
-description: Search Unity project via uloop CLI. Use when you need to: (1) Find assets by name or type (scenes, prefabs, scripts, materials), (2) Search for project resources using Unity's search system, (3) Locate files within the Unity project.
+description: "Search Unity project via uloop CLI. Use when you need to: (1) Find assets by name or type (scenes, prefabs, scripts, materials), (2) Search for project resources using Unity's search system, (3) Locate files within the Unity project."
 ---
 
 # uloop unity-search
diff --git a/Packages/src/Editor/Api/McpTools/UnitySearchProviderDetails/SKILL.md b/Packages/src/Editor/Api/McpTools/UnitySearchProviderDetails/SKILL.md
@@ -1,6 +1,6 @@
 ---
 name: uloop-get-provider-details
-description: Get Unity Search provider details via uloop CLI. Use when you need to: (1) Discover available search providers, (2) Understand search capabilities and filters, (3) Configure searches with specific provider options.
+description: "Get Unity Search provider details via uloop CLI. Use when you need to: (1) Discover available search providers, (2) Understand search capabilities and filters, (3) Configure searches with specific provider options."
 ---
 
 # uloop get-provider-details
PATCH

echo "Gold patch applied."
