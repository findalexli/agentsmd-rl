#!/usr/bin/env bash
set -euo pipefail

cd /workspace/langchain

# Idempotency guard
if grep -qF "Model profiles are generated using the `langchain-profiles` CLI in `libs/model-p" "AGENTS.md" && grep -qF "Model profiles are generated using the `langchain-profiles` CLI in `libs/model-p" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -194,6 +194,29 @@ def send_email(to: str, msg: str, *, priority: str = "normal") -> bool:
 - Ensure American English spelling (e.g., "behavior", not "behaviour")
 - Do NOT use Sphinx-style double backtick formatting (` ``code`` `). Use single backticks (`` `code` ``) for inline code references in docstrings and comments.
 
+## Model profiles
+
+Model profiles are generated using the `langchain-profiles` CLI in `libs/model-profiles`. The `--data-dir` must point to the directory containing `profile_augmentations.toml`, not the top-level package directory.
+
+```bash
+# Run from libs/model-profiles
+cd libs/model-profiles
+
+# Refresh profiles for a partner in this repo
+uv run langchain-profiles refresh --provider openai --data-dir ../partners/openai/langchain_openai/data
+
+# Refresh profiles for a partner in an external repo (requires echo y to confirm)
+echo y | uv run langchain-profiles refresh --provider google --data-dir /path/to/langchain-google/libs/genai/langchain_google_genai/data
+```
+
+Example partners with profiles in this repo:
+
+- `libs/partners/openai/langchain_openai/data/` (provider: `openai`)
+- `libs/partners/anthropic/langchain_anthropic/data/` (provider: `anthropic`)
+- `libs/partners/perplexity/langchain_perplexity/data/` (provider: `perplexity`)
+
+The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.
+
 ## Additional resources
 
 - **Documentation:** https://docs.langchain.com/oss/python/langchain/overview and source at https://github.com/langchain-ai/docs or `../docs/`. Prefer the local install and use file search tools for best results. If needed, use the docs MCP server as defined in `.mcp.json` for programmatic access.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -194,6 +194,29 @@ def send_email(to: str, msg: str, *, priority: str = "normal") -> bool:
 - Ensure American English spelling (e.g., "behavior", not "behaviour")
 - Do NOT use Sphinx-style double backtick formatting (` ``code`` `). Use single backticks (`` `code` ``) for inline code references in docstrings and comments.
 
+## Model profiles
+
+Model profiles are generated using the `langchain-profiles` CLI in `libs/model-profiles`. The `--data-dir` must point to the directory containing `profile_augmentations.toml`, not the top-level package directory.
+
+```bash
+# Run from libs/model-profiles
+cd libs/model-profiles
+
+# Refresh profiles for a partner in this repo
+uv run langchain-profiles refresh --provider openai --data-dir ../partners/openai/langchain_openai/data
+
+# Refresh profiles for a partner in an external repo (requires echo y to confirm)
+echo y | uv run langchain-profiles refresh --provider google --data-dir /path/to/langchain-google/libs/genai/langchain_google_genai/data
+```
+
+Example partners with profiles in this repo:
+
+- `libs/partners/openai/langchain_openai/data/` (provider: `openai`)
+- `libs/partners/anthropic/langchain_anthropic/data/` (provider: `anthropic`)
+- `libs/partners/perplexity/langchain_perplexity/data/` (provider: `perplexity`)
+
+The `echo y |` pipe is required when `--data-dir` is outside the `libs/model-profiles` working directory.
+
 ## Additional resources
 
 - **Documentation:** https://docs.langchain.com/oss/python/langchain/overview and source at https://github.com/langchain-ai/docs or `../docs/`. Prefer the local install and use file search tools for best results. If needed, use the docs MCP server as defined in `.mcp.json` for programmatic access.
PATCH

echo "Gold patch applied."
