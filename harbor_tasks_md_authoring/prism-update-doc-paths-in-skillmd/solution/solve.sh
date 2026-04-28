#!/usr/bin/env bash
set -euo pipefail

cd /workspace/prism

# Idempotency guard
if grep -qF "read vendor/prism-php/prism/docs/core-concepts/text-generation.md" "resources/boost/skills/developing-with-prism/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/resources/boost/skills/developing-with-prism/SKILL.md b/resources/boost/skills/developing-with-prism/SKILL.md
@@ -108,19 +108,19 @@ $response = Prism::text()
 
 1. **Read a specific doc file directly:**
    ```
-   read docs/core-concepts/text-generation.md
-   read docs/providers/openai.md
+   read vendor/prism-php/prism/docs/core-concepts/text-generation.md
+   read vendor/prism-php/prism/docs/providers/openai.md
    ```
 
 2. **Search for a topic across docs:**
    ```
-   grep "streaming" docs/
-   grep "withProviderOptions" docs/providers/
+   grep "streaming" vendor/prism-php/prism/docs/
+   grep "withProviderOptions" vendor/prism-php/prism/docs/providers/
    ```
 
 3. **Find all doc files:**
    ```
-   glob "docs/**/*.md"
+   glob "vendor/prism-php/prism/docs/**/*.md"
    ```
 
 ### Documentation Paths
PATCH

echo "Gold patch applied."
