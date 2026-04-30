#!/usr/bin/env bash
set -euo pipefail

cd /workspace/snipe-it

# Idempotency guard
if grep -qF "- Use Form Requests for validation. The request class should utilize the rules s" ".github/copilot-instructions.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/copilot-instructions.md b/.github/copilot-instructions.md
@@ -30,18 +30,14 @@ These instructions guide Copilot to generate code that aligns with modern Larave
     - `app/Http/Requests` - Form request validation
     - `app/Http/Resources` - API resource responses
     - `app/Enums` - Enums
-    - `app/Services` - Business logic
-    - `app/Data` - Data Transfer Objects (DTOs)
     - `app/Actions` - Single-responsibility action classes
     - `app/Policies` - Authorization logic
 
 - Controllers must:
-    - Be thin.
     - Use dependency injection.
-    - Use Form Requests for validation.
+    - Use Form Requests for validation. The request class should utilize the rules set on the model.
     - Return typed responses (e.g., `JsonResponse`).
-    - Use Resource classes for API responses.
-
+    - Use Transformers for API responses.
 
 ## ✅ Eloquent ORM & Database
 
@@ -56,7 +52,7 @@ These instructions guide Copilot to generate code that aligns with modern Larave
 
 ## ✅ API Development
 
-- Use **API Resource classes** for consistent and structured JSON responses.
+- Use **Transformer classes** for consistent and structured JSON responses.
 - Apply **route model binding** where possible.
 - Use Form Requests for input validation.
 
PATCH

echo "Gold patch applied."
