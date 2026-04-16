#!/bin/bash
set -e

cd /workspace/openhands

# Check if already patched (idempotency)
if grep -q "deprecated=True" openhands/server/routes/git.py 2>/dev/null; then
    echo "Patch already applied, exiting"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/openhands/server/routes/git.py b/openhands/server/routes/git.py
index bce73549fb11..2cbb3d9864c8 100644
--- a/openhands/server/routes/git.py
+++ b/openhands/server/routes/git.py
@@ -308,6 +308,7 @@ def _extract_repo_name(repository_name: str) -> str:
 @app.get(
     '/repository/{repository_name:path}/microagents',
     response_model=list[MicroagentResponse],
+    deprecated=True,
 )
 async def get_repository_microagents(
     repository_name: str,
@@ -317,6 +318,10 @@ async def get_repository_microagents(
 ) -> list[MicroagentResponse] | JSONResponse:
     """Scan the microagents directory of a repository and return the list of microagents.

+    .. deprecated::
+        This endpoint is deprecated. The microagents UI has already been removed
+        and is not supported in V1.
+
     The microagents directory location depends on the git provider and actual repository name:
     - If git provider is not GitLab and actual repository name is ".openhands": scans "microagents" folder
     - If git provider is GitLab and actual repository name is "openhands-config": scans "microagents" folder
@@ -371,6 +376,7 @@ async def get_repository_microagents(
 @app.get(
     '/repository/{repository_name:path}/microagents/content',
     response_model=MicroagentContentResponse,
+    deprecated=True,
 )
 async def get_repository_microagent_content(
     repository_name: str,
@@ -383,6 +389,10 @@ async def get_repository_microagent_content(
 ) -> MicroagentContentResponse | JSONResponse:
     """Fetch the content of a specific microagent file from a repository.

+    .. deprecated::
+        This endpoint is deprecated. The microagents UI has already been removed
+        and is not supported in V1.
+
     Args:
         repository_name: Repository name in the format 'owner/repo' or 'domain/owner/repo'
         file_path: Query parameter - Path to the microagent file within the repository
PATCH

echo "Patch applied successfully"
