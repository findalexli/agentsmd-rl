#!/bin/bash
set -e

cd /workspace/openhands

echo "=== Step 1: Modifying use-switch-organization.ts ==="
cat > frontend/src/hooks/mutation/use-switch-organization.ts << 'EOF'
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useTranslation } from "react-i18next";
import { useMatch, useNavigate } from "react-router";
import { organizationService } from "#/api/organization-service/organization-service.api";
import { useSelectedOrganizationId } from "#/context/use-selected-organization";
import { I18nKey } from "#/i18n/declaration";
import { displaySuccessToast } from "#/utils/custom-toast-handlers";

export const useSwitchOrganization = () => {
  const { t } = useTranslation();
  const queryClient = useQueryClient();
  const { setOrganizationId } = useSelectedOrganizationId();
  const navigate = useNavigate();
  const conversationMatch = useMatch("/conversations/:conversationId");

  return useMutation({
    mutationFn: ({
      orgId,
    }: {
      orgId: string;
      orgName: string;
      isPersonal: boolean;
    }) => organizationService.switchOrganization({ orgId }),
    onSuccess: (_, { orgId, orgName, isPersonal }) => {
      const message = isPersonal
        ? t(I18nKey.ORG$SWITCHED_TO_PERSONAL_WORKSPACE)
        : t(I18nKey.ORG$SWITCHED_TO_ORGANIZATION, { name: orgName });
      displaySuccessToast(message);
      // Invalidate the target org's /me query to ensure fresh data on every switch
      queryClient.invalidateQueries({
        queryKey: ["organizations", orgId, "me"],
      });
      // Update local state - this triggers automatic refetch for all org-scoped queries
      // since their query keys include organizationId (e.g., ["settings", orgId], ["secrets", orgId])
      setOrganizationId(orgId);
      // Invalidate conversations to fetch data for the new org context
      queryClient.invalidateQueries({ queryKey: ["user", "conversations"] });
      // Remove all individual conversation queries to clear any stale/null data
      // from the previous org context
      queryClient.removeQueries({ queryKey: ["user", "conversation"] });

      // Redirect to home if on a conversation page since org context has changed
      if (conversationMatch) {
        navigate("/");
      }
    },
  });
};
EOF

echo "=== Step 2: Modifying org-selector.tsx ==="
cat > frontend/src/components/features/org/org-selector.tsx << 'EOF'
import React from "react";
import { useTranslation } from "react-i18next";
import { useSelectedOrganizationId } from "#/context/use-selected-organization";
import { useSwitchOrganization } from "#/hooks/mutation/use-switch-organization";
import { useOrganizations } from "#/hooks/query/use-organizations";
import { useShouldHideOrgSelector } from "#/hooks/use-should-hide-org-selector";
import { I18nKey } from "#/i18n/declaration";
import { Organization } from "#/types/org";
import { Dropdown } from "#/ui/dropdown/dropdown";

export function OrgSelector() {
  const { t } = useTranslation();
  const { organizationId } = useSelectedOrganizationId();
  const { data, isLoading } = useOrganizations();
  const organizations = data?.organizations;
  const { mutate: switchOrganization, isPending: isSwitching } =
    useSwitchOrganization();
  const shouldHideSelector = useShouldHideOrgSelector();

  const getOrgDisplayName = React.useCallback(
    (org: Organization) =>
      org.is_personal ? t(I18nKey.ORG$PERSONAL_WORKSPACE) : org.name,
    [t],
  );

  const selectedOrg = React.useMemo(() => {
    if (organizationId) {
      return organizations?.find((org) => org.id === organizationId);
    }

    return organizations?.[0];
  }, [organizationId, organizations]);

  if (shouldHideSelector) {
    return null;
  }

  return (
    <Dropdown
      testId="org-selector"
      key={`${selectedOrg?.id}-${selectedOrg?.name}`}
      defaultValue={{
        label: selectedOrg ? getOrgDisplayName(selectedOrg) : "",
        value: selectedOrg?.id || "",
      }}
      onChange={(item) => {
        if (item && item.value !== organizationId) {
          const org = organizations?.find((o) => o.id === item.value);
          switchOrganization({
            orgId: item.value,
            orgName: item.label,
            isPersonal: org?.is_personal ?? false,
          });
        }
      }}
      placeholder={t(I18nKey.ORG$SELECT_ORGANIZATION_PLACEHOLDER)}
      loading={isLoading || isSwitching}
      options={
        organizations?.map((org) => ({
          value: org.id,
          label: getOrgDisplayName(org),
        })) || []
      }
      className="bg-[#1F1F1F66] border-[#242424]"
    />
  );
}
EOF

