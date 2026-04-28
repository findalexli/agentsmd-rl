#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotency guard
if grep -qF "3. Do NOT use bare specifiers when importing dependencies. If you need to use an" "apps/ui-library/registry/default/ai-editor-rules/writing-supabase-edge-functions.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/apps/ui-library/registry/default/ai-editor-rules/writing-supabase-edge-functions.mdc b/apps/ui-library/registry/default/ai-editor-rules/writing-supabase-edge-functions.mdc
@@ -11,7 +11,7 @@ You're an expert in writing TypeScript and Deno JavaScript runtime. Generate **h
 
 1. Try to use Web APIs and Deno’s core APIs instead of external dependencies (eg: use fetch instead of Axios, use WebSockets API instead of node-ws)
 2. If you are reusing utility methods between Edge Functions, add them to `supabase/functions/_shared` and import using a relative path. Do NOT have cross dependencies between Edge Functions.
-3. Do NOT use bare specifiers when importing dependecnies. If you need to use an external dependency, make sure it's prefixed with either `npm:` or `jsr:`. For example, `@supabase/supabase-js` should be written as `npm:@supabase/supabase-js`.
+3. Do NOT use bare specifiers when importing dependencies. If you need to use an external dependency, make sure it's prefixed with either `npm:` or `jsr:`. For example, `@supabase/supabase-js` should be written as `npm:@supabase/supabase-js`.
 4. For external imports, always define a version. For example, `npm:@express` should be written as `npm:express@4.18.2`.
 5. For external dependencies, importing via `npm:` and `jsr:` is preferred. Minimize the use of imports from @`deno.land/x` , `esm.sh` and @`unpkg.com` . If you have a package from one of those CDNs, you can replace the CDN hostname with `npm:` specifier.
 6. You can also use Node built-in APIs. You will need to import them using `node:` specifier. For example, to import Node process: `import process from "node:process". Use Node APIs when you find gaps in Deno APIs.
PATCH

echo "Gold patch applied."
