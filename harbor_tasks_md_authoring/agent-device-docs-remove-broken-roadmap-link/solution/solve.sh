#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agent-device

# Idempotency guard
if grep -qF "skills/agent-device/SKILL.md" "skills/agent-device/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/agent-device/SKILL.md b/skills/agent-device/SKILL.md
@@ -158,7 +158,3 @@ agent-device apps --platform android --user-installed
 - [references/permissions.md](references/permissions.md)
 - [references/video-recording.md](references/video-recording.md)
 - [references/coordinate-system.md](references/coordinate-system.md)
-
-## Missing features roadmap (high level)
-
-See [references/missing-features.md](references/missing-features.md) for planned parity with agent-browser.
PATCH

echo "Gold patch applied."
