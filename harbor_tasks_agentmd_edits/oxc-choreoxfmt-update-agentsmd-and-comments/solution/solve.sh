#!/usr/bin/env bash
set -euo pipefail

cd /workspace/oxc

# Idempotent: skip if already applied
if grep -q "To compare formatting output with Prettier:" apps/oxfmt/AGENTS.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
From ff8422ab18601112251effdfcbec533c7949c02e Mon Sep 17 00:00:00 2001
From: leaysgur <6259812+leaysgur@users.noreply.github.com>
Date: Mon, 23 Mar 2026 01:36:27 +0000
Subject: [PATCH] chore(oxfmt): Update AGENTS.md (#20637)

---
 apps/oxfmt/AGENTS.md | 9 +++++++++
 1 file changed, 9 insertions(+)

diff --git a/apps/oxfmt/AGENTS.md b/apps/oxfmt/AGENTS.md
index fda4e4b40859e..6ec907df699e1 100644
--- a/apps/oxfmt/AGENTS.md
+++ b/apps/oxfmt/AGENTS.md
@@ -69,6 +69,15 @@ OXC_LOG=debug node ./dist/cli.js --threads=1 <file>

 NOTE: `pnpm build-test` combines `pnpm build-js` and `pnpm build-napi`, so you don't need to run them separately.

+To compare formatting output with Prettier:
+
+```sh
+# Use a shared config file (e.g., fmt.json) because oxfmt and Prettier have different default printWidth
+# Example fmt.json: { "printWidth": 80 }
+cat <file> | node ./dist/cli.js --config=fmt.json --stdin-filepath=<file>
+npx prettier --config=fmt.json <file>
+```
+
 ## Test Organization (`test/` directory)

 Tests are organized by domain and colocated with strict structural rules.

PATCH

echo "Patch applied successfully."
