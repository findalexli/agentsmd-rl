#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if grep -q 'isMobile && (' apps/studio/components/layouts/DefaultLayout.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Use --whitespace=fix if patch has trailing whitespace issues
# IMPORTANT: patch content MUST end with a blank line before the PATCH delimiter
git apply - <<'PATCH'
diff --git a/apps/studio/components/layouts/DefaultLayout.tsx b/apps/studio/components/layouts/DefaultLayout.tsx
index 630f6fee100f7..42b9c00aff7b4 100644
--- a/apps/studio/components/layouts/DefaultLayout.tsx
+++ b/apps/studio/components/layouts/DefaultLayout.tsx
@@ -1,4 +1,4 @@
-import { LOCAL_STORAGE_KEYS, useParams } from 'common'
+import { LOCAL_STORAGE_KEYS, useBreakpoint, useParams } from 'common'
 import { useRouter } from 'next/router'
 import { PropsWithChildren, useEffect, useState } from 'react'
 import { ResizablePanel, ResizablePanelGroup, SidebarProvider } from 'ui'
@@ -57,6 +57,8 @@ export const DefaultLayout = ({

   useCheckLatestDeploy()

+  const isMobile = useBreakpoint('md')
+
   const contentMinSizePercentage = 50
   const contentMaxSizePercentage = 70

@@ -82,10 +84,12 @@ export const DefaultLayout = ({
                 {/* Top Banner */}
                 <AppBannerWrapper />
                 <div className="flex-shrink-0">
-                  <MobileNavigationBar
-                    hideMobileMenu={hideMobileMenu}
-                    backToDashboardURL={backToDashboardURL}
-                  />
+                  {isMobile && (
+                    <MobileNavigationBar
+                      hideMobileMenu={hideMobileMenu}
+                      backToDashboardURL={backToDashboardURL}
+                    />
+                  )}
                   <LayoutHeader headerTitle={headerTitle} backToDashboardURL={backToDashboardURL} />
                 </div>
                 {/* Main Content Area */}

PATCH

echo "Patch applied successfully."
