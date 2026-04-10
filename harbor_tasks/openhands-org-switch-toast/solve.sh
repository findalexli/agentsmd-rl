#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for adding toast notifications on org switch
cat <<'PATCH' | git apply -
diff --git a/frontend/__tests__/components/features/org/org-selector.test.tsx b/frontend/__tests__/components/features/org/org-selector.test.tsx
index 66f7f9523342..9ed1a284fa44 100644
--- a/frontend/__tests__/components/features/org/org-selector.test.tsx
+++ b/frontend/__tests__/components/features/org/org-selector.test.tsx
@@ -1,9 +1,11 @@
 import { screen, render, waitFor, within } from "@testing-library/react";
 import userEvent from "@testing-library/user-event";
-import { describe, expect, it, vi } from "vitest";
+import { describe, expect, it, vi, beforeEach } from "vitest";
 import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
 import { OrgSelector } from "#/components/features/org/org-selector";
 import { organizationService } from "#/api/organization-service/organization-service.api";
+import * as ToastHandlers from "#/utils/custom-toast-handlers";
+import { useSelectedOrganizationStore } from "#/stores/selected-organization-store";
 import {
   MOCK_PERSONAL_ORG,
   MOCK_TEAM_ORG_ACME,
@@ -32,10 +34,13 @@ vi.mock("react-i18next", async () => {
   return {
     ...actual,
     useTranslation: () => ({
-      t: (key: string) => {
+      t: (key: string, params?: Record<string, string>) => {
         const translations: Record<string, string> = {
           "ORG\$SELECT_ORGANIZATION_PLACEHOLDER": "Please select an organization",
           "ORG\$PERSONAL_WORKSPACE": "Personal Workspace",
+          "ORG\$SWITCHED_TO_ORGANIZATION": \`You have switched to organization: \${params?.name ?? ""}\`,
+          "ORG\$SWITCHED_TO_PERSONAL_WORKSPACE":
+            "You have switched to your personal workspace.",
         };
         return translations[key] || key;
       },
@@ -56,6 +61,9 @@ const renderOrgSelector = () =>
   });

 describe("OrgSelector", () => {
+  beforeEach(() => {
+    useSelectedOrganizationStore.setState({ organizationId: null });
+  });
   it("should not render when user only has a personal workspace", async () => {
     vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
       items: [MOCK_PERSONAL_ORG],
@@ -200,4 +208,80 @@ describe("OrgSelector", () => {
       expect(screen.getByTestId("dropdown-trigger")).toBeDisabled();
     });
   });
+
+  it("should display toast with organization name when switching to a team organization", async () => {
+    // Arrange
+    const user = userEvent.setup();
+    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
+      items: [MOCK_PERSONAL_ORG, MOCK_TEAM_ORG_ACME],
+      currentOrgId: MOCK_PERSONAL_ORG.id,
+    });
+    vi.spyOn(organizationService, "switchOrganization").mockResolvedValue(
+      MOCK_TEAM_ORG_ACME,
+    );
+    const displaySuccessToastSpy = vi.spyOn(
+      ToastHandlers,
+      "displaySuccessToast",
+    );
+
+    renderOrgSelector();
+
+    await waitFor(() => {
+      expect(screen.getByRole("combobox")).toHaveValue("Personal Workspace");
+    });
+
+    // Act
+    const trigger = screen.getByTestId("dropdown-trigger");
+    await user.click(trigger);
+    const listbox = await screen.findByRole("listbox");
+    const acmeOption = within(listbox).getByText("Acme Corp");
+    await user.click(acmeOption);
+
+    // Assert
+    await waitFor(() => {
+      expect(displaySuccessToastSpy).toHaveBeenCalledWith(
+        "You have switched to organization: Acme Corp",
+      );
+    });
+  });
+
+  it("should display toast for personal workspace when switching to personal workspace", async () => {
+    // Arrange
+    const user = userEvent.setup();
+    // Pre-set the store to have team org selected
+    useSelectedOrganizationStore.setState({
+      organizationId: MOCK_TEAM_ORG_ACME.id,
+    });
+    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
+      items: [MOCK_TEAM_ORG_ACME, MOCK_PERSONAL_ORG],
+      currentOrgId: MOCK_TEAM_ORG_ACME.id,
+    });
+    vi.spyOn(organizationService, "switchOrganization").mockResolvedValue(
+      MOCK_PERSONAL_ORG,
+    );
+    const displaySuccessToastSpy = vi.spyOn(
+      ToastHandlers,
+      "displaySuccessToast",
+    );
+
+    renderOrgSelector();
+
+    await waitFor(() => {
+      expect(screen.getByRole("combobox")).toHaveValue("Acme Corp");
+    });
+
+    // Act
+    const trigger = screen.getByTestId("dropdown-trigger");
+    await user.click(trigger);
+    const listbox = await screen.findByRole("listbox");
+    const personalOption = within(listbox).getByText("Personal Workspace");
+    await user.click(personalOption);
+
+    // Assert
+    await waitFor(() => {
+      expect(displaySuccessToastSpy).toHaveBeenCalledWith(
+        "You have switched to your personal workspace.",
+      );
+    });
+  });
 });
diff --git a/frontend/src/components/features/org/org-selector.tsx b/frontend/src/components/features/org/org-selector.tsx
index b32f379e96a8..8f22c549855a 100644
--- a/frontend/src/components/features/org/org-selector.tsx
+++ b/frontend/src/components/features/org/org-selector.tsx
@@ -45,7 +45,12 @@ export function OrgSelector() {
       }}
       onChange={(item) => {
         if (item && item.value !== organizationId) {
-          switchOrganization(item.value);
+          const org = organizations?.find((o) => o.id === item.value);
+          switchOrganization({
+            orgId: item.value,
+            orgName: item.label,
+            isPersonal: org?.is_personal ?? false,
+          });
         }
       }}
       placeholder={t(I18nKey.ORG\$SELECT_ORGANIZATION_PLACEHOLDER)}
diff --git a/frontend/src/hooks/mutation/use-switch-organization.ts b/frontend/src/hooks/mutation/use-switch-organization.ts
index 32e0f7b189c6..1bb36b09bafb 100644
--- a/frontend/src/hooks/mutation/use-switch-organization.ts
+++ b/frontend/src/hooks/mutation/use-switch-organization.ts
@@ -1,18 +1,31 @@
 import { useMutation, useQueryClient } from "@tanstack/react-query";
+import { useTranslation } from "react-i18next";
 import { useMatch, useNavigate } from "react-router";
 import { organizationService } from "#/api/organization-service/organization-service.api";
 import { useSelectedOrganizationId } from "#/context/use-selected-organization";
+import { I18nKey } from "#/i18n/declaration";
+import { displaySuccessToast } from "#/utils/custom-toast-handlers";

 export const useSwitchOrganization = () => {
+  const { t } = useTranslation();
   const queryClient = useQueryClient();
   const { setOrganizationId } = useSelectedOrganizationId();
   const navigate = useNavigate();
   const conversationMatch = useMatch("/conversations/:conversationId");

   return useMutation({
-    mutationFn: (orgId: string) =>
-      organizationService.switchOrganization({ orgId }),
-    onSuccess: (_, orgId) => {
+    mutationFn: ({
+      orgId,
+    }: {
+      orgId: string;
+      orgName: string;
+      isPersonal: boolean;
+    }) => organizationService.switchOrganization({ orgId }),
+    onSuccess: (_, { orgId, orgName, isPersonal }) => {
+      const message = isPersonal
+        ? t(I18nKey.ORG\$SWITCHED_TO_PERSONAL_WORKSPACE)
+        : t(I18nKey.ORG\$SWITCHED_TO_ORGANIZATION, { name: orgName });
+      displaySuccessToast(message);
       // Invalidate the target org's /me query to ensure fresh data on every switch
       queryClient.invalidateQueries({
         queryKey: ["organizations", orgId, "me"],
diff --git a/frontend/src/i18n/declaration.ts b/frontend/src/i18n/declaration.ts
index 574486f02429..d6e5a58c7141 100644
--- a/frontend/src/i18n/declaration.ts
+++ b/frontend/src/i18n/declaration.ts
@@ -1072,6 +1072,8 @@ export enum I18nKey {
   ORG\$SELECT_ORGANIZATION_PLACEHOLDER = "ORG\$SELECT_ORGANIZATION_PLACEHOLDER",
   ORG\$PERSONAL_WORKSPACE = "ORG\$PERSONAL_WORKSPACE",
   ORG\$ENTER_NEW_ORGANIZATION_NAME = "ORG\$ENTER_NEW_ORGANIZATION_NAME",
+  ORG\$SWITCHED_TO_ORGANIZATION = "ORG\$SWITCHED_TO_ORGANIZATION",
+  ORG\$SWITCHED_TO_PERSONAL_WORKSPACE = "ORG\$SWITCHED_TO_PERSONAL_WORKSPACE",
   CONVERSATION\$SHOW_SKILLS = "CONVERSATION\$SHOW_SKILLS",
   SKILLS_MODAL\$TITLE = "SKILLS_MODAL\$TITLE",
   CONVERSATION\$SHARE_PUBLICLY = "CONVERSATION\$SHARE_PUBLICLY",
diff --git a/frontend/src/i18n/translation.json b/frontend/src/i18n/translation.json
index f9e3c03b3042..9d41f33e43c0 100644
--- a/frontend/src/i18n/translation.json
+++ b/frontend/src/i18n/translation.json
@@ -18224,6 +18224,40 @@
     "uk": "Введіть нову назву організації",
     "ca": "Introduïu el nou nom de l'organització"
   },
+  "ORG\$SWITCHED_TO_ORGANIZATION": {
+    "en": "You have switched to organization: {{name}}",
+    "ja": "組織「{{name}}」に切り替えました",
+    "zh-CN": "您已切换到组织：{{name}}",
+    "zh-TW": "您已切換到組織：{{name}}",
+    "ko-KR": "조직으로 전환되었습니다: {{name}}",
+    "no": "Du har byttet til organisasjon: {{name}}",
+    "it": "Sei passato all'organizzazione: {{name}}",
+    "pt": "Você mudou para a organização: {{name}}",
+    "es": "Has cambiado a la organización: {{name}}",
+    "ar": "لقد انتقلت إلى المنظمة: {{name}}",
+    "fr": "Vous êtes passé à l'organisation : {{name}}",
+    "tr": "Organizasyona geçtiniz: {{name}}",
+    "de": "Sie haben zur Organisation gewechselt: {{name}}",
+    "uk": "Ви перейшли до організації: {{name}}",
+    "ca": "Heu canviat a l'organització: {{name}}"
+  },
+  "ORG\$SWITCHED_TO_PERSONAL_WORKSPACE": {
+    "en": "You have switched to your personal workspace.",
+    "ja": "個人ワークスペースに切り替えました。",
+    "zh-CN": "您已切换到个人工作区。",
+    "zh-TW": "您已切換到個人工作區。",
+    "ko-KR": "개인 워크스페이스로 전환되었습니다.",
+    "no": "Du har byttet til ditt personlige arbeidsområde.",
+    "it": "Sei passato alla tua area di lavoro personale.",
+    "pt": "Você mudou para sua área de trabalho pessoal.",
+    "es": "Has cambiado a tu espacio de trabajo personal.",
+    "ar": "لقد انتقلت إلى مساحة العمل الشخصية الخاصة بك.",
+    "fr": "Vous êtes passé à votre espace de travail personnel.",
+    "tr": "Kişisel çalışma alanınıza geçtiniz.",
+    "de": "Sie haben zu Ihrem persönlichen Arbeitsbereich gewechselt.",
+    "uk": "Ви перейшли до свого особистого робочого простору.",
+    "ca": "Heu canviat al vostre espai de treball personal."
+  },
   "CONVERSATION\$SHOW_SKILLS": {
     "en": "You have switched to your personal workspace.",
PATCH

echo "Gold patch applied successfully"
