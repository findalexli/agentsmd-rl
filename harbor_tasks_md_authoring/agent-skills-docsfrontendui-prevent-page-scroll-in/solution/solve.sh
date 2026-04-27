#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-skills

# Idempotency guard
if grep -qF "if (e.key === ' ') e.preventDefault();" "skills/frontend-ui-engineering/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/frontend-ui-engineering/SKILL.md b/skills/frontend-ui-engineering/SKILL.md
@@ -173,7 +173,13 @@ Every component must meet these standards:
 <button onClick={handleClick}>Click me</button>        // ✓ Focusable by default
 <div onClick={handleClick}>Click me</div>               // ✗ Not focusable
 <div role="button" tabIndex={0} onClick={handleClick}    // ✓ But prefer <button>
-     onKeyDown={e => (e.key === 'Enter' || e.key === ' ') && handleClick()}>
+     onKeyDown={e => {
+       if (e.key === 'Enter') handleClick();
+       if (e.key === ' ') e.preventDefault();
+     }}
+     onKeyUp={e => {
+       if (e.key === ' ') handleClick();
+     }}>
   Click me
 </div>
 ```
PATCH

echo "Gold patch applied."
