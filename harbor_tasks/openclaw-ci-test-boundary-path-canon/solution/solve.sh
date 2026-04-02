#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Check if already applied (look for the in-tree telegramCommandTestPlugin)
if grep -q 'createChannelTestPluginBase' src/auto-reply/reply/commands.test.ts 2>/dev/null && \
   grep -q 'canonicalAttachmentPath' src/media-understanding/media-understanding-misc.test.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/auto-reply/reply/commands.test.ts b/src/auto-reply/reply/commands.test.ts
index 1c9aafff1ea5..9a7bc5144e02 100644
--- a/src/auto-reply/reply/commands.test.ts
+++ b/src/auto-reply/reply/commands.test.ts
@@ -2,13 +2,21 @@ import fs from "node:fs/promises";
 import os from "node:os";
 import path from "node:path";
 import { afterAll, beforeAll, beforeEach, describe, expect, it, vi } from "vitest";
-import { telegramCommandTestPlugin } from "../../../extensions/telegram/test-support.js";
 import type { ChannelPlugin } from "../../channels/plugins/types.js";
 import type { OpenClawConfig } from "../../config/config.js";
 import { updateSessionStore, type SessionEntry } from "../../config/sessions.js";
+import { formatAllowFromLowercase } from "../../plugin-sdk/allow-from.js";
+import { buildDmGroupAccountAllowlistAdapter } from "../../plugin-sdk/allowlist-config-edit.js";
+import { resolveApprovalApprovers } from "../../plugin-sdk/approval-approvers.js";
+import { createApproverRestrictedNativeApprovalAdapter } from "../../plugin-sdk/approval-runtime.js";
+import { createScopedChannelConfigAdapter } from "../../plugin-sdk/channel-config-helpers.js";
 import { setActivePluginRegistry } from "../../plugins/runtime.js";
+import { DEFAULT_ACCOUNT_ID, normalizeAccountId } from "../../routing/session-key.js";
 import { loadBundledPluginPublicSurfaceSync } from "../../test-utils/bundled-plugin-public-surface.js";
-import { createTestRegistry } from "../../test-utils/channel-plugins.js";
+import {
+  createChannelTestPluginBase,
+  createTestRegistry,
+} from "../../test-utils/channel-plugins.js";
 import { typedCases } from "../../test-utils/typed-cases.js";
 import { INTERNAL_MESSAGE_CHANNEL } from "../../utils/message-channel.js";
 import type { MsgContext } from "../templating.js";
@@ -157,6 +165,246 @@ const { createTaskRecord, resetTaskRegistryForTests } =

 let testWorkspaceDir = os.tmpdir();

