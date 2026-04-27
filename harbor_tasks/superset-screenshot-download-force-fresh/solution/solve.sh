#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

TARGET="superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts"

# Idempotency check: distinctive line introduced by the gold patch.
if grep -q "rison.encode({ force: true })" "$TARGET"; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts b/superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts
index df494bad20a5..7610c18daa12 100644
--- a/superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts
+++ b/superset-frontend/src/dashboard/hooks/useDownloadScreenshot.ts
@@ -20,6 +20,7 @@ import { useCallback, useEffect, useRef } from 'react';
 import { useSelector } from 'react-redux';
 import { useToasts } from 'src/components/MessageToasts/withToasts';
 import { last } from 'lodash';
+import rison from 'rison';
 import contentDisposition from 'content-disposition';
 import { t } from '@apache-superset/core/translation';
 import { SupersetClient, SupersetApiError } from '@superset-ui/core';
@@ -145,7 +146,7 @@ export const useDownloadScreenshot = (
       };

       SupersetClient.post({
-        endpoint: `/api/v1/dashboard/${dashboardId}/cache_dashboard_screenshot/`,
+        endpoint: `/api/v1/dashboard/${dashboardId}/cache_dashboard_screenshot/?q=${rison.encode({ force: true })}`,
         jsonPayload: {
           anchor,
           activeTabs,
PATCH

echo "Patch applied."
