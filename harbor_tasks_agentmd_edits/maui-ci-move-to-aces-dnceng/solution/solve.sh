#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'androidPoolInternal' eng/pipelines/ci-uitests.yml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch for CI pool validation fix
git apply - <<'PATCH'
diff --git a/eng/pipelines/ci-device-tests.yml b/eng/pipelines/ci-device-tests.yml
index 427e802f15c8..f1ad386bd2f5 100644
--- a/eng/pipelines/ci-device-tests.yml
+++ b/eng/pipelines/ci-device-tests.yml
@@ -136,10 +136,13 @@ stages:
           skipProvisioning: true
           skipXcode: false
           skipSimulatorSetup: false
-  # Just use the old way for Windows Device Tests
+  # Use the old way for Windows Device Tests
   - template: common/device-tests.yml
     parameters:
-      windowsPool: ${{ parameters.windowsPoolPublic }}
+      ${{ if eq(variables['System.TeamProject'], 'internal') }}:
+        windowsPool: ${{ parameters.windowsPoolInternal }}
+      ${{ else }}:
+        windowsPool: ${{ parameters.windowsPoolPublic }}
       targetFrameworkVersion: ${{ targetFrameworkVersion }}
       windowsVersions: [ 'packaged', 'unpackaged' ]
       skipProvisioning: true
diff --git a/eng/pipelines/ci-uitests.yml b/eng/pipelines/ci-uitests.yml
index d79cd8082031..191282fd62f2 100644
--- a/eng/pipelines/ci-uitests.yml
+++ b/eng/pipelines/ci-uitests.yml
@@ -63,44 +63,83 @@ parameters:
     type: boolean
     default: false

-  - name: androidPool
+  # Internal pools (dnceng)
+  - name: androidPoolInternal
     type: object
     default:
-      name: MAUI
-      vmImage: MAUI
+      name: Azure Pipelines
+      vmImage: macOS-15-arm64
+
+  - name: androidPoolLinuxInternal
+    type: object
+    default:
+      name: MAUI-DNCENG
       demands:
-        - Agent.OSArchitecture -equals ARM64
-
-  - name: androidPoolLinux
+        - ImageOverride -equals 1ESPT-Ubuntu22.04
+
+  - name: iosPoolInternal
+    type: object
+    default:
+      name: Azure Pipelines
+      vmImage: macOS-15-arm64
+
+  - name: windowsBuildPoolInternal
+    type: object
+    default:
+      name: NetCore1ESPool-Internal
+      demands:
+        - ImageOverride -equals 1es-windows-2022
+
+  - name: windowsPoolInternal
+    type: object
+    default:
+      name: NetCore1ESPool-Internal
+      demands:
+        - ImageOverride -equals 1es-windows-2022
+
+  - name: macosPoolInternal
+    type: object
+    default:
+      name: Azure Pipelines
+      vmImage: macOS-14
+
+  # Public pools (dnceng-public)
+  - name: androidPoolPublic
+    type: object
+    default:
+      name: AcesShared
+      demands:
+        - ImageOverride -equals ACES_VM_SharedPool_Tahoe
+
+  - name: androidPoolLinuxPublic
     type: object
     default:
       name: MAUI-DNCENG
       demands:
         - ImageOverride -equals 1ESPT-Ubuntu22.04

-  - name: iosPool
+  - name: iosPoolPublic
     type: object
     default:
-      name: MAUI
-      vmImage: MAUI
+      name: AcesShared
       demands:
-        - Agent.OSArchitecture -equals ARM64
-
-  - name: windowsBuildPool
+        - ImageOverride -equals ACES_VM_SharedPool_Tahoe
+
+  - name: windowsBuildPoolPublic
     type: object
     default:
       name: NetCore-Public
       demands:
         - ImageOverride -equals 1es-windows-2022-open
-
-  - name: windowsPool
+
+  - name: windowsPoolPublic
     type: object
     default:
       name: NetCore-Public
       demands:
         - ImageOverride -equals 1es-windows-2022-open

-  - name: macosPool
+  - name: macosPoolPublic
     type: object
     default:
       name: Azure Pipelines
@@ -110,12 +149,21 @@ stages:

   - template: common/ui-tests.yml
     parameters:
-      androidPool: ${{ parameters.androidPool }}
-      androidLinuxPool: ${{ parameters.androidPoolLinux }}
-      iosPool: ${{ parameters.iosPool }}
-      windowsPool: ${{ parameters.windowsPool }}
-      windowsBuildPool: ${{ parameters.windowsBuildPool }}
-      macosPool: ${{ parameters.macosPool }}
+      # Select pools based on pipeline - internal vs public
+      ${{ if eq(variables['System.TeamProject'], 'internal') }}:
+        androidPool: ${{ parameters.androidPoolInternal }}
+        androidLinuxPool: ${{ parameters.androidPoolLinuxInternal }}
+        iosPool: ${{ parameters.iosPoolInternal }}
+        windowsPool: ${{ parameters.windowsPoolInternal }}
+        windowsBuildPool: ${{ parameters.windowsBuildPoolInternal }}
+        macosPool: ${{ parameters.macosPoolInternal }}
+      ${{ else }}:
+        androidPool: ${{ parameters.androidPoolPublic }}
+        androidLinuxPool: ${{ parameters.androidPoolLinuxPublic }}
+        iosPool: ${{ parameters.iosPoolPublic }}
+        windowsPool: ${{ parameters.windowsPoolPublic }}
+        windowsBuildPool: ${{ parameters.windowsBuildPoolPublic }}
+        macosPool: ${{ parameters.macosPoolPublic }}
       # BuildNativeAOT is false by default, but true in devdiv environment
       BuildNativeAOT: ${{ or(parameters.BuildNativeAOT, and(ne(variables['Build.Reason'], 'PullRequest'), eq(variables['System.TeamProject'], 'devdiv'))) }}
       RunNativeAOT: ${{ parameters.RunNativeAOT }}
@@ -134,6 +182,4 @@ stages:
           iosVersionsExclude: [ '12.4'] # Ignore iOS 12.4 while we can't make it work on CI
           ios: $(System.DefaultWorkingDirectory)/src/Controls/tests/TestCases.iOS.Tests/Controls.TestCases.iOS.Tests.csproj
           winui: $(System.DefaultWorkingDirectory)/src/Controls/tests/TestCases.WinUI.Tests/Controls.TestCases.WinUI.Tests.csproj
-          mac: $(System.DefaultWorkingDirectory)/src/Controls/tests/TestCases.Mac.Tests/Controls.TestCases.Mac.Tests.csproj
-
-
+          mac: $(System.DefaultWorkingDirectory)/src/Controls/tests/TestCases.Mac.Tests/Controls.TestCases.Mac.Tests.csproj
PATCH

echo "Patch applied successfully."
