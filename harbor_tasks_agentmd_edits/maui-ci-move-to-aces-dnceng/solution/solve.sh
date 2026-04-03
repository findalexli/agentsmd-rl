#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q 'AcesShared' eng/pipelines/ci.yml 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/DevelopmentTips.md b/docs/DevelopmentTips.md
index ea179ad1ff5c..230b3f63a3d7 100644
--- a/docs/DevelopmentTips.md
+++ b/docs/DevelopmentTips.md
@@ -21,6 +21,8 @@ for IntelliSense and other tasks to initialize. If the project hasn't 'settled'

 The below parameters can be used with the `dotnet cake` command in the root of your locally cloned .NET MAUI repository folder.

+> **Note:** For provisioning .NET SDK and workloads, prefer using `./build.sh -restore` (or `./build.cmd -restore` on Windows) instead of Cake. The Cake targets below are utility commands.
+
 #### PublicAPI Management
 `--target=publicapi`
 - Clears and regenerates PublicAPI.Unshipped.txt files across all MAUI projects (Core, Controls, Essentials, Graphics)
@@ -55,15 +57,38 @@ To build and run Blazor Desktop samples, check out the [Blazor Desktop](https://

 ### Compile using a local `.dotnet\dotnet` via `build.*` scripts on the root folder

-This method uses the Arcade build infrastructure. For more information, you can look [here](https://github.com/dotnet/arcade/blob/main/Documentation/ArcadeSdk.md#build-scripts-and-extensibility-points)
+This is the **recommended** method for provisioning the .NET SDK and workloads. It uses the Arcade build infrastructure. For more information, you can look [here](https://github.com/dotnet/arcade/blob/main/Documentation/ArcadeSdk.md#build-scripts-and-extensibility-points)

+```bash
+# Restore .NET SDK and workloads to .dotnet folder
+./build.sh -restore
+```
+or on Windows:
+
+```cmd
+.\build.cmd -restore
 ```
-./build.sh -restore -pack
+
+To also build the solution:
+
+```bash
+./build.sh -restore -build
 ```
 or

+```cmd
+.\build.cmd -restore -build
 ```
-./build.cmd -restore -pack
+
+To pack:
+
+```bash
+./build.sh -restore -pack
+```
+or
+
+```cmd
+.\build.cmd -restore -pack
 ```


diff --git a/eng/Build.props b/eng/Build.props
index 3caad25a1c42..691d93a5904d 100644
--- a/eng/Build.props
+++ b/eng/Build.props
@@ -1,14 +1,35 @@
 <Project ToolsVersion="4.0" xmlns="http://schemas.microsoft.com/developer/msbuild/2003">
-  <ItemGroup>
-    <ProjectToBuild Include="$(RepoRoot)Microsoft.Maui.BuildTasks.slnf" Condition="'$(BuildDeviceTests)' != 'true'" />
-    <ProjectToBuild Include="$(RepoRoot)eng/Microsoft.Maui.Packages-mac.slnf" Condition="'$(OS)' != 'Windows_NT' And '$(BuildDeviceTests)' != 'true'" />
-    <ProjectToBuild Include="$(RepoRoot)eng/Microsoft.Maui.Packages.slnf" Condition="'$(OS)' == 'Windows_NT' and '$(BuildDeviceTests)' != 'true'" />
-    <ProjectToBuild Include="$(RepoRoot)src/Controls/tests/DeviceTests/Controls.DeviceTests.csproj" Condition="'$(BuildDeviceTests)' == 'true'" BuildInParallel="false"/>
-    <ProjectToBuild Include="$(RepoRoot)src/Core/tests/DeviceTests/Core.DeviceTests.csproj" Condition="'$(BuildDeviceTests)' == 'true'" BuildInParallel="false"/>
-    <ProjectToBuild Include="$(RepoRoot)src/Graphics/tests/DeviceTests/Graphics.DeviceTests.csproj" Condition="'$(BuildDeviceTests)' == 'true'" BuildInParallel="false" />
-    <ProjectToBuild Include="$(RepoRoot)src/Essentials/test/DeviceTests/Essentials.DeviceTests.csproj" Condition="'$(BuildDeviceTests)' == 'true'" BuildInParallel="false">
-         <AdditionalProperties>CodesignRequireProvisioningProfile=false</AdditionalProperties>
-    </ProjectToBuild>
-    <ProjectToBuild Include="$(RepoRoot)src/BlazorWebView/tests/DeviceTests/MauiBlazorWebView.DeviceTests.csproj" Condition="'$(BuildDeviceTests)' == 'true'" BuildInParallel="false" />
-  </ItemGroup>
-</Project>
\ No newline at end of file
+  <!-- Build tasks always needed first -->
+  <ItemGroup Condition="'$(BuildDeviceTests)' != 'true'">
+    <ProjectToBuild Include="$(RepoRoot)Microsoft.Maui.BuildTasks.slnf" BuildInParallel="false"/>
+  </ItemGroup>
+
+  <!-- Pack only: Microsoft.Maui.Packages -->
+  <ItemGroup Condition="'$(BuildDeviceTests)' != 'true' and '$(Pack)' == 'true'">
+    <ProjectToBuild Include="$(RepoRoot)eng/Microsoft.Maui.Packages-mac.slnf" Condition="'$(OS)' != 'Windows_NT'" BuildInParallel="false">
+        <AdditionalProperties>ValidateXcodeVersion=false</AdditionalProperties>
+    </ProjectToBuild>
+    <ProjectToBuild Include="$(RepoRoot)eng/Microsoft.Maui.Packages.slnf" Condition="'$(OS)' == 'Windows_NT'" BuildInParallel="false" />
+  </ItemGroup>
+
+  <!-- Full build: Microsoft.Maui.sln -->
+  <ItemGroup Condition="'$(BuildDeviceTests)' != 'true' and '$(Pack)' != 'true'">
+    <ProjectToBuild Include="$(RepoRoot)Microsoft.Maui.sln" Condition="'$(OS)' == 'Windows_NT'" BuildInParallel="false">
+        <AdditionalProperties>ValidateXcodeVersion=false;CodesignRequireProvisioningProfile=false;EnableWindowsTargeting=true</AdditionalProperties>
+    </ProjectToBuild>
+    <ProjectToBuild Include="$(RepoRoot)Microsoft.Maui-mac.slnf" Condition="'$(OS)' != 'Windows_NT'" BuildInParallel="false">
+        <AdditionalProperties>ValidateXcodeVersion=false;CodesignRequireProvisioningProfile=false;EnableWindowsTargeting=true</AdditionalProperties>
+    </ProjectToBuild>
+  </ItemGroup>
+
+  <!-- Device tests -->
+  <ItemGroup Condition="'$(BuildDeviceTests)' == 'true'">
+    <ProjectToBuild Include="$(RepoRoot)src/Controls/tests/DeviceTests/Controls.DeviceTests.csproj" BuildInParallel="false"/>
+    <ProjectToBuild Include="$(RepoRoot)src/Core/tests/DeviceTests/Core.DeviceTests.csproj" BuildInParallel="false"/>
+    <ProjectToBuild Include="$(RepoRoot)src/Graphics/tests/DeviceTests/Graphics.DeviceTests.csproj" BuildInParallel="false" />
+    <ProjectToBuild Include="$(RepoRoot)src/Essentials/test/DeviceTests/Essentials.DeviceTests.csproj" BuildInParallel="false">
+        <AdditionalProperties>CodesignRequireProvisioningProfile=false</AdditionalProperties>
+    </ProjectToBuild>
+    <ProjectToBuild Include="$(RepoRoot)src/BlazorWebView/tests/DeviceTests/MauiBlazorWebView.DeviceTests.csproj" BuildInParallel="false" />
+  </ItemGroup>
+</Project>
diff --git a/eng/pipelines/arcade/stage-build.yml b/eng/pipelines/arcade/stage-build.yml
index 84859e656ff4..9942635c8a0a 100644
--- a/eng/pipelines/arcade/stage-build.yml
+++ b/eng/pipelines/arcade/stage-build.yml
@@ -83,5 +83,5 @@ stages:
             - script: ${{ BuildPlatform.buildScript }} -restore -build -configuration ${{ BuildConfiguration }} -projects "${{ parameters.buildTaskProjects }}" /p:ArchiveTests=false /p:TreatWarningsAsErrors=$(TreatWarningsAsErrors) /bl:$(Build.Arcade.LogsPath)${{ BuildConfiguration }}/buildtasks_${{ BuildPlatform.os }}.binlog $(_OfficialBuildIdArgs)
               displayName: 🛠️ Build BuildTasks

-            - script: ${{ BuildPlatform.buildScript }} -restore -build -configuration ${{ BuildConfiguration }} -projects ${{ BuildPlatform.sln }} /p:ArchiveTests=false /p:TreatWarningsAsErrors=$(TreatWarningsAsErrors) /p:CodesignRequireProvisioningProfile=false /p:EnableWindowsTargeting=true /bl:$(Build.Arcade.LogsPath)${{ BuildConfiguration }}/build_${{ BuildPlatform.os }}.binlog $(_OfficialBuildIdArgs)
+            - script: ${{ BuildPlatform.buildScript }} -restore -build -configuration ${{ BuildConfiguration }} /p:ArchiveTests=false /p:TreatWarningsAsErrors=$(TreatWarningsAsErrors) /bl:$(Build.Arcade.LogsPath)${{ BuildConfiguration }}/build_${{ BuildPlatform.os }}.binlog $(_OfficialBuildIdArgs)
               displayName: 🛠️ Build Microsoft.Maui.sln
diff --git a/eng/pipelines/arcade/stage-device-tests.yml b/eng/pipelines/arcade/stage-device-tests.yml
index eacc0041dd58..8583eda11eda 100644
--- a/eng/pipelines/arcade/stage-device-tests.yml
+++ b/eng/pipelines/arcade/stage-device-tests.yml
@@ -439,9 +439,8 @@ stages:
           - script: dotnet tool restore
             displayName: 'Restore .NET tools'
             retryCountOnTaskFailure: 3
-
-          # Install .NET SDK
-          - script: dotnet cake --target=dotnet --configuration="Release" --verbosity=diagnostic
+          # Install .NET SDK and workloads using Arcade build script
+          - script: ./build.cmd -restore -configuration Release
             displayName: 'Install .NET'
             retryCountOnTaskFailure: 3
             env:
@@ -452,7 +451,7 @@ stages:
             displayName: 'Add .NET to PATH'

           # Build BuildTasks first
-          - script: dotnet cake --target=dotnet-buildtasks --configuration="Release"
+          - script: ./build.cmd -build -configuration Release -projects Microsoft.Maui.BuildTasks.slnf
             displayName: Build the MSBuild Tasks

           # Build Windows device tests using Cake script (Packaged/MSIX builds)
diff --git a/eng/pipelines/arcade/stage-integration-tests.yml b/eng/pipelines/arcade/stage-integration-tests.yml
index d7b0a4d75ab7..5810405336a0 100644
--- a/eng/pipelines/arcade/stage-integration-tests.yml
+++ b/eng/pipelines/arcade/stage-integration-tests.yml
@@ -46,7 +46,7 @@ stages:
           # Set IOS_TEST_DEVICE for all iOS-related tests (RunOniOS and RunOniOS_*)
           ${{ if or(eq(job.testCategory, 'RunOniOS'), startsWith(job.testName, 'RunOniOS')) }}:
             envVariables:
-              IOS_TEST_DEVICE: ios-simulator-64_18.5
+              IOS_TEST_DEVICE: ios-simulator-64

       - task: PublishTestResults@2
         inputs:
diff --git a/eng/pipelines/ci.yml b/eng/pipelines/ci.yml
index a171cb8b88aa..b490d283306d 100644
--- a/eng/pipelines/ci.yml
+++ b/eng/pipelines/ci.yml
@@ -74,8 +74,9 @@ parameters:
     os: Windows
     buildScript: $(_buildScript)
     sln: '$(Build.SourcesDirectory)/Microsoft.Maui.sln'
-  - name: Azure Pipelines
-    vmImage: $(HostedMacImage)
+  - name: AcesShared
+    demands:
+        - ImageOverride -equals ACES_VM_SharedPool_Tahoe
     os: macOS
     buildScript: $(_buildScriptMacOS)
     sln: '$(Build.SourcesDirectory)/Microsoft.Maui-mac.slnf'
@@ -97,8 +98,9 @@ parameters:
 - name: MacOSPool
   type: object
   default:
-    name: Azure Pipelines
-    vmImage: $(HostedMacImage)
+    name: AcesShared
+    demands:
+        - ImageOverride -equals ACES_VM_SharedPool_Tahoe
     os: macOS
     label: macOS

@@ -106,8 +108,9 @@ parameters:
 - name: MacOSPoolArm64
   type: object
   default:
-    name: Azure Pipelines
-    vmImage: macOS-15-arm64
+    name: AcesShared
+    demands:
+        - ImageOverride -equals ACES_VM_SharedPool_Tahoe
     os: macOS
     label: macOS-arm64

diff --git a/eng/pipelines/common/provision.yml b/eng/pipelines/common/provision.yml
index 7f4f31e60347..316edd3ef5f6 100644
--- a/eng/pipelines/common/provision.yml
+++ b/eng/pipelines/common/provision.yml
@@ -43,7 +43,7 @@ steps:
   - template: ../../common/templates-official/steps/enable-internal-sources.yml
     parameters:
       legacyCredential: $(dn-bot-dnceng-artifact-feeds-rw)
-
+
   - template: ../../common/templates-official/steps/enable-internal-runtimes.yml
     parameters:
       federatedServiceConnection: ${{ parameters.federatedServiceConnection }}
@@ -51,11 +51,10 @@ steps:
       expiryInHours: ${{ parameters.expiryInHours }}
       base64Encode: ${{ parameters.base64Encode }}

-
 ##################################################
 #               Provisioning macOS               #
 ##################################################
-
+
 #check if the _tool directory exists and remove it
 - pwsh: |
     $dotnetToolsPath = "$(Agent.ToolsDirectory)/dotnet"
@@ -95,7 +94,8 @@ steps:
       sw_vers -productVersion
       echo
       echo Installed Xcode versions:
-      ls -la /Applications | grep 'Xcode'
+      XCODE_LIST=($(ls -1 /Applications | grep '^Xcode_' | sed 's/^Xcode_//;s/.app$//'))
+      for v in "${XCODE_LIST[@]}"; do echo "  $v"; done
       echo
       echo currently selected xcode:
       xcrun xcode-select --print-path
@@ -107,37 +107,51 @@ steps:
       else
         XCODE_VERSION=$(XCODE)
       fi
-
-      # Check if the specified Xcode version exists, if not try fallback
-      XCODE_PATH="/Applications/Xcode_${XCODE_VERSION}.app"
-      if [[ ! -d "$XCODE_PATH" ]]; then
-        echo "Xcode version ${XCODE_VERSION} not found at ${XCODE_PATH}"
-        # Extract fallback version by removing the last part after the final dot (e.g., 26.0.1 -> 26.0.0)
-        if [[ "$XCODE_VERSION" =~ ^([0-9]+\.[0-9]+)\.[0-9]+$ ]]; then
-          FALLBACK_VERSION="${BASH_REMATCH[1]}.0"
-          FALLBACK_PATH="/Applications/Xcode_${FALLBACK_VERSION}.app"
-          echo "Trying fallback Xcode version: ${FALLBACK_VERSION}"
-          if [[ -d "$FALLBACK_PATH" ]]; then
-            echo "Found fallback Xcode version at ${FALLBACK_PATH}"
-            XCODE_VERSION="$FALLBACK_VERSION"
-            XCODE_PATH="$FALLBACK_PATH"
-          else
-            echo "Warning: Fallback Xcode version ${FALLBACK_VERSION} also not found at ${FALLBACK_PATH}"
-            echo "Proceeding with original version ${XCODE_VERSION} - this may fail"
-          fi
+
+      # Check if the specified Xcode version exists, if not try fallbacks
+      # Fallback order: exact version -> major.minor -> major
+      XCODE_PATH=""
+      ORIGINAL_VERSION="$XCODE_VERSION"
+
+      # Build list of versions to try
+      VERSIONS_TO_TRY=("$XCODE_VERSION")
+
+      # Add major.minor fallback (e.g., 26.0.1 -> 26.0)
+      if [[ "$XCODE_VERSION" =~ ^([0-9]+\.[0-9]+)\.[0-9]+$ ]]; then
+        VERSIONS_TO_TRY+=("${BASH_REMATCH[1]}")
+      fi
+
+      # Add major fallback (e.g., 26.0.1 or 26.0 -> 26)
+      if [[ "$XCODE_VERSION" =~ ^([0-9]+)\. ]]; then
+        VERSIONS_TO_TRY+=("${BASH_REMATCH[1]}")
+      fi
+
+      echo "Will try Xcode versions in order: ${VERSIONS_TO_TRY[*]}"
+
+      for VERSION in "${VERSIONS_TO_TRY[@]}"; do
+        CANDIDATE_PATH="/Applications/Xcode_${VERSION}.app"
+        echo "Checking for Xcode ${VERSION} at ${CANDIDATE_PATH}..."
+        if [[ -d "$CANDIDATE_PATH" ]]; then
+          echo "Found Xcode version ${VERSION} at ${CANDIDATE_PATH}"
+          XCODE_VERSION="$VERSION"
+          XCODE_PATH="$CANDIDATE_PATH"
+          break
         else
-          echo "Warning: Cannot determine fallback version for ${XCODE_VERSION}"
-          echo "Proceeding with original version - this may fail"
+          echo "Xcode version ${VERSION} not found"
         fi
-      else
-        echo "Found Xcode version ${XCODE_VERSION} at ${XCODE_PATH}"
+      done
+
+      if [[ -z "$XCODE_PATH" ]]; then
+        echo "ERROR: No suitable Xcode version found for requested version ${ORIGINAL_VERSION}"
+        echo "Tried: ${VERSIONS_TO_TRY[*]}"
+        exit 1
       fi
-
+
       sudo xcode-select -s "$XCODE_PATH"
       xcrun xcode-select --print-path
       xcodebuild -version
       sudo xcodebuild -license accept
-
+
       sudo xcodebuild -runFirstLaunch
     displayName: Select Xcode Version
     condition: and(succeeded(), eq(variables['Agent.OS'], 'Darwin'))
@@ -298,4 +312,4 @@ steps:
     displayName: 'Provision Android SDK - Create AVDs'
     condition: succeeded()
     env:
-      AndroidSdkProvisionApiLevel: ${{ parameters.androidEmulatorApiLevel }}
\ No newline at end of file
+      AndroidSdkProvisionApiLevel: ${{ parameters.androidEmulatorApiLevel }}
diff --git a/eng/pipelines/device-tests.yml b/eng/pipelines/device-tests.yml
index ea46ebcf0429..af6f271db91a 100644
--- a/eng/pipelines/device-tests.yml
+++ b/eng/pipelines/device-tests.yml
@@ -71,7 +71,6 @@ parameters:
     vmImage: $(iosDeviceTestsVmImage)
     demands:
     - macOS.Name -equals Sequoia
-    - Agent.OSVersion -equals 15.6

 - name: catalystPool
   type: object
@@ -80,7 +79,6 @@ parameters:
     vmImage: $(iosDeviceTestsVmImage)
     demands:
     - macOS.Name -equals Sequoia
-    - Agent.OSVersion -equals 15.6

 - name: windowsPool
   type: object
diff --git a/src/Workload/README.md b/src/Workload/README.md
index 1103de50f691..82f4738f5df6 100644
--- a/src/Workload/README.md
+++ b/src/Workload/README.md
@@ -120,8 +120,15 @@ assemblies at build & runtime.

 After you've done a build, such as:

-```dotnetcli
-$ dotnet cake
+```bash
+# Restore .NET SDK and workloads, then pack
+./build.sh -restore -pack
+```
+
+or on Windows:
+
+```cmd
+.\build.cmd -restore -pack
 ```

 You'll have various `artifacts/*.nupkg` files produced, as well as the

PATCH

echo "Patch applied successfully."
