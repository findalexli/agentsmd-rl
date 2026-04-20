#!/bin/bash
set -e

cd /workspace/supabase-project

# Apply the fix: remove Math.round from currency calculations in SubscriptionPlanUpdateDialog.tsx
# The bug: Math.round() was stripping decimal precision from currency values in subscription preview
# The fix: Pass raw sum directly to formatCurrency() which handles 2 decimal places via Intl.NumberFormat

cat > /tmp/fix.patch <<'PATCH'
diff --git a/apps/studio/components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx b/apps/studio/components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx
index d94076756b3c6..ccf817158c6ad 100644
--- a/apps/studio/components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx
+++ b/apps/studio/components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx
@@ -529,11 +529,9 @@ export const SubscriptionPlanUpdateDialog = ({
                                         translate="no"
                                       >
                                         {formatCurrency(
-                                          Math.round(
-                                            subscriptionPreview?.breakdown?.reduce(
-                                              (prev, cur) => prev + cur.total_price,
-                                              0
-                                            ) ?? 0
+                                          subscriptionPreview?.breakdown?.reduce(
+                                            (prev, cur) => prev + cur.total_price,
+                                            0
                                           ) ?? 0
                                         )}
                                       </TableCell>
@@ -547,12 +545,10 @@ export const SubscriptionPlanUpdateDialog = ({
                       </div>
                       <div className="py-2 pr-0 text-right" translate="no">
                         {formatCurrency(
-                          Math.round(
-                            subscriptionPreview?.breakdown.reduce(
-                              (prev: number, cur) => prev + cur.total_price,
-                              0
-                            ) ?? 0
-                          )
+                          subscriptionPreview?.breakdown.reduce(
+                            (prev: number, cur) => prev + cur.total_price,
+                            0
+                          ) ?? 0
                         )}
                       </div>
                     </div>
PATCH

git apply /tmp/fix.patch

# Verify the change applied - grep for the distinctive pattern (no Math.round around reduce)
grep -q "subscriptionPreview?.breakdown?.reduce" apps/studio/components/interfaces/Organization/BillingSettings/Subscription/SubscriptionPlanUpdateDialog.tsx && echo "Patch applied successfully"