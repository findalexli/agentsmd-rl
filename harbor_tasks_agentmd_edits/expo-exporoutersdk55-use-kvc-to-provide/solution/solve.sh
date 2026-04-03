#!/usr/bin/env bash
set -euo pipefail

cd /workspace/expo

# Idempotent: skip if already applied
if grep -q 'RNScreensTabCompat' packages/expo-router/ios/LinkPreview/LinkPreviewNativeNavigation.swift 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Create the new RNScreensTabCompat.swift file
cat > packages/expo-router/ios/LinkPreview/RNScreensTabCompat.swift <<'SWIFT_EOF'
import UIKit

/// Instead of casting to concrete class names (which break on renames),
/// we detect tab views by checking `responds(to:)` for expected selectors
/// and read properties via KVC.
enum RNScreensTabCompat {
  private static let tabKeyName = "tabKey"
  private static let controllerName = "controller"
  private static let reactViewControllerName = "reactViewController"

  private static let tabKeySelector = NSSelectorFromString(tabKeyName)
  private static let controllerSelector = NSSelectorFromString(controllerName)
  private static let reactViewControllerSelector = NSSelectorFromString(reactViewControllerName)

  // MARK: - Type check

  /// A view is a tab screen if it has a `tabKey` property — specific to RNScreens tab views.
  static func isTabScreen(_ view: UIView) -> Bool {
    view.responds(to: tabKeySelector)
  }

  // MARK: - Property access via KVC

  static func tabKey(from view: UIView) -> String? {
    guard view.responds(to: tabKeySelector) else { return nil }
    return view.value(forKey: tabKeyName) as? String
  }

  /// Calls `reactViewController()` dynamically via `perform(_:)`, then returns `.tabBarController`.
  static func tabBarController(fromTabScreen view: UIView) -> UITabBarController? {
    guard isTabScreen(view),
      view.responds(to: reactViewControllerSelector)
    else { return nil }
    let vc = view.perform(reactViewControllerSelector)?.takeUnretainedValue() as? UIViewController
    return vc?.tabBarController
  }

  static func tabBarController(fromTabHost view: UIView) -> UITabBarController? {
    guard view.responds(to: controllerSelector) else { return nil }
    return view.value(forKey: controllerName) as? UITabBarController
  }
}
SWIFT_EOF

