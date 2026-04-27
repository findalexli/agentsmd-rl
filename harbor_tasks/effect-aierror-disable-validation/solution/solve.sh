#!/usr/bin/env bash
set -euo pipefail

cd /workspace/effect

PATCH_TARGET="packages/ai/ai/src/AiError.ts"
DISTINCTIVE='disableValidation: true'

# Idempotency: bail if the patch is already applied.
if grep -q "$DISTINCTIVE" "$PATCH_TARGET"; then
  echo "solution already applied to $PATCH_TARGET"
else
  git apply <<'PATCH'
diff --git a/packages/ai/ai/src/AiError.ts b/packages/ai/ai/src/AiError.ts
index a5ba22f4ab4..f87687ea291 100644
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
fi

# Drop in a changeset (AGENTS.md requires every PR to ship one).
CHANGESET_DIR=".changeset"
mkdir -p "$CHANGESET_DIR"
CHANGESET_FILE="$CHANGESET_DIR/oracle-disable-validation.md"
if [ ! -f "$CHANGESET_FILE" ] && ! grep -lq '@effect/ai' "$CHANGESET_DIR"/*.md 2>/dev/null; then
  cat > "$CHANGESET_FILE" <<'MD'
---
"@effect/ai": patch
---

Prevent schema validation when directly constructing an `AiError.HttpRequestError` / `AiError.HttpResponseError`
MD
fi

echo "solve.sh: done"
