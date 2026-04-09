#!/usr/bin/env bash
set -euo pipefail

cd /workspace/playwright

# Idempotent: skip if already applied
if grep -q "|| 'Global'" packages/dashboard/src/grid.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
git apply --whitespace=fix - <<'PATCH'
diff --git a/packages/dashboard/src/grid.tsx b/packages/dashboard/src/grid.tsx
index f3ea91090b49b..ef162d7cd15b3 100644
--- a/packages/dashboard/src/grid.tsx
+++ b/packages/dashboard/src/grid.tsx
@@ -56,9 +56,10 @@ export const Grid: React.FC<{ model: SessionModel }> = ({ model }) => {
       list.sort((a, b) => a.title.localeCompare(b.title));

     // Current workspace first, then alphabetical.
+    const currentWorkspace = clientInfo?.workspaceDir || 'Global';
     const entries = [...groups.entries()];
-    const current = entries.filter(([key]) => key === clientInfo?.workspaceDir);
-    const other = entries.filter(([key]) => key !== clientInfo?.workspaceDir).sort((a, b) => a[0].localeCompare(b[0]));
+    const current = entries.filter(([key]) => key === currentWorkspace);
+    const other = entries.filter(([key]) => key !== currentWorkspace).sort((a, b) => a[0].localeCompare(b[0]));
     return [...current, ...other];
   }, [sessions, clientInfo?.workspaceDir]);

diff --git a/packages/playwright-core/src/tools/dashboard/DEPS.list b/packages/playwright-core/src/tools/dashboard/DEPS.list
index 232118337c56c..84abdb0beef37 100644
--- a/packages/playwright-core/src/tools/dashboard/DEPS.list
+++ b/packages/playwright-core/src/tools/dashboard/DEPS.list
@@ -6,4 +6,5 @@
 ../../server/utils/
 ../../serverRegistry.ts
 ../../utils/
+../cli-client/registry.ts
 ../utils/
diff --git a/packages/playwright-core/src/tools/dashboard/dashboardApp.ts b/packages/playwright-core/src/tools/dashboard/dashboardApp.ts
index 1ea5a736e5ca7..32100a17e1c00 100644
--- a/packages/playwright-core/src/tools/dashboard/dashboardApp.ts
+++ b/packages/playwright-core/src/tools/dashboard/dashboardApp.ts
@@ -27,6 +27,7 @@ import { findChromiumChannelBestEffort, registryDirectory } from '../../server/r
 import { CDPConnection, DashboardConnection } from './dashboardController';
 import { serverRegistry } from '../../serverRegistry';
 import { connectToBrowserAcrossVersions } from '../utils/connect';
+import { createClientInfo } from '../cli-client/registry';

 import type * as api from '../../..';
 import type { SessionStatus } from '../../../../dashboard/src/sessionModel';
@@ -85,7 +86,8 @@ async function handleApiRequest(httpServer: HttpServer, request: http.IncomingMe

   if (apiPath === '/api/sessions/list' && request.method === 'GET') {
     const sessions = await loadBrowserDescriptorSessions(httpServer.wsGuid()!);
-    sendJSON(response, { sessions });
+    const clientInfo = createClientInfo();
+    sendJSON(response, { sessions, clientInfo });
     return;
   }

PATCH

echo "Patch applied successfully."
