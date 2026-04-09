#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if ! grep -q "Code redemption coming soon" apps/studio/pages/redeem.tsx 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

echo "Applying patch..."

# Create the patch file
patch_file=$(mktemp)
cat > "$patch_file" << 'ENDPATCH'
--- a/apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx
+++ b/apps/studio/components/interfaces/Organization/BillingSettings/CreditCodeRedemption.tsx
@@ -1,7 +1,6 @@
 import HCaptcha from '@hcaptcha/react-hcaptcha'
 import { zodResolver } from '@hookform/resolvers/zod'
 import { PermissionAction } from '@supabase/shared-types/out/constants'
-import { useFlag } from 'common'
 import { Calendar, PartyPopper } from 'lucide-react'
 import Link from 'next/link'
 import { useRouter } from 'next/router'
@@ -53,7 +52,6 @@ export const CreditCodeRedemption = ({
   onClose?: () => void
 }) => {
   const router = useRouter()
-  const redeemCodeEnabled = useFlag('redeemCodeEnabled')
   const [codeRedemptionModalVisible, setCodeRedemptionModalVisible] = useState(
     modalVisible || false
   )
@@ -147,8 +145,6 @@ export const CreditCodeRedemption = ({
     }
   }, [codeRedemptionModalVisible, initHcaptchaRef])

-  if (!redeemCodeEnabled) return null
-
   return (
     <Dialog open={codeRedemptionModalVisible} onOpenChange={onCodeRedemptionDialogVisibilityChange}>
       {!modalVisible && (
--- a/apps/studio/pages/redeem.tsx
+++ b/apps/studio/pages/redeem.tsx
@@ -1,4 +1,4 @@
-import { FeatureFlagContext, useFlag } from 'common'
+import { FeatureFlagContext } from 'common'
 import Link from 'next/link'
 import { useContext, useState } from 'react'
 import { Button } from 'ui'
@@ -19,7 +19,6 @@ import { useProfile } from '@/lib/profile'
 import type { NextPageWithLayout } from '@/types'

 const RedeemCreditsContent = () => {
-  const redeemCodeEnabled = useFlag('redeemCodeEnabled')
   const { isLoading: isLoadingProfile } = useProfile()
   const { hasLoaded } = useContext(FeatureFlagContext)

@@ -72,7 +71,7 @@ const RedeemCreditsContent = () => {
             <ShimmeringLoader className="w-full h-[70px]" />
             <ShimmeringLoader className="w-full h-[70px]" />
           </>
-        ) : redeemCodeEnabled ? (
+        ) : (
           organizations?.map((org) => (
             <OrganizationCard
               key={org.id}
@@ -81,8 +80,6 @@ const RedeemCreditsContent = () => {
               onClick={() => setSelectedOrg(org.slug)}
             />
           ))
-        ) : (
-          <Admonition type="note" title="Code redemption coming soon" />
         )}
       </div>

ENDPATCH

# Apply the patch
git apply "$patch_file"
rm -f "$patch_file"

echo "Patch applied successfully."
