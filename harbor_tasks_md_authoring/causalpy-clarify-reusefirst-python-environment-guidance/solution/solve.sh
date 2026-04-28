#!/usr/bin/env bash
set -euo pipefail

cd /workspace/causalpy

# Idempotency guard
if grep -qF "Git worktrees do not require a fresh env per agent session. Prefer reusing an ex" ".github/skills/python-environment/SKILL.md" && grep -qF "Use `mamba`, `micromamba`, or `conda` (in that preference order) to manage the `" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/python-environment/SKILL.md b/.github/skills/python-environment/SKILL.md
@@ -1,12 +1,32 @@
 ---
 name: python-environment
-description: Detect and configure a conda-compatible tool, create the CausalPy environment, and run commands inside it. Use before any task that requires Python execution.
+description: Detect, configure, and use a conda-compatible tool. Use before tasks that need the project environment, such as importing project code, running tests, building docs, or invoking repo tooling.
 ---
 
 # Python Environment
 
 Set up and run commands inside the CausalPy conda environment.
 
+## Decide whether the env is required
+
+Use the `CausalPy` env when the command:
+
+- imports project code (for example `import causalpy` or project modules)
+- runs tests
+- builds docs
+- invokes repo tooling such as `make`, `prek`, or notebook execution
+
+For simple inspection helpers that only read local text/JSON or use the Python standard library, any Python on `PATH` is acceptable.
+
+## Reuse before creating
+
+Do the least work that will get the task done:
+
+1. Reuse an existing `CausalPy` env if one is already available.
+2. If `run -n CausalPy` cannot resolve the env, check whether it exists under a different prefix and use `run -p`.
+3. Only create the env if no suitable existing env is available.
+4. Only update the env or rerun `make setup` when dependencies changed, the editable install is stale, or the current checkout has not been installed into that env yet.
+
 ## Detect the conda tool
 
 Use whichever of `mamba`, `micromamba`, or `conda` is available (checked in that order):
@@ -24,21 +44,25 @@ If `CONDA_EXE` is empty, no conda-compatible tool was found. Propose installing
 
 After installation, set `CONDA_EXE=micromamba`.
 
-## Create the environment
+## Create the environment only if needed
+
+If no suitable existing env can be reused, create it:
 
 ```bash
 $CONDA_EXE env create -f environment.yml
 ```
 
-## Install the package (required after creating or updating the environment)
+## Install the package only when needed
+
+Run `make setup` after creating or updating the env. Also rerun it when using a different git worktree if that env has not been installed against the current checkout yet.
 
 ```bash
 $CONDA_EXE run -n CausalPy make setup
 ```
 
 ## Run commands
 
-Always use `run -n` instead of `activate`:
+Never use `$CONDA_EXE activate`, instead use `$CONDA_EXE run -n CausalPy <command>`.
 
 ```bash
 $CONDA_EXE run -n CausalPy <command>
@@ -54,6 +78,25 @@ $CONDA_EXE env update --file environment.yml --prune
 
 ## Troubleshooting
 
+### Named env cannot be resolved
+
+If `$CONDA_EXE run -n CausalPy ...` fails with errors such as `The given prefix does not exist`:
+
+```bash
+$CONDA_EXE env list
+$CONDA_EXE run -p "/full/path/to/CausalPy" <command>
+```
+
+Keep using `run -p` with that full prefix for the rest of the session.
+
+### Git worktrees and remote machines
+
+Git worktrees do not require a fresh env per agent session. Prefer reusing an existing env to save time. The main caveat is that this repo uses editable installs, so one shared env can point at whichever checkout most recently ran `make setup`.
+
+- For ordinary local work on one checkout, reuse the existing env.
+- For long-lived parallel worktrees, one env per worktree is the safest option, but do not create one unless needed.
+- On a fresh remote machine or ephemeral container, create the env once. On a persistent remote machine with an existing env, reuse it.
+
 If you hit issues with an outdated tool, update it:
 
 - **mamba / micromamba**: `$CONDA_EXE self-update`
diff --git a/AGENTS.md b/AGENTS.md
@@ -2,10 +2,13 @@
 
 ## Environment
 
-Use `mamba`, `micromamba`, or `conda` (in that preference order) to manage the `CausalPy` environment. Always run commands via `$CONDA_EXE run -n CausalPy <command>` -- never use `$CONDA_EXE activate`.
+Use `mamba`, `micromamba`, or `conda` (in that preference order) to manage the `CausalPy` environment. Reuse an existing `CausalPy` env whenever possible; do not create or update an env unless the task needs the project environment and the existing env is missing, stale, or broken. Use `$CONDA_EXE run -n CausalPy <command>` for commands that import project code, run tests, build docs, or use repo tooling; never use `$CONDA_EXE activate`. For simple text/JSON inspection helpers that do not import project code, any Python on `PATH` is fine.
 
 See the [python-environment skill](.github/skills/python-environment/SKILL.md) for full setup instructions: tool detection, environment creation, editable install, and troubleshooting.
 
+- If `$CONDA_EXE run -n CausalPy ...` fails because the named env cannot be resolved, inspect `$CONDA_EXE env list` and retry with `$CONDA_EXE run -p <full-prefix> <command>`.
+- In git worktrees, prefer reusing an existing env. Because the repo uses editable installs, rerun `make setup` in the current worktree only when that checkout has not been installed into the env yet or when dependencies changed.
+
 - Dependencies live in `pyproject.toml`; `environment.yml` is generated from it (do not edit by hand—see CONTRIBUTING). Optional: `pymc-marketing` is in the `docs` extra only.
 - **Development**: The supported setup is the conda env (`environment.yml`). `pip install -e .[dev]` works but does not include conda-only tooling (e.g. `make`, `pymc-bart`, `marimo`); do not suggest pip-only dev as equivalent.
 
PATCH

echo "Gold patch applied."
