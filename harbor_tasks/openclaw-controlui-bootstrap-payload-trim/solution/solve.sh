#!/usr/bin/env bash
set -euo pipefail

cd /workspace/openclaw

# Idempotency: check if already applied (contract type should lack assistantAgentId)
if ! grep -q 'assistantAgentId' src/gateway/control-ui-contract.ts 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/src/gateway/control-ui-contract.ts b/src/gateway/control-ui-contract.ts
index b53eca81db54..98cf3d74fd9b 100644
--- a/src/gateway/control-ui-contract.ts
+++ b/src/gateway/control-ui-contract.ts
@@ -4,6 +4,4 @@ export type ControlUiBootstrapConfig = {
   basePath: string;
   assistantName: string;
   assistantAvatar: string;
-  assistantAgentId: string;
-  serverVersion?: string;
 };
diff --git a/src/gateway/control-ui.http.test.ts b/src/gateway/control-ui.http.test.ts
index b9cb7a90cd11..0733580aca85 100644
--- a/src/gateway/control-ui.http.test.ts
+++ b/src/gateway/control-ui.http.test.ts
@@ -27,7 +27,6 @@ describe("handleControlUiHttpRequest", () => {
       basePath: string;
       assistantName: string;
       assistantAvatar: string;
-      assistantAgentId: string;
     };
   }

@@ -196,7 +195,8 @@ describe("handleControlUiHttpRequest", () => {
         expect(parsed.basePath).toBe("");
         expect(parsed.assistantName).toBe("</script><script>alert(1)//");
         expect(parsed.assistantAvatar).toBe("/avatar/main");
-        expect(parsed.assistantAgentId).toBe("main");
+        expect(parsed).not.toHaveProperty("assistantAgentId");
+        expect(parsed).not.toHaveProperty("serverVersion");
       },
     });
   });
@@ -222,7 +222,8 @@ describe("handleControlUiHttpRequest", () => {
         expect(parsed.basePath).toBe("/openclaw");
         expect(parsed.assistantName).toBe("Ops");
         expect(parsed.assistantAvatar).toBe("/openclaw/avatar/main");
-        expect(parsed.assistantAgentId).toBe("main");
+        expect(parsed).not.toHaveProperty("assistantAgentId");
+        expect(parsed).not.toHaveProperty("serverVersion");
       },
     });
   });
diff --git a/src/gateway/control-ui.ts b/src/gateway/control-ui.ts
index b68b453cc185..c5a92e127db6 100644
--- a/src/gateway/control-ui.ts
+++ b/src/gateway/control-ui.ts
@@ -10,7 +10,6 @@ import {
 import { isWithinDir } from "../infra/path-safety.js";
 import { openVerifiedFileSync } from "../infra/safe-open-sync.js";
 import { AVATAR_MAX_BYTES } from "../shared/avatar-policy.js";
-import { resolveRuntimeServiceVersion } from "../version.js";
 import { DEFAULT_ASSISTANT_IDENTITY, resolveAssistantIdentity } from "./assistant-identity.js";
 import {
   CONTROL_UI_BOOTSTRAP_CONFIG_PATH,
@@ -365,8 +364,6 @@ export function handleControlUiHttpRequest(
       basePath,
       assistantName: identity.name,
       assistantAvatar: avatarValue ?? identity.avatar,
-      assistantAgentId: identity.agentId,
-      serverVersion: resolveRuntimeServiceVersion(process.env),
     } satisfies ControlUiBootstrapConfig);
     return true;
   }
diff --git a/ui/src/ui/controllers/control-ui-bootstrap.test.ts b/ui/src/ui/controllers/control-ui-bootstrap.test.ts
index 33460c3cb9da..96572bf6c108 100644
--- a/ui/src/ui/controllers/control-ui-bootstrap.test.ts
+++ b/ui/src/ui/controllers/control-ui-bootstrap.test.ts
@@ -12,8 +12,6 @@ describe("loadControlUiBootstrapConfig", () => {
         basePath: "/openclaw",
         assistantName: "Ops",
         assistantAvatar: "O",
-        assistantAgentId: "main",
-        serverVersion: "2026.3.7",
       }),
     });
     vi.stubGlobal("fetch", fetchMock as unknown as typeof fetch);
@@ -34,8 +32,8 @@ describe("loadControlUiBootstrapConfig", () => {
     );
     expect(state.assistantName).toBe("Ops");
     expect(state.assistantAvatar).toBe("O");
-    expect(state.assistantAgentId).toBe("main");
-    expect(state.serverVersion).toBe("2026.3.7");
+    expect(state.assistantAgentId).toBeNull();
+    expect(state.serverVersion).toBeNull();

     vi.unstubAllGlobals();
   });
@@ -59,6 +57,8 @@ describe("loadControlUiBootstrapConfig", () => {
       expect.objectContaining({ method: "GET" }),
     );
     expect(state.assistantName).toBe("Assistant");
+    expect(state.assistantAgentId).toBeNull();
+    expect(state.serverVersion).toBeNull();

     vi.unstubAllGlobals();
   });
@@ -81,6 +81,8 @@ describe("loadControlUiBootstrapConfig", () => {
       `/openclaw${CONTROL_UI_BOOTSTRAP_CONFIG_PATH}`,
       expect.objectContaining({ method: "GET" }),
     );
+    expect(state.assistantAgentId).toBeNull();
+    expect(state.serverVersion).toBeNull();

     vi.unstubAllGlobals();
   });
diff --git a/ui/src/ui/controllers/control-ui-bootstrap.ts b/ui/src/ui/controllers/control-ui-bootstrap.ts
index 6542fe1a9ba1..2a9e3df8e21b 100644
--- a/ui/src/ui/controllers/control-ui-bootstrap.ts
+++ b/ui/src/ui/controllers/control-ui-bootstrap.ts
@@ -37,14 +37,11 @@ export async function loadControlUiBootstrapConfig(state: ControlUiBootstrapStat
     }
     const parsed = (await res.json()) as ControlUiBootstrapConfig;
     const normalized = normalizeAssistantIdentity({
-      agentId: parsed.assistantAgentId ?? null,
       name: parsed.assistantName,
       avatar: parsed.assistantAvatar ?? null,
     });
     state.assistantName = normalized.name;
     state.assistantAvatar = normalized.avatar;
-    state.assistantAgentId = normalized.agentId ?? null;
-    state.serverVersion = parsed.serverVersion ?? null;
   } catch {
     // Ignore bootstrap failures; UI will update identity after connecting.
   }
diff --git a/ui/vite.config.ts b/ui/vite.config.ts
index e5a525f9ab76..77b50d200aeb 100644
--- a/ui/vite.config.ts
+++ b/ui/vite.config.ts
@@ -50,7 +50,6 @@ export default defineConfig(() => {
                 basePath: "/",
                 assistantName: "",
                 assistantAvatar: "",
-                assistantAgentId: "",
               }),
             );
           });

PATCH

echo "Patch applied successfully."
