#!/usr/bin/env bash
set -euo pipefail

cd /repo

TARGET="src/bun.js/bindings/BunString.cpp"

# Idempotency: check if RETURN_IF_EXCEPTION already present between toJSNewlyCreated and jsCast in BunString__toJSDOMURL
if python3 -c "
import sys
with open('$TARGET') as f:
    content = f.read()
idx = content.find('BunString__toJSDOMURL')
if idx < 0:
    sys.exit(1)
region = content[idx:idx+600]
jsn_idx = region.find('toJSNewlyCreated')
jsc_idx = region.find('jsCast')
if jsn_idx < 0 or jsc_idx < 0:
    sys.exit(1)
between = region[jsn_idx:jsc_idx]
if 'RETURN_IF_EXCEPTION' in between or 'throwScope' in between.split('\\n', 1)[-1]:
    sys.exit(0)
sys.exit(1)
" 2>/dev/null; then
  echo "Fix already applied."
  exit 0
fi

git apply - <<'PATCH'
diff --git a/src/bun.js/bindings/BunString.cpp b/src/bun.js/bindings/BunString.cpp
index 008485671cf..15c7e7c67bf 100644
--- a/src/bun.js/bindings/BunString.cpp
+++ b/src/bun.js/bindings/BunString.cpp
@@ -576,6 +576,7 @@ extern "C" JSC::EncodedJSValue BunString__toJSDOMURL(JSC::JSGlobalObject* lexica

     auto object = WebCore::DOMURL::create(str, String());
     auto jsValue = WebCore::toJSNewlyCreated<WebCore::IDLInterface<WebCore::DOMURL>>(*lexicalGlobalObject, globalObject, throwScope, WTF::move(object));
+    RETURN_IF_EXCEPTION(throwScope, {});
     auto* jsDOMURL = jsCast<WebCore::JSDOMURL*>(jsValue.asCell());
     vm.heap.reportExtraMemoryAllocated(jsDOMURL, jsDOMURL->wrapped().memoryCostForGC());
     RELEASE_AND_RETURN(throwScope, JSC::JSValue::encode(jsValue));

PATCH

echo "Patch applied successfully."
