#!/usr/bin/env bash
set -euo pipefail
cd /workspace/openclaw

# Apply the main fix to provider.lifecycle.ts
git apply - <<'PATCH'
diff --git a/extensions/discord/src/monitor/provider.lifecycle.ts b/extensions/discord/src/monitor/provider.lifecycle.ts
index 5f455b61b901..5b61ed2b4836 100644
--- a/extensions/discord/src/monitor/provider.lifecycle.ts
+++ b/extensions/discord/src/monitor/provider.lifecycle.ts
@@ -82,13 +82,10 @@ export async function runDiscordGatewayLifecycle(params: {
       if (decision !== "stop") {
         return "continue";
       }
-      // Don't throw for expected shutdown events — intentional disconnect
-      // (reconnect-exhausted with maxAttempts=0) and disallowed-intents are
-      // both handled without crashing the provider.
-      if (
-        event.type === "disallowed-intents" ||
-        (lifecycleStopping && event.type === "reconnect-exhausted")
-      ) {
+      // Don't throw for expected shutdown events. `reconnect-exhausted` can be
+      // queued before teardown flips `lifecycleStopping`, so treat it as a
+      // graceful stop here and let the health monitor own reconnect behavior.
+      if (event.type === "disallowed-intents" || event.type === "reconnect-exhausted") {
         return "stop";
       }
       throw event.err;
PATCH

# Update the test to expect the new (fixed) behavior using Python
python3 << 'PYEOF'
import re

test_file = "extensions/discord/src/monitor/provider.lifecycle.test.ts"
with open(test_file, "r") as f:
    content = f.read()

# Find and replace the test that expects old buggy behavior
old_test_start = 'it("does not suppress reconnect-exhausted already queued before shutdown"'
new_test_start = 'it("gracefully handles reconnect-exhausted already queued before shutdown"'

# Replace test name
content = content.replace(old_test_start, new_test_start)

# Find and replace the specific assertion that expects the error to be thrown
# Old: await expect(lifecyclePromise).rejects.toThrow(
# New: await expect(lifecyclePromise).resolves.toBeUndefined();
old_assertion = '''await expect(lifecyclePromise).rejects.toThrow(
      "Max reconnect attempts (0) reached after code 1005",
    );'''

new_assertion = '''// After the fix, reconnect-exhausted is handled gracefully (returns "stop")
    // rather than throwing, so the lifecycle resolves normally.
    await expect(lifecyclePromise).resolves.toBeUndefined();'''

content = content.replace(old_assertion, new_assertion)

# Replace the runtimeError expectation
old_error_check = '''expect(runtimeLog).not.toHaveBeenCalledWith(
      expect.stringContaining("ignoring expected reconnect-exhausted during shutdown"),
    );
    expect(runtimeError).toHaveBeenCalledWith(expect.stringContaining("Max reconnect attempts"));'''

new_error_check = '''// After the fix, no error is thrown for reconnect-exhausted
    expect(runtimeError).not.toHaveBeenCalledWith(
      expect.stringContaining("Max reconnect attempts"),
    );'''

content = content.replace(old_error_check, new_error_check)

with open(test_file, "w") as f:
    f.write(content)

print("Updated test file successfully")
PYEOF
