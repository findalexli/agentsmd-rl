#!/usr/bin/env bash
set -euo pipefail

cd /workspace/developer-kit

# Idempotency guard
if grep -qF "7. **Never change issue status autonomously** \u2014 Always present issues to the use" "plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md b/plugins/developer-kit-tools/skills/sonarqube-mcp/SKILL.md
@@ -29,51 +29,49 @@ Use this skill when:
 
 **Trigger phrases:** "check quality gate", "sonarqube quality gate", "find sonar issues", "search sonar issues", "analyze code with sonar", "check sonar rule", "sonarcloud issues", "pre-push sonar check", "sonar pre-commit"
 
-## Prerequisites
+## Prerequisites and Setup
 
 The plugin includes a `.mcp.json` that starts the SonarQube MCP Server automatically via Docker. Before using this skill, set the required environment variables:
 
-**SonarQube Server (remote):**
+**SonarQube Server (remote or local):**
 ```bash
 export SONARQUBE_TOKEN="squ_your_token"
-export SONARQUBE_URL="https://sonarqube.mycompany.com"
-```
-
-**SonarQube Server (local Docker on macOS/Windows):**
-```bash
-export SONARQUBE_TOKEN="squ_your_token"
-export SONARQUBE_URL="http://host.docker.internal:9000"
-# Do NOT use localhost or 127.0.0.1 — Docker containers cannot reach them
+export SONARQUBE_URL="https://sonarqube.mycompany.com"  # or http://host.docker.internal:9000 for local Docker
 ```
 
 **SonarCloud:**
 ```bash
 export SONARQUBE_TOKEN="squ_your_token"
 export SONARQUBE_ORG="your-org-key"   # required for SonarCloud
-# SONARQUBE_URL is not set for SonarCloud
+# SONARQUBE_URL is not needed for SonarCloud
 ```
 
-**Configuration file (all platforms):** The MCP server reads credentials from `~/.sonarqube_mcp`. Create this file once:
-
-```bash
-# ~/.sonarqube_mcp
-export SONARQUBE_TOKEN="squ_your_token"
-export SONARQUBE_URL="http://host.docker.internal:9000"  # local SonarQube
-# export SONARQUBE_ORG="your-org-key"                   # SonarCloud only
-```
-
-> **Note for macOS:** Claude Code is a GUI application and does not inherit variables exported in `.zshrc`. The `~/.sonarqube_mcp` file is sourced directly by the MCP server launcher, so no `launchctl` or shell restart is needed.
-
 **Requirements:**
 - Docker must be installed and running
 - `SONARQUBE_TOKEN` is always required
 - `SONARQUBE_URL` is required for SonarQube Server (use `host.docker.internal` for local instances)
 - `SONARQUBE_ORG` is required for SonarCloud (omit `SONARQUBE_URL` in that case)
 
-Verify MCP tool availability before proceeding:
-- Tool names follow the pattern: `mcp__sonarqube-mcp__<tool-name>`
+## Quick Start
+
+1. Set your SonarQube/SonarCloud credentials:
+   ```bash
+   # SonarQube Server
+   export SONARQUBE_TOKEN="squ_your_token"
+   export SONARQUBE_URL="https://sonarqube.mycompany.com"
+
+   # SonarCloud
+   export SONARQUBE_TOKEN="squ_your_token"
+   export SONARQUBE_ORG="your-org-key"
+   ```
+
+2. Verify MCP tool availability:
+   - Tool names follow the pattern: `mcp__sonarqube-mcp__<tool-name>`
 
-If the MCP server fails to start, check that Docker is running and the environment variables (`SONARQUBE_TOKEN`, `SONARQUBE_URL` or `SONARQUBE_ORG`) are set. Reference: [mcp/sonarqube on Docker Hub](https://hub.docker.com/r/mcp/sonarqube)
+3. If the MCP server fails to start, check:
+   - Docker is running
+   - Environment variables are set
+   - Reference: [mcp/sonarqube on Docker Hub](https://hub.docker.com/r/mcp/sonarqube)
 
 ## Reference Documents
 
@@ -350,13 +348,14 @@ Group results by category (Security, Reliability, Maintainability) and present t
 
 ## Best Practices
 
-1. **Always check quality gate before merge** — Run `get_project_quality_gate_status` as part of any PR review workflow
-2. **Shift left on security issues** — Use `analyze_code_snippet` during development, not only in CI
-3. **Prioritize by severity** — Address BLOCKER and HIGH issues first; document decisions for MEDIUM and LOW
-4. **Use `show_rule` for unfamiliar keys** — Never dismiss a rule without understanding its intent
-5. **Paginate large result sets** — Use `p` and `ps` parameters; handle multi-page responses for complete coverage
-6. **Never change issue status autonomously** — Always present issues to the user and get explicit confirmation before calling `change_sonar_issue_status`
-7. **Provide language hints** — Specify `language` in `analyze_code_snippet` for more accurate analysis
+1. **Environment Setup** — Set credentials once per session; the MCP server automatically picks them up
+2. **Always check quality gate before merge** — Run `get_project_quality_gate_status` as part of any PR review workflow
+3. **Shift left on security issues** — Use `analyze_code_snippet` during development, not only in CI
+4. **Prioritize by severity** — Address BLOCKER and HIGH issues first; document decisions for MEDIUM and LOW
+5. **Use `show_rule` for unfamiliar keys** — Never dismiss a rule without understanding its intent
+6. **Paginate large result sets** — Use `p` and `ps` parameters; handle multi-page responses for complete coverage
+7. **Never change issue status autonomously** — Always present issues to the user and get explicit confirmation before calling `change_sonar_issue_status`
+8. **Provide language hints** — Specify `language` in `analyze_code_snippet` for more accurate analysis
 
 ## Constraints and Warnings
 
PATCH

echo "Gold patch applied."
