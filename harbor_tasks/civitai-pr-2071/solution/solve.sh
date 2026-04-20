#!/bin/bash
set -euo pipefail
cd /workspace/civitai_repo

# Apply the fix: bypass storage resolver for article attachment downloads
# The storage resolver's file_locations table only tracks ModelFile records,
# not File table records (article attachments, bounty files).
# When a File.id collided with a ModelFile.id, the resolver would return the
# wrong file content. Use getDownloadUrl directly instead.

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

# Verify the patch was applied
grep -q "getDownloadUrl" src/pages/api/download/attachments/[fileId].ts
