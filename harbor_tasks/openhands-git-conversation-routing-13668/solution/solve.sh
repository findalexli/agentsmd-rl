#!/bin/bash
set -e

cd /workspace/openhands

# Apply the gold patch for Git Conversation Routing feature
cat <<'PATCH' | git apply -
diff --git a/frontend/src/components/features/org/claim-button.tsx b/frontend/src/components/features/org/claim-button.tsx
new file mode 100644
index 000000000000..210a3c3e3582
--- /dev/null
+++ b/frontend/src/components/features/org/claim-button.tsx
@@ -0,0 +1,84 @@
+import React from "react";
+import { useTranslation } from "react-i18next";
+import { I18nKey } from "#/i18n/declaration";
+import { cn } from "#/utils/utils";
+import type { GitOrg } from "#/hooks/organizations/use-git-conversation-routing";
+
+type ButtonState =
+  | "claiming"
+  | "disconnecting"
+  | "disconnect"
+  | "claimed"
+  | "unclaimed";
+
+const BUTTON_STYLES: Record<ButtonState, string> = {
+  claiming:
+    "bg-[#050505] border border-[#242424] text-[#fafafa] opacity-50 cursor-not-allowed flex items-center justify-center",
+  disconnecting:
+    "bg-[#050505] border border-[#242424] text-[#fafafa] opacity-50 cursor-not-allowed",
+  disconnect:
+    "bg-[rgba(244,63,94,0.15)] border border-[rgba(244,63,94,0.6)] text-[#fda4af] font-medium cursor-pointer",
+  claimed:
+    "bg-[rgba(16,185,129,0.2)] border border-[rgba(16,185,129,0.6)] text-[#6ee7b7] font-medium cursor-pointer flex items-center justify-center",
+  unclaimed:
+    "bg-[#050505] border border-[#242424] text-[#fafafa] cursor-pointer flex items-center justify-center",
+};
+
+const BUTTON_HOVER_STYLES: Partial<Record<ButtonState, string>> = {
+  unclaimed: "bg-[rgba(31,31,31,0.6)]",
+};
+
+const BUTTON_LABELS: Record<ButtonState, I18nKey> = {
+  claiming: I18nKey.ORG$CLAIM,
+  disconnecting: I18nKey.ORG$DISCONNECT,
+  disconnect: I18nKey.ORG$DISCONNECT,
+  claimed: I18nKey.ORG$CLAIMED,
+  unclaimed: I18nKey.ORG$CLAIM,
+};
+
+export function getButtonState(
+  status: GitOrg["status"],
+  isHovered: boolean,
+): ButtonState {
+  if (status === "claiming" || status === "disconnecting") return status;
+  if (status === "claimed" && isHovered) return "disconnect";
+  return status;
+}
+
+interface ClaimButtonProps {
+  org: GitOrg;
+  onClaim: (id: string) => void;
+  onDisconnect: (id: string) => void;
+}
+
+export function ClaimButton({ org, onClaim, onDisconnect }: ClaimButtonProps) {
+  const { t } = useTranslation();
+  const [isHovered, setIsHovered] = React.useState(false);
+
+  const buttonState = getButtonState(org.status, isHovered);
+  const isDisabled =
+    org.status === "claiming" || org.status === "disconnecting";
+
+  const handleClick = () => {
+    if (org.status === "unclaimed") onClaim(org.id);
+    if (org.status === "claimed") onDisconnect(org.id);
+  };
+
+  return (
+    <button
+      type="button"
+      data-testid={`claim-button-${org.id}`}
+      onClick={handleClick}
+      onMouseEnter={() => setIsHovered(true)}
+      onMouseLeave={() => setIsHovered(false)}
+      disabled={isDisabled}
+      className={cn(
+        "h-[28px] rounded px-[13px] text-xs leading-4 text-center whitespace-nowrap transition-colors",
+        BUTTON_STYLES[buttonState],
+        isHovered && BUTTON_HOVER_STYLES[buttonState],
+      )}
+    >
+      {t(BUTTON_LABELS[buttonState])}
+    </button>
+  );
+}
diff --git a/frontend/src/components/features/org/git-conversation-routing.tsx b/frontend/src/components/features/org/git-conversation-routing.tsx
new file mode 100644
index 000000000000..1dd524f6fcd0
--- /dev/null
+++ b/frontend/src/components/features/org/git-conversation-routing.tsx
@@ -0,0 +1,37 @@
+import { useTranslation } from "react-i18next";
+import { I18nKey } from "#/i18n/declaration";
+import { Text, Paragraph } from "#/ui/typography";
+import { useGitConversationRouting } from "#/hooks/organizations/use-git-conversation-routing";
+import { GitOrgRow } from "./git-org-row";
+
+export function GitConversationRouting() {
+  const { t } = useTranslation();
+  const { orgs, claimOrg, disconnectOrg } = useGitConversationRouting();
+
+  return (
+    <div
+      data-testid="git-conversation-routing"
+      className="flex flex-col gap-3 w-full"
+    >
+      <Text className="text-[#fafafa] text-sm font-semibold leading-5">
+        {t(I18nKey.ORG$GIT_CONVERSATION_ROUTING)}
+      </Text>
+
+      <Paragraph className="text-[#8c8c8c] text-sm font-normal leading-5">
+        {t(I18nKey.ORG$GIT_CONVERSATION_ROUTING_DESCRIPTION)}
+      </Paragraph>
+
+      <div className="border border-[#242424] rounded-[6px] overflow-hidden">
+        {orgs.map((org, index) => (
+          <GitOrgRow
+            key={org.id}
+            org={org}
+            isLast={index === orgs.length - 1}
+            onClaim={claimOrg}
+            onDisconnect={disconnectOrg}
+          />
+        ))}
+      </div>
+    </div>
+  );
+}
diff --git a/frontend/src/components/features/org/git-org-row.tsx b/frontend/src/components/features/org/git-org-row.tsx
new file mode 100644
index 000000000000..0d81a65aa2e3
--- /dev/null
+++ b/frontend/src/components/features/org/git-org-row.tsx
@@ -0,0 +1,34 @@
+import { cn } from "#/utils/utils";
+import { Text } from "#/ui/typography";
+import type { GitOrg } from "#/hooks/organizations/use-git-conversation-routing";
+import { ClaimButton } from "./claim-button";
+
+interface GitOrgRowProps {
+  org: GitOrg;
+  isLast: boolean;
+  onClaim: (id: string) => void;
+  onDisconnect: (id: string) => void;
+}
+
+export function GitOrgRow({
+  org,
+  isLast,
+  onClaim,
+  onDisconnect,
+}: GitOrgRowProps) {
+  return (
+    <div
+      data-testid={`org-row-${org.id}`}
+      className={cn(
+        "flex items-center justify-between px-3 h-[53px]",
+        !isLast && "border-b border-[#242424]",
+      )}
+    >
+      <span className="text-sm font-normal leading-5">
+        <Text className="text-[#8c8c8c]">{org.provider}/</Text>
+        <Text className="text-[#fafafa]">{org.name}</Text>
+      </span>
+      <ClaimButton org={org} onClaim={onClaim} onDisconnect={onDisconnect} />
+    </div>
+  );
+}
diff --git a/frontend/src/hooks/organizations/use-git-conversation-routing.ts b/frontend/src/hooks/organizations/use-git-conversation-routing.ts
new file mode 100644
index 000000000000..b3a1a9512d08
--- /dev/null
+++ b/frontend/src/hooks/organizations/use-git-conversation-routing.ts
@@ -0,0 +1,81 @@
+import React from "react";
+import { useTranslation } from "react-i18next";
+import { I18nKey } from "#/i18n/declaration";
+import {
+  displaySuccessToast,
+  displayErrorToast,
+} from "#/utils/custom-toast-handlers";
+
+// TODO: This entire hook uses mock data and simulated async behavior.
+// Replace with real API calls (e.g., organizationService.claimOrg / disconnectOrg)
+// once the backend endpoints for organization claims are implemented.
+export interface GitOrg {
+  id: string;
+  provider: "GitHub" | "GitLab";
+  name: string;
+  status: "unclaimed" | "claimed" | "claiming" | "disconnecting";
+}
+
+// TODO: Remove mock data once the backend API for fetching available git organizations is ready.
+const INITIAL_ORGS: GitOrg[] = [
+  { id: "1", provider: "GitHub", name: "OpenHands", status: "claimed" },
+  { id: "2", provider: "GitHub", name: "AcmeCo", status: "unclaimed" },
+  {
+    id: "3",
+    provider: "GitHub",
+    name: "already-claimed",
+    status: "unclaimed",
+  },
+  { id: "4", provider: "GitLab", name: "OpenHands", status: "unclaimed" },
+];
+
+export function useGitConversationRouting() {
+  const { t } = useTranslation();
+  const [orgs, setOrgs] = React.useState<GitOrg[]>(INITIAL_ORGS);
+
+  const updateOrgStatus = React.useCallback(
+    (id: string, status: GitOrg["status"]) => {
+      setOrgs((prev) =>
+        prev.map((org) => (org.id === id ? { ...org, status } : org)),
+      );
+    },
+    [],
+  );
+
+  const claimOrg = React.useCallback(
+    (id: string) => {
+      const org = orgs.find((o) => o.id === id);
+      if (!org || org.status !== "unclaimed") return;
+
+      updateOrgStatus(id, "claiming");
+
+      setTimeout(() => {
+        if (org.name === "already-claimed") {
+          updateOrgStatus(id, "unclaimed");
+          displayErrorToast(t(I18nKey.ORG$CLAIM_ERROR));
+        } else {
+          updateOrgStatus(id, "claimed");
+          displaySuccessToast(t(I18nKey.ORG$CLAIM_SUCCESS));
+        }
+      }, 1000);
+    },
+    [orgs, updateOrgStatus, t],
+  );
+
+  const disconnectOrg = React.useCallback(
+    (id: string) => {
+      const org = orgs.find((o) => o.id === id);
+      if (!org || org.status !== "claimed") return;
+
+      updateOrgStatus(id, "disconnecting");
+
+      setTimeout(() => {
+        updateOrgStatus(id, "unclaimed");
+        displaySuccessToast(t(I18nKey.ORG$DISCONNECT_SUCCESS));
+      }, 1000);
+    },
+    [orgs, updateOrgStatus, t],
+  );
+
+  return { orgs, claimOrg, disconnectOrg };
+}
diff --git a/frontend/src/i18n/declaration.ts b/frontend/src/i18n/declaration.ts
index 24223a0d34b1..8ca8d76a6a0b 100644
--- a/frontend/src/i18n/declaration.ts
+++ b/frontend/src/i18n/declaration.ts
@@ -1271,4 +1271,12 @@ export enum I18nKey {
   ENTERPRISE$DONE_BUTTON = "ENTERPRISE$DONE_BUTTON",
   COMMON$BACK = "COMMON$BACK",
   MODAL$CLOSE_BUTTON_LABEL = "MODAL$CLOSE_BUTTON_LABEL",
+  ORG$GIT_CONVERSATION_ROUTING = "ORG$GIT_CONVERSATION_ROUTING",
+  ORG$GIT_CONVERSATION_ROUTING_DESCRIPTION = "ORG$GIT_CONVERSATION_ROUTING_DESCRIPTION",
+  ORG$CLAIM = "ORG$CLAIM",
+  ORG$CLAIMED = "ORG$CLAIMED",
+  ORG$DISCONNECT = "ORG$DISCONNECT",
+  ORG$CLAIM_SUCCESS = "ORG$CLAIM_SUCCESS",
+  ORG$DISCONNECT_SUCCESS = "ORG$DISCONNECT_SUCCESS",
+  ORG$CLAIM_ERROR = "ORG$CLAIM_ERROR",
 }
