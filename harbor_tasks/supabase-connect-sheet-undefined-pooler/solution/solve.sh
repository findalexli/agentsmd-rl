#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if grep -q 'connectionStringPooler?\\.ipv4SupportedForDedicatedPooler' apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the gold patch
git apply - <<'PATCH'
diff --git a/apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx b/apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx
index 1111111..2222222 100644
--- a/apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx
+++ b/apps/studio/components/interfaces/ConnectSheet/content/steps/direct-connection/content.tsx
@@ -14,7 +14,10 @@ import {
   type ConnectionStringMethod,
   type DatabaseConnectionType,
 } from '@/components/interfaces/ConnectSheet/Connect.constants'
-import type { StepContentProps } from '@/components/interfaces/ConnectSheet/Connect.types'
+import type {
+  ConnectionStringPooler,
+  StepContentProps,
+} from '@/components/interfaces/ConnectSheet/Connect.types'
 import { ConnectionParameters } from '@/components/interfaces/ConnectSheet/ConnectionParameters'
 import {
   buildConnectionParameters,
@@ -134,9 +137,9 @@ function DirectConnectionContent({ state }: StepContentProps) {
   const useSharedPooler = Boolean(state.useSharedPooler)

   const connectionStrings = useConnectionStringDatabases()
-  const connectionStringPooler =
+  const connectionStringPooler: ConnectionStringPooler | undefined =
     connectionStrings[connectionSource as keyof typeof connectionStrings]
-  const hasIPv4Addon = connectionStringPooler.ipv4SupportedForDedicatedPooler
+  const hasIPv4Addon = connectionStringPooler?.ipv4SupportedForDedicatedPooler ?? false

   // Determine which connection string to use
   const resolvedConnectionString = useMemo(

PATCH

echo "Patch applied successfully."
