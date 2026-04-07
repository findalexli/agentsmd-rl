#!/usr/bin/env bash
set -euo pipefail
cd /workspace/maui

# Idempotency: skip if already patched
if grep -q "AppInfoUtils.IsPackagedApp" src/Essentials/src/Permissions/Permissions.windows.cs; then
    echo "Patch already applied, skipping."
    exit 0
fi

# ── 1. Code fix: guard EnsureDeclared() for unpackaged apps ──

git apply <<'PATCH'
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
@@ -193,13 +198,22 @@ public override Task<PermissionStatus> CheckStatusAsync()
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

# ── 2. Config updates: remove NOTE block from agent instructions ──

python3 << 'PYEOF'
import re
from pathlib import Path

# ── copilot-instructions.md: remove "Opening PRs" section ──
copilot = Path(".github/copilot-instructions.md")
content = copilot.read_text()

content = re.sub(
    r"\n### Opening PRs\n.*?(?=\n\n## )",
    "\n",
    content,
    count=1,
    flags=re.DOTALL,
)
content = re.sub(r"\n{3,}", "\n\n", content)
copilot.write_text(content)

# ── pr-finalize SKILL.md: remove NOTE block requirement ──
skill = Path(".github/skills/pr-finalize/SKILL.md")
content = skill.read_text()

content = content.replace(
    "1. Start with the required NOTE block (so users can test PR artifacts)\n2. Include",
    "1. Include",
)
content = content.replace("3. Match", "2. Match")

note_block = """<!-- Please let the below note in for people that find this PR -->
> [!NOTE]
> Are you waiting for the changes in this PR to be merged?
> It would be very helpful if you could [test the resulting artifacts](https://github.com/dotnet/maui/wiki/Testing-PR-Builds) from this PR and let us know in a comment if this change resolves your issue. Thank you!
"""
content = content.replace(note_block, "")
content = re.sub(r"\n{3,}", "\n\n", content)
skill.write_text(content)

# ── complete-example.md: remove NOTE block ──
example = Path(".github/skills/pr-finalize/references/complete-example.md")
content = example.read_text()
content = content.replace(note_block, "")
content = re.sub(r"\n{3,}", "\n\n", content)
example.write_text(content)

print("Config files updated.")
PYEOF

echo "Gold patch applied."
