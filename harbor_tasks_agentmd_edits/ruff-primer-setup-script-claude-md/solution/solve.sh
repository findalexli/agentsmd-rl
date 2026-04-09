#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'setup_primer_project' CLAUDE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
index 22ca768ac55d2..e07aa1b2f1ede 100644
--- a/CLAUDE.md
+++ b/CLAUDE.md
@@ -62,6 +62,15 @@ Run ty:
 cargo run --bin ty -- check path/to/file.py
 ```

+## Reproducing ty ecosystem changes
+
+If asked to reproduce changes in the ty ecosystem, use this script to clone the project to some
+directory and install its dependencies into `.venv`:
+
+```sh
+uv run scripts/setup_primer_project.py <project-name> <some-temp-dir>
+```
+
 ## Pull Requests

 When working on ty, PR titles should start with `[ty]` and be tagged with the `ty` GitHub label.
diff --git a/scripts/pyproject.toml b/scripts/pyproject.toml
index c90df288ebb4b..b95471ed4ee66 100644
--- a/scripts/pyproject.toml
+++ b/scripts/pyproject.toml
@@ -1,7 +1,7 @@
 [project]
 name = "scripts"
 version = "0.0.1"
-dependencies = ["stdlibs", "tqdm", "mdformat", "pyyaml"]
+dependencies = ["stdlibs", "tqdm", "mdformat", "pyyaml", "mypy-primer"]
 requires-python = ">=3.12"

 [tool.black]
@@ -14,6 +14,9 @@ extend = "../pyproject.toml"
 # `ty_benchmark` is a standalone project with its own pyproject.toml files, search paths, etc.
 exclude = ["./ty_benchmark"]

+[tool.uv.sources]
+mypy-primer = { git = "https://github.com/hauntsaninja/mypy_primer" }
+
 [tool.ty.rules]
 possibly-unresolved-reference = "error"
 division-by-zero = "error"
diff --git a/scripts/setup_primer_project.py b/scripts/setup_primer_project.py
new file mode 100644
index 0000000000000..574ad4bd87f8f
--- /dev/null
+++ b/scripts/setup_primer_project.py
@@ -0,0 +1,104 @@
+#!/usr/bin/env python3
+# /// script
+# requires-python = ">=3.10"
+# dependencies = ["mypy-primer"]
+#
+# [tool.uv.sources]
+# mypy-primer = { git = "https://github.com/hauntsaninja/mypy_primer" }
+# ///
+"""Clone a mypy-primer project and set up a virtualenv with its dependencies installed.
+
+Usage: uv run scripts/setup_primer_project.py <project-name> [directory]
+"""
+
+from __future__ import annotations
+
+import argparse
+import shlex
+import subprocess
+import sys
+from pathlib import Path
+from typing import NoReturn
+
+from mypy_primer.model import Project
+from mypy_primer.projects import get_projects
+
+
+def find_project(name: str) -> Project:
+    projects = get_projects()
+    for p in projects:
+        if p.name == name:
+            return p
+    _project_not_found(name, projects)
+
+
+def _project_not_found(name: str, projects: list[Project]) -> NoReturn:
+    print(f"error: project {name!r} not found", file=sys.stderr)
+    print("available projects:", file=sys.stderr)
+    for p in sorted(projects, key=lambda p: p.name):
+        print(f"  {p.name}", file=sys.stderr)
+    sys.exit(1)
+
+
+def main() -> None:
+    parser = argparse.ArgumentParser(description=__doc__)
+    parser.add_argument("project", help="Name of a mypy-primer project")
+    parser.add_argument(
+        "directory",
+        nargs="?",
+        help="Directory to clone into (default: project name)",
+    )
+    args = parser.parse_args()
+
+    project = find_project(args.project)
+
+    target_dir = Path(args.directory or project.name).resolve()
+
+    # Clone (shallow if no pinned revision, same as primer)
+    clone_cmd = [
+        "git",
+        "clone",
+        "--recurse-submodules",
+        project.location,
+        str(target_dir),
+    ]
+    if not project.revision:
+        clone_cmd += ["--depth", "1"]
+    print(f"Cloning {project.location} into {target_dir}...")
+    subprocess.run(clone_cmd, check=True)
+
+    if project.revision:
+        print(f"Checking out revision {project.revision}...")
+        subprocess.run(
+            ["git", "checkout", project.revision], cwd=target_dir, check=True
+        )
+
+    # Create venv (matching primer's Venv.make_venv())
+    venv_dir = target_dir / ".venv"
+    print(f"Creating virtualenv at {venv_dir}...")
+    subprocess.run(
+        ["uv", "venv", str(venv_dir), "--python", sys.executable, "--seed", "--clear"],
+        check=True,
+    )
+
+    venv_python = venv_dir / "bin" / "python"
+    install_base = f"uv pip install --python {shlex.quote(str(venv_python))}"
+
+    # Run custom install command if the project defines one (matching primer's setup())
+    if project.install_cmd:
+        install_cmd = project.install_cmd.format(install=install_base)
+        print(f"Running install command: {install_cmd}")
+        subprocess.run(install_cmd, shell=True, cwd=target_dir, check=True)
+
+    # Install listed dependencies (matching primer's setup())
+    if project.deps:
+        deps_cmd = f"{install_base} {' '.join(project.deps)}"
+        print(f"Installing dependencies: {', '.join(project.deps)}")
+        subprocess.run(deps_cmd, shell=True, cwd=target_dir, check=True)
+
+    print(f"\nDone! Project set up at {target_dir}")
+    print(f"Activate the venv with: source {venv_dir}/bin/activate")
+
+
+if __name__ == "__main__":
+    main()

PATCH

echo "Patch applied successfully."
