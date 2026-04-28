#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aspire

# Idempotency guard
if grep -qF "Both test projects use hand-rolled fakes \u2014 no mocking framework is used. Cross-p" ".github/skills/dashboard-testing/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/dashboard-testing/SKILL.md b/.github/skills/dashboard-testing/SKILL.md
@@ -128,7 +128,8 @@ public abstract class DashboardTestContext : TestContext
 
 ```csharp
 using Aspire.Dashboard.Components.Tests.Shared;
-using Aspire.Dashboard.Tests.Shared;
+using Aspire.Tests.Shared.DashboardModel;
+using Aspire.Dashboard.Model;
 using Bunit;
 using Xunit;
 
@@ -151,7 +152,7 @@ public class ResourceDetailsTests : DashboardTestContext
         var cut = RenderComponent<ResourceDetails>(builder =>
         {
             builder.Add(p => p.Resource, resource);
-            builder.Add(p => p.ShowSpecificProperties, true);
+            builder.Add(p => p.ShowSpecOnlyToggle, true);
         });
 
         // Assert — query the rendered DOM
@@ -185,7 +186,7 @@ public partial class ResourcesTests : DashboardTestContext
         var viewport = new ViewportInformation(IsDesktop: true, IsUltraLowHeight: false, IsUltraLowWidth: false);
         var initialResources = new List<ResourceViewModel>
         {
-            ModelTestHelpers.CreateResource("Resource1", "Type1", "Running"),
+            ModelTestHelpers.CreateResource(resourceName: "Resource1", resourceType: "Type1", state: KnownResourceState.Running),
         };
         var channel = Channel.CreateUnbounded<IReadOnlyList<ResourceViewModelChange>>();
         var dashboardClient = new TestDashboardClient(
@@ -284,7 +285,7 @@ internal static class MyFeatureSetupHelpers
 
 ## Shared Test Fakes
 
-Both test projects share hand-rolled fakes from `tests/Shared/`. No mocking framework is used.
+Both test projects use hand-rolled fakes — no mocking framework is used. Cross-project fakes live in `tests/Shared/` (e.g., `TestDashboardClient`, `ModelTestHelpers`), while bUnit-specific fakes live in `tests/Aspire.Dashboard.Components.Tests/Shared/` (e.g., `TestLocalStorage`, `TestTimeProvider`).
 
 | Fake | Purpose |
 |------|---------|
@@ -326,9 +327,9 @@ var resource = ModelTestHelpers.CreateResource(
 
 ## Test Conventions
 
-### DO: Use `[UseCulture("en-US")]` on Component Tests
+### DO: Use `[UseCulture("en-US")]` for Culture-Sensitive Component Tests
 
-All bUnit test classes should be decorated with `[UseCulture("en-US")]` for deterministic formatting:
+Apply `[UseCulture("en-US")]` to bUnit test classes that assert culture-sensitive formatting (for example, numbers or dates) so those tests run deterministically across environments:
 
 ```csharp
 [UseCulture("en-US")]
PATCH

echo "Gold patch applied."
