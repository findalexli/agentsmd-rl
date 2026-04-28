#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dstack

# Idempotency guard
if grep -qF "**Grouping:** Prefer `--group-by gpu` (other supported values: `gpu,backend`, `g" "skills/dstack/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dstack/SKILL.md b/skills/dstack/SKILL.md
@@ -58,7 +58,7 @@ description: |
 - Never guess or invent flags. Example verification commands:
   ```bash
   dstack --help                               # List all commands
-  dstack apply --help <configuration tpye>    # Flags for apply per configuration type (dev-environment, task, service, fleet, etc)
+  dstack apply --help <configuration type>    # Flags for apply per configuration type (dev-environment, task, service, fleet, etc)
   dstack fleet --help                         # Fleet subcommands
   dstack ps --help                            # Flags for ps
   ```
@@ -412,12 +412,11 @@ dstack stop my-run-name -y
 dstack stop my-run-name --abort
 ```
 
-### Check available resources
+### List offers
 
-```bash
-# List all available offers across backends
-dstack offer --json
+Offers represent available instance configurations available for provisioning across backends. `dstack offer` lists offers regardless of configured fleets.
 
+```bash
 # Filter by specific backend
 dstack offer --backend aws
 
@@ -429,19 +428,24 @@ dstack offer --gpu 24GB..80GB
 
 # Combine filters
 dstack offer --backend aws --gpu A100:80GB
+
+# JSON output (for troubleshooting/scripting)
+dstack offer --json
 ```
 
-**Note:** `dstack offer` lists offers across backends regardless of configured fleets.
+**Max offers:** By default, `dstack offer` returns first N offers (output also includes the total number). Use `--max-offers N` to increase the limit.
+**Grouping:** Prefer `--group-by gpu` (other supported values: `gpu,backend`, `gpu,backend,region`) for aggregated output across all offers, not `--max-offers`.
 
 ## Troubleshooting
 
 When diagnosing issues with dstack workloads or infrastructure:
 
 1. **Use JSON output for detailed inspection:**
    ```bash
-   dstack fleet get my-fleet --json | jq .
-   dstack run get my-run --json | jq .
-   dstack ps -n 10 --json | jq .
+   dstack fleet get my-fleet --json
+   dstack run get my-run --json
+   dstack ps -n 10 --json
+   dstack offer --json
    ```
 
 2. **Check verbose run status:**
@@ -459,11 +463,6 @@ When diagnosing issues with dstack workloads or infrastructure:
    dstack attach my-run --logs
    ```
 
-5. **Verify resource availability:**
-   ```bash
-   dstack offer --backend aws --gpu A100 --spot-auto --json
-   ```
-
 Common issues:
 - **No offers:** Check `dstack offer` and ensure that at least one fleet matches requirements
 - **No fleet:** Ensure at least one fleet is created
PATCH

echo "Gold patch applied."
