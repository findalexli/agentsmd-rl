#!/usr/bin/env bash
set -euo pipefail

cd /workspace/hail

# Idempotency guard
if grep -qF "If you hit a gap in the CLI during an investigation (e.g. there's no `hailctl ba" ".claude/skills/hail-batch-dev.md" && grep -qF "For inspection tasks (checking status, reading logs, diagnosing failures), **alw" ".claude/skills/hail-batch.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/hail-batch-dev.md b/.claude/skills/hail-batch-dev.md
@@ -0,0 +1,307 @@
+---
+description: Work on the Hail system itself — CI pipeline, flaky tests, Batch service internals, dev namespace deployments, deployed infrastructure management
+---
+
+You are helping a Hail service engineer investigate Hail Batch infrastructure or develop improvements to it.
+
+**For end-user batch investigation (logs, job status, writing scripts), also invoke `/hail-batch`.**
+
+## Running hailctl commands
+
+`hailctl` is likely in a virtual environment — if it isn't found, look for one and activate it. Once activated, it stays active for the session.
+
+**Never suppress stderr** when running hailctl or other Hail tools — important connection info and warnings appear there. Do not use `2>&1` or `2>/dev/null`.
+
+## What this adds over /hail-batch
+
+- Namespace/deploy config targeting (non-default namespaces)
+- Service-level debugging (batch-driver, workers, CloudSQL)
+- ServiceBackend internals (how Hail Query drives Batch)
+- CI batch investigation
+- Developing and testing changes to the batch service itself
+
+## Authentication
+
+Same as end users, plus namespace-specific tokens:
+
+```bash
+gcloud auth application-default login       # GCP ADC for cloud storage
+hailctl auth login                          # Hail service auth
+```
+
+To check which namespaces you have tokens for and confirm your current identity:
+```bash
+hailctl auth list    # lists namespaces (* = current)
+hailctl auth user    # shows current user identity
+```
+
+To switch namespaces persistently:
+```bash
+hailctl dev config set default_namespace my-namespace
+hailctl dev config list                             # show current settings
+```
+
+Or per-command with an env var:
+```bash
+HAIL_DEFAULT_NAMESPACE=my-namespace hailctl batch list
+HAIL_DEFAULT_NAMESPACE=my-namespace hailctl batch get BATCH_ID
+```
+
+For engineers working across multiple namespaces regularly, config profiles are useful:
+```bash
+hailctl config profile create my-namespace
+hailctl config set batch/billing_project my-project
+hailctl config profile load my-namespace
+hailctl config profile list                         # * marks active profile
+hailctl config profile load default                 # switch back
+```
+
+Or in Python:
+```python
+from hailtop.config import DeployConfig
+from hailtop.batch_client import client as bc
+
+deploy_config = DeployConfig(
+    location='external',
+    domain='hail.is',
+    base_path='',
+    default_namespace='my-namespace',
+)
+with bc.BatchClient(billing_project='my-project', deploy_config=deploy_config) as client:
+    batch = client.get_batch(BATCH_ID)
+```
+
+## Troubleshooting connection errors
+
+If you get "no upstream", "connection refused", or "batch not found" errors, the most likely causes are:
+- The target namespace is not running (dev namespaces are ephemeral and may have expired)
+- `hailctl dev config` is pointing at the wrong namespace — run `hailctl dev config list` to check
+- The `HAIL_DEFAULT_NAMESPACE` env var is overriding your config unexpectedly
+
+Check with `hailctl dev config list` first before digging deeper.
+
+If the namespace has expired or doesn't exist, it needs to be started. There are two options:
+
+**Start from scratch** (deploys services via CI into a fresh namespace — takes a while, returns a batch ID to track progress):
+```bash
+HAIL_DEFAULT_NAMESPACE=default hailctl dev deploy \
+  -b <github_user>/hail:<branch> \
+  -s deploy_batch,add_developers   # adjust steps as needed
+```
+This prints a batch ID. Give the user the exact command to monitor it in a separate terminal:
+```bash
+hailctl batch wait <id>
+```
+Then ask whether they'd like you to watch it too and verify the deployment looks good when it comes up (useful if they want to iterate on failures). Waiting can take 20-30 minutes, so only do it if the user explicitly asks.
+
+**Update a running namespace live** (faster, redeploys a single service):
+```bash
+make -C <service> deploy NAMESPACE=<my-namespace>   # e.g. make -C batch deploy NAMESPACE=chrisl
+```
+
+**Important**: both commands affect live infrastructure. Do not run them without explicit confirmation from the user — either ask the user to run the command themselves, or show the exact command and wait for approval before executing.
+
+## Direct API access with hailctl curl
+
+For raw API calls not covered by `hailctl batch` subcommands, use `hailctl curl` — it handles auth automatically:
+
+```bash
+# hailctl curl NAMESPACE SERVICE PATH [curl args]
+hailctl curl default batch /api/v1alpha/batches/1234
+hailctl curl my-namespace batch /api/v1alpha/billing_projects
+
+# Pass extra curl flags after the path
+hailctl curl default batch /api/v1alpha/batches -X GET
+hailctl curl default batch /api/v1alpha/batches/1234 -o output.json
+```
+
+### Discovering available endpoints
+
+Each service exposes an OpenAPI spec. Fetch it to see all available endpoints before reaching for `hailctl curl`:
+
+```bash
+hailctl curl default batch /openapi.yaml
+hailctl curl default auth /openapi.yaml
+hailctl curl default ci /openapi.yaml
+hailctl curl default batch-driver /openapi.yaml
+hailctl curl default monitoring /openapi.yaml
+```
+
+The spec is the authoritative source — prefer it over any cached list of endpoints in documentation.
+
+**When adding a new endpoint**, update `openapi.yaml` in the same PR. The spec lives alongside the service code (e.g. `batch/openapi.yaml`).
+
+**When an endpoint doesn't match the spec** (wrong path, missing params, incorrect response shape), fix the spec too — a drift between implementation and spec is a bug.
+
+## Investigating with the CLI (prefer this for inspection)
+
+The `hailctl batch` CLI works against any namespace via `HAIL_DEFAULT_NAMESPACE`. Prefer it for inspection — see `/hail-batch` for the full command reference.
+
+For listing jobs within a batch, `hailctl curl` is often better than the Python client because the response is paginated and curl makes it easy to inspect pages and compose with `jq`:
+
+```bash
+# First page of jobs
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs
+
+# Filter to failed jobs
+hailctl curl default batch "/api/v1alpha/batches/BATCH_ID/jobs?q=state%3DFailed"
+
+# Next page (use last_job_id from previous response)
+hailctl curl default batch "/api/v1alpha/batches/BATCH_ID/jobs?last_job_id=42"
+
+# Pipe through jq for readability
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs | jq '.jobs[] | {job_id, state, exit_code}'
+```
+
+The response contains `jobs` (array) and `last_job_id` (present if more pages remain). Repeat with `?last_job_id=<value>` to page through.
+
+For anything the CLI can't reach (job attempts, raw DB state, worker-level details), drop into the Python client:
+
+```python
+from hailtop.batch_client import client as bc
+
+with bc.BatchClient(billing_project='my-project') as client:
+    job = client.get_job(BATCH_ID, JOB_ID)
+    attempts = job.attempts()           # retry history
+    usage = job.resource_usage()        # per-container resource metrics
+    status = job.status()               # full status dict including worker name
+```
+
+### OOM diagnosis
+```python
+status = job.status()
+# Worker-level OOM (job killed by cgroup, not user code):
+oom = status.get('status', {}).get('main', {}).get('out_of_memory')
+# Or use the helper:
+from hailtop.batch_client.aioclient import Job
+oom = Job._get_out_of_memory(status, 'main')
+```
+
+### Worker identification
+```python
+worker = status.get('status', {}).get('main', {}).get('worker')
+# Use this to find worker VM logs in Cloud Logging
+```
+
+## Worker-level logs (GCP Cloud Logging)
+
+Worker logs aren't in the batch API — go to Cloud Logging:
+```bash
+gcloud logging read \
+  'resource.type="gce_instance" resource.labels.instance_name="<worker-name>"' \
+  --project=<gcp-project> --limit=100
+```
+
+## Batch service architecture
+
+- **`batch`**: API server — handles client requests, validates, persists to MySQL
+- **`batch-driver`**: Schedules jobs, manages the state machine, provisions/deprovisions workers
+- **workers**: GCE VMs that pull and execute jobs
+
+State machine:
+```
+Pending → Ready → Creating → Running → {Success, Failed, Error, Cancelled}
+```
+
+`Error` = infrastructure failure (batch-driver or worker), not user code.
+
+Key source directories:
+- `batch/batch/` — API server and driver Python code
+- `batch/jvm-entryway/` — Scala JVM worker entrypoint (for Query jobs)
+- `batch/worker/` — Worker Python code
+
+## ServiceBackend internals
+
+When users do `hl.init(backend='batch')`, Hail Query uses `ServiceBackend` to:
+1. Serialize the query IR to cloud storage
+2. Submit a Batch job via `hailtop.batch_client.aioclient.BatchClient`
+3. The JVM worker (`jvm-entryway`) reads the IR, executes, writes results back
+4. Python side reads results from cloud storage
+
+Key source: `hail/python/hail/backend/service_backend.py`
+
+To find the batch submitted by a Query operation, look for batches with names/attributes matching the IR token logged by the ServiceBackend.
+
+## Database
+
+Batch state lives in MySQL (Google CloudSQL). Schema: `batch` database.
+
+Key tables: `batches`, `jobs`, `job_groups`, `attempts`, `resources`, `billing_projects`
+
+To connect (requires port-forward or `make local-mysql`):
+```bash
+kubectl -n <namespace> port-forward svc/db 3306:3306
+mysql -h 127.0.0.1 -P 3306 -u batch -pbatch batch
+```
+
+## kubectl
+
+```bash
+# Pod logs
+kubectl -n <namespace> logs -l app=batch --tail=200
+kubectl -n <namespace> logs -l app=batch-driver --tail=200
+
+# Pod status
+kubectl -n <namespace> get pods -l app=batch
+kubectl -n <namespace> get pods -l app=batch-driver
+
+# Port-forward batch API
+kubectl -n <namespace> port-forward svc/batch 5000:5000
+```
+
+## Developing changes to batch
+
+### Local dev loop
+```bash
+# Sync Python changes to running pods without rebuilding images
+python3 devbin/sync.py \
+  --namespace <ns> \
+  --app batch --app batch-driver \
+  --path batch/batch /opt/venv/lib/python3.11/site-packages/
+
+# Deploy a full image rebuild to a dev namespace
+HAIL_DEFAULT_NAMESPACE=default hailctl dev deploy \
+  -b <github_user>/hail:<branch> \
+  -s deploy_batch
+```
+
+### Running batch tests
+```bash
+# Integration tests against a deployed namespace
+make -C hail pytest-qob NAMESPACE=default
+
+# Batch service tests
+make -C hail jvm-test   # if touching JVM/Scala side
+```
+
+### DB migrations
+
+New migrations go in `batch/sql/`. They're applied by the `*_database` CI steps. For dev namespaces, apply manually:
+```bash
+mysql -h ... batch < batch/sql/your-migration.sql
+```
+
+## CI batch investigation
+
+CI submits batches to the `ci` billing project. To investigate a CI build failure:
+1. Find the batch ID from the CI UI or `ci/ci/ci.py` logs
+2. Use `HAIL_DEFAULT_NAMESPACE=default hailctl batch get BATCH_ID`
+3. CI batches are large — filter to failed jobs and check their logs
+4. Job names correspond to step names in `build.yaml`
+
+## Enhancing the hailctl CLI
+
+If you hit a gap in the CLI during an investigation (e.g. there's no `hailctl batch jobs BATCH_ID` to list jobs within a batch — you currently need the Python client or `hailctl curl` for that), it may be worth adding the missing command. The CLI lives in `hail/python/hailtop/hailctl/` and is straightforward to extend.
+
+That said, CLI additions should be a **separate PR** from whatever you're currently working on — note it as a follow-up rather than doing it now.
+
+## Common dev-level failure patterns
+
+| Symptom | Likely cause | Action |
+|---|---|---|
+| Many `Error` jobs | batch-driver bug or worker crash | Check batch-driver pod logs |
+| Jobs stuck in `Creating` | Worker pool exhausted or GCE quota | Check batch-driver scheduling logs |
+| Worker VM crash (OOM) | Worker itself OOM (not the job) | Cloud Logging for the worker VM |
+| Auth failures in jobs | SA key missing/expired | Check `create_test_gsa_keys` CI step |
+| ServiceBackend hangs | IR too large or batch not completing | Find the submitted batch; check driver logs |
+| `make local-mysql` fails | Port conflict or prior container | `docker ps` and kill the old container |
diff --git a/.claude/skills/hail-batch.md b/.claude/skills/hail-batch.md
@@ -0,0 +1,189 @@
+---
+description: Submit jobs, debug failures, and write Hail Batch submission scripts as an end user
+---
+
+You are helping a user work with Hail Batch — a job orchestration service for running analysis pipelines on cloud compute.
+
+## Running hailctl commands
+
+If `hailctl` isn't found, it may be in a virtual environment — look for one and activate it. Once activated, it stays active for the session.
+
+**Never suppress stderr** when running hailctl or other Hail tools — important connection info and warnings appear there. Do not use `2>&1` or `2>/dev/null`.
+
+## Authentication
+
+Users need two things on GCP:
+
+```bash
+# 1. GCP Application Default Credentials (for cloud storage access)
+gcloud auth application-default login
+
+# 2. Hail service auth (reads ~/.hail/tokens.json)
+hailctl auth login
+```
+
+Both are needed. If a user gets auth errors, check which one is missing.
+
+## Investigating batches: use the CLI
+
+For inspection tasks (checking status, reading logs, diagnosing failures), **always prefer `hailctl batch` CLI commands** — they're simpler and don't require writing Python.
+
+### List recent batches
+```bash
+hailctl batch list                          # last 50 batches
+hailctl batch list --limit 20 --query 'state=failure'
+hailctl batch list -o json                  # machine-readable
+```
+
+### Get batch status
+```bash
+hailctl batch get BATCH_ID                  # full details (yaml)
+hailctl batch get BATCH_ID -o json
+```
+
+### Inspect a specific job
+```bash
+hailctl batch job BATCH_ID JOB_ID           # status + spec (yaml)
+```
+
+### Get logs
+```bash
+hailctl batch log BATCH_ID JOB_ID                       # all containers (yaml)
+hailctl batch log BATCH_ID JOB_ID --container main      # just main (raw text)
+hailctl batch log BATCH_ID JOB_ID --container input     # input sidecar
+hailctl batch log BATCH_ID JOB_ID --container output    # output sidecar
+```
+
+Note: `--container` requires a recent hailtop version. If it fails, fall back to the raw API (container is a path segment):
+```bash
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs/JOB_ID/log/main
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs/JOB_ID/log/input
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs/JOB_ID/log/output
+```
+
+### Wait for a batch to complete
+```bash
+hailctl batch wait BATCH_ID
+hailctl batch wait BATCH_ID -o json
+```
+
+### Cancel or delete
+```bash
+hailctl batch cancel BATCH_ID
+hailctl batch delete BATCH_ID
+```
+
+### Billing
+```bash
+hailctl batch billing list
+hailctl batch billing get BILLING_PROJECT
+```
+
+## Writing batch submission scripts: use the Python API
+
+For writing scripts that *submit* batches programmatically, use `hailtop.batch`:
+
+```python
+import hailtop.batch as hb
+
+b = hb.Batch(
+    name='my-analysis',
+    backend=hb.ServiceBackend(
+        billing_project='my-project',
+        remote_tmpdir='gs://my-bucket/tmp',
+    ),
+)
+
+j = b.new_job(name='step1')
+j.image('hailgenetics/hail:0.2.x')
+j.memory('4Gi')
+j.cpu(2)
+j.command('python3 my_script.py')
+
+b.run()
+```
+
+For quick one-off jobs, `hailctl batch submit` works too:
+```bash
+hailctl batch submit --image hailgenetics/hail:0.2.x --memory 4Gi python3 my_script.py
+```
+
+### Hail Query within a Batch job
+
+Use the `hailgenetics/hail:<version>` image. Write outputs to cloud storage and read them back:
+
+```python
+# In the batch job script (runs on the worker):
+import hail as hl
+hl.init()
+mt = hl.read_matrix_table('gs://bucket/input.mt')
+results = mt.some_analysis()
+results.write('gs://bucket/output.ht')
+
+# Back in the parent script after b.run():
+results = hl.read_table('gs://bucket/output.ht')
+```
+
+## Direct API access with hailctl curl
+
+For endpoints not covered by `hailctl batch` subcommands, use `hailctl curl` — it handles auth automatically:
+
+```bash
+hailctl curl default batch /PATH
+```
+
+To discover all available endpoints, fetch the OpenAPI spec:
+```bash
+hailctl curl default batch /openapi.yaml
+```
+
+## Listing jobs within a batch
+
+The `hailctl batch` CLI doesn't have a `jobs` subcommand yet. Use `hailctl curl` instead, which lets you filter and paginate:
+
+```bash
+# List jobs (first page)
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs
+
+# Filter to failed jobs only
+hailctl curl default batch "/api/v1alpha/batches/BATCH_ID/jobs?q=state%3DFailed"
+
+# Next page — use last_job_id from the previous response
+hailctl curl default batch "/api/v1alpha/batches/BATCH_ID/jobs?last_job_id=42"
+
+# Extract just job_id, state, exit_code with jq
+hailctl curl default batch /api/v1alpha/batches/BATCH_ID/jobs | jq '.jobs[] | {job_id, state, exit_code}'
+```
+
+The response has a `last_job_id` field when more pages exist — repeat the call with `?last_job_id=<value>` to continue.
+
+## Job states
+
+| State | Meaning |
+|---|---|
+| `Pending` | Waiting on dependencies |
+| `Ready` | Dependencies met, queued for a worker |
+| `Creating` | Worker being provisioned |
+| `Running` | Executing on a worker |
+| `Success` | Exited 0 |
+| `Failed` | User code exited non-zero |
+| `Error` | Infrastructure/platform failure (not user code) |
+| `Cancelled` | Cancelled before completion |
+
+## Common failure patterns
+
+| Symptom | Likely cause | Action |
+|---|---|---|
+| `Failed`, exit code 1 | Script error | `hailctl batch log BATCH JOB --container main` |
+| `Failed`, exit code 137 | OOM kill | Increase `j.memory()` in the submission script |
+| `Error` state | Infrastructure failure | Check `--container input` or `--container output` logs; may be transient |
+| Jobs stuck in `Pending` | Dependency failure or quota | Check upstream jobs |
+| High cost, slow progress | Insufficient parallelism | Increase job fan-out in the script |
+
+## How to investigate a specific batch
+
+When given a batch ID:
+1. Run `hailctl batch get BATCH_ID` — report state, n_jobs, n_succeeded, n_failed, cost
+2. Run `hailctl batch list` with a failure query to find failed jobs, or page through jobs
+3. For each failed job (up to ~5), run `hailctl batch log BATCH_ID JOB_ID --container main`
+4. Identify the root cause and suggest next steps
PATCH

echo "Gold patch applied."
