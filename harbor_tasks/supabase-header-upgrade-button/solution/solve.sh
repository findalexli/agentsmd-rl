#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if grep -q 'HeaderUpgradeCtaClickedEvent' packages/common/telemetry-constants.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/apps/studio/components/layouts/Navigation/LayoutHeader/HeaderUpgradeButton.tsx b/apps/studio/components/layouts/Navigation/LayoutHeader/HeaderUpgradeButton.tsx
new file mode 100644
index 0000000000000..f7f833d716d39
--- /dev/null
+++ b/apps/studio/components/layouts/Navigation/LayoutHeader/HeaderUpgradeButton.tsx
@@ -0,0 +1,35 @@
+import { UpgradePlanButton } from '@/components/ui/UpgradePlanButton'
+import { useSelectedOrganizationQuery } from '@/hooks/misc/useSelectedOrganization'
+import { useTrackExperimentExposure } from '@/hooks/misc/useTrackExperimentExposure'
+import { usePHFlag } from '@/hooks/ui/useFlag'
+import { useTrack } from '@/lib/telemetry/track'
+
+const EXPERIMENT_ID = 'headerUpgradeCta'
+type HeaderUpgradeCtaVariant = 'control' | 'test'
+
+interface HeaderUpgradeButtonProps {
+  className?: string
+}
+
+export const HeaderUpgradeButton = ({ className }: HeaderUpgradeButtonProps) => {
+  const track = useTrack()
+  const { data: organization } = useSelectedOrganizationQuery()
+  const flagValue = usePHFlag<HeaderUpgradeCtaVariant | false>(EXPERIMENT_ID)
+
+  const isFreePlan = organization?.plan?.id === 'free'
+  const isInExperiment = flagValue === 'control' || flagValue === 'test'
+  const showButton = flagValue === 'test'
+
+  // Track experiment exposure for all free-plan users in the experiment (both control and test)
+  const variant = isFreePlan && isInExperiment ? (flagValue as string) : undefined
+  useTrackExperimentExposure(EXPERIMENT_ID, variant)
+
+  if (!isFreePlan) return null
+  if (!showButton) return null
+
+  const handleClick = () => {
+    track('header_upgrade_cta_clicked')
+  }
+
+  return <UpgradePlanButton source={EXPERIMENT_ID} className={className} onClick={handleClick} />
+}
diff --git a/apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx b/apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx
index 44ea0d757fc43..fa775bd1aa0d7 100644
--- a/apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx
+++ b/apps/studio/components/layouts/Navigation/LayoutHeader/LayoutHeader.tsx
@@ -11,6 +11,7 @@ import { CommandMenuTriggerInput } from 'ui-patterns'

 import { BreadcrumbsView } from './BreadcrumbsView'
 import { FeedbackDropdown } from './FeedbackDropdown/FeedbackDropdown'
+import { HeaderUpgradeButton } from './HeaderUpgradeButton'
 import { HomeIcon } from './HomeIcon'
 import { LocalVersionPopover } from './LocalVersionPopover'
 import { MergeRequestButton } from './MergeRequestButton'
@@ -253,6 +254,7 @@ export const LayoutHeader = ({
                     )}
                   </AnimatePresence>
                 </div>
+                <HeaderUpgradeButton className="hidden md:flex" />
                 <UserDropdown triggerClassName="hidden md:flex" />
               </>
             ) : (
diff --git a/apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx b/apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx
index e913295d49bdb..6c2949f83fff6 100644
--- a/apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx
+++ b/apps/studio/components/layouts/Navigation/NavigationBar/MobileNavigationBar.tsx
@@ -5,6 +5,7 @@ import { useState } from 'react'
 import { Button, cn } from 'ui'
 import { CommandMenuTrigger, MobileSheetNav } from 'ui-patterns'

+import { HeaderUpgradeButton } from '../LayoutHeader/HeaderUpgradeButton'
 import { HomeIcon } from '../LayoutHeader/HomeIcon'
 import { useMobileSheet } from './MobileSheetContext'
 import { OrgSelector } from './OrgSelector'
@@ -91,6 +92,7 @@ const MobileNavigationBar = ({
               </button>
             </CommandMenuTrigger>
           )}
+          {IS_PLATFORM && <HeaderUpgradeButton />}
           {IS_PLATFORM ? <UserDropdown /> : <LocalDropdown />}
           {!hideMobileMenu && (
             <Button
diff --git a/apps/studio/components/ui/UpgradePlanButton.tsx b/apps/studio/components/ui/UpgradePlanButton.tsx
index b5d87a2ab292f..1366da87a9cb1 100644
--- a/apps/studio/components/ui/UpgradePlanButton.tsx
+++ b/apps/studio/components/ui/UpgradePlanButton.tsx
@@ -25,6 +25,7 @@ interface UpgradePlanButtonProps {
   disabled?: boolean
   className?: string
   slug?: string
+  onClick?: () => void
 }

 /**
@@ -42,6 +43,7 @@ export const UpgradePlanButton = ({
   children,
   className,
   slug: slugParam,
+  onClick,
 }: PropsWithChildren<UpgradePlanButtonProps>) => {
   const { ref } = useParams()
   const { data: organization } = useSelectedOrganizationQuery()
@@ -120,7 +122,7 @@ export const UpgradePlanButton = ({
   }

   return (
-    <Button asChild type={variant} disabled={disabled} className={className}>
+    <Button asChild type={variant} disabled={disabled} className={className} onClick={onClick}>
       {link}
     </Button>
   )
diff --git a/packages/common/telemetry-constants.ts b/packages/common/telemetry-constants.ts
index ded331b54fef9..f17511275bb82 100644
--- a/packages/common/telemetry-constants.ts
+++ b/packages/common/telemetry-constants.ts
@@ -3021,6 +3021,18 @@ export interface PricingPageExperimentExposedEvent {
   }
 }

+/**
+ * User clicked the "Upgrade to Pro" CTA in the dashboard header.
+ * GROWTH-615: always-visible upgrade button in dashboard header for free-plan users.
+ *
+ * @group Events
+ * @source studio
+ */
+export interface HeaderUpgradeCtaClickedEvent {
+  action: 'header_upgrade_cta_clicked'
+  groups: Omit<TelemetryGroups, 'project'>
+}
+
 /**
  * @hidden
  */
@@ -3190,3 +3202,4 @@ export type TelemetryEvent =
   | FreeMicroUpgradeBannerDismissedEvent
   | FreeMicroUpgradeBannerCtaClickedEvent
   | PricingPageExperimentExposedEvent
+  | HeaderUpgradeCtaClickedEvent

PATCH

echo "Patch applied successfully."
