#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

# Idempotency: bail out if patch is already applied.
if grep -q "disableValidation: true" packages/ai/ai/src/AiError.ts; then
    echo "[solve.sh] gold patch already applied; nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/ai/ai/src/AiError.ts b/packages/ai/ai/src/AiError.ts
--- a/packages/ai/ai/src/AiError.ts
+++ b/packages/ai/ai/src/AiError.ts
@@ -241,7 +241,7 @@ export class HttpRequestError extends Schema.TaggedError<HttpRequestError>(
         url: error.request.url,
         urlParams: error.request.urlParams
       }
-    })
+    }, { disableValidation: true })
   }

   get message(): string {
@@ -413,7 +413,7 @@ export class HttpResponseError extends Schema.TaggedError<HttpResponseError>(
           status: error.response.status
         },
         body: Inspectable.format(body)
-      }))
+      }, { disableValidation: true }))
   }

   get message(): string {
PATCH

echo "[solve.sh] gold patch applied."
