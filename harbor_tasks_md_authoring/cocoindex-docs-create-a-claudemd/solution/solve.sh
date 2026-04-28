#!/usr/bin/env bash
set -euo pipefail

cd /workspace/cocoindex

# Idempotency guard
if grep -qF "This file provides guidance to Claude Code (claude.ai/claude-code) when working " "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1,71 @@
+# CLAUDE.md
+
+This file provides guidance to Claude Code (claude.ai/claude-code) when working with code in this repository.
+
+## Build and Test Commands
+
+### Building
+
+```bash
+maturin develop          # Build Rust code and install Python package (required after Rust changes)
+```
+
+### Testing
+
+```bash
+cargo test               # Run Rust tests
+dmypy run                # Type check Python code (uses mypy daemon)
+pytest python/           # Run Python tests (use after both Rust and Python changes)
+```
+
+### Workflow Summary
+
+| Change Type | Commands to Run |
+|-------------|-----------------|
+| Rust code only | `maturin develop && cargo test` |
+| Python code only | `dmypy run && pytest python/` |
+| Both Rust and Python | Run all commands from both categories above |
+
+## Code Structure
+
+```
+cocoindex/
+├── rust/                       # Rust crates (workspace)
+│   ├── cocoindex/              # Main crate - core indexing engine
+│   │   └── src/
+│   │       ├── base/           # Core types: schema, value, spec, json_schema
+│   │       ├── builder/        # Flow/pipeline builder logic
+│   │       ├── execution/      # Runtime execution: evaluator, indexer, live_updater
+│   │       ├── llm/            # LLM integration
+│   │       ├── ops/            # Operations: sources, targets, functions
+│   │       ├── py/             # Python bindings (PyO3)
+│   │       ├── service/        # Service layer
+│   │       └── setup/          # Setup and configuration
+│   ├── py_utils/               # Python-Rust utility helpers
+│   └── utils/                  # General utilities: error handling, batching, etc.
+│
+├── python/
+│   └── cocoindex/              # Python package
+│       ├── __init__.py         # Package entry point
+│       ├── _engine.abi3.so     # Compiled Rust extension (generated)
+│       ├── cli.py              # CLI commands (cocoindex CLI)
+│       ├── flow.py             # Flow definition API
+│       ├── op.py               # Operation definitions
+│       ├── engine_*.py         # Engine types, values, objects
+│       ├── functions/          # Built-in functions
+│       ├── sources/            # Data source connectors
+│       ├── targets/            # Output target connectors
+│       └── tests/              # Python tests
+│
+├── examples/                   # Example applications
+├── docs/                       # Documentation
+└── dev/                        # Development utilities
+```
+
+## Key Concepts
+
+- **CocoIndex** is an data processing framework that maintains derived data from source data incrementally
+- The core engine is written in Rust for performance, with Python bindings via PyO3
+- **Flows** define data transformation pipelines from sources to targets
+- **Operations** (ops) include sources, functions, and targets
+- The system supports incremental updates - only reprocessing changed data
PATCH

echo "Gold patch applied."
