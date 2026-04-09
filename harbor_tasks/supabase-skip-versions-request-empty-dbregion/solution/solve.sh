#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied (check for the distinctive !!dbRegion pattern)
if grep -q '!!dbRegion' apps/studio/data/config/project-creation-postgres-versions-query.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/apps/studio/data/config/project-creation-postgres-versions-query.ts b/apps/studio/data/config/project-creation-postgres-versions-query.ts
index edb53b5305121..2b974a1d06f3b 100644
--- a/apps/studio/data/config/project-creation-postgres-versions-query.ts
+++ b/apps/studio/data/config/project-creation-postgres-versions-query.ts
@@ -48,10 +48,7 @@ export const useProjectCreationPostgresVersionsQuery = <TData = ProjectCreation
     queryFn: ({ signal }) =>
       getPostgresCreationVersions({ organizationSlug, cloudProvider, dbRegion }, signal),
     enabled:
-      enabled &&
-      typeof organizationSlug !== 'undefined' &&
-      organizationSlug !== '_' &&
-      typeof dbRegion !== 'undefined',
+      enabled && typeof organizationSlug !== 'undefined' && organizationSlug !== '_' && !!dbRegion,
     ...options,
   })
 }

PATCH

echo "Patch applied successfully."
