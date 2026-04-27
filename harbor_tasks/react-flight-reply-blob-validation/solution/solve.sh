#!/usr/bin/env bash
# Apply the gold patch idempotently.
set -euo pipefail

cd /workspace/react

# Idempotency guard: a distinctive line from the gold patch.  If it is
# already present we have nothing to do.
if grep -q "Referenced Blob is not a Blob." \
       packages/react-server/src/ReactFlightReplyServer.js; then
    echo "Gold patch already applied, skipping."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js b/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js
index 77ae692e9800..b569f02390f4 100644
--- a/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js
+++ b/packages/react-server-dom-webpack/src/__tests__/ReactFlightDOMReply-test.js
@@ -744,4 +744,17 @@ describe('ReactFlightDOMReply', () => {
     // has closed but that's a bug in both ReactFlightReplyServer and ReactFlightClient.
     // It just halts in this case.
   });
+
+  it('cannot deserialize a Blob reference backed by a string', async () => {
+    const formData = new FormData();
+    formData.set('1', '-'.repeat(50000));
+    formData.set('0', JSON.stringify(['$B1']));
+    let error;
+    try {
+      await ReactServerDOMServer.decodeReply(formData, webpackServerMap);
+    } catch (x) {
+      error = x;
+    }
+    expect(error.message).toContain('Referenced Blob is not a Blob.');
+  });
 });
diff --git a/packages/react-server/src/ReactFlightReplyServer.js b/packages/react-server/src/ReactFlightReplyServer.js
index 21ff08a8aa02..5f58e918f3e8 100644
--- a/packages/react-server/src/ReactFlightReplyServer.js
+++ b/packages/react-server/src/ReactFlightReplyServer.js
@@ -1806,7 +1806,10 @@ function parseModelString(
         const blobKey = prefix + id;
         // We should have this backingEntry in the store already because we emitted
         // it before referencing it. It should be a Blob.
-        const backingEntry: Blob = (response._formData.get(blobKey): any);
+        const backingEntry = response._formData.get(blobKey);
+        if (!(backingEntry instanceof Blob)) {
+          throw new Error('Referenced Blob is not a Blob.');
+        }
         return backingEntry;
       }
       case 'R': {
diff --git a/scripts/error-codes/codes.json b/scripts/error-codes/codes.json
index 09e60d8b257b..36cba98f5a9a 100644
--- a/scripts/error-codes/codes.json
+++ b/scripts/error-codes/codes.json
@@ -566,5 +566,6 @@
   "578": "Already initialized Iterator.",
   "579": "Invalid data for bytes stream.",
   "580": "Server Function has too many bound arguments. Received %s but the limit is %s.",
-  "581": "BigInt is too large. Received %s digits but the limit is %s."
+  "581": "BigInt is too large. Received %s digits but the limit is %s.",
+  "582": "Referenced Blob is not a Blob."
 }
PATCH

echo "Gold patch applied."
