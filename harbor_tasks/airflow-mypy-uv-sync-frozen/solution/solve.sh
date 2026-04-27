#!/bin/bash
set -euo pipefail

cd /workspace/airflow

if grep -q 'uv sync --frozen --project' scripts/ci/prek/mypy_local_folder.py; then
    echo "Solution already applied."
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.pre-commit-config.yaml b/.pre-commit-config.yaml
index 77033ceadc584..53df1dd0af140 100644
--- a/.pre-commit-config.yaml
+++ b/.pre-commit-config.yaml
@@ -1006,12 +1006,14 @@ repos:
         pass_filenames: false
         files: ^dev/breeze/src/airflow_breeze/global_constants\.py$
         require_serial: true
-        # This is a fast regular hook that runs when any pyproject.toml changes
-        # It runs locally and usually will not result in modifying the lock unnecessarily
-        # Unless there is a conflict and uv will determine that the lock needs to be updated to resolve it
+        # This is a fast regular hook that runs when any pyproject.toml changes.
+        # It runs locally with `--frozen` so the lock is only verified against pyproject.toml,
+        # never silently rewritten during a commit. If a pyproject.toml change makes the lock
+        # stale, the hook fails and the contributor must run `uv lock` explicitly and commit
+        # the refreshed uv.lock — which keeps lock updates intentional and reviewable.
       - id: update-uv-lock
         name: Update uv.lock
-        entry: uv lock
+        entry: uv lock --frozen
         language: system
         files: >
           (?x)
diff --git a/AGENTS.md b/AGENTS.md
index 36af179f50b9d..f38bc2dd33703 100644
--- a/AGENTS.md
+++ b/AGENTS.md
@@ -30,7 +30,7 @@
 - **Run other suites of tests** `breeze testing <test_group>` (test groups: `airflow-ctl-tests`, `docker-compose-tests`, `task-sdk-tests`)
 - **Run scripts tests:** `uv run --project scripts pytest scripts/tests/ -xvs`
 - **Run Airflow CLI:** `breeze run airflow dags list`
-- **Type-check (non-providers):** `uv run --project <PROJECT> --with "apache-airflow-devel-common[mypy]" mypy path/to/code`
+- **Type-check (non-providers):** first run `uv sync --frozen --project <PROJECT>` to align the local virtualenv with `uv.lock` (the dependency set CI uses), then `uv run --frozen --project <PROJECT> --with "apache-airflow-devel-common[mypy]" mypy path/to/code`
 - **Type-check (providers):** `breeze run mypy path/to/code`
 - **Lint with ruff only:** `prek run ruff --from-ref <target_branch>`
 - **Format with ruff only:** `prek run ruff-format --from-ref <target_branch>`
diff --git a/contributing-docs/08_static_code_checks.rst b/contributing-docs/08_static_code_checks.rst
index 23256c6c0e026..4eed1a98a13f9 100644
--- a/contributing-docs/08_static_code_checks.rst
+++ b/contributing-docs/08_static_code_checks.rst
@@ -287,7 +287,16 @@ For **non-provider projects** (airflow-core, task-sdk, airflow-ctl, dev, scripts
 runs locally using the ``uv`` virtualenv — no breeze CI image is needed. These checks run as regular
 prek hooks in the ``pre-commit`` stage, checking whole directories at once. This means they run both
 as part of local commits and as part of regular static checks in CI (not as separate mypy CI jobs).
-You can also run mypy directly. Use ``--frozen`` to avoid updating ``uv.lock``:
+
+Before running mypy directly (or via the ``mypy-*`` prek hooks), synchronize your local virtualenv
+with ``uv.lock`` so it matches the dependency set CI uses — otherwise mypy may pick up a different
+set of installed packages than CI and produce results that diverge from CI:
+
+.. code-block:: bash
+
+  uv sync --frozen --project <PROJECT>
+
+Then run mypy directly. Use ``--frozen`` so ``uv`` does not update ``uv.lock``:

 .. code-block:: bash

diff --git a/scripts/ci/prek/mypy_local_folder.py b/scripts/ci/prek/mypy_local_folder.py
index e578079b11fa8..568fe1c06e49f 100755
--- a/scripts/ci/prek/mypy_local_folder.py
+++ b/scripts/ci/prek/mypy_local_folder.py
@@ -186,7 +186,33 @@ def get_all_files(folder: str) -> list[str]:
         },
     )
 else:
-    # Locally, run via uv with --frozen to not update the lock file.
+    # Locally, first synchronize the project's virtualenv with uv.lock so that mypy runs
+    # against the same dependency set CI uses. Without this, the local .venv can drift from
+    # uv.lock (e.g. after switching branches or installing extras) and mypy results would
+    # diverge from CI. --frozen ensures uv.lock itself is not updated.
+    sync_cmd = ["uv", "sync", "--frozen", "--project", project]
+    if console:
+        console.print(f"[magenta]Syncing virtualenv for project {project}: {' '.join(sync_cmd)}[/]")
+    else:
+        print(f"Syncing virtualenv for project {project}: {' '.join(sync_cmd)}")
+    sync_result = subprocess.run(
+        sync_cmd,
+        cwd=str(AIRFLOW_ROOT_PATH),
+        check=False,
+        env={**os.environ, "TERM": "ansi"},
+    )
+    if sync_result.returncode != 0:
+        msg = (
+            f"`uv sync --frozen --project {project}` failed. Fix the sync error before running mypy — "
+            "otherwise the local virtualenv may not match uv.lock and mypy results will diverge from CI.\n"
+        )
+        if console:
+            console.print(f"[red]{msg}")
+        else:
+            print(msg)
+        sys.exit(sync_result.returncode)
+
+    # Then run mypy via uv with --frozen to not update the lock file.
     cmd = [
         "uv",
         "run",
@@ -211,8 +237,9 @@ def get_all_files(folder: str) -> list[str]:
     msg = (
         "Mypy check failed. You can run mypy locally with:\n"
         f"  prek run mypy-{mypy_folders[0]} --all-files\n"
-        "Or directly with:\n"
-        f'  uv run --project {project} --with "apache-airflow-devel-common[mypy]" mypy <files>\n'
+        "Or directly (first sync the virtualenv to match CI's dependency set):\n"
+        f"  uv sync --frozen --project {project}\n"
+        f'  uv run --frozen --project {project} --with "apache-airflow-devel-common[mypy]" mypy <files>\n'
         "You can also clear the mypy cache with:\n"
         "  breeze down --cleanup-mypy-cache\n"
     )
PATCH

echo "Patch applied."
