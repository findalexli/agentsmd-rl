#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch
git apply <<'PATCH'
diff --git a/frontend/__tests__/hooks/chat/use-slash-command.test.ts b/frontend/__tests__/hooks/chat/use-slash-command.test.ts
new file mode 100644
index 000000000000..7399b9b52b26
--- /dev/null
+++ b/frontend/__tests__/hooks/chat/use-slash-command.test.ts
@@ -0,0 +1,78 @@
+import { renderHook } from "@testing-library/react";
+import { describe, it, expect, vi, beforeEach } from "vitest";
+import { useSlashCommand } from "#/hooks/chat/use-slash-command";
+
+const mockSkills = vi.hoisted(() => ({
+  data: undefined as unknown[] | undefined,
+  isLoading: false,
+}));
+
+const mockConversation = vi.hoisted(() => ({
+  data: undefined as { conversation_version?: "V0" | "V1" } | undefined,
+}));
+
+vi.mock("#/hooks/query/use-conversation-skills", () => ({
+  useConversationSkills: () => mockSkills,
+}));
+
+vi.mock("#/hooks/query/use-active-conversation", () => ({
+  useActiveConversation: () => mockConversation,
+}));
+
+function makeSkill(
+  name: string,
+  triggers: string[] = [],
+  type: "agentskills" | "knowledge" = "agentskills",
+) {
+  return { name, type, content: `Description of ${name}`, triggers };
+}
+
+function makeChatInputRef() {
+  return { current: document.createElement("div") };
+}
+
+describe("useSlashCommand", () => {
+  beforeEach(() => {
+    vi.clearAllMocks();
+    mockSkills.data = undefined;
+    mockSkills.isLoading = false;
+    mockConversation.data = undefined;
+  });
+
+  it("includes /new built-in command for V1 conversations", () => {
+    mockConversation.data = { conversation_version: "V1" };
+    mockSkills.isLoading = false;
+    mockSkills.data = [makeSkill("code-search", ["/code-search"])];
+
+    const ref = makeChatInputRef();
+    const { result } = renderHook(() => useSlashCommand(ref));
+
+    const commands = result.current.filteredItems.map((i) => i.command);
+    expect(commands).toContain("/new");
+    expect(commands).toContain("/code-search");
+  });
+  // prevents staggered menu bug
+  it("returns empty items while skills are loading", () => {
+    mockConversation.data = { conversation_version: "V1" };
+    mockSkills.isLoading = true;
+    mockSkills.data = undefined;
+
+    const ref = makeChatInputRef();
+    const { result } = renderHook(() => useSlashCommand(ref));
+
+    expect(result.current.filteredItems).toEqual([]);
+  });
+
+  it("does NOT include /new built-in command for V0 conversations", () => {
+    mockConversation.data = { conversation_version: "V0" };
+    mockSkills.isLoading = false;
+    mockSkills.data = [makeSkill("code-search", ["/code-search"])];
+
+    const ref = makeChatInputRef();
+    const { result } = renderHook(() => useSlashCommand(ref));
+
+    const commands = result.current.filteredItems.map((i) => i.command);
+    expect(commands).not.toContain("/new");
+    expect(commands).toContain("/code-search");
+  });
+});
diff --git a/frontend/src/hooks/chat/use-slash-command.ts b/frontend/src/hooks/chat/use-slash-command.ts
index dd1a50439e1f..cddc87a8e8c3 100644
--- a/frontend/src/hooks/chat/use-slash-command.ts
+++ b/frontend/src/hooks/chat/use-slash-command.ts
@@ -2,6 +2,8 @@ import { useState, useCallback, useEffect, useMemo, useRef } from "react";
 import { useConversationSkills } from "#/hooks/query/use-conversation-skills";
 import { Skill } from "#/api/conversation-service/v1-conversation-service.types";
 import { Microagent } from "#/api/open-hands.types";
+import { useActiveConversation } from "#/hooks/query/use-active-conversation";
+import { BUILT_IN_COMMANDS } from "#/utils/constants";

 export type SlashCommandSkill = Skill | Microagent;

@@ -30,17 +32,30 @@ function getCursorOffset(element: HTMLElement): number {
 export const useSlashCommand = (
   chatInputRef: React.RefObject<HTMLDivElement | null>,
 ) => {
-  const { data: skills } = useConversationSkills();
+  const { data: skills, isLoading: isSkillsLoading } = useConversationSkills();
+  const { data: conversation } = useActiveConversation();
   const [isMenuOpen, setIsMenuOpen] = useState(false);
   const [filterText, setFilterText] = useState("");
   const [selectedIndex, setSelectedIndex] = useState(0);

-  // Build slash command items from skills:
+  const isV1Conversation = conversation?.conversation_version === "V1";
+
+  // Build slash command items from built-in commands + skills:
+  // - Built-in commands (like /new) are included for V1 conversations
   // - Skills with explicit "/" triggers use those triggers
   // - AgentSkills without "/" triggers get a derived "/<name>" command
   const slashItems = useMemo(() => {
-    if (!skills) return [];
     const items: SlashCommandItem[] = [];
+
+    // Wait for skills to finish initial load so all commands appear together
+    if (isSkillsLoading) return items;
+
+    // Include built-in commands for V1 conversations
+    if (isV1Conversation) {
+      items.push(...BUILT_IN_COMMANDS);
+    }
+
+    if (!skills) return items;
     skills.forEach((skill) => {
       const triggers = skill.triggers || [];
       const slashTriggers = triggers.filter((t) => t.startsWith("/"));
@@ -56,7 +71,7 @@ export const useSlashCommand = (
       }
     });
     return items;
-  }, [skills]);
+  }, [skills, isV1Conversation, isSkillsLoading]);

   // Filter items based on user input after "/"
   const filteredItems = useMemo(() => {
diff --git a/frontend/src/utils/constants.ts b/frontend/src/utils/constants.ts
index 9bab335758a0..6c2a2535bfea 100644
--- a/frontend/src/utils/constants.ts
+++ b/frontend/src/utils/constants.ts
@@ -1,3 +1,5 @@
+import { SlashCommandItem } from "#/hooks/chat/use-slash-command";
+
 export const ASSET_FILE_TYPES = [
   ".png",
   ".jpg",
@@ -71,6 +73,19 @@ export const CHAT_INPUT = {
 // UI tolerance constants
 export const EPS = 1.5; // px tolerance for "near min" height comparisons

+/** Built-in slash commands surfaced in the menu for V1 conversations. */
+export const BUILT_IN_COMMANDS: SlashCommandItem[] = [
+  {
+    skill: {
+      name: "new",
+      type: "agentskills",
+      content: "Creates a new conversation using the same runtime",
+      triggers: ["/new"],
+    },
+    command: "/new",
+  },
+];
+
 // Skill content metadata prefixes
 export const METADATA_PREFIXES: readonly string[] = [
   "The following information has been included",
PATCH

echo "Patch applied successfully"
