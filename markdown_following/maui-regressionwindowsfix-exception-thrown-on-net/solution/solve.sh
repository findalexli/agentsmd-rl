#!/usr/bin/env bash
set -euo pipefail

cd /workspace/maui

# Idempotent: skip if already applied
if grep -q "if (AppInfoUtils.IsPackagedApp)" src/Essentials/src/Permissions/Permissions.windows.cs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply gold patch (only the code changes - config file changes are already at base)
git apply - <<'PATCH'
diff --git a/src/Essentials/src/Permissions/Permissions.windows.cs b/src/Essentials/src/Permissions/Permissions.windows.cs
index ee13b9a47d0e..ac9b25186d1e 100644
--- a/src/Essentials/src/Permissions/Permissions.windows.cs
+++ b/src/Essentials/src/Permissions/Permissions.windows.cs
@@ -180,7 +180,12 @@ public partial class Microphone : BasePlatformPermission
 			/// <inheritdoc/>
 			public override Task<PermissionStatus> CheckStatusAsync()
 			{
-				EnsureDeclared();
+				// For packaged apps, ensure manifest declaration is present
+				if (AppInfoUtils.IsPackagedApp)
+				{
+					EnsureDeclared();
+				}
+
 				return Task.FromResult(CheckStatus() switch
 				{
 					DeviceAccessStatus.Allowed => PermissionStatus.Granted,
@@ -193,13 +198,22 @@ public partial class Microphone : BasePlatformPermission
 			/// <inheritdoc/>
 			public override async Task<PermissionStatus> RequestAsync()
 			{
-				EnsureDeclared();
-
-				// If already explicitly allowed, return that
+				// Check status first - if already allowed, return early
 				var status = CheckStatus();
 				if (status == DeviceAccessStatus.Allowed)
 					return PermissionStatus.Granted;
 
+				// For packaged apps, ensure manifest declaration is present
+				if (AppInfoUtils.IsPackagedApp)
+				{
+					EnsureDeclared();
+				}
+
+				return await TryRequestPermissionAsync();
+			}
+
+			async Task<PermissionStatus> TryRequestPermissionAsync()
+			{
 				try
 				{
 					var settings = new MediaCaptureInitializationSettings
PATCH

echo "Patch applied successfully."
