#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sitf

# Idempotency guard
if grep -qF "description: Generate SITF-compliant attack flow JSON files from attack descript" ".claude/skills/attack-flow/SKILL.md" && grep -qF "description: Generate a PR-ready technique proposal when an attack step doesn't " ".claude/skills/technique-proposal/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/attack-flow/SKILL.md b/.claude/skills/attack-flow/SKILL.md
@@ -0,0 +1,146 @@
+---
+name: attack-flow
+description: Generate SITF-compliant attack flow JSON files from attack descriptions or incident reports. Use when analyzing supply chain attacks, breaches, or security incidents.
+argument-hint: <attack-name> [websearch|url]
+tools: Read, Grep, Glob, WebSearch, WebFetch, Write, Bash
+---
+
+# Attack Flow Generator
+
+Generate SITF-compliant attack flow JSON files from attack descriptions or incident reports.
+
+## Usage
+
+```
+/attack-flow <attack-name> [source]
+```
+
+- `attack-name`: Identifier for the attack (e.g., "s1ngularity", "solarwinds")
+- `source`: URL, "websearch" for auto-research, or omit to use conversation context
+
+Arguments: $ARGUMENTS
+
+## Instructions
+
+When this skill is invoked:
+
+### Phase 1: Research
+
+1. If source is "websearch" or a URL, gather attack details:
+   - Attack timeline and phases
+   - Entry point and initial access method
+   - Lateral movement and persistence techniques
+   - Data exfiltration or impact
+   - Affected components (CI/CD, VCS, Registry, Endpoint, Production)
+
+2. If source is omitted, use context from the current conversation.
+
+### Phase 2: Technique Mapping
+
+1. Read `techniques.json` to get the full technique library.
+
+2. For each attack step, find the best matching technique:
+   - Match by **action semantics**, not surface keywords
+   - Example: Uploading stolen data to repos → T-V003 (Secret Exfiltration), NOT T-V008 (Malicious Hosting)
+   - Example: Accessing VCS with stolen creds → T-V001 must come BEFORE any VCS actions
+
+3. If no matching technique exists:
+   - Create a placeholder node with `"type": "technique-gap"`
+   - Include suggested technique metadata in the data field
+   - Note in output that `/technique-proposal` should be run for gaps
+
+### Phase 3: Layout Calculation
+
+Apply these layout rules:
+
+#### Rule 1: Component Layout (Left-to-Right by Attack Flow)
+- Order components by their **sequence in the attack chain**, not by standard SITF order
+- If attack flows CI/CD → Registry → Endpoint → VCS, layout left-to-right accordingly
+- Minimum horizontal gap between components: 80-100px
+- Component x-positions: Use increments of ~300px starting from x=0
+
+#### Rule 2: Technique Ordering (Top-to-Bottom)
+- **Primary**: Order techniques by their **sequence in the attack flow**
+- **Secondary**: Within same attack step, order by stage (Initial Access → Discovery → Post-Compromise)
+- Vertical gap between techniques: ~130-150px
+- First technique starts at y = component.y + 80
+
+#### Rule 3: Technique-Component Alignment
+- Every technique node MUST be visually positioned within its parent component
+- Calculate x-position: `component.x + 30`
+- Validate technique.data.component matches parent component.data.componentId
+
+#### Rule 4: Component Sizing
+- Height = (technique_count × 150) + 120 (padding)
+- Width = 230-250px
+
+#### Rule 5: Edge Connections
+- Connect source.bottom → target.top for vertical flows within component
+- Connect source.right → target.left for cross-component flows
+- Add labels for significant transitions ("Second wave", etc.)
+- Use `"type": "smoothstep"` for all edges
+
+### Phase 4: JSON Generation
+
+Generate the attack flow JSON with this structure:
+
+```json
+{
+  "metadata": {
+    "name": "Attack Name",
+    "created": "ISO-8601 timestamp",
+    "version": "1.0",
+    "framework": "SITF",
+    "description": "Brief attack description"
+  },
+  "nodes": [
+    // Entry points, components, techniques, exit points
+  ],
+  "edges": [
+    // Connections between nodes
+  ]
+}
+```
+
+Node types:
+- `entryPoint`: Attack entry (Phishing, Vulnerability Exploit, Stolen Credentials, etc.)
+- `component`: SITF component container (endpoint, vcs, cicd, registry, production)
+- `technique`: Attack technique from techniques.json
+- `technique-gap`: Placeholder for missing technique (flag for /technique-proposal)
+- `exitPoint`: Attack outcome (Future Breach, Persistence, Secondary Supply Chain Attack, etc.)
+
+### Phase 5: Validation
+
+Run this checklist before outputting:
+
+```
+[ ] Valid JSON structure (parse test passes)
+[ ] Required fields present: metadata.{name,created,version,framework}, nodes[], edges[]
+[ ] All node IDs are unique
+[ ] All edge source/target reference valid node IDs
+[ ] All techniques positioned within their component boundaries (x/y validation)
+[ ] Techniques ordered by attack flow sequence
+[ ] Initial Access techniques appear first when order is ambiguous
+[ ] All technique IDs exist in techniques.json OR flagged as technique-gap
+[ ] Exit points connected to terminal techniques
+[ ] No orphaned nodes (every non-entry node has incoming edge)
+```
+
+### Phase 6: Output
+
+1. Write the JSON file to `sample-flows/<attack-name>.json`
+2. Validate the JSON with Python: `python3 -c "import json; json.load(open('file'))"`
+3. Provide a summary table of the attack flow
+4. If any technique-gaps exist, list them and recommend running `/technique-proposal`
+
+## Example
+
+```
+/attack-flow s1ngularity websearch
+```
+
+This will:
+1. Search for s1ngularity attack details
+2. Map attack steps to SITF techniques
+3. Generate `sample-flows/s1ngularity.json`
+4. Output attack flow summary
diff --git a/.claude/skills/technique-proposal/SKILL.md b/.claude/skills/technique-proposal/SKILL.md
@@ -0,0 +1,226 @@
+---
+name: technique-proposal
+description: Generate a PR-ready technique proposal when an attack step doesn't map to existing SITF techniques. Use after /attack-flow identifies technique gaps.
+argument-hint: "<description>" [component]
+tools: Read, Grep, Glob
+---
+
+# Technique Proposal Generator
+
+Generate a PR-ready technique proposal when an attack step doesn't map to existing SITF techniques.
+
+## Usage
+
+```
+/technique-proposal <description> [component]
+```
+
+- `description`: Description of the attack step or gap
+- `component`: Target component (endpoint, vcs, cicd, registry, production) - optional, will be inferred if omitted
+
+Arguments: $ARGUMENTS
+
+## Instructions
+
+When this skill is invoked:
+
+### Phase 1: Gap Analysis
+
+1. Read `techniques.json` to understand existing techniques.
+
+2. Confirm the gap:
+   - Search for semantically similar techniques
+   - Verify no existing technique covers this attack step
+   - If a match exists, report it and exit
+
+3. Identify the correct component:
+   - endpoint: Developer workstations, IDEs, local tools
+   - vcs: Version control systems (GitHub, GitLab, etc.)
+   - cicd: CI/CD pipelines, runners, workflows
+   - registry: Package registries, container registries
+   - production: Production infrastructure, cloud environments
+
+4. Determine the attack stage:
+   - Initial Access: First foothold in the component
+   - Discovery and Lateral Movement: Enumeration, pivoting, credential theft
+   - Post-Compromise: Data exfiltration, destruction, persistence
+
+### Phase 2: Technique ID Assignment
+
+1. Find the highest existing ID for the target component:
+   - Endpoint: T-E###
+   - VCS: T-V###
+   - CI/CD: T-C###
+   - Registry: T-R###
+   - Production: T-P###
+
+2. Assign the next sequential number.
+
+### Phase 3: Technique Definition
+
+Generate the technique entry following these conventions:
+
+#### Name
+- Action-oriented verb phrase
+- Match style of existing techniques in same component
+- Avoid vendor-specific terms unless unavoidable
+- Examples: "Abuse Local AI Tools", "Harvest Local Secrets", "Turn Private Repos Public"
+
+#### Description
+- Single sentence describing the attack action
+- Focus on what the attacker does, not the impact
+- Start with "Attacker..." for consistency
+
+#### Risks
+- Focus on **why** this attack is possible (enabling conditions)
+- Describe misconfigurations, missing controls, insecure defaults
+- Keep each risk as a concise phrase, not a full sentence
+- Reference similar risks from related techniques for consistency
+
+#### Controls
+- Balance preventive and detective controls
+- Reference existing controls from techniques.json for consistency
+- Ensure controls are actionable and specific
+- Consider both technical and process controls
+
+### Phase 4: Generate Output
+
+Produce a structured proposal with three sections:
+
+#### Section 1: Rationale
+Explain:
+- What attack behavior this technique covers
+- Why existing techniques don't cover it
+- Reference to real-world attack(s) demonstrating this technique
+
+#### Section 2: Technique JSON
+```json
+{
+  "id": "T-X###",
+  "name": "Technique Name",
+  "component": "component-id",
+  "stage": "Attack Stage",
+  "description": "Attacker does X to achieve Y",
+  "risks": [
+    "Enabling condition 1",
+    "Enabling condition 2"
+  ],
+  "controls": [
+    "Control measure 1",
+    "Control measure 2"
+  ]
+}
+```
+
+#### Section 3: PR Description
+Markdown-formatted PR description including:
+- Title: "Add technique T-X###: Technique Name"
+- Summary of the technique
+- Real-world references
+- Link to related attack flow if applicable
+
+### Phase 5: Validation
+
+Run this checklist before outputting:
+
+```
+[ ] ID follows component naming pattern (T-E/V/C/R/P + number)
+[ ] ID doesn't conflict with existing techniques in techniques.json
+[ ] Name is action-oriented verb phrase
+[ ] Name matches naming style of component's existing techniques
+[ ] Stage correctly reflects attack progression semantics
+[ ] Description starts with "Attacker..."
+[ ] Risks explain enabling conditions, not impacts
+[ ] Controls are actionable and specific
+[ ] No semantic duplicate of existing technique
+[ ] JSON is valid and properly formatted
+```
+
+### Phase 6: Output Location
+
+1. Display the full proposal in the conversation
+2. Optionally create a file at `technique-proposals/<technique-id>.md` if requested
+
+## Example
+
+```
+/technique-proposal "Malware invokes AI CLI tools with permission-bypass flags to scan filesystem" endpoint
+```
+
+### Example Output
+
+```markdown
+## Technique Proposal: T-E019
+
+### Rationale
+
+The s1ngularity attack (August 2025) demonstrated a novel technique where
+malware invoked AI CLI tools (Claude, Gemini, Q) with permission-bypass
+flags like `--dangerously-skip-permissions` to scan filesystems and catalog
+sensitive files.
+
+Existing technique T-E009 (Abuse Local AI Tools) focuses on using AI
+assistants to exfiltrate code or inject malicious suggestions via AI
+services. It does not cover the scenario where attackers weaponize local
+AI tools for automated reconnaissance by exploiting dangerous CLI flags.
+
+### Proposed Addition to techniques.json
+
+{
+  "id": "T-E019",
+  "name": "Weaponize AI CLI Tools for Reconnaissance",
+  "component": "endpoint",
+  "stage": "Discovery and Lateral Movement",
+  "description": "Attacker invokes AI CLI tools with permission-bypass flags to scan filesystem and catalog sensitive files for exfiltration",
+  "risks": [
+    "AI CLI tools support dangerous permission-bypass flags",
+    "No restrictions on AI tool command-line invocation",
+    "AI tools have broad filesystem access",
+    "No monitoring of AI tool execution patterns",
+    "AI tools can be invoked non-interactively by scripts"
+  ],
+  "controls": [
+    "Disable or remove dangerous permission-bypass flags from AI tools",
+    "AI tool invocation monitoring and alerting",
+    "Filesystem access restrictions for AI tool processes",
+    "EDR detection rules for AI tool abuse patterns",
+    "Require interactive confirmation for sensitive AI operations",
+    "Application allowlisting for AI tool binaries"
+  ]
+}
+
+### PR Description
+
+**Add technique T-E019: Weaponize AI CLI Tools for Reconnaissance**
+
+This PR adds a new endpoint technique to cover the weaponization of AI CLI
+tools for automated reconnaissance, as demonstrated in the s1ngularity
+supply chain attack (August 2025).
+
+The attack showed that malware can invoke AI coding assistants with
+permission-bypass flags (e.g., `--dangerously-skip-permissions`, `--yolo`,
+`--trust-all-tools`) to recursively scan filesystems and catalog sensitive
+files without user interaction.
+
+**References:**
+- https://www.wiz.io/blog/s1ngularity-supply-chain-attack
+- https://www.stepsecurity.io/blog/supply-chain-security-alert-popular-nx-build-system-package-compromised-with-data-stealing-malware
+
+**Related:** sample-flows/s1ngularity.json
+```
+
+## Workflow Integration
+
+This skill is typically used after `/attack-flow` identifies technique gaps:
+
+```
+/attack-flow <attack-name>
+    ↓
+[Gaps identified]
+    ↓
+/technique-proposal "<gap description>" <component>
+    ↓
+[Submit PR with proposed technique]
+    ↓
+[After merge, re-run /attack-flow]
+```
PATCH

echo "Gold patch applied."
