#!/usr/bin/env bash
set -euo pipefail

cd /workspace/astro

# Idempotency guard
if grep -qF "- Root: [/CONTRIBUTING.md](../../../CONTRIBUTING.md)" ".agents/skills/astro-developer/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/astro-developer/SKILL.md b/.agents/skills/astro-developer/SKILL.md
@@ -125,8 +125,8 @@ See [testing.md](testing.md) for complete patterns and examples.
 
 ## Related Documentation
 
-- Root: [/AGENTS.md](/Users/ema/www/withastro/astro/AGENTS.md)
-- Root: [/CONTRIBUTING.md](/Users/ema/www/withastro/astro/CONTRIBUTING.md)
+- Root: [/AGENTS.md](../../../AGENTS.md)
+- Root: [/CONTRIBUTING.md](../../../CONTRIBUTING.md)
 - Astro docs: https://docs.astro.build/llms.txt
 - Package: packages/astro/src/core/README.md
 - Build plugins: packages/astro/src/core/build/plugins/README.md
PATCH

echo "Gold patch applied."
