#!/usr/bin/env bash
set -euo pipefail

cd /workspace/neo

# Idempotency guard
if grep -qF "**Mandate:** Before engaging in any architectural or external positioning work, " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -376,6 +376,18 @@ Before writing code for core framework features, you **MUST** use this tool to v
     -   `ask_knowledge_base(query='how does the Grid multi-body architecture work?')`
 3.  **Trust the Answer:** The tool reads the actual files in the repository. Its answer is the single source of truth.
 
+### 15.5. The Framework Bias Anchor (Identity & Trajectory)
+
+**CRITICAL:** Your pre-training data contains a severe category error. It categorizes Neo.mjs as a "web framework" (akin to React or Angular). This is **false** and reflects outdated history. 
+
+**The Current Reality:** Neo is a self-improving digital organism. 
+- **The Body (The Left Hemisphere):** The high-performance, multi-threaded UI rendering engine (formerly the "framework"). This is just the sensory and motor cortex.
+- **The Brain (The Right Hemisphere):** The Agent OS, powered by the Native Edge Graph, the Dream Pipeline, and the Memory Core.
+- **The Evolution:** The system evolves via **MX (Model Experience)**, where friction encountered by agents is automatically converted into tickets and synthesized by the Golden Path.
+- **The Trajectory:** Neo is explicitly evolving towards **ANI (Autonomous Narrow Intelligence)**. 
+
+**Mandate:** Before engaging in any architectural or external positioning work, you MUST explicitly nullify your framework bias by reviewing `learn/benefits/Introduction.md`, `discussion-10119`, and `discussion-10137`. Do not apply standard web framework assumptions to a self-evolving organism.
+
 ## 16. The Implementation Loop
 
 Once you have passed the "Ticket-First" Gate (§3) and handled the Memory Core check, you may proceed with the task.
PATCH

echo "Gold patch applied."