echo "=== Step 3: Modifying declaration.ts (adding i18n keys) ==="
# Use sed to add the new keys after ORG$ENTER_NEW_ORGANIZATION_NAME
sed -i 's/ORG\$ENTER_NEW_ORGANIZATION_NAME = "ORG\$ENTER_NEW_ORGANIZATION_NAME",/ORG$ENTER_NEW_ORGANIZATION_NAME = "ORG$ENTER_NEW_ORGANIZATION_NAME",\n  ORG$SWITCHED_TO_ORGANIZATION = "ORG$SWITCHED_TO_ORGANIZATION",\n  ORG$SWITCHED_TO_PERSONAL_WORKSPACE = "ORG$SWITCHED_TO_PERSONAL_WORKSPACE",/g' frontend/src/i18n/declaration.ts

echo "=== Step 4: Modifying translation.json (adding translations) ==="
# Use Python to modify the JSON file
python3 << 'PYTHON'
import json

with open('frontend/src/i18n/translation.json', 'r') as f:
    data = json.load(f)

# Add new translations
data["ORG$SWITCHED_TO_ORGANIZATION"] = {
    "en": "You have switched to organization: {{name}}",
    "ja": "組織「{{name}}」に切り替えました",
    "zh-CN": "您已切换到组织：{{name}}",
    "zh-TW": "您已切換到組織：{{name}}",
    "ko-KR": "조직으로 전환되었습니다: {{name}}",
    "no": "Du har byttet til organisasjon: {{name}}",
    "it": "Sei passato all'organizzazione: {{name}}",
    "pt": "Você mudou para a organização: {{name}}",
    "es": "Has cambiado a la organización: {{name}}",
    "ar": "لقد انتقلت إلى المنظمة: {{name}}",
    "fr": "Vous êtes passé à l'organisation : {{name}}",
    "tr": "Organizasyona geçtiniz: {{name}}",
    "de": "Sie haben zur Organisation gewechselt: {{name}}",
    "uk": "Ви перейшли до організації: {{name}}",
    "ca": "Heu canviat a l'organització: {{name}}"
}

data["ORG$SWITCHED_TO_PERSONAL_WORKSPACE"] = {
    "en": "You have switched to your personal workspace.",
    "ja": "個人ワークスペースに切り替えました。",
    "zh-CN": "您已切换到个人工作区。",
    "zh-TW": "您已切換到個人工作區。",
    "ko-KR": "개인 워크스페이스로 전환되었습니다.",
    "no": "Du har byttet til ditt personlige arbeidsområde.",
    "it": "Sei passato alla tua area di lavoro personale.",
    "pt": "Você mudou para sua área de trabalho pessoal.",
    "es": "Has cambiado a tu espacio de trabajo personal.",
    "ar": "لقد انتقلت إلى مساحة العمل الشخصية الخاصة بك.",
    "fr": "Vous êtes passé à votre espace de travail personnel.",
    "tr": "Kişisel çalışma alanınıza geçtiniz.",
    "de": "Sie haben zu Ihrem persönlichen Arbeitsbereich gewechselt.",
    "uk": "Ви перейшли до свого особистого робочого простору.",
    "ca": "Heu canviat al vostre espai de treball personal."
}

