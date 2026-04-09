#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q 'locatorOrSelectorAsSelector' packages/playwright-core/src/tools/backend/tab.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/playwright-core/src/tools/backend/tab.ts b/packages/playwright-core/src/tools/backend/tab.ts
index 1570af91752ac..4fb129b9ec979 100644
--- a/packages/playwright-core/src/tools/backend/tab.ts
+++ b/packages/playwright-core/src/tools/backend/tab.ts
@@ -18,6 +18,7 @@ import url from 'url';

 import { EventEmitter } from 'events';
 import { asLocator } from '../../utils/isomorphic/locatorGenerators';
+import { locatorOrSelectorAsSelector } from '../../utils/isomorphic/locatorParser';
 import { ManualPromise } from '../../utils/isomorphic/manualPromise';
 import { debug } from '../../utilsBundle';

@@ -438,10 +439,12 @@ export class Tab extends EventEmitter<TabEventsInterface> {
     await this._initializedPromise;
     return Promise.all(params.map(async param => {
       if (param.selector) {
-        const locator = this.page.locator(param.selector);
-        if (!await locator.isVisible())
-          throw new Error(`Selector ${param.selector} does not match any elements.`);
-        return { locator, resolved: asLocator('javascript', param.selector) };
+        const selector = locatorOrSelectorAsSelector('javascript', param.selector, this.context.config.testIdAttribute || 'data-testid');
+        const handle = await this.page.$(selector);
+        if (!handle)
+          throw new Error(`"${param.selector}" does not match any elements.`);
+        handle.dispose().catch(() => {});
+        return { locator: this.page.locator(selector), resolved: asLocator('javascript', selector) };
       } else {
         try {
           let locator = this.page.locator(`aria-ref=${param.ref}`);
diff --git a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
index 2d417d46789f4..33bc1bc3612f7 100644
--- a/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
+++ b/packages/playwright-core/src/tools/cli-client/skill/SKILL.md
@@ -222,17 +222,17 @@ playwright-cli snapshot
 playwright-cli click e15
 ```

-You can also use css or role selectors, for example when explicitly asked for it.
+You can also use css selectors or Playwright locators.

 ```bash
 # css selector
 playwright-cli click "#main > button.submit"

-# role selector
-playwright-cli click "role=button[name=Submit]"
+# role locator
+playwright-cli click "getByRole('button', { name: 'Submit' })"

-# chaining css and role selectors
-playwright-cli click "#footer >> role=button[name=Submit]"
+# test id
+playwright-cli click "getByTestId('submit-button')"
 ```

 ## Browser Sessions

PATCH

echo "Patch applied successfully."
