#!/bin/bash
set -e

cd /workspace/openhands

# Check if patch was already applied (idempotency check)
if grep -q "const amount = searchParams.get(\"amount\");" frontend/src/routes/billing.tsx; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/frontend/__tests__/routes/billing.test.tsx b/frontend/__tests__/routes/billing.test.tsx
index f4a943c2b97f..436192f9a0a3 100644
--- a/frontend/__tests__/routes/billing.test.tsx
+++ b/frontend/__tests__/routes/billing.test.tsx
@@ -25,10 +25,19 @@ vi.mock("react-i18next", async () => {
   };
 });

+// Mock toast handlers
+const mockDisplaySuccessToast = vi.fn();
+const mockDisplayErrorToast = vi.fn();
+vi.mock("#/utils/custom-toast-handlers", () => ({
+  displaySuccessToast: (...args: unknown[]) => mockDisplaySuccessToast(...args),
+  displayErrorToast: (...args: unknown[]) => mockDisplayErrorToast(...args),
+}));
+
 // Mock useTracking hook
+const mockTrackCreditsPurchased = vi.fn();
 vi.mock("#/hooks/use-tracking", () => ({
   useTracking: () => ({
-    trackCreditsPurchased: vi.fn(),
+    trackCreditsPurchased: mockTrackCreditsPurchased,
   }),
 }));

@@ -311,6 +320,77 @@ describe("Billing Route", () => {
     });
   });

+  describe("checkout success flow", () => {
+    beforeEach(() => {
+      mockUseBalance.mockReturnValue({
+        data: "150.00",
+        isLoading: false,
+      });
+    });
+
+    it("should display success toast exactly once and track credits on checkout success", async () => {
+      const RouterStub = createRoutesStub([
+        {
+          Component: BillingSettingsScreen,
+          path: "/settings/billing",
+        },
+      ]);
+
+      render(
+        <RouterStub
+          initialEntries={[
+            "/settings/billing?checkout=success&amount=25&session_id=sess_123",
+          ]}
+        />,
+        {
+          wrapper: ({ children }) => (
+            <QueryClientProvider client={mockQueryClient}>
+              {children}
+            </QueryClientProvider>
+          ),
+        },
+      );
+
+      await waitFor(() => {
+        expect(mockDisplaySuccessToast).toHaveBeenCalledTimes(1);
+      });
+
+      expect(mockTrackCreditsPurchased).toHaveBeenCalledTimes(1);
+      expect(mockTrackCreditsPurchased).toHaveBeenCalledWith({
+        amountUsd: 25,
+        stripeSessionId: "sess_123",
+      });
+    });
+
+    it("should display error toast exactly once on checkout cancel", async () => {
+      const RouterStub = createRoutesStub([
+        {
+          Component: BillingSettingsScreen,
+          path: "/settings/billing",
+        },
+      ]);
+
+      render(
+        <RouterStub
+          initialEntries={["/settings/billing?checkout=cancel"]}
+        />,
+        {
+          wrapper: ({ children }) => (
+            <QueryClientProvider client={mockQueryClient}>
+              {children}
+            </QueryClientProvider>
+          ),
+        },
+      );
+
+      await waitFor(() => {
+        expect(mockDisplayErrorToast).toHaveBeenCalledTimes(1);
+      });
+
+      expect(mockTrackCreditsPurchased).not.toHaveBeenCalled();
+    });
+  });
+
   describe("PaymentForm permission behavior", () => {
     beforeEach(() => {
       mockUseBalance.mockReturnValue({
diff --git a/frontend/src/routes/billing.tsx b/frontend/src/routes/billing.tsx
index 195d8eb0c160..eaac3189a7ea 100644
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
       displayErrorToast(t(I18nKey.PAYMENT\$CANCELLED));
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

echo "Patch applied successfully!"
