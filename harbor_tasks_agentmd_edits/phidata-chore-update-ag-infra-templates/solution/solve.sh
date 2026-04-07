#!/usr/bin/env bash
set -euo pipefail

cd /workspace/phidata

# Idempotent: skip if already applied
if grep -q 'agentos_docker = "agentos-docker"' libs/agno_infra/agno/infra/enums.py 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index e9d5041688..a782f16fac 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -189,6 +189,22 @@ Both scripts must pass with no errors before code review.

 ---

+## GitHub Operations
+
+**Updating PR descriptions:**
+
+The `gh pr edit` command may fail with GraphQL errors related to classic projects. Use the API directly instead:
+
+```bash
+# Update PR body
+gh api repos/agno-agi/agno/pulls/<PR_NUMBER> -X PATCH -f body="<PR_BODY>"
+
+# Or with a file
+gh api repos/agno-agi/agno/pulls/<PR_NUMBER> -X PATCH -f body="$(cat /path/to/body.md)"
+```
+
+---
+
 ## Don't

 - Don't implement features without checking for a design doc first
diff --git a/libs/agno_infra/agno/infra/enums.py b/libs/agno_infra/agno/infra/enums.py
index 4417c3ea30..d299c74a27 100644
--- a/libs/agno_infra/agno/infra/enums.py
+++ b/libs/agno_infra/agno/infra/enums.py
@@ -2,6 +2,6 @@


 class InfraStarterTemplate(str, Enum):
-    agentos_docker_template = "agentos-docker-template"
-    agentos_aws_template = "agentos-aws-template"
-    agentos_railway_template = "agentos-railway-template"
+    agentos_docker = "agentos-docker"
+    agentos_aws = "agentos-aws"
+    agentos_railway = "agentos-railway"
diff --git a/libs/agno_infra/agno/infra/operator.py b/libs/agno_infra/agno/infra/operator.py
index dffd21dc10..bc5bffccf8 100644
--- a/libs/agno_infra/agno/infra/operator.py
+++ b/libs/agno_infra/agno/infra/operator.py
@@ -18,14 +18,14 @@
 from agno.utils.log import log_info

 TEMPLATE_TO_NAME_MAP: Dict[InfraStarterTemplate, str] = {
-    InfraStarterTemplate.agentos_docker_template: "agentos-docker-template",
-    InfraStarterTemplate.agentos_aws_template: "agentos-aws-template",
-    InfraStarterTemplate.agentos_railway_template: "agentos-railway-template",
+    InfraStarterTemplate.agentos_docker: "agentos-docker",
+    InfraStarterTemplate.agentos_aws: "agentos-aws",
+    InfraStarterTemplate.agentos_railway: "agentos-railway",
 }
 TEMPLATE_TO_REPO_MAP: Dict[InfraStarterTemplate, str] = {
-    InfraStarterTemplate.agentos_docker_template: "https://github.com/agno-agi/agentos-docker-template",
-    InfraStarterTemplate.agentos_aws_template: "https://github.com/agno-agi/agentos-aws-template",
-    InfraStarterTemplate.agentos_railway_template: "https://github.com/agno-agi/agentos-railway-template",
+    InfraStarterTemplate.agentos_docker: "https://github.com/agno-agi/agentos-docker-template",
+    InfraStarterTemplate.agentos_aws: "https://github.com/agno-agi/agentos-aws-template",
+    InfraStarterTemplate.agentos_railway: "https://github.com/agno-agi/agentos-railway-template",
 }


@@ -61,7 +61,7 @@ def create_infra_from_template(

     infra_dir_name: Optional[str] = name
     repo_to_clone: Optional[str] = url
-    infra_template = InfraStarterTemplate.agentos_docker_template
+    infra_template = InfraStarterTemplate.agentos_docker
     templates = list(InfraStarterTemplate.__members__.values())

     print_subheading("Creating a new AgentOS codebase...\n")
@@ -71,7 +71,7 @@ def create_infra_from_template(
         if template is None:
             # Get starter template from the user if template is not provided
             # Display available starter templates and ask user to select one
-            print_info("Select starter template or press Enter for default (agentos-docker-template)")
+            print_info("Select starter template or press Enter for default (agentos-docker)")
             for template_id, template_name in enumerate(templates, start=1):
                 print_info("  [b][{}][/b] {}".format(template_id, InfraStarterTemplate(template_name).value))

@@ -104,7 +104,7 @@ def create_infra_from_template(
             default_infra_name = url.split("/")[-1].split(".")[0]
         else:
             # Get default_infra_name from template
-            default_infra_name = TEMPLATE_TO_NAME_MAP.get(infra_template, "agentos-docker-template")
+            default_infra_name = TEMPLATE_TO_NAME_MAP.get(infra_template, "agentos-docker")
         logger.debug(f"Asking for infra name with default: {default_infra_name}")
         # Ask user for infra name if not provided
         infra_dir_name = Prompt.ask("Infra Project Directory", default=default_infra_name, console=console)
diff --git a/libs/agno_infra/pyproject.toml b/libs/agno_infra/pyproject.toml
index cb692d6c91..d669edfc39 100644
--- a/libs/agno_infra/pyproject.toml
+++ b/libs/agno_infra/pyproject.toml
@@ -1,6 +1,6 @@
 [project]
 name = "agno-infra"
-version = "1.0.6"
+version = "1.0.7"
 description = "A lightweight framework and CLI for managing Agentic Infrastructure"
 requires-python = ">=3.7,<4"
 readme = "README.md"

PATCH

echo "Patch applied successfully."
