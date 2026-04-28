#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rtk

# Idempotency guard
if grep -qF "- **Testing**: Validated on a production T3 Stack project" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -376,7 +376,7 @@ pub fn execute_with_filter(cmd: &str, args: &[&str]) -> Result<()> {
   - `rtk prisma`: Prisma CLI without ASCII art (88% reduction)
 - **Shared Infrastructure**: utils.rs module for package manager auto-detection
 - **Features**: Exit code preservation, error grouping, consistent formatting
-- **Testing**: Validated on production T3 Stack project (methode-aristote/app)
+- **Testing**: Validated on a production T3 Stack project
 
 ### Python & Go Support (2026-02-12)
 - **Python Commands**: 3 commands for Python development workflows
PATCH

echo "Gold patch applied."
