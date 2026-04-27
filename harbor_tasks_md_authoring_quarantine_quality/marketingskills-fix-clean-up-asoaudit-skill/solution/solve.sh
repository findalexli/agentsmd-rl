#!/usr/bin/env bash
set -euo pipefail

cd /workspace/marketingskills

# Idempotency guard
if grep -qF "description: \"When the user wants to audit or optimize an App Store or Google Pl" "skills/aso-audit/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/aso-audit/SKILL.md b/skills/aso-audit/SKILL.md
@@ -1,12 +1,6 @@
 ---
 name: aso-audit
-description: >
-  Use when auditing an App Store or Google Play listing for optimization.
-  Triggers: "ASO audit", "app store optimization", "optimize my app listing",
-  "improve app visibility", "app store ranking", "audit my listing", or when
-  user shares an App Store / Google Play URL and wants to improve it. Also
-  triggers on: "why aren't people downloading my app", "improve my app
-  conversion", "keyword optimization for app", "compare my app to competitors".
+description: "When the user wants to audit or optimize an App Store or Google Play listing. Also use when the user mentions 'ASO audit,' 'app store optimization,' 'optimize my app listing,' 'improve app visibility,' 'app store ranking,' 'audit my listing,' 'why aren't people downloading my app,' 'improve my app conversion,' 'keyword optimization for app,' or 'compare my app to competitors.' Use when the user shares an App Store or Google Play URL and wants to improve it."
 metadata:
   version: 1.0.0
 ---
@@ -90,14 +84,13 @@ work with what's available. Ask the user to paste missing fields if critical.
 
 ### Visual asset assessment
 
-WebFetch cannot extract screenshot images or caption text. **Always use the
-Playwright browser tool** to get visual data:
+WebFetch cannot extract screenshot images or caption text. **Take a screenshot
+of the listing page** to get visual data:
 
-1. Navigate to the listing URL with `browser_navigate`
-2. Take a full-page screenshot with `browser_take_screenshot`
-3. Read the screenshot image to assess: icon, screenshot count, caption text,
+1. Navigate to the listing URL and capture a full-page screenshot
+2. Assess the screenshot for: icon quality, screenshot count, caption text,
    messaging quality, preview video presence, feature graphic (Google Play)
-4. If Playwright is unavailable, ask the user to share a screenshot of the
+3. If browser tools are unavailable, ask the user to share a screenshot of the
    listing page
 
 **Promotional text (Apple):** This 170-char field appears above the description
@@ -297,3 +290,23 @@ the app's brand maturity tier — they may be deliberate choices for Dominant ap
 
 - [ ] No developer responses to negative reviews _(note volume — responding at 10M+ reviews is a different challenge than at 1K)_
 - [ ] Generic "What's New" text _(acceptable at weekly+ release cadence for Established/Dominant)_
+
+---
+
+## Task-Specific Questions
+
+1. What is the App Store or Google Play URL?
+2. Is this your app or a competitor's?
+3. What category does the app compete in?
+4. Do you have competitor URLs to compare against?
+5. Are you focused on search visibility, conversion rate, or both?
+6. Do you have access to App Store Connect or Google Play Console data?
+
+---
+
+## Related Skills
+
+- **page-cro**: For optimizing the conversion of web-based landing pages that drive app installs
+- **ad-creative**: For creating App Store and Google Play ad creatives
+- **analytics-tracking**: For setting up install attribution and in-app event tracking
+- **customer-research**: For understanding user needs and language to inform listing copy
PATCH

echo "Gold patch applied."
