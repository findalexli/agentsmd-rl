#!/usr/bin/env bash
set -euo pipefail

cd /workspace/posthog

# Idempotent: skip if already applied
if grep -q 'sandbox_environment_id' products/tasks/backend/models.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/published/handbook/engineering/ai/sandboxed-agents.md b/docs/published/handbook/engineering/ai/sandboxed-agents.md
index ff1067c0d80e..a41fec09b710 100644
--- a/docs/published/handbook/engineering/ai/sandboxed-agents.md
+++ b/docs/published/handbook/engineering/ai/sandboxed-agents.md
@@ -70,19 +70,20 @@ task = Task.create_and_run(

 ### Parameters

-| Parameter              | Required | Description                                                                |
-| ---------------------- | -------- | -------------------------------------------------------------------------- |
-| `team`                 | Yes      | The team this task belongs to                                              |
-| `title`                | Yes      | Human-readable task title                                                  |
-| `description`          | Yes      | Detailed description of what the agent should do                           |
-| `origin_product`       | Yes      | Which product created this task (see `Task.OriginProduct` choices)         |
-| `user_id`              | Yes      | User ID — used for feature flag validation and creating the scoped API key |
-| `repository`           | Yes      | GitHub repo in `org/repo` format (e.g., `posthog/posthog-js`)              |
-| `posthog_mcp_scopes`   | No       | Scope preset or explicit scope list (default: `"full"`)                    |
-| `create_pr`            | No       | Whether the agent should create a PR (default: `True`)                     |
-| `mode`                 | No       | Execution mode (default: `"background"`)                                   |
-| `slack_thread_context` | No       | Slack thread context for agents triggered from Slack                       |
-| `start_workflow`       | No       | Whether to start the Temporal workflow immediately (default: `True`)       |
+| Parameter                | Required | Description                                                                |
+| ------------------------ | -------- | -------------------------------------------------------------------------- |
+| `team`                   | Yes      | The team this task belongs to                                              |
+| `title`                  | Yes      | Human-readable task title                                                  |
+| `description`            | Yes      | Detailed description of what the agent should do                           |
+| `origin_product`         | Yes      | Which product created this task (see `Task.OriginProduct` choices)         |
+| `user_id`                | Yes      | User ID — used for feature flag validation and creating the scoped API key |
+| `repository`             | Yes      | GitHub repo in `org/repo` format (e.g., `posthog/posthog-js`)              |
+| `posthog_mcp_scopes`     | No       | Scope preset or explicit scope list (default: `"full"`)                    |
+| `create_pr`              | No       | Whether the agent should create a PR (default: `True`)                     |
+| `mode`                   | No       | Execution mode (default: `"background"`)                                   |
+| `slack_thread_context`   | No       | Slack thread context for agents triggered from Slack                       |
+| `start_workflow`         | No       | Whether to start the Temporal workflow immediately (default: `True`)       |
+| `sandbox_environment_id` | No       | ID of a `SandboxEnvironment` to apply network restrictions (see below)     |

 ### Adding a new origin product

@@ -188,6 +189,42 @@ Network access is configured per-team via `SandboxEnvironment`:
 - **Full** — unrestricted network access
 - **Custom** — explicit allowlist of domains, optionally including the trusted defaults

+To apply network restrictions from your product code,
+create a `SandboxEnvironment` and pass its ID to `Task.create_and_run`:
+
+```python
+from products.tasks.backend.models import SandboxEnvironment, Task
+
+# 1. Create an environment (once, or look up an existing one)
+env = SandboxEnvironment.objects.create(
+    team=team,
+    created_by=user,
+    name="Restricted agent env",
+    network_access_level="custom",  # "full" | "trusted" | "custom"
+    allowed_domains=["github.com", "api.example.com"],
+    include_default_domains=True,  # merge GitHub, npm, PyPI defaults
+)
+
+# 2. Pass its ID when creating the task
+task = Task.create_and_run(
+    team=team,
+    title="My restricted task",
+    description="...",
+    origin_product=Task.OriginProduct.YOUR_PRODUCT,
+    user_id=user.id,
+    repository="org/repo",
+    sandbox_environment_id=str(env.id),
+)
+```
+
+The temporal workflow resolves the allowed domains at execution time from the environment,
+so updates to the environment take effect on the next run.
+Domain restrictions are enforced at the syscall level by `agentsh` via ptrace —
+the agent cannot bypass them through proxy settings or DNS tricks.
+
+Environments can also be managed via the REST API (`SandboxEnvironmentViewSet`)
+or the PostHog Code settings UI.
+
 ## Local development

 See the [Cloud runs setup guide](https://github.com/PostHog/posthog/blob/master/products/tasks/backend/temporal/process_task/SETUP_GUIDE.md)
diff --git a/products/tasks/backend/models.py b/products/tasks/backend/models.py
index 0f16f4a1bf17..ef1fef8a7960 100644
--- a/products/tasks/backend/models.py
+++ b/products/tasks/backend/models.py
@@ -224,6 +224,7 @@ def create_and_run(
         start_workflow: bool = True,
         posthog_mcp_scopes: PosthogMcpScopes = "full",
         branch: str | None = None,
+        sandbox_environment_id: str | None = None,
     ) -> "Task":
         from products.tasks.backend.temporal.client import execute_task_processing_workflow

@@ -235,6 +236,12 @@ def create_and_run(
             if not github_integration:
                 raise ValueError(f"Team {team.id} does not have a GitHub integration")

+        sandbox_env = None
+        if sandbox_environment_id is not None:
+            sandbox_env = SandboxEnvironment.objects.filter(id=sandbox_environment_id, team=team).first()
+            if not sandbox_env:
+                raise ValueError(f"Invalid sandbox_environment_id: {sandbox_environment_id}")
+
         task = Task.objects.create(
             team=team,
             title=title,
@@ -253,6 +260,10 @@ def create_and_run(
             if slack_thread_context:
                 extra_state["interaction_origin"] = "slack"

+        if sandbox_env is not None:
+            extra_state = extra_state or {}
+            extra_state["sandbox_environment_id"] = str(sandbox_env.id)
+
         task_run = task.create_run(mode=mode, extra_state=extra_state, branch=branch)

         if start_workflow:

PATCH

echo "Patch applied successfully."
