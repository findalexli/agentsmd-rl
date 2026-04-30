#!/bin/bash
set -euo pipefail

cd /workspace/litellm

# Idempotency check
if grep -q 'delete updatedLitellmParams.vector_store_ids' ui/litellm-dashboard/src/components/model_info_view.tsx; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix <<'PATCH'
diff --git a/ui/litellm-dashboard/src/components/model_info_view.test.tsx b/ui/litellm-dashboard/src/components/model_info_view.test.tsx
--- a/ui/litellm-dashboard/src/components/model_info_view.test.tsx
+++ b/ui/litellm-dashboard/src/components/model_info_view.test.tsx
@@ -552,6 +552,33 @@ describe("ModelInfoView", () => {
     expect(updatePayload.litellm_params.litellm_credential_name).not.toBe("from-json");
   });

+  it("should not include vector_store_ids in update payload when model has none", async () => {
+    // Regression: editing a model without vector stores used to inject
+    // vector_store_ids: [] into litellm_params, which then propagated to
+    // inference requests and broke Anthropic calls.
+    const user = userEvent.setup();
+    render(<ModelInfoView {...DEFAULT_ADMIN_PROPS} />, { wrapper });
+
+    await waitFor(() => {
+      expect(screen.getByRole("button", { name: /edit settings/i })).toBeInTheDocument();
+    });
+
+    await user.click(screen.getByRole("button", { name: /edit settings/i }));
+
+    await waitFor(() => {
+      expect(screen.getByRole("button", { name: /save changes/i })).toBeInTheDocument();
+    });
+
+    await user.click(screen.getByRole("button", { name: /save changes/i }));
+
+    await waitFor(() => {
+      expect(mockModelPatchUpdateCall).toHaveBeenCalled();
+    });
+
+    const updatePayload = mockModelPatchUpdateCall.mock.calls[0][1];
+    expect(updatePayload.litellm_params).not.toHaveProperty("vector_store_ids");
+  });
+
   it("should display health check model field for wildcard models", async () => {
     const wildcardModelData = {
       ...defaultModelData,
diff --git a/ui/litellm-dashboard/src/components/model_info_view.tsx b/ui/litellm-dashboard/src/components/model_info_view.tsx
--- a/ui/litellm-dashboard/src/components/model_info_view.tsx
+++ b/ui/litellm-dashboard/src/components/model_info_view.tsx
@@ -265,10 +265,13 @@ export default function ModelInfoView({
       if (values.guardrails) {
         updatedLitellmParams.guardrails = values.guardrails;
       }
-      if (values.vector_store_ids !== undefined) {
-        updatedLitellmParams.vector_store_ids = Array.isArray(values.vector_store_ids)
-          ? values.vector_store_ids
-          : [];
+      if (values.vector_store_ids?.length > 0) {
+        updatedLitellmParams.vector_store_ids = values.vector_store_ids;
+      } else if (values.vector_store_ids !== undefined) {
+        // User explicitly cleared previously-set vector stores — send [] to clear on backend
+        updatedLitellmParams.vector_store_ids = [];
+      } else {
+        delete updatedLitellmParams.vector_store_ids;
       }

       // Handle cache control settings
@@ -631,9 +634,11 @@ export default function ModelInfoView({
                     guardrails: Array.isArray(localModelData.litellm_params?.guardrails)
                       ? localModelData.litellm_params.guardrails
                       : [],
-                    vector_store_ids: Array.isArray(localModelData.litellm_params?.vector_store_ids)
-                      ? localModelData.litellm_params.vector_store_ids
-                      : [],
+                    vector_store_ids:
+                      Array.isArray(localModelData.litellm_params?.vector_store_ids) &&
+                      localModelData.litellm_params.vector_store_ids.length > 0
+                        ? localModelData.litellm_params.vector_store_ids
+                        : undefined,
                     tags: Array.isArray(localModelData.litellm_params?.tags) ? localModelData.litellm_params.tags : [],
                     health_check_model: isWildcardModel ? localModelData.model_info?.health_check_model : null,
                     litellm_credential_name: localModelData.litellm_params?.litellm_credential_name || "",
PATCH

echo "Gold patch applied successfully."
