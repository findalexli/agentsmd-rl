#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sdk-typescript

# Idempotency guard
if grep -qF "- **`strands-py/strands/`**: Python package source with agent, models, multiagen" "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -180,6 +180,50 @@ sdk-typescript/
 │   ├── vitest.config.ts          # Testing configuration
 │   └── eslint.config.js          # Linting configuration
 │
+├── strands-py/                   # Python SDK bindings (WASM-based)
+│   ├── strands/                  # Python package source
+│   │   ├── _generated/           # Auto-generated type bindings
+│   │   ├── agent/                # Agent implementation
+│   │   │   └── conversation_manager/
+│   │   ├── event_loop/           # Event loop and retry logic
+│   │   ├── models/               # Model providers (Bedrock, Anthropic, OpenAI, Gemini)
+│   │   ├── multiagent/           # Multi-agent orchestration (Graph, Swarm)
+│   │   ├── session/              # Session management (file, S3)
+│   │   ├── tools/                # Tool definitions and MCP client
+│   │   │   └── mcp/
+│   │   ├── types/                # Type definitions
+│   │   ├── _conversions.py       # Type conversions between TS and Python
+│   │   ├── _wasm_host.py         # WASM host runtime bridge
+│   │   ├── hooks.py              # Hooks system
+│   │   └── interrupt.py          # Interrupt handling
+│   ├── scripts/                  # Build/codegen scripts
+│   │   └── generate_types.py     # Type generation from WIT definitions
+│   ├── examples/                 # Example applications
+│   ├── tests_integ/              # Integration tests
+│   ├── pyproject.toml            # Python package configuration
+│   └── pyrightconfig.json        # Python type checking configuration
+│
+├── strands-wasm/                 # WASM build tooling
+│   ├── entry.ts                  # WASM entry point (TS SDK surface for WASM compilation)
+│   ├── build.js                  # Build script for WASM compilation
+│   ├── patches/                  # Runtime patches for WASM compatibility
+│   │   └── getChunkedStream.js
+│   └── package.json              # WASM package configuration
+│
+├── strands-dev/                  # Developer CLI tooling
+│   ├── src/
+│   │   └── cli.ts                # CLI entry point
+│   ├── package.json              # Dev CLI package configuration
+│   └── tsconfig.json             # TypeScript configuration
+│
+├── wit/                          # WebAssembly Interface Type definitions
+│   └── agent.wit                 # WIT contract between TS SDK and WASM hosts
+│
+├── docs/                         # Project documentation
+│   ├── TESTING.md                # Comprehensive testing guidelines
+│   ├── DEPENDENCIES.md           # Dependency management guidelines
+│   └── PR.md                     # Pull request guidelines and template
+│
 ├── .github/                      # GitHub Actions workflows
 │   └── workflows/
 │
@@ -216,6 +260,14 @@ sdk-typescript/
 - **`strands-ts/src/vended-tools/`**: Optional vended tools (bash, file-editor, http-request, notebook)
 - **`strands-ts/test/integ/`**: Integration tests (tests public API and external integrations)
 - **`strands-ts/examples/`**: Example applications
+- **`strands-py/`**: Python SDK bindings powered by the TS SDK compiled to WASM
+- **`strands-py/strands/`**: Python package source with agent, models, multiagent, session, tools, and type modules
+- **`strands-py/scripts/`**: Build and codegen scripts (type generation from WIT definitions)
+- **`strands-py/tests_integ/`**: Python integration tests
+- **`strands-wasm/`**: WASM build tooling for compiling the TS SDK to WebAssembly
+- **`strands-dev/`**: Developer CLI tooling for local development workflows
+- **`wit/`**: WebAssembly Interface Type (WIT) definitions defining the contract between the TS SDK and WASM hosts
+- **`docs/`**: Project documentation (testing guidelines, dependency management, PR guidelines)
 - **`.github/workflows/`**: CI/CD automation and quality gates
 
 **IMPORTANT**: After making changes that affect the directory structure (adding new directories, moving files, or adding significant new files), you MUST update this directory structure section to reflect the current state of the repository.
PATCH

echo "Gold patch applied."