# Apply the diff to LinkPreviewNativeNavigation.swift
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/expo-router/ios/LinkPreview/LinkPreviewNativeNavigation.swift b/packages/expo-router/ios/LinkPreview/LinkPreviewNativeNavigation.swift
index d958ec1c6e33e3..268716b1c93c48 100644
--- a/packages/expo-router/ios/LinkPreview/LinkPreviewNativeNavigation.swift
+++ b/packages/expo-router/ios/LinkPreview/LinkPreviewNativeNavigation.swift
@@ -48,12 +48,12 @@ internal class LinkPreviewNativeNavigation {
     guard let stackOrTabView else {
       return
     }
-    if let tabView = stackOrTabView as? RNSBottomTabsScreenComponentView {
+    if RNScreensTabCompat.isTabScreen(stackOrTabView) {
       let newTabKeys = tabPath?.path.map { $0.newTabKey } ?? []
       // The order is important here. findStackViewWithScreenIdInSubViews must be called
       // even if screenId is nil to compute the tabChangeCommands.
       if let stackView = findStackViewWithScreenIdInSubViews(
-        screenId: screenId, tabKeys: newTabKeys, rootView: tabView), let screenId {
+        screenId: screenId, tabKeys: newTabKeys, rootView: stackOrTabView), let screenId {
         setPreloadedView(stackView: stackView, screenId: screenId)
       }
     } else if let stackView = stackOrTabView as? RNSScreenStackView, let screenId {
@@ -150,8 +150,7 @@ internal class LinkPreviewNativeNavigation {
     if let result =
       enumeratedViews
       .first(where: { _, view in
-        guard let tabView = view as? RNSBottomTabsScreenComponentView, let tabKey = tabView.tabKey
-        else {
+        guard let tabKey = RNScreensTabCompat.tabKey(from: view) else {
           return false
         }
         return tabKeys.contains(tabKey)
@@ -162,13 +161,10 @@ internal class LinkPreviewNativeNavigation {
   }

   private func getTabBarControllerFromTabView(view: UIView) -> UITabBarController? {
-    if let tabScreenView = view as? RNSBottomTabsScreenComponentView {
-      return tabScreenView.reactViewController()?.tabBarController as? UITabBarController
+    if let tabBarController = RNScreensTabCompat.tabBarController(fromTabScreen: view) {
+      return tabBarController
     }
-    if let tabHostView = view as? RNSBottomTabsHostComponentView {
-      return tabHostView.controller as? UITabBarController
-    }
-    return nil
+    return RNScreensTabCompat.tabBarController(fromTabHost: view)
   }

   private func findStackViewWithScreenIdOrTabBarController(
@@ -182,10 +178,10 @@ internal class LinkPreviewNativeNavigation {
         if view.screenIds.contains(screenId) {
           return view
         }
-      } else if let tabView = nextResponder as? RNSBottomTabsScreenComponentView {
-        if let tabKey = tabView.tabKey, tabKeys.contains(tabKey) {
-          return tabView
-        }
+      } else if let nextView = nextResponder as? UIView,
+        let tabKey = RNScreensTabCompat.tabKey(from: nextView),
+        tabKeys.contains(tabKey) {
+          return nextView
       }
       currentResponder = nextResponder
     }

PATCH

# Apply podspec changes
git apply --whitespace=fix - <<'PATCH2'
diff --git a/packages/expo-router/ios/ExpoRouter.podspec b/packages/expo-router/ios/ExpoRouter.podspec
index 06f4c44f0a1425..de4d8b9090463b 100644
--- a/packages/expo-router/ios/ExpoRouter.podspec
+++ b/packages/expo-router/ios/ExpoRouter.podspec
@@ -36,10 +36,16 @@ Pod::Spec.new do |s|
     'OTHER_SWIFT_FLAGS' => "$(inherited) #{compiler_flags}",
   }

+  s.exclude_files = 'Tests/**/*'
+
   if !$ExpoUseSources&.include?(package['name']) && ENV['EXPO_USE_SOURCE'].to_i == 0 && File.exist?("#{s.name}.xcframework") && Gem::Version.new(Pod::VERSION) >= Gem::Version.new('1.10.0')
     s.source_files = "**/*.h"
     s.vendored_frameworks = "#{s.name}.xcframework"
   else
     s.source_files = "**/*.{h,m,swift,mm,cpp}"
   end
+
+  s.test_spec 'Tests' do |test_spec|
+    test_spec.source_files = 'Tests/**/*.{m,swift}'
+  end
 end

PATCH2

# Create test directory and test file
mkdir -p packages/expo-router/ios/Tests
cat > packages/expo-router/ios/Tests/RNScreensTabCompatTests.swift <<'TEST_EOF'
import Testing
import UIKit

@testable import ExpoRouter

// MARK: - Mock views

/// Mock tab screen: has @objc tabKey property, mimicking RNScreens tab screen views.
private class MockTabScreenView: UIView {
  @objc var tabKey: String?
}

/// Mock tab host: has @objc controller property, mimicking RNScreens tab host views.
private class MockTabHostView: UIView {
  @objc var controller: UIViewController?
}

/// Mock tab host with a non-UIViewController controller property.
private class MockTabHostWithBadController: UIView {
  @objc var controller: NSObject? = NSObject()
}

/// Mock view with a reactViewController() method that returns a UIViewController.
private class MockTabScreenWithReactVC: UIView {
  @objc var tabKey: String?
  private var _reactViewController: UIViewController?

  func configure(reactViewController: UIViewController) {
    _reactViewController = reactViewController
  }

  @objc override func reactViewController() -> UIViewController? {
    return _reactViewController
  }
}

// MARK: - Unit tests

@Suite("RNScreensTabCompat unit tests")
struct RNScreensTabCompatUnitTests {

  @Suite("isTabScreen")
  struct IsTabScreen {
    @Test
    func `detects mock tab screen`() {
      let tabScreen = MockTabScreenView()
      #expect(RNScreensTabCompat.isTabScreen(tabScreen))
    }

    @Test
    func `rejects plain UIView`() {
      let plainView = UIView()
      #expect(!RNScreensTabCompat.isTabScreen(plainView))
    }

    @Test
    func `rejects mock tab host`() {
      let tabHost = MockTabHostView()
      #expect(!RNScreensTabCompat.isTabScreen(tabHost))
    }
  }

  @Suite("tabKey")
  struct TabKey {
    @Test
    func `reads value`() {
      let tabScreen = MockTabScreenView()
      tabScreen.tabKey = "home"
      #expect(RNScreensTabCompat.tabKey(from: tabScreen) == "home")
    }

    @Test
    func `returns nil for nil tab key`() {
      let tabScreen = MockTabScreenView()
      tabScreen.tabKey = nil
      #expect(RNScreensTabCompat.tabKey(from: tabScreen) == nil)
    }

    @Test
    func `returns nil for plain UIView`() {
      let plainView = UIView()
      #expect(RNScreensTabCompat.tabKey(from: plainView) == nil)
    }
  }

  @Suite("tabBarController(fromTabHost:)")
  struct TabBarControllerFromTabHost {
    @Test
    func `returns tab bar controller`() {
      let tabHost = MockTabHostView()
      let tabBarController = UITabBarController()
      tabHost.controller = tabBarController
      #expect(RNScreensTabCompat.tabBarController(fromTabHost: tabHost) === tabBarController)
    }

    @Test
    func `returns nil for non-tab bar controller`() {
      let tabHost = MockTabHostView()
      tabHost.controller = UIViewController()
      #expect(RNScreensTabCompat.tabBarController(fromTabHost: tabHost) == nil)
    }

    @Test
    func `returns nil for nil controller`() {
      let tabHost = MockTabHostView()
      tabHost.controller = nil
      #expect(RNScreensTabCompat.tabBarController(fromTabHost: tabHost) == nil)
    }

    @Test
    func `returns nil for non-UIViewController type`() {
      let tabHost = MockTabHostWithBadController()
      #expect(RNScreensTabCompat.tabBarController(fromTabHost: tabHost) == nil)
    }

    @Test
    func `returns nil for plain UIView`() {
      let plainView = UIView()
      #expect(RNScreensTabCompat.tabBarController(fromTabHost: plainView) == nil)
    }
  }

  @Suite("tabBarController(fromTabScreen:)")
  struct TabBarControllerFromTabScreen {
    @Test
    func `returns tab bar controller via reactViewController`() {
      let tabBarController = UITabBarController()
      let childVC = UIViewController()
      tabBarController.viewControllers = [childVC]

      let mockView = MockTabScreenWithReactVC()
      mockView.tabKey = "tab1"
      mockView.configure(reactViewController: childVC)
      childVC.view.addSubview(mockView)

      let result = RNScreensTabCompat.tabBarController(fromTabScreen: mockView)
      #expect(result === tabBarController)
    }

    @Test
    func `returns nil when reactViewController returns nil`() {
      let mockView = MockTabScreenWithReactVC()
      mockView.tabKey = "tab1"
      // Don't configure — reactViewController() returns nil
      #expect(RNScreensTabCompat.tabBarController(fromTabScreen: mockView) == nil)
    }

    @Test
    func `returns nil when no reactViewController method`() {
      // MockTabScreenView has tabKey but no reactViewController() method
      let mockView = MockTabScreenView()
      mockView.tabKey = "tab1"
      #expect(RNScreensTabCompat.tabBarController(fromTabScreen: mockView) == nil)
    }

    @Test
    func `returns nil for plain UIView`() {
      let plainView = UIView()
      #expect(RNScreensTabCompat.tabBarController(fromTabScreen: plainView) == nil)
    }

    @Test
    func `returns nil when not in tab bar controller`() {
      let navController = UINavigationController()
      let childVC = UIViewController()
      navController.viewControllers = [childVC]

      let mockView = MockTabScreenWithReactVC()
      mockView.tabKey = "tab1"
      mockView.configure(reactViewController: childVC)
      childVC.view.addSubview(mockView)

      #expect(RNScreensTabCompat.tabBarController(fromTabScreen: mockView) == nil)
    }
  }
}

// MARK: - Integration tests (RNScreens API contract)

@Suite("RNScreens API contract")
struct RNScreensAPIContractTests {

  @Test
  func `tab screen class responds to tabKey`() throws {
    let cls = NSClassFromString("RNSTabsScreenComponentView")
      ?? NSClassFromString("RNSBottomTabsScreenComponentView")
    guard let cls else {
      Issue.record("No tab screen class found — neither RNSTabsScreenComponentView nor RNSBottomTabsScreenComponentView")
      return
    }
    let view = try #require((cls as? UIView.Type)?.init(), "Failed to instantiate tab screen class")
    #expect(view.responds(to: NSSelectorFromString("tabKey")))
  }

  @Test
  func `tab host class responds to controller`() throws {
    let cls = NSClassFromString("RNSTabsHostComponentView")
      ?? NSClassFromString("RNSBottomTabsHostComponentView")
    guard let cls else {
      Issue.record("No tab host class found — neither RNSTabsHostComponentView nor RNSBottomTabsHostComponentView")
      return
    }
    let view = try #require((cls as? UIView.Type)?.init(), "Failed to instantiate tab host class")
    #expect(view.responds(to: NSSelectorFromString("controller")))
  }

  @Test
  func `tab screen class responds to reactViewController`() throws {
    let cls = NSClassFromString("RNSTabsScreenComponentView")
      ?? NSClassFromString("RNSBottomTabsScreenComponentView")
    guard let cls else {
      Issue.record("No tab screen class found")
      return
    }
    let view = try #require((cls as? UIView.Type)?.init(), "Failed to instantiate tab screen class")
    #expect(view.responds(to: NSSelectorFromString("reactViewController")))
  }
}
TEST_EOF

# Update CLAUDE.md to add Swift testing section
git apply --whitespace=fix - <<'PATCH3'
diff --git a/packages/expo-router/CLAUDE.md b/packages/expo-router/CLAUDE.md
index 2f03efb529a0b0..622b5fa87af1ee 100644
--- a/packages/expo-router/CLAUDE.md
+++ b/packages/expo-router/CLAUDE.md
@@ -128,6 +128,25 @@ To verify if the types used in tests are correct, run:
 yarn test:types
 ```

+### Swift Tests (iOS)
+
+Native Swift tests live in `ios/Tests/` and use Apple's Swift Testing framework (`import Testing`).
+
+Run from the `packages/expo-router` directory:
+
+```bash
+et native-unit-tests --packages expo-router -p ios
+```
+
+> Pods must be installed in `apps/native-tests/ios` first (`pod install`).
+
+**Conventions:**
+
+- Use `@Test` / `@Suite` from Swift Testing (not XCTest)
+- Backtick-quoted test names for readability (e.g., `` @Test func `converts options correctly`() ``)
+- Inner structs for grouping related tests within a `@Suite`
+- `#expect` / `#require` for assertions
+
 ### Testing Patterns

 Tests use the custom `renderRouter` testing utility:

PATCH3

echo "Patch applied successfully."