diff --git a/frontend/src/i18n/translation.json b/frontend/src/i18n/translation.json
index d244f77f326f..9d08de518ad9 100644
--- a/frontend/src/i18n/translation.json
+++ b/frontend/src/i18n/translation.json
@@ -21611,5 +21611,141 @@
     "ca": "Tancar",
     "tr": "Kapat",
     "uk": "Закрити"
+  },
+  "ORG$GIT_CONVERSATION_ROUTING": {
+    "en": "Git Conversation Routing",
+    "ja": "Git会話ルーティング",
+    "zh-CN": "Git 会话路由",
+    "zh-TW": "Git 对话路由",
+    "ko-KR": "Git 대화 라우팅",
+    "no": "Git-samtale-ruting",
+    "it": "Instradamento conversazioni Git",
+    "pt": "Roteamento de conversas Git",
+    "es": "Enrutamiento de conversaciones Git",
+    "ar": "توجيه محادثات Git",
+    "fr": "Routage des conversations Git",
+    "tr": "Git Konuşma Yönlendirme",
+    "de": "Git-Gesprächsweiterleitung",
+    "uk": "Маршрутизація розмов Git",
+    "ca": "Encaminament de converses Git"
+  },
+  "ORG$GIT_CONVERSATION_ROUTING_DESCRIPTION": {
+    "en": "Claim organizations so resolver requests route to the appropriate OpenHands org for shared visibility, auditing, and ownership. If a requester is not a member of the claiming org, the conversation falls back to their Personal Workspace. Available organizations are derived from your connected GitHub/GitLab identity. Only organization admins and owners can manage organization claims.",
+    "ja": "組織を申請して、リゾルバーリクエストが適切なOpenHands組織にルーティングされるようにします。共有の可視性、監査、所有権のためです。リクエスターが申請元組織のメンバーでない場合、会話はパーソナルワークスペースにフォールバックします。利用可能な組織は、接続されたGitHub/GitLabアイデンティティから取得されます。組織の申請を管理できるのは、組織の管理者とオーナーのみです。",
+    "zh-CN": "认领组织，使解析器请求路由到适当的 OpenHands 组织，以实现共享可见性、审计和所有权。如果请求者不是认领组织的成员，对话将回退到其个人工作区。可用组织来源于您连接的 GitHub/GitLab 身份。只有组织管理员和所有者可以管理组织认领。",
+    "zh-TW": "認領組織，使解析器請求路由到適當的 OpenHands 組織，以實現共享可見性、審計和所有權。如果請求者不是認領組織的成員，對話將回退到其個人工作區。可用組織來源於您連接的 GitHub/GitLab 身份。只有組織管理員和所有者可以管理組織認領。",
+    "ko-KR": "조직을 클레임하여 리졸버 요청이 공유 가시성, 감사 및 소유권을 위해 적절한 OpenHands 조직으로 라우팅되도록 합니다. 요청자가 클레임 조직의 구성원이 아닌 경우 대화는 개인 워크스페이스로 대체됩니다. 사용 가능한 조직은 연결된 GitHub/GitLab ID에서 파생됩니다. 조직 관리자와 소유자만 조직 클레임을 관리할 수 있습니다.",
+    "no": "Krev organisasjoner slik at resolver-forespørsler rutes til riktig OpenHands-organisasjon for delt synlighet, revisjon og eierskap. Hvis en forespørrer ikke er medlem av den krevende organisasjonen, faller samtalen tilbake til deres personlige arbeidsområde. Tilgjengelige organisasjoner er hentet fra din tilkoblede GitHub/GitLab-identitet. Bare organisasjonsadministratorer og eiere kan administrere organisasjonskrav.",
+    "it": "Rivendica le organizzazioni in modo che le richieste del resolver vengano instradate all'organizzazione OpenHands appropriata per visibilità condivisa, auditing e proprietà. Se un richiedente non è membro dell'organizzazione richiedente, la conversazione torna al suo spazio di lavoro personale. Le organizzazioni disponibili derivano dalla tua identità GitHub/GitLab connessa. Solo gli amministratori e i proprietari dell'organizzazione possono gestire le rivendicazioni.",
+    "pt": "Reivindique organizações para que as solicitações do resolver sejam roteadas para a organização OpenHands apropriada para visibilidade compartilhada, auditoria e propriedade. Se um solicitante não for membro da organização reivindicante, a conversa retorna ao seu espaço de trabalho pessoal. As organizações disponíveis são derivadas da sua identidade GitHub/GitLab conectada. Apenas administradores e proprietários da organização podem gerenciar reivindicações.",
+    "es": "Reclame organizaciones para que las solicitudes del resolver se dirijan a la organización OpenHands apropiada para visibilidad compartida, auditoría y propiedad. Si un solicitante no es miembro de la organización reclamante, la conversación vuelve a su espacio de trabajo personal. Las organizaciones disponibles se derivan de su identidad de GitHub/GitLab conectada. Solo los administradores y propietarios de la organización pueden gestionar las reclamaciones.",
+    "ar": "اطلب المنظمات حتى يتم توجيه طلبات المحلل إلى منظمة OpenHands المناسبة للرؤية المشتركة والتدقيق والملكية. إذا لم يكن مقدم الطلب عضوًا في المنظمة المطالبة، تعود المحادثة إلى مساحة العمل الشخصية الخاصة به. المنظمات المتاحة مشتقة من هوية GitHub/GitLab المتصلة. يمكن فقط لمسؤولي ومالكي المنظمة إدارة مطالبات المنظمة.",
+    "fr": "Revendiquez des organisations pour que les demandes du résolveur soient acheminées vers l'organisation OpenHands appropriée pour la visibilité partagée, l'audit et la propriété. Si un demandeur n'est pas membre de l'organisation revendicatrice, la conversation revient à son espace de travail personnel. Les organisations disponibles sont dérivées de votre identité GitHub/GitLab connectée. Seuls les administrateurs et propriétaires d'organisation peuvent gérer les revendications.",
+    "tr": "Çözümleyici isteklerinin paylaşılan görünürlük, denetim ve sahiplik için uygun OpenHands organizasyonuna yönlendirilmesi amacıyla organizasyonları talep edin. İstekte bulunan kişi talep eden organizasyonun üyesi değilse, konuşma kişisel çalışma alanına geri döner. Kullanılabilir organizasyonlar, bağlı GitHub/GitLab kimliğinizden türetilir. Yalnızca organizasyon yöneticileri ve sahipleri organizasyon taleplerini yönetebilir.",
+    "de": "Beanspruchen Sie Organisationen, damit Resolver-Anfragen zur entsprechenden OpenHands-Organisation für gemeinsame Sichtbarkeit, Prüfung und Eigentümerschaft weitergeleitet werden. Wenn ein Anfragender kein Mitglied der beanspruchenden Organisation ist, fällt das Gespräch auf seinen persönlichen Arbeitsbereich zurück. Verfügbare Organisationen werden aus Ihrer verbundenen GitHub/GitLab-Identität abgeleitet. Nur Organisationsadministratoren und -eigentümer können Organisationsansprüche verwalten.",
+    "uk": "Заявляйте організації, щоб запити резолвера направлялися до відповідної організації OpenHands для спільної видимості, аудиту та власності. Якщо запитувач не є членом організації, що заявляє, розмова повертається до його персонального робочого простору. Доступні організації визначаються з вашої підключеної ідентифікації GitHub/GitLab. Лише адміністратори та власники організації можуть керувати заявками.",
+    "ca": "Reclameu organitzacions perquè les sol·licituds del resolver s'encaminin a l'organització OpenHands adequada per a visibilitat compartida, auditoria i propietat. Si un sol·licitant no és membre de l'organització reclamant, la conversa torna al seu espai de treball personal. Les organitzacions disponibles es deriven de la vostra identitat GitHub/GitLab connectada. Només els administradors i propietaris de l'organització poden gestionar les reclamacions."
+  },
+  "ORG$CLAIM": {
+    "en": "Claim",
+    "ja": "申請",
+    "zh-CN": "认领",
+    "zh-TW": "認領",
+    "ko-KR": "클레임",
+    "no": "Krev",
+    "it": "Rivendica",
+    "pt": "Reivindicar",
+    "es": "Reclamar",
+    "ar": "مطالبة",
+    "fr": "Revendiquer",
+    "tr": "Talep Et",
+    "de": "Beanspruchen",
+    "uk": "Заявити",
+    "ca": "Reclamar"
+  },
+  "ORG$CLAIMED": {
+    "en": "Claimed",
+    "ja": "申請済み",
+    "zh-CN": "已认领",
+    "zh-TW": "已認領",
+    "ko-KR": "클레임됨",
+    "no": "Krevd",
+    "it": "Rivendicata",
+    "pt": "Reivindicada",
+    "es": "Reclamada",
+    "ar": "تمت المطالبة",
+    "fr": "Revendiquée",
+    "tr": "Talep Edildi",
+    "de": "Beansprucht",
+    "uk": "Заявлено",
+    "ca": "Reclamada"
+  },
+  "ORG$DISCONNECT": {
+    "en": "Disconnect",
+    "ja": "切断",
+    "zh-CN": "断开连接",
+    "zh-TW": "斷開連接",
+    "ko-KR": "연결 해제",
+    "no": "Koble fra",
+    "it": "Disconnetti",
+    "pt": "Desconectar",
+    "es": "Desconectar",
+    "ar": "قطع الاتصال",
+    "fr": "Déconnecter",
+    "tr": "Bağlantıyı Kes",
+    "de": "Trennen",
+    "uk": "Від'єднати",
+    "ca": "Desconnectar"
+  },
+  "ORG$CLAIM_SUCCESS": {
+    "en": "Organization claimed successfully.",
+    "ja": "組織の申請が完了しました。",
+    "zh-CN": "组织认领成功。",
+    "zh-TW": "組織認領成功。",
+    "ko-KR": "조직이 성공적으로 클레임되었습니다.",
+    "no": "Organisasjonen ble krevd.",
+    "it": "Organizzazione rivendicata con successo.",
+    "pt": "Organização reivindicada com sucesso.",
+    "es": "Organización reclamada exitosamente.",
+    "ar": "تمت المطالبة بالمنظمة بنجاح.",
+    "fr": "Organisation revendiquée avec succès.",
+    "tr": "Organizasyon başarıyla talep edildi.",
+    "de": "Organisation erfolgreich beansprucht.",
+    "uk": "Організацію успішно заявлено.",
+    "ca": "Organització reclamada amb èxit."
+  },
+  "ORG$DISCONNECT_SUCCESS": {
+    "en": "Organization disconnected.",
+    "ja": "組織の接続が解除されました。",
+    "zh-CN": "组织已断开连接。",
+    "zh-TW": "組織已斷開連接。",
+    "ko-KR": "조직 연결이 해제되었습니다.",
+    "no": "Organisasjonen ble frakoblet.",
+    "it": "Organizzazione disconnessa.",
+    "pt": "Organização desconectada.",
+    "es": "Organização desconectada.",
+    "ar": "تم قطع اتصال المنظمة.",
+    "fr": "Organisation déconnectée.",
+    "tr": "Organizasyon bağlantısı kesildi.",
+    "de": "Organisation getrennt.",
+    "uk": "Організацію від'єднано.",
+    "ca": "Organització desconnectada."
+  },
+  "ORG$CLAIM_ERROR": {
+    "en": "Connection failed. Org is already claimed.",
+    "ja": "接続に失敗しました。組織はすでに申請されています。",
+    "zh-CN": "连接失败。组织已被认领。",
+    "zh-TW": "連接失敗。組織已被認領。",
+    "ko-KR": "연결에 실패했습니다. 조직이 이미 클레임되었습니다.",
+    "no": "Tilkobling mislyktes. Organisasjonen er allerede krevd.",
+    "it": "Connessione fallita. L'organizzazione è già stata rivendicata.",
+    "pt": "Falha na conexão. A organização já foi reivindicada.",
+    "es": "Error de conexión. La organización ya fue reclamada.",
+    "ar": "فشل الاتصال. المنظمة مطالب بها بالفعل.",
+    "fr": "Échec de la connexion. L'organisation est déjà revendiquée.",
+    "tr": "Bağlantı başarısız. Organizasyon zaten talep edilmiş.",
+    "de": "Verbindung fehlgeschlagen. Organisation wurde bereits beansprucht.",
+    "uk": "Помилка з'єднання. Організація вже заявлена.",
+    "ca": "Error de connexió. L'organització ja ha estat reclamada."
   }
 }
