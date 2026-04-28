#!/usr/bin/env bash
set -euo pipefail

cd /workspace/genlayer-studio

# Idempotency guard
if grep -qF ".claude/skills/argocd-debug/SKILL.md" ".claude/skills/argocd-debug/SKILL.md" && grep -qF "argocd app logs studio-prd-workload --name studio-consensus-worker --tail 500 2>" ".claude/skills/discord-community-feedback/SKILL.md" && grep -qF "**Important:** The `argocd app logs --name <container>` command automatically ag" ".claude/skills/hosted-studio-debug/SKILL.md" && grep -qF "source .venv/bin/activate && export PYTHONPATH=\"$(pwd)\" && gltest --contracts-di" ".claude/skills/integration-tests/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/argocd-debug/SKILL.md b/.claude/skills/argocd-debug/SKILL.md
@@ -1,102 +0,0 @@
----
-name: argocd-debug
-description: Debug GenLayer Studio deployments via ArgoCD CLI
----
-
-# ArgoCD Debug Skill
-
-Debug GenLayer Studio deployments via ArgoCD CLI.
-
-## Workload Manifests
-
-Kubernetes manifests are in sibling repo `../devexp-apps-workload` (assume by default, ask user if not found):
-
-```
-devexp-apps-workload/workload/
-├── dev/           # studio-dev, rally-studio-dev
-├── stg/           # studio-stg
-├── prd/           # studio-prd, rally-studio-prd
-```
-
-Each contains Deployments, Services, Ingresses, ExternalSecrets managed by ArgoCD.
-
-## Prerequisites
-
-- Logged into ArgoCD CLI
-- Access to target cluster
-
-## Quick Commands
-
-```bash
-# Check app health
-argocd app get <app>-workload
-
-# List resources
-argocd app resources <app>-workload
-
-# Tail consensus worker logs
-argocd app logs <app>-workload --name studio-consensus-worker --tail 200
-
-# Check for errors
-argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -i error
-```
-
-## Common Issues
-
-### Transaction Timeouts
-
-Consensus worker timeouts usually mean GenVM Manager is unresponsive.
-
-```bash
-# Check for GenVM timeouts
-argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(timeout|SocketTimeoutError|127.0.0.1:3999)"
-
-# Empty stdout = GenVM never started
-argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep "stdout=''"
-```
-
-**Root cause**: GenVM Manager (`genvm-modules manager --port 3999`) becomes unresponsive.
-**Fix**: Worker restart (auto or manual) restarts GenVM Manager.
-
-Key files:
-- `backend/node/genvm/origin/base_host.py:463` - where timeouts occur
-- `backend/node/base.py` - Manager.create() spawns GenVM
-- `backend/consensus/worker_service.py` - worker startup/health
-
-### Pod Restarts
-
-```bash
-# Check restart timestamps in logs
-argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(Started|Uvicorn running)"
-
-# Via kubectl
-kubectl get pods -n <namespace> -o wide
-kubectl get events -n <namespace> --sort-by='.lastTimestamp'
-```
-
-### External API Failures
-
-Contracts calling external APIs (Twitter, etc.) through proxies:
-
-```bash
-# Check for HTTP errors in contract execution
-argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(HTTP|fetch|proxy|api)"
-```
-
-## Environment Apps
-
-| Env | App | Namespace |
-|-----|-----|-----------|
-| dev | studio-dev-workload | studio-dev |
-| stg | studio-stg-workload | studio-stg |
-| prd | studio-prd-workload | studio-prd |
-| rally-prd | rally-studio-prd-workload | rally-studio-prd |
-
-## Components
-
-| Component | Purpose | Common Issues |
-|-----------|---------|---------------|
-| studio-consensus-worker | Tx processing | Timeouts, GenVM crashes |
-| studio-jsonrpc | RPC API | DB connections |
-| studio-webdriver | Browser sandbox | Memory, crashes |
-| database-migration | Schema updates | Lock contention |
diff --git a/.claude/skills/discord-community-feedback/SKILL.md b/.claude/skills/discord-community-feedback/SKILL.md
@@ -0,0 +1,103 @@
+---
+name: discord-community-feedback
+description: Monitor Discord community channel for user-reported bugs and issues
+---
+
+# Discord Community Feedback Skill
+
+Monitor the GenLayer Discord community feedback channel for user-reported bugs, issues, and problems.
+
+## Prerequisites
+
+- Discord MCP server configured and running ([discordmcp](https://github.com/v-3/discordmcp))
+- Bot added to the GenLayer Discord server with read permissions
+
+## Channel Information
+
+| Field | Value |
+|-------|-------|
+| Server ID | 1237055789441487021 |
+| Channel ID | 1237114454877929482 |
+
+## Quick Commands
+
+Use the Discord MCP `read-messages` tool to fetch recent messages:
+
+```
+Tool: read-messages
+Channel: 1237114454877929482
+Limit: 100  (max allowed)
+```
+
+## Identifying User Problems
+
+When reviewing messages, look for these indicators of issues:
+
+### Problem Keywords
+- **Errors**: error, bug, broken, crash, fail, exception
+- **Functionality**: not working, doesn't work, can't, unable, stuck
+- **Help requests**: help, issue, problem, wrong, weird
+- **Performance**: slow, timeout, hang, freeze, unresponsive
+
+### Common User-Reported Issues
+
+| Category | Example Patterns | Related Component |
+|----------|------------------|-------------------|
+| Transaction failures | "tx failed", "transaction stuck" | consensus-worker |
+| Contract errors | "contract not deploying", "execution error" | genvm, consensus-worker |
+| UI issues | "page not loading", "button doesn't work" | frontend |
+| API errors | "RPC error", "connection failed" | jsonrpc |
+| Wallet issues | "can't connect wallet", "balance wrong" | frontend, jsonrpc |
+
+## Workflow
+
+1. **Fetch recent messages** from the feedback channel (up to 100)
+2. **Scan for problem indicators** using keywords above
+3. **Categorize issues** by component (frontend, backend, consensus, etc.)
+4. **Cross-reference with logs** using the `hosted-studio-debug` skill if needed
+5. **Summarize findings** for the team
+
+## Triage Priority
+
+| Priority | Indicators |
+|----------|------------|
+| High | Multiple users reporting same issue, "everything broken", data loss |
+| Medium | Single user with reproducible issue, feature not working |
+| Low | Questions, minor UI glitches, feature requests |
+
+## Integration with Hosted Studio Debug
+
+If a user reports an issue that might be related to the hosted environment:
+
+1. Note the approximate time of the user's report
+2. Use `hosted-studio-debug` skill to check logs around that time
+3. Look for correlating errors in consensus-worker or jsonrpc logs
+
+```bash
+# Example: Check for errors around the time of a user report
+argocd app logs studio-prd-workload --name studio-consensus-worker --tail 500 2>&1 | grep -iE "(error|exception|timeout)"
+```
+
+## Response Template
+
+When summarizing community feedback:
+
+```
+## Community Feedback Summary
+
+**Period**: [time range of messages reviewed]
+**Total Messages**: [count]
+**Issues Identified**: [count]
+
+### High Priority
+- [Issue description] - Reported by [count] users
+
+### Medium Priority
+- [Issue description]
+
+### Low Priority / Questions
+- [Description]
+
+### No Issues
+[If no problems found, note this]
+```
diff --git a/.claude/skills/hosted-studio-debug/SKILL.md b/.claude/skills/hosted-studio-debug/SKILL.md
@@ -0,0 +1,150 @@
+---
+name: hosted-studio-debug
+description: Debug GenLayer Studio deployments via ArgoCD CLI
+---
+
+# Hosted Studio Debug Skill
+
+Debug GenLayer Studio deployments via ArgoCD CLI.
+
+## Workload Manifests
+
+Kubernetes manifests are in sibling repo `../devexp-apps-workload` (assume by default, ask user if not found):
+
+```
+devexp-apps-workload/workload/
+├── dev/           # studio-dev, rally-studio-dev
+├── stg/           # studio-stg
+├── prd/           # studio-prd, rally-studio-prd
+```
+
+Each contains Deployments, Services, Ingresses, ExternalSecrets managed by ArgoCD.
+
+## Prerequisites
+
+- Logged into ArgoCD CLI
+- Access to target cluster
+
+## Full Status Check
+
+To get complete visibility into Studio status, check all components across all replicas:
+
+```bash
+# 1. Overall app health
+argocd app get <app>-workload
+
+# 2. List all pods and their status
+argocd app resources <app>-workload --kind Pod
+
+# 3. Check consensus worker logs (all 4 replicas in prd)
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -iE "(error|exception|timeout|failed)"
+
+# 4. Check JSON-RPC logs (all 2 replicas in prd)
+argocd app logs <app>-workload --name studio-jsonrpc --tail 500 2>&1 | grep -iE "(error|exception|timeout|failed)"
+
+# 5. Check webdriver logs
+argocd app logs <app>-workload --name studio-webdriver --tail 200 2>&1 | grep -iE "(error|exception|crash)"
+```
+
+## Quick Commands
+
+```bash
+# Check app health
+argocd app get <app>-workload
+
+# List all resources (pods, deployments, services, etc.)
+argocd app resources <app>-workload
+
+# List all pods with their status
+argocd app resources <app>-workload --kind Pod
+
+# Tail consensus worker logs (aggregates from ALL replicas)
+argocd app logs <app>-workload --name studio-consensus-worker --tail 200
+
+# Tail JSON-RPC logs (aggregates from ALL replicas)
+argocd app logs <app>-workload --name studio-jsonrpc --tail 200
+
+# Check for errors across all replicas
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -i error
+argocd app logs <app>-workload --name studio-jsonrpc --tail 500 2>&1 | grep -i error
+```
+
+## Multi-Replica Log Access
+
+**Important:** The `argocd app logs --name <container>` command automatically aggregates logs from ALL pod replicas. This ensures full visibility across the entire deployment.
+
+```bash
+# Get logs from all consensus worker replicas (production has 4)
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500
+
+# Get logs from all JSON-RPC replicas (production has 2)
+argocd app logs <app>-workload --name studio-jsonrpc --tail 500
+
+# Get logs from a specific pod (if needed for isolation)
+argocd app logs <app>-workload --pod <pod-name> --tail 200
+
+# List pods first to get pod names
+argocd app resources <app>-workload --kind Pod
+```
+
+## Common Issues
+
+### Transaction Timeouts
+
+Consensus worker timeouts usually mean GenVM Manager is unresponsive. Check all 4 workers in production:
+
+```bash
+# Check for GenVM timeouts across all consensus worker replicas
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(timeout|SocketTimeoutError|127.0.0.1:3999)"
+
+# Empty stdout = GenVM never started
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep "stdout=''"
+```
+
+**Root cause**: GenVM Manager (`genvm-modules manager --port 3999`) becomes unresponsive.
+**Fix**: Worker restart (auto or manual) restarts GenVM Manager.
+
+Key files:
+- `backend/node/genvm/origin/base_host.py:463` - where timeouts occur
+- `backend/node/base.py` - Manager.create() spawns GenVM
+- `backend/consensus/worker_service.py` - worker startup/health
+
+### Pod Restarts
+
+```bash
+# Check restart timestamps in logs
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(Started|Uvicorn running)"
+
+# Via kubectl
+kubectl get pods -n <namespace> -o wide
+kubectl get events -n <namespace> --sort-by='.lastTimestamp'
+```
+
+### External API Failures
+
+Contracts calling external APIs (Twitter, etc.) through proxies:
+
+```bash
+# Check for HTTP errors in contract execution
+argocd app logs <app>-workload --name studio-consensus-worker --tail 500 2>&1 | grep -E "(HTTP|fetch|proxy|api)"
+```
+
+## Environment Apps
+
+| Env | App | Namespace |
+|-----|-----|-----------|
+| dev | studio-dev-workload | studio-dev |
+| stg | studio-stg-workload | studio-stg |
+| prd | studio-prd-workload | studio-prd |
+| rally-prd | rally-studio-prd-workload | rally-studio-prd |
+
+## Components
+
+| Component | Purpose | Prd Replicas | Common Issues |
+|-----------|---------|--------------|---------------|
+| studio-consensus-worker | Tx processing | 4 | Timeouts, GenVM crashes |
+| studio-jsonrpc | RPC API | 2 | DB connections |
+| studio-webdriver | Browser sandbox | 1 | Memory, crashes |
+| database-migration | Schema updates | 1 (job) | Lock contention |
+
+**Note:** When debugging, always check logs from ALL replicas to get complete visibility. The `argocd app logs --name <container>` command handles this automatically.
diff --git a/.claude/skills/integration-tests/SKILL.md b/.claude/skills/integration-tests/SKILL.md
@@ -5,15 +5,28 @@ description: Setup Python virtual environment and run integration tests with glt
 
 # Run Integration Tests
 
-Setup the Python environment and run integration tests for GenLayer Studio.
+Setup the Python environment, start the studio, and run integration tests for GenLayer Studio.
 
 ## Prerequisites
 
 - Python 3.12 installed
 - virtualenv installed (`pip install virtualenv`)
-- Docker containers running (`docker compose up -d`)
+- Docker and Docker Compose installed
 
-## Setup Virtual Environment (first time or reset)
+## Step 1: Start the Studio
+
+The studio must be running before executing integration tests.
+
+```bash
+# Stop any existing containers and rebuild
+docker-compose down && docker-compose up --build
+```
+
+Wait for all services to be healthy before proceeding.
+
+## Step 2: Setup Virtual Environment (first time or reset)
+
+In a separate terminal:
 
 ```bash
 # Remove existing venv if present
@@ -37,20 +50,7 @@ pip install -r backend/requirements.txt
 export PYTHONPATH="$(pwd)"
 ```
 
-## Ensure Services Are Running
-
-Integration tests require the backend services:
-
-```bash
-# Start all services
-docker compose up -d
-
-# Verify services are healthy
-docker compose ps
-curl -s http://localhost:4000/health | jq .
-```
-
-## Run Tests
+## Step 3: Run Integration Tests
 
 ```bash
 # Activate venv (if not already)
@@ -60,38 +60,67 @@ export PYTHONPATH="$(pwd)"
 # Run all integration tests
 gltest --contracts-dir . tests/integration
 
+# Run faster with leader-only mode (skips validator consensus)
+gltest --contracts-dir . tests/integration --leader-only
+
 # Run specific test file
 gltest --contracts-dir . tests/integration/test_specific.py
 
 # Run with verbose output
-gltest --contracts-dir . tests/integration -svv
+gltest --contracts-dir . tests/integration -v
 
 # Run specific test function
 gltest --contracts-dir . tests/integration/test_file.py::test_function_name
 ```
 
-## Quick One-Liner (after initial setup)
+## Quick Commands
 
+### Full Setup (first time)
 ```bash
-source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration
+# Terminal 1: Start studio
+docker-compose down && docker-compose up --build
+
+# Terminal 2: Setup and run tests
+rm -rf .venv && \
+virtualenv -p python3.12 .venv && \
+source .venv/bin/activate && \
+pip install --upgrade pip && \
+pip install -r requirements.txt && \
+pip install -r requirements.test.txt && \
+pip install -r backend/requirements.txt && \
+export PYTHONPATH="$(pwd)" && \
+gltest --contracts-dir . tests/integration
 ```
 
-## Test Contracts
-
-Integration test contracts are located in:
+### Quick Run (after initial setup, studio already running)
+```bash
+source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration
 ```
-tests/integration/test_contracts/
+
+### Fast Run (leader-only mode)
+```bash
+source .venv/bin/activate && export PYTHONPATH="$(pwd)" && gltest --contracts-dir . tests/integration --leader-only
 ```
 
 ## Troubleshooting
 
+### Studio Not Running
+```bash
+# Check if containers are up
+docker-compose ps
+
+# Check container logs
+docker-compose logs -f backend
+```
+
 ### Connection Refused Errors
+The studio needs time to initialize. Wait for all services to be healthy:
 ```bash
-# Ensure Docker services are running
-docker compose ps
+# Watch container status
+docker-compose ps
 
-# Restart services if needed
-docker compose restart
+# Check backend health
+curl http://localhost:4000/health
 ```
 
 ### Python 3.12 Not Found
@@ -121,10 +150,12 @@ export PYTHONPATH="$(pwd)"
 pwd  # Should be genlayer-studio
 ```
 
-### Timeout Errors
+### Test Timeouts
+Integration tests may timeout if the studio is under load. Try:
 ```bash
-# Check backend logs for issues
-docker compose logs -f backend
+# Run with leader-only for faster execution
+gltest --contracts-dir . tests/integration --leader-only
 
-# Increase timeout if needed (in test or via env)
+# Run a single test file to isolate issues
+gltest --contracts-dir . tests/integration/test_specific.py -v
 ```
PATCH

echo "Gold patch applied."
