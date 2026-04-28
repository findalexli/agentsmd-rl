#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mcp-context-forge

# Idempotency guard
if grep -qF "- [Multi-Transport Design](docs/docs/architecture/adr/003-expose-multi-transport" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -6,7 +6,9 @@ Never mention Claude or Claude Code in your PRs, diffs, etc.
 
 ## Project Overview
 
-MCP Gateway (ContextForge) is a production-grade gateway, proxy, and registry for Model Context Protocol (MCP) servers and A2A Agents. It federates MCP and REST services, providing unified discovery, auth, rate-limiting, observability, virtual servers, multi-transport protocols, and an optional Admin UI.
+MCP Gateway (ContextForge) is a production-grade gateway, proxy, and registry for Model Context Protocol (MCP) servers
+and A2A Agents. It federates MCP and REST services, providing unified discovery, auth, rate-limiting, observability,
+virtual servers, multi-transport protocols, and an optional Admin UI.
 
 ## Essential Commands
 
@@ -45,121 +47,15 @@ make doctest test htmlcov smoketest lint-web flake8 bandit interrogate pylint ve
 make doctest test htmlcov         # Doctests + unit tests + coverage (→ docs/docs/coverage/index.html)
 make smoketest                    # End-to-end container testing
 
-# Testing individual files (activate env first)
-. /home/cmihai/.venv/mcpgateway/bin/activate && pytest --cov-report=annotate tests/unit/mcpgateway/test_translate.py
+# Testing individual files (using uv environment manager)
+uv run pytest --cov-report=annotate tests/unit/mcpgateway/test_translate.py
 ```
 
-## Performance Configuration
-
-### Response Compression
-
-The gateway includes automatic response compression middleware (Brotli, Zstd, GZip) that reduces bandwidth usage by 30-70% for text-based responses (JSON, HTML, CSS, JS).
-
-**Configuration** (`.env.example`):
-```bash
-# Enable/disable compression
-COMPRESSION_ENABLED=true                 # Default: true
-
-# Minimum response size to compress (bytes)
-COMPRESSION_MINIMUM_SIZE=500             # Default: 500 bytes
-
-# Compression quality levels
-COMPRESSION_GZIP_LEVEL=6                 # GZip: 1-9 (default: 6 balanced)
-COMPRESSION_BROTLI_QUALITY=4             # Brotli: 0-11 (default: 4 balanced)
-COMPRESSION_ZSTD_LEVEL=3                 # Zstd: 1-22 (default: 3 fast)
-```
-
-**Algorithm Priority**: Brotli (best) > Zstd (fast) > GZip (universal)
-
-**Testing Compression** (requires running server):
-```bash
-# Start server
-make dev
-
-# Test Brotli compression (best compression ratio)
-curl -H "Accept-Encoding: br" http://localhost:8000/openapi.json -v 2>&1 | grep -i "content-encoding"
-# Should show: content-encoding: br
-
-# Test GZip compression (universal fallback)
-curl -H "Accept-Encoding: gzip" http://localhost:8000/openapi.json -v 2>&1 | grep -i "content-encoding"
-# Should show: content-encoding: gzip
-
-# Test Zstd compression (fastest)
-curl -H "Accept-Encoding: zstd" http://localhost:8000/openapi.json -v 2>&1 | grep -i "content-encoding"
-# Should show: content-encoding: zstd
-
-# Verify Vary header (for cache compatibility)
-curl -H "Accept-Encoding: br" http://localhost:8000/openapi.json -v 2>&1 | grep -i "vary"
-# Should show: vary: Accept-Encoding
-
-# Test minimum size threshold (small responses not compressed)
-curl -H "Accept-Encoding: br" http://localhost:8000/health -v 2>&1 | grep -i "content-encoding"
-# Should NOT show content-encoding (response too small)
-
-# Measure compression ratio
-curl -w "%{size_download}\n" -o /dev/null -s http://localhost:8000/openapi.json  # Uncompressed
-curl -H "Accept-Encoding: br" -w "%{size_download}\n" -o /dev/null -s http://localhost:8000/openapi.json  # Brotli
-```
-
-**Implementation Details**:
-- Middleware location: `mcpgateway/main.py:888-907`
-- Config settings: `mcpgateway/config.py:379-384`
-- Only compresses responses > `COMPRESSION_MINIMUM_SIZE` bytes
-- Automatically negotiates algorithm based on client `Accept-Encoding` header
-- Adds `Vary: Accept-Encoding` header for proper cache behavior
-- No client changes required (browsers handle decompression automatically)
-
-### JSON Serialization (orjson)
-
-The gateway uses **orjson** for high-performance JSON serialization, providing **5-6x faster serialization** and **1.5-2x faster deserialization** compared to Python's standard library.
-
-**Performance Benefits**:
-- **Serialization**: 5-6x faster (550-623% speedup)
-- **Deserialization**: 1.5-2x faster (55-115% speedup)
-- **Output size**: 7% smaller (more compact JSON)
-- **Zero configuration**: Drop-in replacement, works automatically
-
-**Why orjson?**
-- Rust-based implementation for maximum performance
-- RFC 8259 compliant (strict JSON specification)
-- Native support for datetime, UUID, numpy arrays
-- Used by major companies (Reddit, Stripe, etc.)
-
-**Testing JSON Serialization** (requires running server):
-```bash
-# Start server
-make dev
-
-# Benchmark JSON serialization performance
-python scripts/benchmark_json_serialization.py
-
-# Test endpoint response times
-time curl -s http://localhost:8000/tools > /dev/null
-
-# Verify orjson unit tests
-pytest tests/unit/mcpgateway/utils/test_orjson_response.py -v --cov=mcpgateway.utils.orjson_response --cov-report=term-missing
-```
-
-**Implementation Details**:
-- Response class: `mcpgateway/utils/orjson_response.py`
-- FastAPI config: `mcpgateway/main.py:408` (default_response_class=ORJSONResponse)
-- Benchmark script: `scripts/benchmark_json_serialization.py`
-- Options: OPT_NON_STR_KEYS (allows int keys), OPT_SERIALIZE_NUMPY (numpy support)
-- Datetime format: RFC 3339 (ISO 8601 with timezone)
-- No client changes required (standard JSON, fully compatible)
-
-**Performance Impact**:
-- Large endpoints (GET /tools, GET /servers): 20-40% faster response time
-- Bulk exports: 50-60% faster serialization
-- API throughput: 15-30% higher requests/second
-- CPU usage: 10-20% lower per request
-
-**Documentation**: See `docs/docs/testing/performance.md` for detailed benchmarks
-
 ## Architecture Overview
 
 ### Technology Stack
 - **FastAPI** with **Pydantic** validation and **SQLAlchemy** ORM
+  - FastAPI is build on Starlette ASGI framework
 - **HTMX + Alpine.js** for admin UI
 - **SQLite** default, **PostgreSQL** support, **Redis** for caching/federation
 - **Alembic** for database migrations
@@ -315,52 +211,14 @@ make security-scan                   # Trivy + Grype vulnerability scans
 4. Implement hooks: pre/post request/response
 5. Test: `pytest tests/unit/mcpgateway/plugins/`
 
-## A2A (Agent-to-Agent) Integration
-
-A2A agents are external AI agents (OpenAI, Anthropic, custom) integrated as tools within virtual servers.
-
-### Integration Workflow
-1. **Register Agent**: Add via `/a2a` API or Admin UI
-2. **Associate with Server**: Include agent ID in virtual server's `associated_a2a_agents`
-3. **Auto-Tool Creation**: Gateway creates tools for associated agents
-4. **Tool Invocation**: Standard tool invocation routes to A2A agents
-5. **Metrics Collection**: Comprehensive interaction tracking
-
-### Configuration Effects
-- `MCPGATEWAY_A2A_ENABLED=false`: Disables all A2A features (API 404, UI hidden)
-- `MCPGATEWAY_A2A_METRICS_ENABLED=false`: Disables metrics collection only
-
-## API Endpoints Overview
-
-### Core MCP Protocol
-- `POST /` - JSON-RPC endpoint for MCP protocol
-- `GET /servers/{id}/sse` - Server-Sent Events transport
-- `WS /servers/{id}/ws` - WebSocket transport
-- `GET /.well-known/mcp` - Well-known URI handler
-
-### Admin APIs (when `MCPGATEWAY_ADMIN_API_ENABLED=true`)
-- `GET/POST /tools` - Tool management and invocation
-- `GET/POST /resources` - Resource management
-- `GET/POST /prompts` - Prompt templates
-- `GET/POST /servers` - Virtual server management
-- `GET/POST /gateways` - Peer gateway federation
-- `GET/POST /a2a` - A2A agent management
-- `GET/POST /tags` - Tag management system
-- `POST /bulk-import` - Bulk import operations
-- `GET /admin` - Admin UI dashboard
-
-### Observability
-- `GET /health` - Health check endpoint
-- `GET /metrics` - Prometheus metrics (when enabled)
-- `GET /openapi.json` - OpenAPI specification
-
 ## Development Guidelines
 
 ### Git & Commit Standards
 - **Always sign commits**: Use `git commit -s` (DCO requirement)
 - **Conventional Commits**: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
 - **Link Issues**: Include `Closes #123` in commit messages
 - **No Claude mentions**: Never mention Claude or Claude Code in PRs/diffs