diff --git a/frontend/src/routes/manage-org.tsx b/frontend/src/routes/manage-org.tsx
index cc142749236f..d1751861758f 100644
--- a/frontend/src/routes/manage-org.tsx
+++ b/frontend/src/routes/manage-org.tsx
@@ -9,7 +9,9 @@ import { InteractiveChip } from "#/ui/interactive-chip";
 import { usePermission } from "#/hooks/organizations/use-permissions";
 import { createPermissionGuard } from "#/utils/org/permission-guard";
 import { isBillingHidden } from "#/utils/org/billing-visibility";
+import { ENABLE_ORG_CLAIMS_RESOLVER_ROUTING } from "#/utils/feature-flags";
 import { DeleteOrgConfirmationModal } from "#/components/features/org/delete-org-confirmation-modal";
+import { GitConversationRouting } from "#/components/features/org/git-conversation-routing";
 import { ChangeOrgNameModal } from "#/components/features/org/change-org-name-modal";
 import { AddCreditsModal } from "#/components/features/org/add-credits-modal";
 import { useBalance } from "#/hooks/query/use-balance";
@@ -37,6 +39,7 @@ function ManageOrg() {
   const canChangeOrgName = !!me && hasPermission("change_organization_name");
   const canDeleteOrg = !!me && hasPermission("delete_organization");
   const canAddCredits = !!me && hasPermission("add_credits");
+  const canManageOrgClaims = !!me && hasPermission("manage_org_claims");
   const shouldHideBilling = isBillingHidden(
     config,
     hasPermission("view_billing"),
@@ -113,6 +116,10 @@ function ManageOrg() {
           {t(I18nKey.ORG$DELETE_ORGANIZATION)}
         </button>
       )}
+
+      {canManageOrgClaims && ENABLE_ORG_CLAIMS_RESOLVER_ROUTING() && (
+        <GitConversationRouting />
+      )}
     </div>
   );
 }
