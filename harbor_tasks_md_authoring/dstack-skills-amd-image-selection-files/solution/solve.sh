#!/usr/bin/env bash
set -euo pipefail

cd /workspace/dstack

# Idempotency guard
if grep -qF "2. **If the user asks for a specific framework/runtime, prefer official `rocm/*`" "skills/dstack/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/dstack/SKILL.md b/skills/dstack/SKILL.md
@@ -140,7 +140,7 @@ If background attach fails in the sandbox (permissions writing `~/.dstack` or `~
 `dstack` supports five main configuration types. Configuration files can be named `<name>.dstack.yml` or simply `.dstack.yml`.
 
 **Common parameters:** All run configurations (dev environments, tasks, services) support many parameters including:
-- **Git integration:** Clone repos automatically (`repo`), mount existing repos (`repos`), upload local files (`working_dir`)
+- **Git integration:** Clone repos automatically (`repo`), mount existing repos (`repos`)
 - **File upload:** `files` (see concept docs for examples)
 - **Docker support:** Use custom Docker images (`image`); use `docker: true` if you want to use Docker from inside the container (VM-based backends only)
 - **Environment:** Set environment variables (`env`), often via `.envrc`. Secrets are supported but less common.
@@ -150,6 +150,42 @@ If background attach fails in the sandbox (permissions writing `~/.dstack` or `~
 **Best practices:**
 - Prefer giving configurations a `name` property for easier management
 - When configurations need credentials (API keys, tokens), list only env var names in the `env` section (e.g., `- HF_TOKEN`), not values. Recommend storing actual values in a `.envrc` file alongside the configuration, applied via `source .envrc && dstack apply`.
+- `python` and `image` are mutually exclusive in run configurations. If `image` is set, do not set `python`.
+
+### `files` and `repos` intent policy
+
+Use `files` and `repos` only when the user intends to use local/repo files inside the run.
+
+- If user asks to use project code/data/config in the run, then add `files` or `repos` as appropriate.
+- If it is totally unclear whether files ore repos must be mounted, ask one explicit clarification question or default to not mounting.
+
+`files` guidance:
+- Relative paths are valid and preferred for local project files.
+- A relative `files` path is placed under the run's `working_dir` (default or set by user).
+
+`repos` + image/working directory guidance:
+- With non-default Docker images, prefer explicit absolute mount targets for `repos` (e.g., `.:/dstack/run`).
+- When setting an explicit repo mount path, also set `working_dir` to the same path.
+- Reason: custom images may have a different/non-empty default working directory, and mounting a repo into a non-empty path can fail.
+- With `dstack` default images, the default `working_dir` is already `/dstack/run`.
+
+### AMD image selection policy
+
+When `resources.gpu` targets AMD (e.g., `MI300X`), you have to set `image`.
+
+Use the official ROCm Docker image namespace as the default source: `https://hub.docker.com/u/rocm`
+
+1. **If the user provides an image, use it as-is.** Do not override user intent.
+2. **If the user asks for a specific framework/runtime, prefer official `rocm/*` framework images and select tags with the latest available ROCm version by default. Pick the most recent ROCm-compatible tag appropriate for the requested AMD GPU family.**
+   - **SGLang:** `rocm/sgl-dev`
+   - **vLLM:** `rocm/vllm`
+   - **PyTorch-only:** `rocm/pytorch`
+3. **If no framework is specified (generic AMD dev/task use case), default to**
+   `rocm/dev-ubuntu-24.04`.
+
+Additional guidance:
+- Prefer `:latest` where applicable for generic/default recommendations, unless the user asks for pinning or reproducibility.
+- Ensure AMD-compatible images include ROCm userspace/tooling; avoid non-ROCm images for AMD GPU runs.
 
 ### 1. Dev environments
 **Use for:** Interactive development with IDE integration (VS Code, Cursor, etc.).
PATCH

echo "Gold patch applied."
