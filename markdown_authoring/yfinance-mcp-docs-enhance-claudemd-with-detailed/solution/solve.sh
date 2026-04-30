#!/usr/bin/env bash
set -euo pipefail

cd /workspace/yfinance-mcp

# Idempotency guard
if grep -qF "Charts use WebP format for efficient token usage in MCP responses. The demo chat" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -38,20 +38,37 @@ uv run ty src/
 ## Architecture
 
 ### MCP Server
-- `src/yfmcp/server.py` - Main FastMCP server with all tool implementations (`get_ticker_info`, `get_ticker_news`, `search`, `get_top`, `get_price_history`)
+- `src/yfmcp/server.py` - Main FastMCP server with all tool implementations
+  - All tools are async and use `asyncio.to_thread()` to wrap blocking yfinance calls
+  - Tools: `get_ticker_info`, `get_ticker_news`, `search`, `get_top`, `get_price_history`
+  - Error handling returns JSON with `{"error": "message"}` format via `_error()` helper
+  - All MCP tools are prefixed with `yfinance_` to avoid naming conflicts
 - `src/yfmcp/types.py` - Literal type definitions for enums (Sector, TopType, Period, Interval, ChartType, SearchType)
+- `src/yfmcp/chart.py` - Chart generation using mplfinance and matplotlib
+  - `generate_chart()` - Main function that returns base64-encoded WebP images
+  - `_calculate_volume_profile()` - Helper for volume profile chart type
+  - Uses non-interactive matplotlib backend (`Agg`) to avoid display issues
+  - Converts WebP images to base64 for efficient token usage in MCP responses
 - Entry point: `yfmcp.server:main` via `yfmcp` command
 
 ### Demo Chatbot
 - `demo.py` - Chainlit-based chatbot demo that connects to the MCP server
-  - Supports both OpenAI and LiteLLM backends
+  - Supports both OpenAI and LiteLLM backends (configurable via environment variables)
   - Handles tool calling with automatic image/chart display
-  - Manages persistent MCP session throughout chat lifecycle
+  - Manages persistent MCP session throughout chat lifecycle (reuses session across messages)
+  - WebP to PNG conversion for better Chainlit compatibility
   - Key functions:
-    - `get_mcp_client()` - Creates MCP client connection
+    - `get_mcp_client()` - Creates MCP client connection using stdio transport
     - `extract_tool_result()` - Extracts text and images from tool results
-    - `convert_mcp_tools_to_openai_format()` - Converts MCP tools to OpenAI format
+    - `convert_mcp_tools_to_openai_format()` - Converts MCP tools to OpenAI tool format
     - `handle_error()` - Unified error handling and logging
+    - `chat_completion()` - Unified API call wrapper supporting both OpenAI and LiteLLM
+
+### Testing
+- `tests/test_server.py` - Integration tests for MCP server
+  - Tests use `stdio_client` to connect to the actual server
+  - All tests are async using `@pytest.mark.asyncio`
+  - Tests verify JSON response structure and data correctness
 
 ## Key Dependencies
 
@@ -67,3 +84,17 @@ uv run ty src/
 - `python-dotenv` - Environment variable management
 - `loguru` - Logging library
 - `Pillow` - Image processing (for WebP to PNG conversion)
+
+## Development Notes
+
+### Async/Await Pattern
+All MCP tool functions in `server.py` are async. Since `yfinance` is synchronous, all blocking calls are wrapped with `asyncio.to_thread()` to avoid blocking the event loop. This pattern should be maintained for any new tools.
+
+### Chart Generation
+Charts use WebP format for efficient token usage in MCP responses. The demo chatbot converts WebP to PNG for better browser compatibility. When adding new chart types, follow the pattern in `chart.py` using mplfinance and return `ImageContent` objects.
+
+### Tool Naming Convention
+All MCP tools are prefixed with `yfinance_` (e.g., `yfinance_get_ticker_info`) to avoid naming conflicts when this server is used alongside other MCP servers.
+
+### Error Handling
+Use the `_error()` helper function to return consistent JSON error messages: `{"error": "message"}`. Always provide helpful error messages that guide users on how to fix the issue.
PATCH

echo "Gold patch applied."