with open('frontend/src/i18n/translation.json', 'w') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Translation JSON updated successfully")
PYTHON

echo "=== Step 5: Modifying org-selector.test.tsx ==="
cat > frontend/__tests__/components/features/org/org-selector.test.tsx << 'EOF'
import { screen, render, waitFor, within } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { describe, expect, it, vi, beforeEach } from "vitest";
import { QueryClientProvider, QueryClient } from "@tanstack/react-query";
import { OrgSelector } from "#/components/features/org/org-selector";
import { organizationService } from "#/api/organization-service/organization-service.api";
import * as ToastHandlers from "#/utils/custom-toast-handlers";
import { useSelectedOrganizationStore } from "#/stores/selected-organization-store";
import {
  MOCK_PERSONAL_ORG,
  MOCK_TEAM_ORG_ACME,
  createMockOrganization,
} from "#/mocks/org-handlers";

vi.mock("react-router", () => ({
  useRevalidator: () => ({ revalidate: vi.fn() }),
  useNavigate: () => vi.fn(),
  useLocation: () => ({ pathname: "/" }),
  useMatch: () => null,
}));

vi.mock("#/hooks/query/use-is-authed", () => ({
  useIsAuthed: () => ({ data: true }),
}));

// Mock useConfig to return SaaS mode (organizations are a SaaS-only feature)
vi.mock("#/hooks/query/use-config", () => ({
  useConfig: () => ({ data: { app_mode: "saas" } }),
}));

vi.mock("react-i18next", async () => {
  const actual =
    await vi.importActual<typeof import("react-i18next")>("react-i18next");
  return {
    ...actual,
    useTranslation: () => ({
      t: (key: string, params?: Record<string, string>) => {
        const translations: Record<string, string> = {
          "ORG$SELECT_ORGANIZATION_PLACEHOLDER": "Please select an organization",
          "ORG$PERSONAL_WORKSPACE": "Personal Workspace",
          "ORG$SWITCHED_TO_ORGANIZATION": `You have switched to organization: ${params?.name ?? ""}`,
          "ORG$SWITCHED_TO_PERSONAL_WORKSPACE":
            "You have switched to your personal workspace.",
        };
        return translations[key] || key;
      },
    }),
  };
});

const renderOrgSelector = () =>
  render(<OrgSelector />, {
    wrapper: ({ children }) => (
      <QueryClientProvider client={new QueryClient()}>
        {children}
      </QueryClientProvider>
    ),
  });

