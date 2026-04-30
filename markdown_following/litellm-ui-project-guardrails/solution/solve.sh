#!/usr/bin/env bash
# Reference (oracle) solution: apply the gold patch from PR #25100.
# The patch is inlined as a HEREDOC — no external network fetch.
set -euo pipefail

cd /workspace/litellm

# Idempotency guard: a distinctive line from the patch.
if grep -q 'Select existing guardrails or enter new ones' \
        ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.tsx 2>/dev/null; then
    echo "Gold patch already applied — nothing to do."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useCreateProject.ts b/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useCreateProject.ts
index 3943f23794e..e206c770b19 100644
--- a/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useCreateProject.ts
+++ b/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useCreateProject.ts
@@ -17,6 +17,7 @@ export interface ProjectCreateParams {
   models?: string[];
   max_budget?: number;
   blocked?: boolean;
+  guardrails?: string[];
   metadata?: Record<string, unknown>;
   model_rpm_limit?: Record<string, number>;
   model_tpm_limit?: Record<string, number>;
diff --git a/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useUpdateProject.ts b/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useUpdateProject.ts
index e6cd3071f5f..2042c8fc7cd 100644
--- a/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useUpdateProject.ts
+++ b/ui/litellm-dashboard/src/app/(dashboard)/hooks/projects/useUpdateProject.ts
@@ -17,6 +17,7 @@ export interface ProjectUpdateParams {
   models?: string[];
   max_budget?: number;
   blocked?: boolean;
+  guardrails?: string[];
   metadata?: Record<string, unknown>;
   model_rpm_limit?: Record<string, number>;
   model_tpm_limit?: Record<string, number>;
diff --git a/ui/litellm-dashboard/src/components/Projects/ProjectModals/EditProjectModal.tsx b/ui/litellm-dashboard/src/components/Projects/ProjectModals/EditProjectModal.tsx
index dc3b43ef73c..6c65e518cfd 100644
--- a/ui/litellm-dashboard/src/components/Projects/ProjectModals/EditProjectModal.tsx
+++ b/ui/litellm-dashboard/src/components/Projects/ProjectModals/EditProjectModal.tsx
@@ -33,6 +33,9 @@ export function EditProjectModal({
       const metadataObj = (project.metadata ?? {}) as Record<string, unknown>;
       const rpmLimits = (metadataObj.model_rpm_limit ?? {}) as Record<string, number>;
       const tpmLimits = (metadataObj.model_tpm_limit ?? {}) as Record<string, number>;
+      const guardrails = (Array.isArray(metadataObj.guardrails)
+        ? metadataObj.guardrails
+        : []) as string[];
 
       const modelLimits: ProjectFormValues["modelLimits"] = [];
       const allLimitModels = new Set([
@@ -48,7 +51,7 @@ export function EditProjectModal({
       }
 
       // Filter out internal keys from user-facing metadata
-      const internalKeys = new Set(["model_rpm_limit", "model_tpm_limit"]);
+      const internalKeys = new Set(["model_rpm_limit", "model_tpm_limit", "guardrails"]);
       const metadata: ProjectFormValues["metadata"] = [];
       for (const [key, value] of Object.entries(metadataObj)) {
         if (!internalKeys.has(key)) {
@@ -63,6 +66,7 @@ export function EditProjectModal({
         models: project.models ?? [],
         max_budget: project.litellm_budget_table?.max_budget ?? undefined,
         isBlocked: project.blocked,
+        guardrails: guardrails.length > 0 ? guardrails : undefined,
         modelLimits: modelLimits.length > 0 ? modelLimits : undefined,
         metadata: metadata.length > 0 ? metadata : undefined,
       });
diff --git a/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.test.tsx b/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.test.tsx
index 04e3ed64f47..d8532146566 100644
--- a/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.test.tsx
+++ b/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.test.tsx
@@ -14,6 +14,10 @@ vi.mock("@/components/organisms/create_key_button", () => ({
   fetchTeamModels: vi.fn().mockResolvedValue([]),
 }));
 
+vi.mock("@/components/networking", () => ({
+  getGuardrailsList: vi.fn().mockResolvedValue({ guardrails: [] }),
+}));
+
 vi.mock("@/components/key_team_helpers/fetch_available_models_team_key", () => ({
   getModelDisplayName: (model: string) => model,
 }));
@@ -86,4 +90,13 @@ describe("ProjectBaseForm", () => {
     renderWithProviders(<FormWrapper />);
     expect(screen.getByText("Advanced Settings")).toBeInTheDocument();
   });
+
+  it("should show a Guardrails field in the Advanced Settings section", async () => {
+    const user = userEvent.setup();
+    renderWithProviders(<FormWrapper />);
+    await user.click(screen.getByText("Advanced Settings"));
+    await waitFor(() => {
+      expect(screen.getByText("Guardrails")).toBeInTheDocument();
+    });
+  });
 });
diff --git a/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.tsx b/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.tsx
index bf1eca882c3..81d8fabe084 100644
--- a/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.tsx
+++ b/ui/litellm-dashboard/src/components/Projects/ProjectModals/ProjectBaseForm.tsx
@@ -22,6 +22,7 @@ import { useTeams } from "@/app/(dashboard)/hooks/teams/useTeams";
 import { Team } from "../../key_team_helpers/key_list";
 import { fetchTeamModels } from "../../organisms/create_key_button";
 import { getModelDisplayName } from "../../key_team_helpers/fetch_available_models_team_key";
+import { getGuardrailsList } from "@/components/networking";
 
 export interface ProjectFormValues {
   project_alias: string;
@@ -30,6 +31,7 @@ export interface ProjectFormValues {
   models: string[];
   max_budget?: number;
   isBlocked: boolean;
+  guardrails?: string[];
   modelLimits?: { model: string; tpm?: number; rpm?: number }[];
   metadata?: { key: string; value: string }[];
 }
@@ -46,6 +48,23 @@ export function ProjectBaseForm({
 
   const [selectedTeam, setSelectedTeam] = useState<Team | null>(null);
   const [modelsToPick, setModelsToPick] = useState<string[]>([]);
+  const [guardrailsList, setGuardrailsList] = useState<string[]>([]);
+
+  useEffect(() => {
+    const fetchGuardrails = async () => {
+      if (!accessToken) return;
+      try {
+        const response = await getGuardrailsList(accessToken);
+        const names = response.guardrails.map(
+          (g: { guardrail_name: string }) => g.guardrail_name
+        );
+        setGuardrailsList(names);
+      } catch (error) {
+        console.error("Failed to fetch guardrails:", error);
+      }
+    };
+    fetchGuardrails();
+  }, [accessToken]);
 
   // Sync selectedTeam from form value (needed for edit mode pre-fill)
   const teamIdValue = Form.useWatch("team_id", form);
@@ -259,6 +278,24 @@ export function ProjectBaseForm({
 
                     <Divider />
 
+                    <Form.Item
+                      label="Guardrails"
+                      name="guardrails"
+                      help="Select existing guardrails or enter new ones"
+                    >
+                      <Select
+                        mode="tags"
+                        style={{ width: "100%" }}
+                        placeholder="Select or enter guardrails"
+                        options={guardrailsList.map((name) => ({
+                          value: name,
+                          label: name,
+                        }))}
+                      />
+                    </Form.Item>
+
+                    <Divider />
+
                     <Typography.Text
                       strong
                       style={{ display: "block", marginBottom: 12 }}
diff --git a/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.test.ts b/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.test.ts
index f910fd7f819..26acee01edb 100644
--- a/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.test.ts
+++ b/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.test.ts
@@ -98,4 +98,20 @@ describe("buildProjectApiParams", () => {
     });
     expect(result).not.toHaveProperty("metadata");
   });
+
+  it("should include guardrails as a top-level field when provided", () => {
+    const result = buildProjectApiParams({
+      ...baseValues,
+      guardrails: ["pii-check", "content-filter"],
+    });
+    expect(result.guardrails).toEqual(["pii-check", "content-filter"]);
+  });
+
+  it("should omit guardrails when the array is empty", () => {
+    const result = buildProjectApiParams({
+      ...baseValues,
+      guardrails: [],
+    });
+    expect(result).not.toHaveProperty("guardrails");
+  });
 });
diff --git a/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.ts b/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.ts
index 97c093b57d9..bf18e2b1c12 100644
--- a/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.ts
+++ b/ui/litellm-dashboard/src/components/Projects/ProjectModals/projectFormUtils.ts
@@ -25,6 +25,9 @@ export function buildProjectApiParams(values: ProjectFormValues) {
     models: values.models ?? [],
     max_budget: values.max_budget,
     blocked: values.isBlocked ?? false,
+    ...(values.guardrails && values.guardrails.length > 0 && {
+      guardrails: values.guardrails,
+    }),
     ...(Object.keys(modelRpmLimit).length > 0 && {
       model_rpm_limit: modelRpmLimit,
     }),
PATCH

echo "Gold patch applied successfully."
