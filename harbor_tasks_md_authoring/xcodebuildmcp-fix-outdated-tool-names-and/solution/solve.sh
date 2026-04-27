#!/usr/bin/env bash
set -euo pipefail

cd /workspace/xcodebuildmcp

# Idempotency guard
if grep -qF "xcodebuildmcp simulator build-and-run --scheme MyApp --project-path ./MyApp.xcod" "skills/xcodebuildmcp-cli/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/xcodebuildmcp-cli/SKILL.md b/skills/xcodebuildmcp-cli/SKILL.md
@@ -38,48 +38,48 @@ Notes:
 
 If app and project details are not known:
 ```bash
-xcodebuildmcp simulator discover-projs --workspace-root .
+xcodebuildmcp simulator discover-projects --workspace-root .
 xcodebuildmcp simulator list-schemes --project-path ./MyApp.xcodeproj
-xcodebuildmcp simulator list-sims
+xcodebuildmcp simulator list
 ```
 
 To build, install and launch the app in one command:
 ```bash
-xcodebuildmcp simulator build-run-sim --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"
+xcodebuildmcp simulator build-and-run --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"
 ```
 
 ### Build only
 
 When you only need to check that there are no build errors, you can build without running the app.
 
 ```bash
-xcodebuildmcp simulator build-sim --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"
+xcodebuildmcp simulator build --scheme MyApp --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"
 ```
 
 ### Run Tests
 
-When you need to run tests, you can do so with the `test-sim` tool.
+When you need to run tests, you can do so with the `test` tool.
 
 ```bash
-xcodebuildmcp simulator test-sim --scheme MyAppTests --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"
+xcodebuildmcp simulator test --scheme MyAppTests --project-path ./MyApp.xcodeproj --simulator-name "iPhone 17 Pro"
 ```
 
 ### Install And Launch On Physical Device
 
 ```bash
-xcodebuildmcp device list-devices
-xcodebuildmcp device build-device --scheme MyApp --project-path ./MyApp.xcodeproj
-xcodebuildmcp device get-device-app-path --scheme MyApp --project-path ./MyApp.xcodeproj
+xcodebuildmcp device list
+xcodebuildmcp device build --scheme MyApp --project-path ./MyApp.xcodeproj
+xcodebuildmcp device get-app-path --scheme MyApp --project-path ./MyApp.xcodeproj
 xcodebuildmcp device get-app-bundle-id --app-path /path/to/MyApp.app
-xcodebuildmcp device install-app-device --device-id DEVICE_UDID --app-path /path/to/MyApp.app
-xcodebuildmcp device launch-app-device --device-id DEVICE_UDID --bundle-id io.sentry.MyApp --app-path /path/to/MyApp.app
+xcodebuildmcp device install --device-id DEVICE_UDID --app-path /path/to/MyApp.app
+xcodebuildmcp device launch --device-id DEVICE_UDID --bundle-id io.sentry.MyApp
 ```
 
 ### Capture Logs On Simulator
 
 ```bash
-xcodebuildmcp logging start-sim-log-cap --simulator-id SIMULATOR_UDID --bundle-id io.sentry.MyApp
-xcodebuildmcp logging stop-sim-log-cap --log-session-id LOG_SESSION_ID
+xcodebuildmcp logging start-simulator-log-capture --simulator-id SIMULATOR_UDID --bundle-id io.sentry.MyApp
+xcodebuildmcp logging stop-simulator-log-capture --log-session-id LOG_SESSION_ID
 ```
 
 ### Debug A Running App (Simulator)
@@ -89,15 +89,15 @@ xcodebuildmcp logging stop-sim-log-cap --log-session-id LOG_SESSION_ID
 
 Launch if not already running:
 ```bash
-xcodebuildmcp simulator launch-app-sim --bundle-id io.sentry.MyApp --simulator-id SIMULATOR_UDID
+xcodebuildmcp simulator launch-app --bundle-id io.sentry.MyApp --simulator-id SIMULATOR_UDID
 ```
 
 Attach the debugger:
 
 It's generally a good idea to wait for 1-2s for the app to fully launch before attaching the debugger.
 
 ```bash
-xcodebuildmcp debugging debug-attach-sim --bundle-id io.sentry.MyApp --simulator-id SIMULATOR_UDID
+xcodebuildmcp debugging attach --bundle-id io.sentry.MyApp --simulator-id SIMULATOR_UDID
 ```
 
 To add/remove breakpoints, inspect stack/variables, and issue arbitrary LLDB commands, view debugging help:
@@ -125,8 +125,8 @@ xcodebuildmcp ui-automation --help
 ### macOS App Build/Run
 
 ```bash
-xcodebuildmcp macos build-macos --scheme MyMacApp --project-path ./MyMacApp.xcodeproj
-xcodebuildmcp macos build-run-macos --scheme MyMacApp --project-path ./MyMacApp.xcodeproj
+xcodebuildmcp macos build --scheme MyMacApp --project-path ./MyMacApp.xcodeproj
+xcodebuildmcp macos build-and-run --scheme MyMacApp --project-path ./MyMacApp.xcodeproj
 ```
 
 To see all macOS tools, view macOS help:
@@ -137,7 +137,7 @@ xcodebuildmcp macos --help
 ### SwiftPM Package Workflows
 
 ```bash
-xcodebuildmcp swift-package list --package-path ./MyPackage
+xcodebuildmcp swift-package list
 xcodebuildmcp swift-package build --package-path ./MyPackage
 xcodebuildmcp swift-package test --package-path ./MyPackage
 ```
@@ -150,7 +150,7 @@ xcodebuildmcp swift-package --help
 ### Project Discovery
 
 ```bash
-xcodebuildmcp project-discovery discover-projs --workspace-root .
+xcodebuildmcp project-discovery discover-projects --workspace-root .
 xcodebuildmcp project-discovery list-schemes --project-path ./MyApp.xcodeproj
 xcodebuildmcp project-discovery get-app-bundle-id --app-path ./Build/MyApp.app
 ```
@@ -166,8 +166,8 @@ It's worth viewing the --help for the scaffolding tools to see the available opt
 Here are some minimal examples:
 
 ```bash
-xcodebuildmcp project-scaffolding scaffold-ios-project --project-name MyApp --output-path ./Projects
-xcodebuildmcp project-scaffolding scaffold-macos-project --project-name MyMacApp --output-path ./Projects
+xcodebuildmcp project-scaffolding scaffold-ios --project-name MyApp --output-path ./Projects
+xcodebuildmcp project-scaffolding scaffold-macos --project-name MyMacApp --output-path ./Projects
 ```
 
 To see all project scaffolding tools, view project scaffolding help:
@@ -187,4 +187,4 @@ xcodebuildmcp daemon restart
 To see all daemon commands, view daemon help:
 ```bash
 xcodebuildmcp daemon --help
-```
\ No newline at end of file
+```
PATCH

echo "Gold patch applied."