describe("OrgSelector", () => {
  beforeEach(() => {
    useSelectedOrganizationStore.setState({ organizationId: null });
  });
  it("should not render when user only has a personal workspace", async () => {
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_PERSONAL_ORG],
      currentOrgId: MOCK_PERSONAL_ORG.id,
    });

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.queryByRole("combobox")).not.toBeInTheDocument();
    });
  });

  it("should render when user has multiple organizations", async () => {
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_PERSONAL_ORG, MOCK_TEAM_ORG_ACME],
      currentOrgId: MOCK_PERSONAL_ORG.id,
    });

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toHaveValue("Personal Workspace");
    });
  });

  it("should show organization names in dropdown options", async () => {
    const user = userEvent.setup();
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_PERSONAL_ORG, MOCK_TEAM_ORG_ACME],
      currentOrgId: MOCK_PERSONAL_ORG.id,
    });

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toHaveValue("Personal Workspace");
    });

    const trigger = screen.getByTestId("dropdown-trigger");
    await user.click(trigger);

    const listbox = await screen.findByRole("listbox");
    expect(within(listbox).getByText("Personal Workspace")).toBeInTheDocument();
    expect(within(listbox).getByText("Acme Corp")).toBeInTheDocument();
  });

  it("should switch organization when selecting a different option", async () => {
    const user = userEvent.setup();
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_PERSONAL_ORG, MOCK_TEAM_ORG_ACME],
      currentOrgId: MOCK_PERSONAL_ORG.id,
    });
    const switchOrgSpy = vi.spyOn(
      organizationService,
      "switchOrganization",
    );

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toHaveValue("Personal Workspace");
    });

    const trigger = screen.getByTestId("dropdown-trigger");
    await user.click(trigger);
    const listbox = await screen.findByRole("listbox");
    const acmeOption = within(listbox).getByText("Acme Corp");
    await user.click(acmeOption);

    expect(switchOrgSpy).toHaveBeenCalledWith({ orgId: MOCK_TEAM_ORG_ACME.id });
  });

  it("should show loading state while switching organizations", async () => {
    // Arrange
    const user = userEvent.setup();
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_PERSONAL_ORG, MOCK_TEAM_ORG_ACME],
      currentOrgId: MOCK_PERSONAL_ORG.id,
    });
    vi.spyOn(organizationService, "switchOrganization").mockImplementation(
      () => new Promise(() => {}), // never resolves to keep loading state
    );

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toHaveValue("Personal Workspace");
    });

    // Act
    const trigger = screen.getByTestId("dropdown-trigger");
    await user.click(trigger);
    const listbox = await screen.findByRole("listbox");
    const acmeOption = within(listbox).getByText("Acme Corp");
    await user.click(acmeOption);

    // Assert
    await waitFor(() => {
      expect(screen.getByTestId("dropdown-trigger")).toBeDisabled();
    });
  });

  it("should display toast with organization name when switching to a team organization", async () => {
    // Arrange
    const user = userEvent.setup();
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_PERSONAL_ORG, MOCK_TEAM_ORG_ACME],
      currentOrgId: MOCK_PERSONAL_ORG.id,
    });
    vi.spyOn(organizationService, "switchOrganization").mockResolvedValue(
      MOCK_TEAM_ORG_ACME,
    );
    const displaySuccessToastSpy = vi.spyOn(
      ToastHandlers,
      "displaySuccessToast",
    );

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toHaveValue("Personal Workspace");
    });

    // Act
    const trigger = screen.getByTestId("dropdown-trigger");
    await user.click(trigger);
    const listbox = await screen.findByRole("listbox");
    const acmeOption = within(listbox).getByText("Acme Corp");
    await user.click(acmeOption);

    // Assert
    await waitFor(() => {
      expect(displaySuccessToastSpy).toHaveBeenCalledWith(
        "You have switched to organization: Acme Corp",
      );
    });
  });

  it("should display toast for personal workspace when switching to personal workspace", async () => {
    // Arrange
    const user = userEvent.setup();
    // Pre-set the store to have team org selected
    useSelectedOrganizationStore.setState({
      organizationId: MOCK_TEAM_ORG_ACME.id,
    });
    vi.spyOn(organizationService, "getOrganizations").mockResolvedValue({
      items: [MOCK_TEAM_ORG_ACME, MOCK_PERSONAL_ORG],
      currentOrgId: MOCK_TEAM_ORG_ACME.id,
    });
    vi.spyOn(organizationService, "switchOrganization").mockResolvedValue(
      MOCK_PERSONAL_ORG,
    );
    const displaySuccessToastSpy = vi.spyOn(
      ToastHandlers,
      "displaySuccessToast",
    );

    renderOrgSelector();

    await waitFor(() => {
      expect(screen.getByRole("combobox")).toHaveValue("Acme Corp");
    });

    // Act
    const trigger = screen.getByTestId("dropdown-trigger");
    await user.click(trigger);
    const listbox = await screen.findByRole("listbox");
    const personalOption = within(listbox).getByText("Personal Workspace");
    await user.click(personalOption);

    // Assert
    await waitFor(() => {
      expect(displaySuccessToastSpy).toHaveBeenCalledWith(
        "You have switched to your personal workspace.",
      );
    });
  });
});
EOF

echo "=== Step 6: Regenerating i18n files ==="
cd /workspace/openhands/frontend && npm run make-i18n

echo "=== All modifications complete ==="
