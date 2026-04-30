#!/usr/bin/env bash
set -euo pipefail

cd /workspace/n8n

# Idempotency guard
if grep -qF "must be the **exact** Unix millisecond timestamp at the time of creation \u2014 do" "packages/@n8n/db/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/@n8n/db/AGENTS.md b/packages/@n8n/db/AGENTS.md
@@ -2,6 +2,13 @@
 
 Extra information specific to the `@n8n/db` package.
 
+## Creating Migrations
+
+Migration files are named `{TIMESTAMP}-{DescriptiveName}.ts`. The timestamp
+must be the **exact** Unix millisecond timestamp at the time of creation — do
+not round or fabricate a value. Use `Date.now()` in a Node REPL or
+`date +%s%3N` in a shell (GNU `date`) to generate it.
+
 ## Migration DSL
 
 ### UUID Primary Keys
PATCH

echo "Gold patch applied."
