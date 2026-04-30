#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cloudbase-mcp

# Idempotency guard
if grep -qF "- When generating mini program code, if material images are needed, such as tabb" "config/.claude/skills/miniprogram-development/SKILL.md" && grep -qF "- When generating mini program code, if material images are needed, such as tabb" "config/.codebuddy/skills/miniprogram-development/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/config/.claude/skills/miniprogram-development/SKILL.md b/config/.claude/skills/miniprogram-development/SKILL.md
@@ -40,7 +40,20 @@ Use this skill for **WeChat Mini Program development** when you need to:
    - Use CLI command to open project pointing to directory containing `project.config.json`
 
 4. **Handle resources properly**
-   - Download icon images (e.g., tabbar iconPath) from Unsplash or similar sources
+   - **Icons8 (Recommended)**: Use Icons8 for icon images (e.g., tabbar iconPath)
+     - URL format: `https://img.icons8.com/{style}/{size}/{color}/{icon-name}.png`
+     - Parameters:
+       - `style`: `ios` (outline style) or `ios-filled` (filled style)
+       - `size`: `100` (recommended 100px, file size < 5KB)
+       - `color`: hex color code without # (e.g., `8E8E93` for gray, `FF3B30` for red)
+       - `icon-name`: icon name (e.g., `checked--v1`)
+     - Examples:
+       - Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`
+       - Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`
+     - Advantages:
+       - ✅ Very small file size (usually < 3KB)
+       - ✅ Supports custom colors
+       - ✅ Clean and professional icons
    - Use `downloadRemoteFile` tool to download resources
    - Avoid build errors by ensuring all referenced resources exist
 
@@ -81,8 +94,8 @@ Use this skill for **WeChat Mini Program development** when you need to:
    - Environment ID can be queried via `envQuery` tool
 
 2. **Resource Management**:
-   - When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, can download from Unsplash via URL
-   - Can refer to workflow's download remote resources process
+   - When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)
+   - Use `downloadRemoteFile` tool to download resources
    - When generating mini program code, if using `iconPath` and similar, must simultaneously help user download icons to avoid build errors
 
 ## Mini Program Authentication Characteristics
diff --git a/config/.codebuddy/skills/miniprogram-development/SKILL.md b/config/.codebuddy/skills/miniprogram-development/SKILL.md
@@ -40,7 +40,20 @@ Use this skill for **WeChat Mini Program development** when you need to:
    - Use CLI command to open project pointing to directory containing `project.config.json`
 
 4. **Handle resources properly**
-   - Download icon images (e.g., tabbar iconPath) from Unsplash or similar sources
+   - **Icons8 (Recommended)**: Use Icons8 for icon images (e.g., tabbar iconPath)
+     - URL format: `https://img.icons8.com/{style}/{size}/{color}/{icon-name}.png`
+     - Parameters:
+       - `style`: `ios` (outline style) or `ios-filled` (filled style)
+       - `size`: `100` (recommended 100px, file size < 5KB)
+       - `color`: hex color code without # (e.g., `8E8E93` for gray, `FF3B30` for red)
+       - `icon-name`: icon name (e.g., `checked--v1`)
+     - Examples:
+       - Unselected (gray outline): `https://img.icons8.com/ios/100/8E8E93/checked--v1.png`
+       - Selected (red filled): `https://img.icons8.com/ios-filled/100/FF3B30/checked--v1.png`
+     - Advantages:
+       - ✅ Very small file size (usually < 3KB)
+       - ✅ Supports custom colors
+       - ✅ Clean and professional icons
    - Use `downloadRemoteFile` tool to download resources
    - Avoid build errors by ensuring all referenced resources exist
 
@@ -81,8 +94,8 @@ Use this skill for **WeChat Mini Program development** when you need to:
    - Environment ID can be queried via `envQuery` tool
 
 2. **Resource Management**:
-   - When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, can download from Unsplash via URL
-   - Can refer to workflow's download remote resources process
+   - When generating mini program code, if material images are needed, such as tabbar's `iconPath` and other places, **prefer Icons8** (see section 4 above for details)
+   - Use `downloadRemoteFile` tool to download resources
    - When generating mini program code, if using `iconPath` and similar, must simultaneously help user download icons to avoid build errors
 
 ## Mini Program Authentication Characteristics
PATCH

echo "Gold patch applied."
