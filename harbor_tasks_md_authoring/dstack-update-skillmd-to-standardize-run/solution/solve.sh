#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dstack

# Idempotency guard
if grep -qF "**\"Connect to\" or \"open\" a dev environment:** If a dev environment is already ru" "skills/dstack/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dstack/SKILL.md b/skills/dstack/SKILL.md
@@ -101,27 +101,29 @@ If you need to prompt for next actions, be explicit about the dstack step and co
 
 `dstack attach` runs until interrupted and blocks the terminal. **Agents must avoid indefinite blocking.** If a brief attach is needed, use a timeout to capture initial output (IDE link, SSH alias) and then detach.
 
-Note: `dstack attach` writes SSH alias info under `~/.dstack/ssh/config` (and may update `~/.ssh/config`) to enable `ssh <run-name>`, IDE connections, port forwarding, and real-time logs (`dstack attach --logs`). If the sandbox cannot write there, the alias will not be created.
+Note: `dstack attach` writes SSH alias info under `~/.dstack/ssh/config` (and may update `~/.ssh/config`) to enable `ssh <run name>`, IDE connections, port forwarding, and real-time logs (`dstack attach --logs`). If the sandbox cannot write there, the alias will not be created.
+
+**Permissions guardrail:** If `dstack attach` fails due to sandbox permissions, request permission escalation to run it outside the sandbox. If escalation isn’t approved or attach still fails, ask the user to run `dstack attach` locally and share the IDE link/SSH alias output.
 
 **Background attach (non-blocking default for agents):**
 ```bash
-nohup dstack attach <run-name> --logs > /tmp/<run-name>.attach.log 2>&1 & echo $! > /tmp/<run-name>.attach.pid
+nohup dstack attach <run name> --logs > /tmp/<run name>.attach.log 2>&1 & echo $! > /tmp/<run name>.attach.pid
 ```
 Then read the output:
 ```bash
-tail -n 50 /tmp/<run-name>.attach.log
+tail -n 50 /tmp/<run name>.attach.log
 ```
 Offer live follow only if asked:
 ```bash
-tail -f /tmp/<run-name>.attach.log
+tail -f /tmp/<run name>.attach.log
 ```
 Stop the background attach (preferred):
 ```bash
-kill "$(cat /tmp/<run-name>.attach.pid)"
+kill "$(cat /tmp/<run name>.attach.pid)"
 ```
 If the PID file is missing, fall back to a specific match (avoid killing all attaches):
 ```bash
-pkill -f "dstack attach <run-name>"
+pkill -f "dstack attach <run name>"
 ```
 **Why this helps:** it keeps the attach session alive (including port forwarding) while the agent remains usable. IDE links and SSH instructions appear in the log file -- surface them and ask whether to open the link (`open "<link>"` on macOS, `xdg-open "<link>"` on Linux) only after explicit approval.
 
@@ -131,7 +133,7 @@ If background attach fails in the sandbox (permissions writing `~/.dstack` or `~
 
 **"Run something":** When the user asks to run a workload (dev environment, task, service), use `dstack apply` with the appropriate configuration. Note: `dstack run` only supports `dstack run get --json` for retrieving run details -- it cannot start workloads.
 
-**"Connect to" or "open" a dev environment:** If a dev environment is already running, use `dstack attach <run-name> --logs` (agent runs it in the background by default) to surface the IDE URL (`cursor://`, `vscode://`, etc.) and SSH alias. If sandboxed attach fails, request escalation or ask the user to run attach locally and share the link.
+**"Connect to" or "open" a dev environment:** If a dev environment is already running, use `dstack attach <run name> --logs` (agent runs it in the background by default) to surface the IDE URL (`cursor://`, `vscode://`, etc.) and SSH alias. If sandboxed attach fails, request escalation or ask the user to run attach locally and share the link.
 
 ## Configuration types
 
@@ -187,7 +189,7 @@ resources:
   gpu: A100:40GB:2
 ```
 
-**Port forwarding:** When you specify `ports`, `dstack apply` forwards them to `localhost` while attached. Use `dstack attach <run-name>` to reconnect and restore port forwarding. The run name becomes an SSH alias (e.g., `ssh <run-name>`) for direct access.
+**Port forwarding:** When you specify `ports`, `dstack apply` forwards them to `localhost` while attached. Use `dstack attach <run name>` to reconnect and restore port forwarding. The run name becomes an SSH alias (e.g., `ssh <run name>`) for direct access.
 
 **Distributed training:** Multi-node tasks are supported (e.g., via `nodes`) and require fleets that support inter-node communication (see `placement: cluster` in fleets).
 
@@ -217,10 +219,10 @@ resources:
 ```
 
 **Service endpoints:**
-- Without gateway: `<dstack server URL>/proxy/services/<project name>/<run name>/`
+- Without gateway: `<dstack server URL>/proxy/services/f/<run name>/`
 - With gateway: `https://<run name>.<gateway domain>/`
 - Authentication: Unless `auth` is `false`, include `Authorization: Bearer <DSTACK_TOKEN>` on all service requests.
-- OpenAI-compatible models: Use `service.url` from `dstack run get <run-name> --json` and append `/v1` as the base URL; do **not** use deprecated `service.model.base_url` for requests.
+- OpenAI-compatible models: Use `service.url` from `dstack run get <run name> --json` and append `/v1` as the base URL; do **not** use deprecated `service.model.base_url` for requests.
 - Example (with gateway):
   ```bash
   curl -sS -X POST "https://<run name>.<gateway domain>/v1/chat/completions" \
PATCH

echo "Gold patch applied."
