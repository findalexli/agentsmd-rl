#!/usr/bin/env bash
# Apply gold patch from All-Hands-AI/OpenHands PR #14000.
# Patch is inlined verbatim; never fetched from a remote source.
set -euo pipefail

cd /workspace/openhands

# Idempotency: if patch already applied, no-op.
if grep -q 'mcp-search-settings-section' frontend/src/routes/mcp-settings.tsx 2>/dev/null; then
  echo "Patch already applied — skipping."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.gitattributes b/.gitattributes
index 0a3e3b5cb8fe..ce9ef23652e1 100644
--- a/.gitattributes
+++ b/.gitattributes
@@ -4,4 +4,5 @@
 * text eol=lf
 # Git incorrectly thinks some media is text
 *.png -text
+*.gif -text
 *.mp4 -text
diff --git a/AGENTS.md b/AGENTS.md
index 4351a9dc5cbd..1905a96ffd79 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -13,6 +13,12 @@ export RUNTIME=local
 make build && make run FRONTEND_PORT=12000 FRONTEND_HOST=0.0.0.0 BACKEND_HOST=0.0.0.0 &> /tmp/openhands-log.txt &
 ```
 
+Local run troubleshooting notes:
+- If the backend fails with `nc: command not found`, install `netcat-openbsd`.
+- If local runtime startup fails with `duplicate session: test-session`, clear the stale tmux session on the default socket: `tmux -S /tmp/tmux-$(id -u)/default kill-session -t test-session`.
+- Local runtime browser startup expects Playwright browsers under `~/.cache/playwright`; if needed run `PLAYWRIGHT_BROWSERS_PATH=$HOME/.cache/playwright poetry run playwright install chromium`.
+- In this sandbox environment, an inherited `SESSION_API_KEY` can make `/api/v1/settings` return 401 in the browser. Unset it before `make run` when you want to use the local web UI directly.
+
 IMPORTANT: Before making any changes to the codebase, ALWAYS run `make install-pre-commit-hooks` to ensure pre-commit hooks are properly installed.
 
 Before pushing any changes, you MUST ensure that any lint errors or simple test errors have been fixed.
diff --git a/frontend/__tests__/routes/llm-settings.test.tsx b/frontend/__tests__/routes/llm-settings.test.tsx
index 0b9bfc8b52a3..740dcc0ff163 100644
--- a/frontend/__tests__/routes/llm-settings.test.tsx
+++ b/frontend/__tests__/routes/llm-settings.test.tsx
@@ -718,7 +718,7 @@ describe("LlmSettingsScreen", () => {
     });
   });
 
-  it("clears hidden search API key state when saving basic view", async () => {
+  it("does not include search API key updates when saving basic LLM settings", async () => {
     let persistedSettings = buildSettingsWithAdvancedToggle({
       llm_model: "openai/gpt-4o",
       search_api_key: "tavily-key",
@@ -746,15 +746,8 @@ describe("LlmSettingsScreen", () => {
           }
         });
 
-        const nextSearchApiKey =
-          typeof payload.search_api_key === "string"
-            ? payload.search_api_key
-            : (persistedSettings.search_api_key ?? "");
-
         persistedSettings = buildSettings({
           ...persistedSettings,
-          search_api_key: nextSearchApiKey,
-          search_api_key_set: nextSearchApiKey.trim().length > 0,
           agent_settings: nextAgentSettings,
         });
 
@@ -772,7 +765,6 @@ describe("LlmSettingsScreen", () => {
     await waitFor(() => {
       expect(saveSettingsSpy).toHaveBeenCalledWith(
         expect.objectContaining({
-          search_api_key: "",
           agent_settings: expect.objectContaining({
             llm: expect.objectContaining({ api_key: "test-api-key" }),
           }),
@@ -780,6 +772,9 @@ describe("LlmSettingsScreen", () => {
       );
     });
 
+    const payload = saveSettingsSpy.mock.calls[0]?.[0] as Record<string, unknown>;
+    expect(payload).not.toHaveProperty("search_api_key");
+
     await waitFor(() => {
       expect(getSettingsSpy).toHaveBeenCalledTimes(2);
     });
@@ -1082,7 +1077,7 @@ describe("LlmSettingsScreen", () => {
     });
   });
 
-  it("keeps the advanced view while typing into the search API key field", async () => {
+  it("does not render the search API key input in advanced LLM settings", async () => {
     vi.spyOn(SettingsService, "getSettings").mockResolvedValue(
       buildSettingsWithAdvancedToggle(),
     );
@@ -1092,21 +1087,15 @@ describe("LlmSettingsScreen", () => {
     await screen.findByTestId("llm-settings-form-basic");
     await userEvent.click(screen.getByTestId("sdk-section-advanced-toggle"));
 
-    const searchApiKeyInput = await screen.findByTestId("search-api-key-input");
-    await userEvent.type(searchApiKeyInput, "a");
-
     await waitFor(() => {
-      expect(searchApiKeyInput).toHaveValue("a");
       expect(
         screen.getByTestId("llm-settings-form-advanced"),
       ).toBeInTheDocument();
-      expect(
-        screen.queryByTestId("llm-settings-form-basic"),
-      ).not.toBeInTheDocument();
+      expect(screen.queryByTestId("search-api-key-input")).not.toBeInTheDocument();
     });
   });
 
-  it("does not reveal all-only fields after save when the search API key remains set on refetch", async () => {
+  it("does not reveal all-only fields after save when refetch includes an MCP-owned search API key", async () => {
     const schema = structuredClone(
       MOCK_DEFAULT_USER_SETTINGS.agent_settings_schema!,
     );
@@ -1166,15 +1155,10 @@ describe("LlmSettingsScreen", () => {
       .mockImplementation(async () => structuredClone(persistedSettings));
     vi.spyOn(SettingsService, "saveSettings").mockImplementation(
       async (payload) => {
-        const nextSearchApiKey =
-          typeof payload.search_api_key === "string"
-            ? payload.search_api_key
-            : "";
-
         persistedSettings = buildSettings({
           agent_settings_schema: schema,
-          search_api_key: nextSearchApiKey,
-          search_api_key_set: nextSearchApiKey.trim().length > 0,
+          search_api_key: "tavily-key",
+          search_api_key_set: true,
           agent_settings: {
             llm: {
               model: "openhands/claude-opus-4-5-20251101",
@@ -1182,6 +1166,7 @@ describe("LlmSettingsScreen", () => {
           },
         });
 
+        expect(payload).not.toHaveProperty("search_api_key");
         return true;
       },
     );
@@ -1194,8 +1179,8 @@ describe("LlmSettingsScreen", () => {
       screen.queryByTestId("sdk-settings-llm.timeout"),
     ).not.toBeInTheDocument();
 
-    const searchApiKeyInput = await screen.findByTestId("search-api-key-input");
-    await userEvent.type(searchApiKeyInput, "tavily-key");
+    const apiKeyInput = await screen.findByTestId("llm-api-key-input");
+    await userEvent.type(apiKeyInput, "test-api-key");
     await userEvent.click(screen.getByTestId("save-button"));
 
     await waitFor(() => {
diff --git a/frontend/__tests__/routes/mcp-settings.test.tsx b/frontend/__tests__/routes/mcp-settings.test.tsx
index ddaf6adea7a8..9cb7ef03d3bd 100644
--- a/frontend/__tests__/routes/mcp-settings.test.tsx
+++ b/frontend/__tests__/routes/mcp-settings.test.tsx
@@ -72,6 +72,52 @@ beforeEach(() => {
 });
 
 describe("MCPSettingsScreen", () => {
+  it("renders and saves the built-in Tavily search settings on the MCP page", async () => {
+    let persistedSettings = buildSettings({
+      search_api_key: "tavily-key",
+      search_api_key_set: true,
+    });
+
+    vi.spyOn(SettingsService, "getSettings").mockImplementation(async () =>
+      structuredClone(persistedSettings),
+    );
+    const saveSettingsSpy = vi
+      .spyOn(SettingsService, "saveSettings")
+      .mockImplementation(async (payload) => {
+        persistedSettings = buildSettings(
+          deepMerge(
+            structuredClone(persistedSettings) as Record<string, unknown>,
+            payload as Record<string, unknown>,
+          ) as Partial<Settings>,
+        );
+        return true;
+      });
+
+    renderMcpSettingsScreen();
+
+    expect(
+      await screen.findByTestId("mcp-search-settings-section"),
+    ).toBeInTheDocument();
+    const searchApiKeyInput = await screen.findByTestId("search-api-key-input");
+    expect(searchApiKeyInput).toHaveValue("tavily-key");
+
+    await userEvent.clear(searchApiKeyInput);
+    await userEvent.type(searchApiKeyInput, "updated-tavily-key");
+    await userEvent.click(screen.getByTestId("save-search-api-key-button"));
+
+    await waitFor(() => {
+      expect(saveSettingsSpy).toHaveBeenCalledWith({
+        search_api_key: "updated-tavily-key",
+      });
+    });
+
+    await waitFor(() => {
+      expect(screen.getByTestId("search-api-key-input")).toHaveValue(
+        "updated-tavily-key",
+      );
+    });
+  });
+
   it("removes a newly added MCP server after the delete flow completes", async () => {
     let persistedSettings = buildSettings();
 
diff --git a/frontend/src/i18n/declaration.ts b/frontend/src/i18n/declaration.ts
index 084da4b01e33..641258ea479f 100644
--- a/frontend/src/i18n/declaration.ts
+++ b/frontend/src/i18n/declaration.ts
@@ -72,6 +72,8 @@ export enum I18nKey {
   SETTINGS$MCP_NO_SERVERS_CONFIGURED = "SETTINGS$MCP_NO_SERVERS_CONFIGURED",
   SETTINGS$MCP_SSE_SERVERS = "SETTINGS$MCP_SSE_SERVERS",
   SETTINGS$MCP_STDIO_SERVERS = "SETTINGS$MCP_STDIO_SERVERS",
+  SETTINGS$MCP_SEARCH_TITLE = "SETTINGS$MCP_SEARCH_TITLE",
+  SETTINGS$MCP_SEARCH_DESCRIPTION = "SETTINGS$MCP_SEARCH_DESCRIPTION",
   SETTINGS$MCP_API_KEY = "SETTINGS$MCP_API_KEY",
   SETTINGS$MCP_API_KEY_NOT_SET = "SETTINGS$MCP_API_KEY_NOT_SET",
   SETTINGS$MCP_COMMAND = "SETTINGS$MCP_COMMAND",
diff --git a/frontend/src/i18n/translation.json b/frontend/src/i18n/translation.json
index 9136024e393b..6379e4300b7d 100644
--- a/frontend/src/i18n/translation.json
+++ b/frontend/src/i18n/translation.json
@@ -1223,6 +1223,40 @@
     "uk": "Сервери Stdio",
     "ca": "Servidors Stdio"
   },
+  "SETTINGS$MCP_SEARCH_TITLE": {
+    "en": "Built-in search (Tavily)",
+    "ja": "組み込み検索（Tavily）",
+    "zh-CN": "内置搜索（Tavily）",
+    "zh-TW": "內建搜尋（Tavily）",
+    "ko-KR": "내장 검색(Tavily)",
+    "no": "Innebygd søk (Tavily)",
+    "it": "Ricerca integrata (Tavily)",
+    "pt": "Pesquisa integrada (Tavily)",
+    "es": "Búsqueda integrada (Tavily)",
+    "ar": "البحث المدمج (Tavily)",
+    "fr": "Recherche intégrée (Tavily)",
+    "tr": "Yerleşik arama (Tavily)",
+    "de": "Integrierte Suche (Tavily)",
+    "uk": "Вбудований пошук (Tavily)",
+    "ca": "Cerca integrada (Tavily)"
+  },
+  "SETTINGS$MCP_SEARCH_DESCRIPTION": {
+    "en": "Configure the Tavily key that OpenHands uses to add its default search MCP server.",
+    "ja": "OpenHands がデフォルトの検索 MCP サーバーを追加するために使用する Tavily キーを設定します。",
+    "zh-CN": "配置 OpenHands 用于添加其默认搜索 MCP 服务器的 Tavily 密钥。",
+    "zh-TW": "設定 OpenHands 用來新增其預設搜尋 MCP 伺服器的 Tavily 金鑰。",
+    "ko-KR": "OpenHands가 기본 검색 MCP 서버를 추가하는 데 사용하는 Tavily 키를 구성합니다.",
+    "no": "Konfigurer Tavily-nøkkelen som OpenHands bruker for å legge til sin standard søke-MCP-server.",
+    "it": "Configura la chiave Tavily che OpenHands usa per aggiungere il suo server MCP di ricerca predefinito.",
+    "pt": "Configure a chave Tavily que o OpenHands usa para adicionar seu servidor MCP de pesquisa padrão.",
+    "es": "Configura la clave de Tavily que OpenHands usa para añadir su servidor MCP de búsqueda predeterminado.",
+    "ar": "قم بتكوين مفتاح Tavily الذي يستخدمه OpenHands لإضافة خادم MCP الافتراضي للبحث.",
+    "fr": "Configurez la clé Tavily qu’OpenHands utilise pour ajouter son serveur MCP de recherche par défaut.",
+    "tr": "OpenHands'in varsayılan arama MCP sunucusunu eklemek için kullandığı Tavily anahtarını yapılandırın.",
+    "de": "Konfigurieren Sie den Tavily-Schlüssel, den OpenHands zum Hinzufügen seines standardmäßigen Such-MCP-Servers verwendet.",
+    "uk": "Налаштуйте ключ Tavily, який OpenHands використовує для додавання свого типового MCP-сервера пошуку.",
+    "ca": "Configura la clau de Tavily que OpenHands utilitza per afegir el seu servidor MCP de cerca predeterminat."
+  },
   "SETTINGS$MCP_API_KEY": {
     "en": "API Key",
     "ja": "APIキー",
diff --git a/frontend/src/routes/llm-settings.tsx b/frontend/src/routes/llm-settings.tsx
index 87af945da3d3..c48aba90d743 100644
--- a/frontend/src/routes/llm-settings.tsx
+++ b/frontend/src/routes/llm-settings.tsx
@@ -154,8 +154,6 @@ export function LlmSettingsScreen({
   const [selectedProvider, setSelectedProvider] = React.useState<string | null>(
     null,
   );
-  const [searchApiKey, setSearchApiKey] = React.useState("");
-  const [searchApiKeyDirty, setSearchApiKeyDirty] = React.useState(false);
   const hasHydratedInitialPersonalSaasViewRef = React.useRef(false);
 
   const defaultModel = String(
@@ -173,11 +171,6 @@ export function LlmSettingsScreen({
     }
   }, [settings?.llm_model]);
 
-  React.useEffect(() => {
-    setSearchApiKey(settings?.search_api_key ?? "");
-    setSearchApiKeyDirty(false);
-  }, [settings?.search_api_key]);
-
   React.useEffect(() => {
     if (settings && isSaasMode && scope !== "org") {
       hasHydratedInitialPersonalSaasViewRef.current = true;
@@ -381,54 +374,22 @@ export function LlmSettingsScreen({
                 "llm-api-key-help-anchor-advanced",
               )}
 
-              {!isSaasMode ? (
-                <>
-                  <SettingsInput
-                    testId="search-api-key-input"
-                    label={t(I18nKey.SETTINGS$SEARCH_API_KEY)}
-                    type="password"
-                    className="w-full"
-                    value={searchApiKey}
-                    placeholder={t(I18nKey.API$TVLY_KEY_EXAMPLE)}
-                    onChange={(value) => {
-                      setSearchApiKey(value);
-                      setSearchApiKeyDirty(
-                        value !== (settings?.search_api_key ?? ""),
-                      );
-                    }}
-                    startContent={
-                      settings?.search_api_key_set ? (
-                        <KeyStatusIcon isSet={settings.search_api_key_set} />
-                      ) : undefined
+              {!isSaasMode && hasAgentField ? (
+                <SettingsDropdownInput
+                  testId="agent-input"
+                  name="agent-input"
+                  label={t(I18nKey.SETTINGS$AGENT)}
+                  items={agentItems}
+                  selectedKey={agentValue}
+                  isClearable={false}
+                  onSelectionChange={(key) => {
+                    if (key) {
+                      onChange("agent", String(key));
                     }
-                    isDisabled={isDisabled}
-                  />
-
-                  <HelpLink
-                    testId="search-api-key-help-anchor"
-                    text={t(I18nKey.SETTINGS$SEARCH_API_KEY_OPTIONAL)}
-                    linkText={t(I18nKey.SETTINGS$SEARCH_API_KEY_INSTRUCTIONS)}
-                    href="https://tavily.com/"
-                  />
-
-                  {hasAgentField ? (
-                    <SettingsDropdownInput
-                      testId="agent-input"
-                      name="agent-input"
-                      label={t(I18nKey.SETTINGS$AGENT)}
-                      items={agentItems}
-                      selectedKey={agentValue}
-                      isClearable={false}
-                      onSelectionChange={(key) => {
-                        if (key) {
-                          onChange("agent", String(key));
-                        }
-                      }}
-                      isDisabled={isDisabled}
-                      wrapperClassName="w-full"
-                    />
-                  ) : null}
-                </>
+                  }}
+                  isDisabled={isDisabled}
+                  wrapperClassName="w-full"
+                />
               ) : null}
             </div>
           )}
@@ -441,11 +402,8 @@ export function LlmSettingsScreen({
       isSaasMode,
       defaultModel,
       schema,
-      searchApiKey,
       selectedProvider,
       settings?.llm_api_key_set,
-      settings?.search_api_key,
-      settings?.search_api_key_set,
       t,
     ],
   );
@@ -460,11 +418,6 @@ export function LlmSettingsScreen({
     ) => {
       // basePayload is a nested dict (e.g. {llm: {model: "gpt-4"}})
       const agentSettings = structuredClone(basePayload);
-      const topLevel: Record<string, unknown> = {};
-
-      if (!isSaasMode && searchApiKeyDirty) {
-        topLevel.search_api_key = searchApiKey.trim();
-      }
 
       const modelValue =
         typeof context.values["llm.model"] === "string"
@@ -490,25 +443,14 @@ export function LlmSettingsScreen({
         llm.base_url = getSchemaFieldDefaultValue(schema, "llm.base_url");
         agentSettings.llm = llm;
 
-        if (!isSaasMode) {
-          topLevel.search_api_key = DEFAULT_SETTINGS.search_api_key;
-        }
-
         if (hasAgentField) {
           agentSettings.agent = getSchemaFieldDefaultValue(schema, "agent");
         }
       }
 
-      return { agent_settings: agentSettings, ...topLevel };
+      return { agent_settings: agentSettings };
     },
-    [
-      hasAgentField,
-      isSaasMode,
-      schema,
-      searchApiKey,
-      searchApiKeyDirty,
-      selectedProvider,
-    ],
+    [hasAgentField, isSaasMode, schema, selectedProvider],
   );
 
   return (
@@ -517,9 +459,7 @@ export function LlmSettingsScreen({
       sectionKeys={["llm", "general"]}
       excludeKeys={LLM_EXCLUDED_KEYS}
       header={buildHeader}
-      extraDirty={searchApiKeyDirty}
       buildPayload={buildPayload}
-      onSaveSuccess={() => setSearchApiKeyDirty(false)}
       getInitialView={getInitialView}
       testId="llm-settings-screen"
     />
diff --git a/frontend/src/routes/mcp-settings.tsx b/frontend/src/routes/mcp-settings.tsx
index ab6dfe9d6a65..6fcebfcb4204 100644
--- a/frontend/src/routes/mcp-settings.tsx
+++ b/frontend/src/routes/mcp-settings.tsx
@@ -1,6 +1,9 @@
-import React, { useState } from "react";
+import React, { useEffect, useState } from "react";
+import { AxiosError } from "axios";
 import { useTranslation } from "react-i18next";
 import { useSettings } from "#/hooks/query/use-settings";
+import { useConfig } from "#/hooks/query/use-config";
+import { useSaveSettings } from "#/hooks/mutation/use-save-settings";
 import { useDeleteMcpServer } from "#/hooks/mutation/use-delete-mcp-server";
 import { useAddMcpServer } from "#/hooks/mutation/use-add-mcp-server";
 import { useUpdateMcpServer } from "#/hooks/mutation/use-update-mcp-server";
@@ -8,10 +11,18 @@ import { I18nKey } from "#/i18n/declaration";
 
 import { MCPServerList } from "#/components/features/settings/mcp-settings/mcp-server-list";
 import { MCPServerForm } from "#/components/features/settings/mcp-settings/mcp-server-form";
+import { KeyStatusIcon } from "#/components/features/settings/key-status-icon";
+import { SettingsInput } from "#/components/features/settings/settings-input";
 import { ConfirmationModal } from "#/components/shared/modals/confirmation-modal";
 import { BrandButton } from "#/components/features/settings/brand-button";
+import { HelpLink } from "#/ui/help-link";
 import { MCPConfig } from "#/types/settings";
+import {
+  displayErrorToast,
+  displaySuccessToast,
+} from "#/utils/custom-toast-handlers";
 import { parseMcpConfig } from "#/utils/mcp-config";
+import { retrieveAxiosErrorMessage } from "#/utils/retrieve-axios-error-message";
 import { createPermissionGuard } from "#/utils/org/permission-guard";
 import { Typography } from "#/ui/typography";
 
@@ -35,6 +46,9 @@ interface MCPServerConfig {
 function MCPSettingsScreen() {
   const { t } = useTranslation();
   const { data: settings, isLoading } = useSettings();
+  const { data: config } = useConfig();
+  const { mutate: saveSettings, isPending: isSavingSearchApiKey } =
+    useSaveSettings();
   const { mutate: deleteMcpServer } = useDeleteMcpServer();
   const { mutate: addMcpServer } = useAddMcpServer();
   const { mutate: updateMcpServer } = useUpdateMcpServer();
@@ -43,10 +57,14 @@ function MCPSettingsScreen() {
   const [editingServer, setEditingServer] = useState<MCPServerConfig | null>(
     null,
   );
+  const [searchApiKey, setSearchApiKey] = useState("");
+  const [searchApiKeyDirty, setSearchApiKeyDirty] = useState(false);
   const [confirmationModalIsVisible, setConfirmationModalIsVisible] =
     useState(false);
   const [serverToDelete, setServerToDelete] = useState<string | null>(null);
 
+  const isSaasMode = config?.app_mode === "saas";
+
   const mcpConfig: MCPConfig = parseMcpConfig(
     settings?.agent_settings?.mcp_config,
   );
@@ -75,6 +93,11 @@ function MCPSettingsScreen() {
     })),
   ];
 
+  useEffect(() => {
+    setSearchApiKey(settings?.search_api_key ?? "");
+    setSearchApiKeyDirty(false);
+  }, [settings?.search_api_key]);
+
   const handleAddServer = (serverConfig: MCPServerConfig) => {
     addMcpServer(serverConfig, {
       onSuccess: () => {
@@ -126,6 +149,22 @@ function MCPSettingsScreen() {
     setServerToDelete(null);
   };
 
+  const handleSaveSearchApiKey = () => {
+    saveSettings(
+      { search_api_key: searchApiKey },
+      {
+        onError: (error) => {
+          const message = retrieveAxiosErrorMessage(error as AxiosError);
+          displayErrorToast(message || t(I18nKey.ERROR$GENERIC));
+        },
+        onSuccess: () => {
+          displaySuccessToast(t(I18nKey.SETTINGS$SAVED_WARNING));
+          setSearchApiKeyDirty(false);
+        },
+      },
+    );
+  };
+
   if (isLoading || !settings) {
     return null;
   }
@@ -182,6 +221,63 @@ function MCPSettingsScreen() {
         onDelete={handleDeleteClick}
       />
 
+      {!isSaasMode ? (
+        <section
+          data-testid="mcp-search-settings-section"
+          className="flex flex-col gap-4 rounded-2xl border border-tertiary p-5"
+        >
+          <div className="flex flex-col gap-2">
+            <Typography.H3>
+              {t(I18nKey.SETTINGS$MCP_SEARCH_TITLE)}
+            </Typography.H3>
+            <Typography.Paragraph className="text-sm text-[#A3A3A3]">
+              {t(I18nKey.SETTINGS$MCP_SEARCH_DESCRIPTION)}
+            </Typography.Paragraph>
+          </div>
+
+          <div className="max-w-xl flex flex-col gap-4">
+            <SettingsInput
+              testId="search-api-key-input"
+              label={t(I18nKey.SETTINGS$SEARCH_API_KEY)}
+              type="password"
+              className="w-full"
+              value={searchApiKey}
+              placeholder={t(I18nKey.API$TVLY_KEY_EXAMPLE)}
+              onChange={(value) => {
+                setSearchApiKey(value);
+                setSearchApiKeyDirty(value !== (settings.search_api_key ?? ""));
+              }}
+              startContent={
+                settings.search_api_key_set ? (
+                  <KeyStatusIcon isSet={settings.search_api_key_set} />
+                ) : undefined
+              }
+            />
+
+            <HelpLink
+              testId="search-api-key-help-anchor"
+              text={t(I18nKey.SETTINGS$SEARCH_API_KEY_OPTIONAL)}
+              linkText={t(I18nKey.SETTINGS$SEARCH_API_KEY_INSTRUCTIONS)}
+              href="https://tavily.com/"
+            />
+
+            <div>
+              <BrandButton
+                testId="save-search-api-key-button"
+                type="button"
+                variant="primary"
+                isDisabled={isSavingSearchApiKey || !searchApiKeyDirty}
+                onClick={handleSaveSearchApiKey}
+              >
+                {isSavingSearchApiKey
+                  ? t(I18nKey.SETTINGS$SAVING)
+                  : t(I18nKey.SETTINGS$SAVE_CHANGES)}
+              </BrandButton>
+            </div>
+          </div>
+        </section>
+      ) : null}
+
       {confirmationModalIsVisible && serverToDelete && (
         <ConfirmationModal
           text={t(I18nKey.SETTINGS$MCP_CONFIRM_DELETE)}
PATCH

# Regenerate i18n declarations to match the patched translation file.
( cd frontend && npm run make-i18n >/dev/null )

echo "Gold patch applied."