+- DO NOT include test plans in pull requests
 - **No estimates**: Don't include effort estimates or "phases"
 
 ### Code Style & Standards
@@ -379,6 +237,7 @@ A2A agents are external AI agents (OpenAI, Anthropic, custom) integrated as tool
 ### CLI Tools Available
 - `gh` for GitHub operations: `gh issue view 586`, `gh pr create`
 - `make` for all build/test operations
+- uv for managing virtual environments
 - Standard development tools: pytest, black, isort, etc.
 
 ## Quick Reference
@@ -400,3 +259,49 @@ make autoflake isort black pre-commit
 # Complete quality pipeline
 make doctest test htmlcov smoketest lint-web flake8 bandit interrogate pylint verify
 ```
+
+## Documentation Quick Links
+
+### Getting Started
+- [Developer Onboarding](docs/docs/development/developer-onboarding.md) - Complete setup guide for new contributors
+- [Building & Testing](docs/docs/development/building.md) - Build system, testing workflows, coverage
+- [Configuration Reference](docs/docs/manage/configuration.md) - Environment variables and settings
+
+### API & Protocol Reference
+- [REST API Usage](docs/docs/manage/api-usage.md) - Comprehensive REST API guide with curl examples
+- [MCP JSON-RPC Guide](docs/docs/development/mcp-developer-guide-json-rpc.md) - Low-level MCP protocol implementation
+- [OpenAPI Interactive Docs](http://localhost:4444/docs) - Swagger UI (requires running server)
+- [OpenAPI Schema](http://localhost:4444/openapi.json) - Machine-readable API specification
+
+### Core Features
+- [A2A Agent Integration](docs/docs/using/agents/a2a.md) - Agent-to-Agent setup, authentication, monitoring
+- [Plugin Development](docs/docs/architecture/plugins.md) - Plugin framework, hooks, creating custom plugins
+- [Virtual Servers](docs/docs/manage/api-usage.md#virtual-server-management) - Creating and managing composite MCP servers
+- [Export/Import Reference](docs/docs/manage/export-import-reference.md) - Bulk operations and configuration migration
+
+### Architecture & Design
+- [Architecture Overview](docs/docs/architecture/index.md) - System design, components, data flow
+- [ADR Index](docs/docs/architecture/adr/index.md) - Architecture Decision Records
+- [Security Architecture](docs/docs/architecture/security-features.md) - Authentication, authorization, security features
+- [Multi-Transport Design](docs/docs/architecture/adr/003-expose-multi-transport-endpoints.md) - HTTP, WebSocket, SSE, STDIO
+
+### Operations & Management
+- [Logging & Monitoring](docs/docs/manage/logging.md) - Log configuration, rotation, analysis
+- [Performance Tuning](docs/docs/testing/performance.md) - Benchmarks, optimization, profiling
+- [Scaling & High Availability](docs/docs/manage/scale.md) - Horizontal scaling, load balancing, federation
+- [Well-Known URIs](docs/docs/manage/well-known-uris.md) - Standard endpoints (robots.txt, security.txt)
+
+### Deployment
+- [Container Deployment](docs/docs/deployment/container.md) - Docker/Podman setup and configuration
+- [Kubernetes Deployment](docs/docs/deployment/kubernetes.md) - K8s manifests and Helm charts
+- [Cloud Deployments](docs/docs/deployment/) - AWS, Azure, GCP, Fly.io guides
+
+### Testing & Quality
+- [Testing Guide](docs/docs/testing/basic.md) - Unit, integration, E2E, security testing
+- [Fuzzing & Property Testing](docs/docs/testing/fuzzing.md) - Advanced testing techniques
+- [Documentation Standards](docs/docs/development/documentation.md) - Writing and maintaining docs
+
+### Integration Guides
+- [Agent Frameworks](docs/docs/using/agents/) - LangChain, CrewAI, LangGraph, AutoGen
+- [MCP Clients](docs/docs/using/clients/) - Claude Desktop, Continue, Zed, OpenWebUI
+- [MCP Servers](docs/docs/using/servers/) - Example server integrations
PATCH

echo "Gold patch applied."
