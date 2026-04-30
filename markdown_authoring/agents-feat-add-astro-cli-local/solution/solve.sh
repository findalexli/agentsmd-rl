#!/usr/bin/env bash
set -euo pipefail

cd /workspace/agents

# Idempotency guard
if grep -qF "description: Manage local Airflow environment with Astro CLI. Use when the user " "shared-skills/astro-local-env/SKILL.md" && grep -qF "description: Initialize and configure Astro/Airflow projects. Use when the user " "shared-skills/astro-project-setup/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/shared-skills/astro-local-env/SKILL.md b/shared-skills/astro-local-env/SKILL.md
@@ -0,0 +1,125 @@
+---
+name: astro-local-env
+description: Manage local Airflow environment with Astro CLI. Use when the user wants to start, stop, or restart Airflow, view logs, troubleshoot containers, or fix environment issues. For project setup, see astro-project-setup.
+---
+
+# Astro Local Environment
+
+This skill helps you manage your local Airflow environment using the Astro CLI.
+
+> **To set up a new project**, see the **astro-project-setup** skill.
+> **When Airflow is running**, use MCP tools from **dag-authoring** and **dag-testing** skills.
+
+---
+
+## Start / Stop / Restart
+
+```bash
+# Start local Airflow (webserver at http://localhost:8080)
+astro dev start
+
+# Stop containers (preserves data)
+astro dev stop
+
+# Kill and remove volumes (clean slate)
+astro dev kill
+
+# Restart all containers
+astro dev restart
+
+# Restart specific component
+astro dev restart --scheduler
+astro dev restart --webserver
+```
+
+**Default credentials:** admin / admin
+
+**Restart after modifying:** `requirements.txt`, `packages.txt`, `Dockerfile`
+
+---
+
+## Check Status
+
+```bash
+astro dev ps
+```
+
+---
+
+## View Logs
+
+```bash
+# All logs
+astro dev logs
+
+# Specific component
+astro dev logs --scheduler
+astro dev logs --webserver
+
+# Follow in real-time
+astro dev logs -f
+```
+
+---
+
+## Access Container Shell
+
+```bash
+# Bash into scheduler container
+astro dev bash
+
+# Run Airflow CLI commands
+astro dev run airflow info
+astro dev run airflow dags list
+```
+
+---
+
+## Troubleshooting
+
+| Issue | Solution |
+|-------|----------|
+| Port 8080 in use | Stop other containers or edit `.astro/config.yaml` |
+| Container won't start | `astro dev kill` then `astro dev start` |
+| Package install failed | Check `requirements.txt` syntax |
+| DAG not appearing | Run `astro dev parse` to check for import errors |
+| Out of disk space | `docker system prune` |
+
+### Reset Environment
+
+When things are broken:
+
+```bash
+astro dev kill
+astro dev start
+```
+
+---
+
+## Upgrade Airflow
+
+### Test compatibility first
+
+```bash
+astro dev upgrade-test
+```
+
+### Change version
+
+1. Edit `Dockerfile`:
+   ```dockerfile
+   FROM quay.io/astronomer/astro-runtime:13.0.0
+   ```
+
+2. Restart:
+   ```bash
+   astro dev kill && astro dev start
+   ```
+
+---
+
+## Related Skills
+
+- **astro-project-setup**: Initialize projects and configure dependencies
+- **dag-authoring**: Write DAGs (uses MCP tools, requires running Airflow)
+- **dag-testing**: Test DAGs (uses MCP tools, requires running Airflow)
diff --git a/shared-skills/astro-project-setup/SKILL.md b/shared-skills/astro-project-setup/SKILL.md
@@ -0,0 +1,119 @@
+---
+name: astro-project-setup
+description: Initialize and configure Astro/Airflow projects. Use when the user wants to create a new project, set up dependencies, configure connections/variables, or understand project structure. For running the local environment, see astro-local-env.
+---
+
+# Astro Project Setup
+
+This skill helps you initialize and configure Airflow projects using the Astro CLI.
+
+> **To run the local environment**, see the **astro-local-env** skill.
+> **To write DAGs**, see the **dag-authoring** skill.
+
+---
+
+## Initialize a New Project
+
+```bash
+astro dev init
+```
+
+Creates this structure:
+```
+project/
+├── dags/                # DAG files
+├── include/             # SQL, configs, supporting files
+├── plugins/             # Custom Airflow plugins
+├── tests/               # Unit tests
+├── Dockerfile           # Image customization
+├── packages.txt         # OS-level packages
+├── requirements.txt     # Python packages
+└── airflow_settings.yaml # Connections, variables, pools
+```
+
+---
+
+## Adding Dependencies
+
+### Python Packages (requirements.txt)
+
+```
+apache-airflow-providers-snowflake==5.3.0
+pandas==2.1.0
+requests>=2.28.0
+```
+
+### OS Packages (packages.txt)
+
+```
+gcc
+libpq-dev
+```
+
+### Custom Dockerfile
+
+For complex setups (private PyPI, custom scripts):
+
+```dockerfile
+FROM quay.io/astronomer/astro-runtime:12.4.0
+
+RUN pip install --extra-index-url https://pypi.example.com/simple my-package
+```
+
+**After modifying dependencies:** Run `astro dev restart`
+
+---
+
+## Configuring Connections & Variables
+
+### airflow_settings.yaml
+
+Loaded automatically on environment start:
+
+```yaml
+airflow:
+  connections:
+    - conn_id: my_postgres
+      conn_type: postgres
+      host: host.docker.internal
+      port: 5432
+      login: user
+      password: pass
+      schema: mydb
+
+  variables:
+    - variable_name: env
+      variable_value: dev
+
+  pools:
+    - pool_name: limited_pool
+      pool_slot: 5
+```
+
+### Export/Import
+
+```bash
+# Export from running environment
+astro dev object export --connections --file connections.yaml
+
+# Import to environment
+astro dev object import --connections --file connections.yaml
+```
+
+---
+
+## Validate Before Running
+
+Parse DAGs to catch errors without starting the full environment:
+
+```bash
+astro dev parse
+```
+
+---
+
+## Related Skills
+
+- **astro-local-env**: Start, stop, and troubleshoot the local environment
+- **dag-authoring**: Write and validate DAGs (uses MCP tools)
+- **dag-testing**: Test DAGs (uses MCP tools)
PATCH

echo "Gold patch applied."