diff --git a/frontend/src/utils/org/permissions.ts b/frontend/src/utils/org/permissions.ts
index ab17f5b5e47e..25f65b6e3c3b 100644
--- a/frontend/src/utils/org/permissions.ts
+++ b/frontend/src/utils/org/permissions.ts
@@ -18,6 +18,8 @@ type ManageAPIKeysPermission = "manage_api_keys";
 type ViewLLMSettingsPermission = "view_llm_settings";
 type EditLLMSettingsPermission = "edit_llm_settings";

+type ManageOrgClaimsPermission = "manage_org_claims";
+
 // Union of all permission keys
 export type PermissionKey =
   | UserRoleChangePermissionKey
@@ -32,7 +34,8 @@ export type PermissionKey =
   | ManageApplicationSettingsPermission
   | ManageAPIKeysPermission
   | ViewLLMSettingsPermission
-  | EditLLMSettingsPermission;
+  | EditLLMSettingsPermission
+  | ManageOrgClaimsPermission;

 /* PERMISSION ARRAYS */
 const memberPerms: PermissionKey[] = [
@@ -51,6 +54,7 @@ const adminOnly: PermissionKey[] = [
   "invite_user_to_organization",
   "change_user_role:member",
   "change_user_role:admin",
+  "manage_org_claims",
 ];

 const ownerOnly: PermissionKey[] = [
PATCH

# Idempotency check - verify the patch was applied
grep -q "ORG\$GIT_CONVERSATION_ROUTING" frontend/src/i18n/declaration.ts && echo "Patch applied successfully"
