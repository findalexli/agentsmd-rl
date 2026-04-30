#!/bin/bash
set -euo pipefail

cd /workspace/civitai

# Idempotency check - skip if patch already applied
if grep -q 'getDownloadUrl(file\.url, file\.name)' 'src/pages/api/download/attachments/[fileId].ts'; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch to the attachment endpoint
patch -p1 <<'PATCH'
diff --git a/src/pages/api/download/attachments/[fileId].ts b/src/pages/api/download/attachments/[fileId].ts
index cff9fb62ab..39bd81ea48 100644
--- a/src/pages/api/download/attachments/[fileId].ts
+++ b/src/pages/api/download/attachments/[fileId].ts
@@ -5,7 +5,7 @@ import * as z from 'zod';
 import { env } from '~/env/server';
 import { dbRead } from '~/server/db/client';
 import { getServerAuthSession } from '~/server/auth/get-server-auth-session';
-import { resolveDownloadUrl } from '~/utils/delivery-worker';
+import { getDownloadUrl } from '~/utils/delivery-worker';
 import { getLoginLink } from '~/utils/login-helpers';
 import { getFileWithPermission } from '~/server/services/file.service';
 import { Tracker } from '~/server/clickhouse/client';
@@ -106,7 +106,11 @@ export default PublicEndpoint(
     // }

     try {
-      const { url } = await resolveDownloadUrl(fileId, file.url, file.name);
+      // Use delivery worker directly — File table records are not synced to
+      // the storage resolver's file_locations table (which only tracks ModelFile).
+      // Using resolveDownloadUrl here would cause the storage resolver to match
+      // against a ModelFile with the same ID, serving the wrong file content.
+      const { url } = await getDownloadUrl(file.url, file.name);

       const tracker = new Tracker(req, res);
       tracker
PATCH

# Update CLAUDE.md to document the download URL resolution pattern
# This aligns with the repo's convention of documenting API patterns
if ! grep -q 'attachment.*download.*getDownloadUrl\|getDownloadUrl.*attachment' CLAUDE.md 2>/dev/null; then
  cat >> CLAUDE.md <<'CLAUDE_PATCH'

### Download URL Resolution

- Use `getDownloadUrl(file.url, file.name)` for non-model file downloads (article attachments, bounty files)
- Use `resolveDownloadUrl(fileId, file.url, file.name)` only for model file downloads where storage resolver tracking is needed
- The storage resolver's `file_locations` table only tracks `ModelFile` records — never pass a generic `File.id` to `resolveDownloadUrl`
- Use type imports when possible: `import type { ... } from '...'` for type-only imports
- Never commit secrets or API keys; use environment variables
CLAUDE_PATCH
fi
