#!/usr/bin/env bash
set -euo pipefail

cd /workspace/yfinance-mcp

# Idempotency guard
if grep -qF "- `README.md`: end-user setup and usage guide. Demo chatbot link points to the d" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -6,7 +6,7 @@
 - `src/yfmcp/types.py`: shared Literal types (`SearchType`, `TopType`, `Period`, `Interval`, `ChartType`, `ErrorCode`).
 - `src/yfmcp/utils.py`: JSON helpers, including `create_error_response()`.
 - `tests/`: async pytest suite for server tools, charts, and type behavior.
-- `demo.py`: Chainlit demo client that calls MCP tools and renders chart images.
+- `README.md`: end-user setup and usage guide. Demo chatbot link points to the dedicated `yfinance-mcp-demo` repository.
 
 ## Architecture Overview
 - MCP tools are exposed from `yfmcp.server` with `yfinance_`-prefixed names:
@@ -17,9 +17,8 @@
 
 ## Build, Test, and Development Commands
 - `uv sync`: install runtime dependencies.
-- `uv sync --extra dev`: install dev/demo dependencies.
+- `uv sync --extra dev`: install development dependencies.
 - `uv run yfmcp`: run the MCP server.
-- `uv run chainlit run demo.py`: run the demo chatbot.
 - `uv run ruff check .` and `uv run ruff format .`: lint/format.
 - `uv run ty check src tests`: type check.
 - `uv run pytest -v -s --cov=src tests`: full test run with coverage.
@@ -33,8 +32,7 @@
 ## Commit & Pull Request Guidelines
 - Prefer short, imperative commit subjects (for example: `Fix import order`, `Update README`).
 - Keep commits focused; include tests when behavior changes.
-- PRs should summarize intent, validation commands run, and screenshots for demo/chart UI changes.
+- PRs should summarize intent and list the validation commands run.
 
 ## Configuration & Secrets
-- Use `.env` for demo credentials (`OPENAI_API_KEY` or LiteLLM settings).
 - Never commit secrets or generated artifacts.
PATCH

echo "Gold patch applied."
