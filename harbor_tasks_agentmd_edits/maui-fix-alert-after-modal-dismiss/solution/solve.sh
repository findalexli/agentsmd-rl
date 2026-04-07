#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'IsBeingDismissed' src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
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
diff --git a/eng/pipelines/common/ui-tests-steps.yml b/eng/pipelines/common/ui-tests-steps.yml
index e3c1188e329c..b5b2a8f79a8a 100644
--- a/eng/pipelines/common/ui-tests-steps.yml
+++ b/eng/pipelines/common/ui-tests-steps.yml
@@ -186,6 +186,8 @@ steps:
 - task: PublishBuildArtifacts@1
   condition: always()
   displayName: publish artifacts
+  inputs:
+    artifactName: drop-$(System.StageName)-$(System.JobName)-$(System.JobAttempt)

 # Enable Notification Center re-enabled only for catalyst
 - ${{ if eq(parameters.platform, 'catalyst')}}:
diff --git a/src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs b/src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs
index 3dda756c751a..a1ca70b403e6 100644
--- a/src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs
+++ b/src/Controls/src/Core/Platform/AlertManager/AlertManager.iOS.cs
@@ -201,7 +201,8 @@ alert.PopoverPresentationController is not null &&
 			static UIViewController GetTopUIViewController(UIWindow platformWindow)
 			{
 				var topUIViewController = platformWindow.RootViewController;
-				while (topUIViewController?.PresentedViewController is not null)
+				while (topUIViewController?.PresentedViewController is not null &&
+					   !topUIViewController.PresentedViewController.IsBeingDismissed)
 				{
 					topUIViewController = topUIViewController.PresentedViewController;
 				}
diff --git a/src/Controls/tests/TestCases.HostApp/Issues/Issue32807.xaml b/src/Controls/tests/TestCases.HostApp/Issues/Issue32807.xaml
new file mode 100644
index 000000000000..d30163558914
--- /dev/null
+++ b/src/Controls/tests/TestCases.HostApp/Issues/Issue32807.xaml
@@ -0,0 +1,22 @@
+<?xml version="1.0" encoding="utf-8" ?>
+<ContentPage xmlns="http://schemas.microsoft.com/dotnet/2021/maui"
+             xmlns:x="http://schemas.microsoft.com/winfx/2009/xaml"
+             x:Class="Maui.Controls.Sample.Issues.Issue32807"
+             Title="Issue 32807">
+    <VerticalStackLayout Padding="20" Spacing="10">
+        <Label Text="Test alert after dismissing modal page" FontSize="18" FontAttributes="Bold"/>
+        <Label Text="1. Tap 'Open Modal Page' button"/>
+        <Label Text="2. Tap 'Dismiss' on the modal page"/>
+        <Label Text="3. Verify that all three alerts appear immediately"/>
+
+        <Button x:Name="OpenModalButton"
+                Text="Open Modal Page"
+                AutomationId="OpenModalButton"
+                Clicked="OnOpenModalClicked"/>
+
+        <Label x:Name="StatusLabel"
+               Text="Ready"
+               AutomationId="StatusLabel"
+               FontAttributes="Italic"/>
+    </VerticalStackLayout>
+</ContentPage>
diff --git a/src/Controls/tests/TestCases.HostApp/Issues/Issue32807.xaml.cs b/src/Controls/tests/TestCases.HostApp/Issues/Issue32807.xaml.cs
new file mode 100644
index 000000000000..c39b544e51e6
--- /dev/null
+++ b/src/Controls/tests/TestCases.HostApp/Issues/Issue32807.xaml.cs
@@ -0,0 +1,71 @@
+using System;
+using System.Threading.Tasks;
+using Microsoft.Maui.Controls;
+
+namespace Maui.Controls.Sample.Issues
+{
+	[Issue(IssueTracker.Github, 32807, "Alert popup not displaying when dismissing modal page on iOS/MacOS", PlatformAffected.iOS | PlatformAffected.macOS)]
+	public partial class Issue32807 : ContentPage
+	{
+		public Issue32807()
+		{
+			InitializeComponent();
+		}
+
+		async void OnOpenModalClicked(object sender, EventArgs e)
+		{
+			// Present a modal page
+			var modalPage = new ModalTestPage();
+			await Navigation.PushModalAsync(modalPage);
+
+			// Wait for the modal to be dismissed
+			await modalPage.DismissedTask;
+
+			// Try to show alerts immediately after dismissal
+			// Without the fix, these alerts won't appear because GetTopUIViewController
+			// returns the dismissing modal view controller instead of the main view controller
+			StatusLabel.Text = "Modal dismissed, showing alerts...";
+
+			await DisplayAlert("Alert 1", "First alert after modal dismissal", "OK");
+			StatusLabel.Text = "Alert 1 shown";
+
+			await DisplayAlert("Alert 2", "Second alert after modal dismissal", "OK");
+			StatusLabel.Text = "Alert 2 shown";
+
+			await DisplayAlert("Alert 3", "Third alert after modal dismissal", "OK");
+			StatusLabel.Text = "All alerts shown successfully!";
+		}
+	}
+
+	public class ModalTestPage : ContentPage
+	{
+		private TaskCompletionSource<bool> _dismissedTcs = new TaskCompletionSource<bool>();
+
+		public Task DismissedTask => _dismissedTcs.Task;
+
+		public ModalTestPage()
+		{
+			Title = "Modal Page";
+
+			Content = new VerticalStackLayout
+			{
+				Padding = 20,
+				Spacing = 10,
+				Children =
+				{
+					new Label { Text = "This is a modal page", FontSize = 18 },
+					new Button
+					{
+						Text = "Dismiss",
+						AutomationId = "DismissButton",
+						Command = new Command(async () =>
+						{
+							await Navigation.PopModalAsync();
+							_dismissedTcs.TrySetResult(true);
+						})
+					}
+				}
+			};
+		}
+	}
+}
diff --git a/src/Controls/tests/TestCases.Shared.Tests/Tests/Issues/Issue32807.cs b/src/Controls/tests/TestCases.Shared.Tests/Tests/Issues/Issue32807.cs
new file mode 100644
index 000000000000..17658cf30b83
--- /dev/null
+++ b/src/Controls/tests/TestCases.Shared.Tests/Tests/Issues/Issue32807.cs
@@ -0,0 +1,48 @@
+using NUnit.Framework;
+using UITest.Appium;
+using UITest.Core;
+
+namespace Microsoft.Maui.TestCases.Tests.Issues
+{
+	public class Issue32807 : _IssuesUITest
+	{
+		public override string Issue => "Alert popup not displaying when dismissing modal page on iOS/MacOS";
+
+		public Issue32807(TestDevice device) : base(device) { }
+
+		[Test]
+		[Category(UITestCategories.DisplayAlert)]
+		public void AlertsShouldDisplayImmediatelyAfterDismissingModal()
+		{
+			// Wait for the page to load
+			App.WaitForElement("OpenModalButton");
+
+			// Open the modal page
+			App.Tap("OpenModalButton");
+
+			// Wait for modal to appear and then dismiss it
+			App.WaitForElement("DismissButton");
+			App.Tap("DismissButton");
+
+			// After dismissing the modal, alerts should appear without delay
+			// If the bug exists, these alerts won't appear (or will be delayed significantly)
+
+			// Wait for Alert 1 to appear - this is the critical test
+			// The alert should appear within a reasonable time (not 750ms+)
+			App.WaitForElement("OK", timeout: System.TimeSpan.FromSeconds(2));
+			App.TapDisplayAlertButton("OK");
+
+			// Wait for Alert 2
+			App.WaitForElement("OK", timeout: System.TimeSpan.FromSeconds(2));
+			App.TapDisplayAlertButton("OK");
+
+			// Wait for Alert 3
+			App.WaitForElement("OK", timeout: System.TimeSpan.FromSeconds(2));
+			App.TapDisplayAlertButton("OK");
+
+			// Verify all alerts were shown successfully
+			var statusText = App.FindElement("StatusLabel").GetText();
+			Assert.That(statusText, Does.Contain("All alerts shown successfully"));
+		}
+	}
+}

PATCH

echo "Patch applied successfully."
