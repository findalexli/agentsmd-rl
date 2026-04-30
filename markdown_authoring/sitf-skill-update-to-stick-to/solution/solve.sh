#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sitf

# Idempotency guard
if grep -qF "**Example:** If an attacker uses CI/CD as initial access, then pivots to cloud p" ".claude/skills/technique-proposal/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/technique-proposal/SKILL.md b/.claude/skills/technique-proposal/SKILL.md
@@ -33,18 +33,53 @@ When this skill is invoked:
    - Verify no existing technique covers this attack step
    - If a match exists, report it and exit
 
-3. Identify the correct component:
+3. **Verify the attack step is within SITF scope** (see Scope Boundaries below)
+
+4. Identify the correct component:
    - endpoint: Developer workstations, IDEs, local tools
    - vcs: Version control systems (GitHub, GitLab, etc.)
    - cicd: CI/CD pipelines, runners, workflows
    - registry: Package registries, container registries
-   - production: Production infrastructure, cloud environments
+   - production: Production infrastructure **as it relates to supply chain attacks**
 
-4. Determine the attack stage:
+5. Determine the attack stage:
    - Initial Access: First foothold in the component
    - Discovery and Lateral Movement: Enumeration, pivoting, credential theft
    - Post-Compromise: Data exfiltration, destruction, persistence
 
+### Scope Boundaries
+
+**SITF covers SDLC infrastructure and software supply chain attacks specifically.** Not all attack steps in an incident warrant new SITF techniques.
+
+#### In Scope (propose technique)
+- Attacks on developer workstations, IDEs, and local development tools
+- Attacks on version control systems and source code
+- Attacks on CI/CD pipelines, runners, and build systems
+- Attacks on package/container registries
+- Production techniques that are **supply-chain-specific**:
+  - Backdooring deployed artifacts to compromise downstream consumers
+  - Stealing code signing keys or certificates
+  - Modifying release pipelines or deployment configurations
+  - Accessing production to pivot back into SDLC systems
+
+#### Out of Scope (do NOT propose technique)
+- Generic cloud infrastructure attacks (IAM privilege escalation, cloud misconfigurations)
+- Generic container/Kubernetes attacks (pod escape, RBAC abuse, kubelet exploits)
+- Generic network attacks (lateral movement via SSH, RDP exploitation)
+- Post-exploitation techniques that don't relate to software supply chain
+
+**Example:** If an attacker uses CI/CD as initial access, then pivots to cloud production and uses a Kubernetes privilege escalation technique, the K8s privesc is **out of scope** for SITF. Instead:
+
+1. For attack flows: Mark the step with `"type": "out-of-scope"` and reference the appropriate framework (e.g., "MITRE ATT&CK: Escape to Host - T1611")
+2. For technique proposals: Report that the attack step is outside SITF's domain and does not warrant a new technique
+
+**Rationale:** These generic infrastructure techniques are already well-documented in:
+- MITRE ATT&CK for Enterprise (Cloud, Containers matrices)
+- MITRE ATT&CK for ICS
+- Cloud-specific frameworks (AWS Security Maturity Model, Azure Security Benchmark)
+
+SITF adds value by covering the **unique attack surface of SDLC infrastructure** that these frameworks don't address comprehensively.
+
 ### Phase 2: Technique ID Assignment
 
 1. Find the highest existing ID for the target component:
@@ -124,6 +159,7 @@ Markdown-formatted PR description including:
 Run this checklist before outputting:
 
 ```
+[ ] Attack step is within SITF scope (SDLC/supply-chain-specific, not generic infra)
 [ ] ID follows component naming pattern (T-E/V/C/R/P + number)
 [ ] ID doesn't conflict with existing techniques in techniques.json
 [ ] Name is action-oriented verb phrase
@@ -136,6 +172,8 @@ Run this checklist before outputting:
 [ ] JSON is valid and properly formatted
 ```
 
+**If scope check fails:** Do not generate a technique proposal. Instead, explain why the attack step is out of scope and recommend the appropriate framework (MITRE ATT&CK, etc.).
+
 ### Phase 6: Output Location
 
 1. Display the full proposal in the conversation
PATCH

echo "Gold patch applied."
