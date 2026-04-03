#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'mergedData.Count > 0 || !isPopping' src/Controls/src/Core/Shell/ShellNavigationManager.cs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
index 934fe7623e1d..c2d342fc8af4 100644
--- a/.github/copilot-instructions.md
+++ b/.github/copilot-instructions.md
@@ -200,20 +200,6 @@ git commit -m "Fix: Description of the change"
 - `.github/instructions/android.instructions.md` - Android handler implementation
 - `.github/instructions/xaml-unittests.instructions.md` - XAML unit test guidelines

-### Opening PRs
-
-All PRs are required to have this at the top of the description:
-
-```
-<!-- Please let the below note in for people that find this PR -->
-> [!NOTE]
-> Are you waiting for the changes in this PR to be merged?
-> It would be very helpful if you could [test the resulting artifacts](https://github.com/dotnet/maui/wiki/Testing-PR-Builds) from this PR and let us know in a comment if this change resolves your issue. Thank you!
-```
-
-Always put that at the top, without the block quotes. Without it, users will NOT be able to try the PR and your work will have been in vain!
-
-

 ## Custom Agents and Skills

diff --git a/.github/skills/pr-finalize/SKILL.md b/.github/skills/pr-finalize/SKILL.md
index 28ba6916dd8b..9932ac6534c5 100644
--- a/.github/skills/pr-finalize/SKILL.md
+++ b/.github/skills/pr-finalize/SKILL.md
@@ -127,16 +127,10 @@ Examples:
 ## Description Requirements

 PR description should:
-1. Start with the required NOTE block (so users can test PR artifacts)
-2. Include the base sections from `.github/PULL_REQUEST_TEMPLATE.md` ("Description of Change" and "Issues Fixed"). The skill adds additional structured fields (Root cause, Fix, Key insight, etc.) as recommended enhancements for better agent context.
-3. Match the actual implementation
+1. Include the base sections from `.github/PULL_REQUEST_TEMPLATE.md` ("Description of Change" and "Issues Fixed"). The skill adds additional structured fields (Root cause, Fix, Key insight, etc.) as recommended enhancements for better agent context.
+2. Match the actual implementation

 ```markdown
-<!-- Please let the below note in for people that find this PR -->
-> [!NOTE]
-> Are you waiting for the changes in this PR to be merged?
-> It would be very helpful if you could [test the resulting artifacts](https://github.com/dotnet/maui/wiki/Testing-PR-Builds) from this PR and let us know in a comment if this change resolves your issue. Thank you!
-
 ### Description of Change
 [Must match actual implementation]

@@ -229,11 +223,6 @@ Example: "Before: Safe area applied by default (opt-out). After: Only views impl
 Use structured template only when existing description is inadequate:

 ```markdown
-<!-- Please let the below note in for people that find this PR -->
-> [!NOTE]
-> Are you waiting for the changes in this PR to be merged?
-> It would be very helpful if you could [test the resulting artifacts](https://github.com/dotnet/maui/wiki/Testing-PR-Builds) from this PR and let us know in a comment if this change resolves your issue. Thank you!
-
 ### Root Cause

 [Why the bug occurred - be specific about the code path]
diff --git a/.github/skills/pr-finalize/references/complete-example.md b/.github/skills/pr-finalize/references/complete-example.md
index 034da2e3d09d..6f8ff08d1006 100644
--- a/.github/skills/pr-finalize/references/complete-example.md
+++ b/.github/skills/pr-finalize/references/complete-example.md
@@ -9,10 +9,6 @@ This example shows a PR description optimized for future agent success.

 ## Description
 ```markdown
-> [!NOTE]
-> Are you waiting for the changes in this PR to be merged?
-> It would be very helpful if you could [test the resulting artifacts](https://github.com/dotnet/maui/wiki/Testing-PR-Builds) from this PR and let us know in a comment if this change resolves your issue. Thank you!
-
 ### Root Cause

 In `MauiView.GetAdjustedSafeAreaInsets()` on iOS, views that don't implement `ISafeAreaView` or `ISafeAreaView2` (such as `ContentPresenter`, `Border`) were falling through to return `baseSafeArea`. This applied full device safe area insets to views that never opted into safe area handling, causing double-padding when used inside ControlTemplates.
diff --git a/src/Controls/src/Core/Shell/ShellNavigationManager.cs b/src/Controls/src/Core/Shell/ShellNavigationManager.cs
index dbe205c51e56..efac0f54f2e6 100644
--- a/src/Controls/src/Core/Shell/ShellNavigationManager.cs
+++ b/src/Controls/src/Core/Shell/ShellNavigationManager.cs
@@ -313,14 +313,27 @@ public static void ApplyQueryAttributes(Element element, ShellRouteParameters qu
 				var mergedData = MergeData(element, filteredQuery, isPopping);

 				//if we are pop or navigating back, we need to apply the query attributes to the ShellContent
-				if (isPopping)
+				if (isPopping && mergedData.Count > 0 )
 				{
 					element.SetValue(ShellContent.QueryAttributesProperty, mergedData);
 				}
-				baseShellItem.ApplyQueryAttributes(mergedData);
+
+				// Skip applying query attributes if the merged data is empty and we're popping back
+				// This respects when user calls query.Clear() - they don't want attributes applied on back navigation
+				if (mergedData.Count > 0 || !isPopping)
+				{
+					baseShellItem.ApplyQueryAttributes(mergedData);
+				}
 			}
 			else if (isLastItem)
-				element.SetValue(ShellContent.QueryAttributesProperty, MergeData(element, query, isPopping));
+			{
+				var mergedData = MergeData(element, query, isPopping);
+				// Skip setting query attributes if the merged data is empty and we're popping back
+				if (mergedData.Count > 0 || !isPopping)
+				{
+					element.SetValue(ShellContent.QueryAttributesProperty, mergedData);
+				}
+			}

 			ShellRouteParameters MergeData(Element shellElement, ShellRouteParameters data, bool isPopping)
 			{

PATCH

echo "Patch applied successfully."
