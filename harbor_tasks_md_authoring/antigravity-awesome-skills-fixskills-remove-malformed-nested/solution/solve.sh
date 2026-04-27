#!/usr/bin/env bash
set -euo pipefail

cd /workspace/antigravity-awesome-skills

# Idempotency guard
if grep -qF "skills/browser-extension-builder/SKILL.md" "skills/browser-extension-builder/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/browser-extension-builder/SKILL.md b/skills/browser-extension-builder/SKILL.md
@@ -34,9 +34,6 @@ Structure for modern browser extensions
 
 **When to use**: When starting a new extension
 
-```javascript
-## Extension Architecture
-
 ### Project Structure
 ```
 extension/
@@ -91,17 +88,13 @@ Popup ←→ Background (Service Worker) ←→ Content Script
               ↓
         chrome.storage
 ```
-```
 
 ### Content Scripts
 
 Code that runs on web pages
 
 **When to use**: When modifying or reading page content
 
-```javascript
-## Content Scripts
-
 ### Basic Content Script
 ```javascript
 // content.js - Runs on every matched page
@@ -159,17 +152,13 @@ injectUI();
   }]
 }
 ```
-```
 
 ### Storage and State
 
 Persisting extension data
 
 **When to use**: When saving user settings or data
 
-```javascript
-## Storage and State
-
 ### Chrome Storage API
 ```javascript
 // Save data
@@ -218,7 +207,6 @@ async function setStorage(data) {
 const { settings } = await getStorage(['settings']);
 await setStorage({ settings: { ...settings, theme: 'dark' } });
 ```
-```
 
 ## Anti-Patterns
 
PATCH

echo "Gold patch applied."
