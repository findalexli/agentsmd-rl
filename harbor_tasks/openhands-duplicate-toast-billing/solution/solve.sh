#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already applied (idempotency check - look for amount extracted OUTSIDE useEffect)
# The fix extracts amount/sessionId before useEffect, not inside
if grep -B 3 "React.useEffect" frontend/src/routes/billing.tsx | grep -q "const amount = searchParams"; then
    echo "Fix already applied."
    exit 0
fi

# Apply only the fix patch (tests are already in the image)
cat <<'PATCH' | git apply -
diff --git a/frontend/src/routes/billing.tsx b/frontend/src/routes/billing.tsx
index abc..def 100644
--- a/frontend/src/routes/billing.tsx
+++ b/frontend/src/routes/billing.tsx
@@ -56,13 +56,11 @@ function BillingSettingsScreen() {
   const { hasPermission } = usePermission(me?.role ?? "member");
   const canAddCredits = !!me && hasPermission("add_credits");
   const checkoutStatus = searchParams.get("checkout");
+  const amount = searchParams.get("amount");
+  const sessionId = searchParams.get("session_id");

   React.useEffect(() => {
     if (checkoutStatus === "success") {
-      // Get purchase details from URL params
-      const amount = searchParams.get("amount");
-      const sessionId = searchParams.get("session_id");
-
       // Track credits purchased if we have the necessary data
       if (amount && sessionId) {
         trackCreditsPurchased({
@@ -78,7 +76,14 @@ function BillingSettingsScreen() {
       displayErrorToast(t(I18nKey.PAYMENT$CANCELLED));
       setSearchParams({});
     }
-  }, [checkoutStatus, searchParams, setSearchParams, t, trackCreditsPurchased]);
+  }, [
+    checkoutStatus,
+    amount,
+    sessionId,
+    setSearchParams,
+    t,
+    trackCreditsPurchased,
+  ]);

   return <PaymentForm isDisabled={!canAddCredits} />;
 }
PATCH

echo "Fix applied successfully!"
