#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied (check for the hook import)
if grep -q "useSelectedOrganizationQuery" apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx b/apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx
index 79006d1ab0a33..8411f59f79a11 100644
--- a/apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx
+++ b/apps/studio/components/interfaces/Billing/NoProjectsOnPaidOrgInfo.tsx
@@ -2,15 +2,12 @@ import Link from 'next/link'
 import { Admonition } from 'ui-patterns'

 import { useOrgProjectsInfiniteQuery } from '@/data/projects/org-projects-infinite-query'
-import type { Organization } from '@/types'
-
-interface NoProjectsOnPaidOrgInfoProps {
-  organization?: Organization
-}
+import { useSelectedOrganizationQuery } from '@/hooks/misc/useSelectedOrganization'

 const EXCLUDED_PLANS = ['free', 'platform', 'enterprise']

-export const NoProjectsOnPaidOrgInfo = ({ organization }: NoProjectsOnPaidOrgInfoProps) => {
+export const NoProjectsOnPaidOrgInfo = () => {
+  const { data: organization } = useSelectedOrganizationQuery()
   const isEligible = organization != null && !EXCLUDED_PLANS.includes(organization.plan.id ?? '')

   const { data } = useOrgProjectsInfiniteQuery(

PATCH

echo "Patch applied successfully."
