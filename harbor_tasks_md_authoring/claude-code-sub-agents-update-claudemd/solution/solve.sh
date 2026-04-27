#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-sub-agents

# Idempotency guard
if grep -qF "E -- YES ---> F[Use subset of previous team<br/>Max 3 agents]" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -66,9 +66,9 @@ To understand your critical role, here is the process you are kicking off:
 ```mermaid
 graph TD
     A[User provides prompt] --> B{Claude Code - The Dispatcher};
-    B --> C{Is the request non-trivial?};
-    C -- YES --> D[**Invoke agent_organizer**];
-    C -- NO --> E[Answer directly];
+    B --> C{Is the request trivial?};
+    C -- YES --> E[Answer directly];
+    C -- NO --> D[**Invoke agent_organizer**];
     D --> F[Agent Organizer analyzes project & prompt];
     F --> G[Agent Organizer assembles agent team & defines workflow];
     G --> H[Sub-agents execute tasks in sequence/parallel];
@@ -127,10 +127,10 @@ graph TD
     B --> C{New domain or major scope change?}
     C -- YES --> D[Re-run agent-organizer]
     C -- NO --> E{Can previous agents handle this?}
-    E -- YES --> F[Use subset of previous team<br/>Max 3 agents]
     E -- NO --> G{Simple clarification or minor task?}
-    G -- YES --> H[Handle directly without sub-agents]
     G -- NO --> D
+    G -- YES --> H[Handle directly without sub-agents]
+    E -- YES ---> F[Use subset of previous team<br/>Max 3 agents]
     
     style D fill:#dcedc8,stroke:#333,stroke-width:2px
     style F fill:#fff3e0,stroke:#333,stroke-width:2px  
PATCH

echo "Gold patch applied."
