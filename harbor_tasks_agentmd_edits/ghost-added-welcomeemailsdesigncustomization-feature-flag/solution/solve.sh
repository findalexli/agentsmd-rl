#!/usr/bin/env bash
set -euo pipefail

cd /workspace/Ghost

# Idempotent: skip if already applied
if grep -q 'welcomeEmailsDesignCustomization' ghost/core/core/shared/labs.js 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.claude/skills/add-private-feature-flag/SKILL.md b/.claude/skills/add-private-feature-flag/SKILL.md
new file mode 100644
index 00000000000..19680ff4b4c
--- /dev/null
+++ b/.claude/skills/add-private-feature-flag/SKILL.md
@@ -0,0 +1,28 @@
+---
+name: add-private-feature-flag
+description: Use when adding a new private (developer experiments) feature flag to Ghost, including the backend registration and settings UI toggle.
+---
+
+# Add Private Feature Flag
+
+## Overview
+Adds a new private feature flag to Ghost. Private flags appear in Labs settings under the "Private features" tab, visible only when developer experiments are enabled.
+
+## Steps
+
+1. **Add the flag to `ghost/core/core/shared/labs.js`**
+   - Add the flag name (camelCase string) to the `PRIVATE_FEATURES` array.
+
+2. **Add a UI toggle in `apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx`**
+   - Add a new entry to the `features` array with `title`, `description`, and `flag` (must match the string in `labs.js`).
+
+3. **Run tests and update the config API snapshot**
+   - Unit: `cd ghost/core && yarn test:single test/unit/shared/labs.test.js`
+   - Update snapshot and run e2e: `cd ghost/core && UPDATE_SNAPSHOTS=1 yarn test:single test/e2e-api/admin/config.test.js`
+   - Review the diff of `ghost/core/test/e2e-api/admin/__snapshots__/config.test.js.snap` to confirm only your new flag was added.
+
+## Notes
+- No database migration is needed. Labs flags are stored in a single JSON `labs` setting.
+- The flag name must be identical in `labs.js`, `private-features.tsx`, and the snapshot.
+- Flags are camelCase strings (e.g. `welcomeEmailDesignCustomization`).
+- For public beta flags (visible to all users), add to `PUBLIC_BETA_FEATURES` in `labs.js` instead and add the toggle to `apps/admin-x-settings/src/components/settings/advanced/labs/beta-features.tsx`.
diff --git a/apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx b/apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx
index 1ee3f656240..75959921fe2 100644
--- a/apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx
+++ b/apps/admin-x-settings/src/components/settings/advanced/labs/private-features.tsx
@@ -63,6 +63,10 @@ const features: Feature[] = [{
     title: 'Members Forward',
     description: 'Use the new React-based members list instead of the Ember implementation',
     flag: 'membersForward'
+}, {
+    title: 'Welcome Emails Design Customization',
+    description: 'Enable design customization options for welcome emails',
+    flag: 'welcomeEmailsDesignCustomization'
 }];

 const AlphaFeatures: React.FC = () => {
diff --git a/ghost/core/core/shared/labs.js b/ghost/core/core/shared/labs.js
index 003722278c3..299607a1d98 100644
--- a/ghost/core/core/shared/labs.js
+++ b/ghost/core/core/shared/labs.js
@@ -50,7 +50,8 @@ const PRIVATE_FEATURES = [
     'transistor',
     'retentionOffers',
     'welcomeEmailEditor',
-    'membersForward'
+    'membersForward',
+    'welcomeEmailsDesignCustomization'
 ];

 module.exports.GA_KEYS = [...GA_FEATURES];
diff --git a/ghost/core/test/e2e-api/admin/__snapshots__/config.test.js.snap b/ghost/core/test/e2e-api/admin/__snapshots__/config.test.js.snap
index 5baac4be94d..887cd0eb6c6 100644
--- a/ghost/core/test/e2e-api/admin/__snapshots__/config.test.js.snap
+++ b/ghost/core/test/e2e-api/admin/__snapshots__/config.test.js.snap
@@ -31,6 +31,7 @@ Object {
       "transistor": true,
       "urlCache": true,
       "welcomeEmailEditor": true,
+      "welcomeEmailsDesignCustomization": true,
     },
     "mail": "",
     "mailgunIsConfigured": false,

PATCH

echo "Patch applied successfully."