+type TelegramTestAccountConfig = {
+  enabled?: boolean;
+  allowFrom?: Array<string | number>;
+  groupAllowFrom?: Array<string | number>;
+  dmPolicy?: string;
+  groupPolicy?: string;
+  configWrites?: boolean;
+  execApprovals?: {
+    enabled?: boolean;
+    approvers?: string[];
+    target?: "dm" | "channel" | "both";
+  };
+};
+
+type TelegramTestSectionConfig = TelegramTestAccountConfig & {
+  accounts?: Record<string, TelegramTestAccountConfig>;
+};
+
+function listConfiguredTelegramAccountIds(cfg: OpenClawConfig): string[] {
+  const channel = cfg.channels?.telegram as TelegramTestSectionConfig | undefined;
+  const accountIds = Object.keys(channel?.accounts ?? {});
+  if (accountIds.length > 0) {
+    return accountIds;
+  }
+  if (!channel) {
+    return [];
+  }
+  const { accounts: _accounts, ...base } = channel;
+  return Object.values(base).some((value) => value !== undefined) ? [DEFAULT_ACCOUNT_ID] : [];
+}
+
+function resolveTelegramTestAccount(
+  cfg: OpenClawConfig,
+  accountId?: string | null,
+): TelegramTestAccountConfig {
+  const resolvedAccountId = normalizeAccountId(accountId);
+  const channel = cfg.channels?.telegram as TelegramTestSectionConfig | undefined;
+  const scoped = channel?.accounts?.[resolvedAccountId];
+  const base = resolvedAccountId === DEFAULT_ACCOUNT_ID ? channel : undefined;
+  return {
+    ...base,
+    ...scoped,
+    enabled:
+      typeof scoped?.enabled === "boolean"
+        ? scoped.enabled
+        : typeof channel?.enabled === "boolean"
+          ? channel.enabled
+          : true,
+  };
+}
+
+function normalizeTelegramAllowFromEntries(values: Array<string | number>): string[] {
+  return formatAllowFromLowercase({ allowFrom: values, stripPrefixRe: /^(telegram|tg):/i });
+}
+
+function stripTelegramInternalPrefixes(value: string): string {
+  let trimmed = value.trim();
+  let strippedTelegramPrefix = false;
+  while (true) {
+    const next = (() => {
+      if (/^(telegram|tg):/i.test(trimmed)) {
+        strippedTelegramPrefix = true;
+        return trimmed.replace(/^(telegram|tg):/i, "").trim();
+      }
+      if (strippedTelegramPrefix && /^group:/i.test(trimmed)) {
+        return trimmed.replace(/^group:/i, "").trim();
+      }
+      return trimmed;
+    })();
+    if (next === trimmed) {
+      return trimmed;
+    }
+    trimmed = next;
+  }
+}
+
+function normalizeTelegramDirectApproverId(value: string | number): string | undefined {
+  const normalized = stripTelegramInternalPrefixes(String(value));
+  if (!normalized || normalized.startsWith("-")) {
+    return undefined;
+  }
+  return normalized;
+}
+
+function getTelegramExecApprovalApprovers(params: {
+  cfg: OpenClawConfig;
+  accountId?: string | null;
+}): string[] {
+  const account = resolveTelegramTestAccount(params.cfg, params.accountId);
+  return resolveApprovalApprovers({
+    explicit: account.execApprovals?.approvers,
+    allowFrom: account.allowFrom,
+    normalizeApprover: normalizeTelegramDirectApproverId,
+  });
+}
+
+function isTelegramExecApprovalTargetRecipient(params: {
+  cfg: OpenClawConfig;
+  senderId?: string | null;
+  accountId?: string | null;
+}): boolean {
+  const senderId = params.senderId?.trim();
+  const execApprovals = params.cfg.approvals?.exec;
+  if (
+    !senderId ||
+    execApprovals?.enabled !== true ||
+    (execApprovals.mode !== "targets" && execApprovals.mode !== "both")
+  ) {
+    return false;
+  }
+  const accountId = params.accountId ? normalizeAccountId(params.accountId) : undefined;
+  return (execApprovals.targets ?? []).some((target) => {
+    if (target.channel?.trim().toLowerCase() !== "telegram") {
+      return false;
+    }
+    if (accountId && target.accountId && normalizeAccountId(target.accountId) !== accountId) {
+      return false;
+    }
+    const to = target.to ? normalizeTelegramDirectApproverId(target.to) : undefined;
+    return Boolean(to && to === senderId);
+  });
+}
+
+function isTelegramExecApprovalAuthorizedSender(params: {
+  cfg: OpenClawConfig;
+  accountId?: string | null;
+  senderId?: string | null;
+}): boolean {
+  const senderId = params.senderId ? normalizeTelegramDirectApproverId(params.senderId) : undefined;
+  if (!senderId) {
+    return false;
+  }
+  return (
+    getTelegramExecApprovalApprovers(params).includes(senderId) ||
+    isTelegramExecApprovalTargetRecipient(params)
+  );
+}
+
+function isTelegramExecApprovalClientEnabled(params: {
+  cfg: OpenClawConfig;
+  accountId?: string | null;
+}): boolean {
+  const config = resolveTelegramTestAccount(params.cfg, params.accountId).execApprovals;
+  return Boolean(config?.enabled && getTelegramExecApprovalApprovers(params).length > 0);
+}
+
+function resolveTelegramExecApprovalTarget(params: {
+  cfg: OpenClawConfig;
+  accountId?: string | null;
+}): "dm" | "channel" | "both" {
+  return resolveTelegramTestAccount(params.cfg, params.accountId).execApprovals?.target ?? "dm";
+}
+
+const telegramNativeApprovalAdapter = createApproverRestrictedNativeApprovalAdapter({
+  channel: "telegram",
+  channelLabel: "Telegram",
+  listAccountIds: listConfiguredTelegramAccountIds,
+  hasApprovers: ({ cfg, accountId }) =>
+    getTelegramExecApprovalApprovers({ cfg, accountId }).length > 0,
+  isExecAuthorizedSender: isTelegramExecApprovalAuthorizedSender,
+  isPluginAuthorizedSender: ({ cfg, accountId, senderId }) => {
+    const normalizedSenderId = senderId?.trim();
+    return Boolean(
+      normalizedSenderId &&
+      getTelegramExecApprovalApprovers({ cfg, accountId }).includes(normalizedSenderId),
+    );
+  },
+  isNativeDeliveryEnabled: isTelegramExecApprovalClientEnabled,
+  resolveNativeDeliveryMode: resolveTelegramExecApprovalTarget,
+  requireMatchingTurnSourceChannel: true,
+});
+
+const telegramCommandTestPlugin: ChannelPlugin = {
+  ...createChannelTestPluginBase({
+    id: "telegram",
+    label: "Telegram",
+    docsPath: "/channels/telegram",
+    capabilities: {
+      chatTypes: ["direct", "group", "channel", "thread"],
+      reactions: true,
+      threads: true,
+      media: true,
+      polls: true,
+      nativeCommands: true,
+      blockStreaming: true,
+    },
+  }),
+  config: createScopedChannelConfigAdapter({
+    sectionKey: "telegram",
+    listAccountIds: listConfiguredTelegramAccountIds,
+    resolveAccount: (cfg, accountId) => resolveTelegramTestAccount(cfg, accountId),
+    defaultAccountId: () => DEFAULT_ACCOUNT_ID,
+    clearBaseFields: [],
+    resolveAllowFrom: (account) => account.allowFrom,
+    formatAllowFrom: normalizeTelegramAllowFromEntries,
+  }),
+  auth: telegramNativeApprovalAdapter.auth,
+  pairing: {
+    idLabel: "telegramUserId",
+  },
+  allowlist: buildDmGroupAccountAllowlistAdapter({
+    channelId: "telegram",
+    resolveAccount: ({ cfg, accountId }) => resolveTelegramTestAccount(cfg, accountId),
+    normalize: ({ values }) => normalizeTelegramAllowFromEntries(values),
+    resolveDmAllowFrom: (account) => account.allowFrom,
+    resolveGroupAllowFrom: (account) => account.groupAllowFrom,
+    resolveDmPolicy: (account) => account.dmPolicy,
+    resolveGroupPolicy: (account) => account.groupPolicy,
+  }),
+};
+
+describe("telegram command test plugin helpers", () => {
+  it("normalizes telegram allowFrom entries like the production adapter", () => {
+    expect(normalizeTelegramAllowFromEntries([" TG:123 ", "telegram:456", "@Alice"])).toEqual([
+      "123",
+      "456",
+      "@alice",
+    ]);
+  });
+
+  it("falls back to allowFrom when explicit exec approvers are empty", () => {
+    expect(
+      getTelegramExecApprovalApprovers({
+        cfg: {
+          channels: {
+            telegram: {
+              allowFrom: ["tg:123"],
+              execApprovals: { enabled: true, approvers: [] },
+            },
+          },
+        } as OpenClawConfig,
+      }),
+    ).toEqual(["123"]);
+  });
+
+  it("rejects prefixed telegram group ids as direct approvers", () => {
+    expect(normalizeTelegramDirectApproverId("tg:-100123456")).toBeUndefined();
+  });
+});
+
 function setMinimalChannelPluginRegistryForTests(): void {
   setActivePluginRegistry(
     createTestRegistry([
diff --git a/src/media-understanding/media-understanding-misc.test.ts b/src/media-understanding/media-understanding-misc.test.ts
index 4b02099b5463..0c1d32971805 100644
--- a/src/media-understanding/media-understanding-misc.test.ts
+++ b/src/media-understanding/media-understanding-misc.test.ts
@@ -125,6 +125,7 @@ describe("media understanding attachments SSRF", () => {
       const attachmentPath = path.join(allowedRoot, "voice-note.m4a");
       await fs.mkdir(allowedRoot, { recursive: true });
       await fs.writeFile(attachmentPath, "ok");
+      const canonicalAttachmentPath = await fs.realpath(attachmentPath).catch(() => attachmentPath);

       const cache = new MediaAttachmentCache([{ index: 0, path: attachmentPath }], {
         localPathRoots: [allowedRoot],
@@ -134,7 +135,8 @@ describe("media understanding attachments SSRF", () => {

       openSpy.mockImplementation(async (filePath, flags) => {
         const handle = await originalOpen(filePath, flags);
-        if (filePath !== attachmentPath) {
+        const candidatePath = await fs.realpath(String(filePath)).catch(() => String(filePath));
+        if (candidatePath !== canonicalAttachmentPath) {
           return handle;
         }
         const mockedHandle = handle as typeof handle & {
@@ -159,6 +161,7 @@ describe("media understanding attachments SSRF", () => {
       const attachmentPath = path.join(allowedRoot, "voice-note.m4a");
       await fs.mkdir(allowedRoot, { recursive: true });
       await fs.writeFile(attachmentPath, "ok");
+      const canonicalAttachmentPath = await fs.realpath(attachmentPath).catch(() => attachmentPath);

       const cache = new MediaAttachmentCache([{ index: 0, path: attachmentPath }], {
         localPathRoots: [allowedRoot],
@@ -167,10 +170,12 @@ describe("media understanding attachments SSRF", () => {

       await cache.getBuffer({ attachmentIndex: 0, maxBytes: 1024, timeoutMs: 1000 });

-      expect(openSpy).toHaveBeenCalledWith(
-        attachmentPath,
-        fsConstants.O_RDONLY | fsConstants.O_NOFOLLOW,
+      expect(openSpy).toHaveBeenCalled();
+      const [openedPath, openedFlags] = openSpy.mock.calls[0] ?? [];
+      expect(await fs.realpath(String(openedPath)).catch(() => String(openedPath))).toBe(
+        canonicalAttachmentPath,
       );
+      expect(openedFlags).toBe(fsConstants.O_RDONLY | fsConstants.O_NOFOLLOW);
     });
   });
 });

PATCH

echo "Patch applied successfully."
