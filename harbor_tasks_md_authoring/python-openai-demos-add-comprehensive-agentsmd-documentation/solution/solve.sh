#!/usr/bin/env bash
set -euo pipefail

cd /workspace/python-openai-demos

# Idempotency guard
if grep -qF "This repository contains a collection of Python scripts that demonstrate how to " "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,406 @@
+# Agent Instructions for python-openai-demos
+
+This document provides comprehensive instructions for coding agents working on this repository. Following these instructions will help you work more efficiently and avoid common pitfalls.
+
+## Overview
+
+This repository contains a collection of Python scripts that demonstrate how to use the OpenAI API (and compatible APIs like Azure OpenAI, GitHub Models, and Ollama) to generate chat completions. The repository includes examples of:
+
+- Basic chat completions (streaming, async, history)
+- Function calling (basic to advanced multi-function scenarios)
+- Structured outputs using Pydantic models
+- Retrieval-Augmented Generation (RAG) with various complexity levels
+- Prompt engineering and safety features
+
+The scripts are designed to be educational and can run with multiple LLM providers: **GitHub Models (preferred for agents)**, Azure OpenAI, OpenAI.com, or local Ollama models.
+
+## Code Layout
+
+### Python Scripts (Root Directory)
+
+All example scripts are located in the root directory. They follow a consistent pattern of setting up an OpenAI client based on environment variables, then demonstrating specific API features.
+
+**Chat Completion Scripts:**
+- `chat.py` - Simple chat completion example
+- `chat_stream.py` - Streaming chat completions
+- `chat_async.py` - Async chat completions with `asyncio.gather` examples
+- `chat_history.py` - Multi-turn chat with message history
+- `chat_history_stream.py` - Multi-turn chat with streaming
+- `chat_safety.py` - Content safety filter exception handling
+
+**Function Calling Scripts:**
+- `function_calling_basic.py` - Single function declaration, prints tool calls
+- `function_calling_call.py` - Executes the function when requested
+- `function_calling_extended.py` - Full round-trip with function execution and response
+- `function_calling_multiple.py` - Multiple functions, demonstrates choice logic
+
+**Structured Outputs Scripts:**
+- `structured_outputs_basic.py` - Basic Pydantic model extraction
+- `structured_outputs_description.py` - Using field descriptions
+- `structured_outputs_enum.py` - Restricting values with enums
+- `structured_outputs_function_calling.py` - Combining function calling with Pydantic
+- `structured_outputs_nested.py` - Nested Pydantic models
+
+**RAG Scripts (require `requirements-rag.txt`):**
+- `rag_csv.py` - RAG with CSV file retrieval
+- `rag_multiturn.py` - RAG with multi-turn chat interface
+- `rag_queryrewrite.py` - RAG with query rewriting step
+- `rag_documents_ingestion.py` - PDF ingestion (uses pymupdf, langchain, creates JSON)
+- `rag_documents_flow.py` - RAG flow using ingested documents
+- `rag_documents_hybrid.py` - Hybrid retrieval with vector + keyword search + RRF + reranking
+
+**Other Scripts:**
+- `prompt_engineering.py` - Prompt engineering examples
+- `reasoning.py` - Reasoning examples
+- `chained_calls.py` - Chained API calls
+- `retrieval_augmented_generation.py` - Alternative RAG example
+
+### Spanish Directory
+
+The `spanish/` directory contains Spanish translations of most example scripts and a Spanish README. The Python scripts are functionally equivalent to their English counterparts.
+
+### Data Directory
+
+The `data/` directory contains PDF files used by the RAG document ingestion examples:
+- `Aphideater_hoverfly.pdf`
+- `California_carpenter_bee.pdf`
+- `Centris_pallida.pdf`
+- `Western_honey_bee.pdf`
+
+### Infrastructure Files (infra/)
+
+**Bicep Infrastructure as Code:**
+- `infra/main.bicep` - Defines Azure OpenAI resource provisioning with GPT-4o and embedding models
+- `infra/main.parameters.json` - Parameters for Bicep deployment
+
+**Environment Setup Scripts:**
+- `infra/write_dot_env.sh` - Shell script to create `.env` from azd environment (Linux/Mac)
+- `infra/write_dot_env.ps1` - PowerShell script to create `.env` from azd environment (Windows)
+
+These scripts are automatically run by `azd provision` via the `azure.yaml` postprovision hooks.
+
+### Configuration Files
+
+**Python Configuration:**
+- `pyproject.toml` - Ruff and Black linter/formatter configuration (line-length: 120, target: py311)
+- `requirements.txt` - Core dependencies: `azure-identity`, `openai>=1.108.1`, `python-dotenv`, `langchain-text-splitters`
+- `requirements-rag.txt` - RAG-specific dependencies: `pymupdf4llm`, `lunr`, `sentence-transformers`
+- `requirements-dev.txt` - Development dependencies: includes requirements.txt + requirements-rag.txt + `pre-commit`, `ruff`, `black`
+
+**Pre-commit Configuration:**
+- `.pre-commit-config.yaml` - Pre-commit hooks for check-yaml, end-of-file-fixer, trailing-whitespace, ruff, and black
+
+**Azure Developer CLI:**
+- `azure.yaml` - Defines azd hooks (postprovision scripts)
+
+**Environment Variables:**
+- `.env.sample` - Example .env file showing all possible configurations
+- `.env.sample.azure` - Azure-specific example
+- `.env.sample.github` - GitHub Models example
+- `.env.sample.ollama` - Ollama example
+- `.env.sample.openai` - OpenAI.com example
+
+### GitHub Workflows (.github/workflows/)
+
+**`python.yaml` - Linting and Formatting Check:**
+- Runs on: push to main, pull requests to main
+- Uses: uv for virtual environment and dependency installation
+- Runs: `uv run ruff check .` and `uv run black . --check --verbose`
+- **Important:** The CI uses `uv` but local development typically uses standard `pip`
+
+**`test-github-models.yaml` - Integration Test:**
+- Runs on: push to main, pull requests to main (limited paths)
+- Tests: `chat.py` and `spanish/chat.py` with GitHub Models
+- Uses: uv for setup, requires models: read permission
+- Sets: `API_HOST=github`, `GITHUB_TOKEN=${{ secrets.GITHUB_TOKEN }}`, `GITHUB_MODEL=openai/gpt-4o-mini`
+
+### Dev Container Files (.devcontainer/)
+
+- `.devcontainer/devcontainer.json` - Default dev container (Azure OpenAI setup with azd)
+- `.devcontainer/Dockerfile` - Base Python 3.12 image, installs all requirements-dev.txt
+- `.devcontainer/github/` - GitHub Models variant
+- `.devcontainer/ollama/` - Ollama variant  
+- `.devcontainer/openai/` - OpenAI.com variant
+
+All dev containers install all dependencies from `requirements-dev.txt` which includes base, RAG, and dev tools.
+
+## Running the Code
+
+### Environment Setup
+
+**ALWAYS follow these steps in order:**
+
+1. **Create a Python virtual environment** (if not in a Dev Container or Codespaces):
+   ```bash
+   python -m venv .venv
+   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
+   ```
+
+2. **Install base dependencies:**
+   ```bash
+   python -m pip install -r requirements.txt
+   ```
+
+3. **For RAG examples, ALSO install RAG dependencies:**
+   ```bash
+   python -m pip install -r requirements-rag.txt
+   ```
+
+4. **For development (linting, formatting), install dev dependencies:**
+   ```bash
+   python -m pip install -r requirements-dev.txt
+   ```
+   Note: `requirements-dev.txt` includes both `requirements.txt` and `requirements-rag.txt` via `-r` directives.
+
+### Configuring LLM Provider
+
+**For agents, ALWAYS prefer GitHub Models** since the agent often won't have access to Azure OpenAI or paid API keys.
+
+The scripts read environment variables from a `.env` file. Create one based on your provider:
+
+#### Option 1: GitHub Models (RECOMMENDED for agents)
+
+**For agents:** Check if `GITHUB_TOKEN` environment variable is available:
+```bash
+if [ -n "$GITHUB_TOKEN" ]; then
+    echo "GitHub Models available - GITHUB_TOKEN is set"
+else
+    echo "GitHub Models not available - GITHUB_TOKEN not found"
+fi
+```
+
+In GitHub Codespaces, `GITHUB_TOKEN` is already set, so **no .env file is needed** - scripts will work immediately.
+
+If `GITHUB_TOKEN` is available, you can optionally set a different model (default is `gpt-4o`):
+```bash
+export GITHUB_MODEL=openai/gpt-4o-mini
+```
+
+**Models that support function calling:** `gpt-4o`, `gpt-4o-mini`, `o3-mini`, `AI21-Jamba-1.5-Large`, `AI21-Jamba-1.5-Mini`, `Codestral-2501`, `Cohere-command-r`, `Ministral-3B`, `Mistral-Large-2411`, `Mistral-Nemo`, `Mistral-small`
+
+#### Option 2: Azure OpenAI (requires Azure resources and costs)
+
+**For agents:** Check if Azure OpenAI environment variables are already configured:
+```bash
+if [ -n "$AZURE_OPENAI_ENDPOINT" ] && [ -n "$AZURE_OPENAI_CHAT_DEPLOYMENT" ]; then
+    echo "Azure OpenAI available - required environment variables are set"
+else
+    echo "Azure OpenAI not available - missing AZURE_OPENAI_ENDPOINT or AZURE_OPENAI_CHAT_DEPLOYMENT"
+fi
+```
+
+If Azure OpenAI variables are not available, an administrator would need to provision Azure resources using:
+```bash
+azd auth login
+azd provision
+```
+
+This creates real Azure resources that incur costs. The `.env` file would be created automatically with all needed variables after provisioning.
+
+#### Option 3: OpenAI.com (requires API key and costs)
+
+**For agents:** Check if OpenAI.com API key is available:
+```bash
+if [ -n "$OPENAI_API_KEY" ]; then
+    echo "OpenAI.com available - OPENAI_API_KEY is set"
+else
+    echo "OpenAI.com not available - OPENAI_API_KEY not found"
+fi
+```
+
+If `OPENAI_API_KEY` is available, ensure `API_HOST=openai` and `OPENAI_MODEL` are also set (e.g., `gpt-4o-mini`).
+
+#### Option 4: Ollama (requires local Ollama installation)
+
+**For agents:** Check if Ollama is installed and running:
+```bash
+if command -v ollama &> /dev/null; then
+    echo "Ollama command found"
+    ollama list
+    if [ $? -eq 0 ]; then
+        echo "Ollama is running and available"
+    else
+        echo "Ollama installed but not running"
+    fi
+else
+    echo "Ollama not installed"
+fi
+```
+
+If Ollama is available, configure the environment:
+```bash
+# API_HOST=ollama
+# OLLAMA_ENDPOINT=http://localhost:11434/v1
+# OLLAMA_MODEL=llama3.1
+```
+**Important:** If running in a Dev Container, use `http://host.docker.internal:11434/v1` instead of `localhost`.
+
+### Running Scripts
+
+After environment setup and .env configuration, run any script:
+
+```bash
+python chat.py
+python function_calling_basic.py
+python rag_csv.py  # Requires requirements-rag.txt to be installed
+```
+
+For Spanish versions:
+```bash
+python spanish/chat.py
+```
+
+## Running Tests
+
+### Linting with Ruff
+
+```bash
+# After installing requirements-dev.txt
+ruff check .
+```
+
+To auto-fix issues:
+```bash
+ruff check . --fix
+```
+
+### Formatting with Black
+
+Check formatting:
+```bash
+black . --check --verbose
+```
+
+Auto-format:
+```bash
+black .
+```
+
+### Pre-commit Hooks
+
+Install pre-commit hooks to automatically run checks before commits:
+```bash
+pre-commit install
+```
+
+Run manually:
+```bash
+pre-commit run --all-files
+```
+
+### Integration Tests
+
+The repository has limited automated testing via GitHub Actions. The primary test runs basic scripts with GitHub Models:
+
+```bash
+# This is what the CI does (requires GitHub token):
+export API_HOST=github
+export GITHUB_TOKEN=$YOUR_TOKEN
+export GITHUB_MODEL=openai/gpt-4o-mini
+python chat.py
+python spanish/chat.py
+```
+
+**Note:** Most scripts are demonstration scripts, not unit-tested. Changes to scripts should be manually verified by running them.
+
+## Important Notes and Gotchas
+
+### Environment Variables
+
+- **All scripts default to `API_HOST=github`** if no .env file is present and no environment variable is set.
+- Scripts use `load_dotenv(override=True)` which means .env values override environment variables.
+
+### Model Compatibility
+
+- **Function calling scripts require models that support tools**. Not all models support this:
+  - ✅ Supported: `gpt-4o`, `gpt-4o-mini`, and many others (see GitHub Models list above)
+  - ❌ Not supported: Older models, some local Ollama models
+- If a script fails with a function calling error, check if your model supports the `tools` parameter.
+
+### RAG Scripts Dependencies
+
+- RAG scripts require `requirements-rag.txt` to be installed. They will fail with import errors if these dependencies are missing.
+- The `rag_documents_ingestion.py` script creates `rag_ingested_chunks.json` (large file, ~6MB) which is used by `rag_documents_flow.py` and `rag_documents_hybrid.py`.
+- The ingestion process requires the PDF files in the `data/` directory.
+
+### Dev Container Behavior
+
+- Dev containers automatically install all dependencies from `requirements-dev.txt` during build.
+- Azure-focused dev container includes `azure-cli` and `azd` features.
+- The default dev container expects Azure OpenAI configuration.
+
+### Linting and Formatting
+
+- **Line length is 120 characters** (configured in `pyproject.toml`).
+- Target Python version is 3.11 (though 3.12 is used in dev containers).
+- Ruff is configured to check: E (errors), F (pyflakes), I (isort), UP (pyupgrade).
+- Black and Ruff should both pass for CI to succeed.
+
+### CI/CD Workflow Differences
+
+- **CI uses `uv`** for faster installation: `uv venv .venv && uv pip install -r requirements-dev.txt`
+- **Local development typically uses `pip`**: `python -m venv .venv && python -m pip install -r requirements-dev.txt`
+- Both approaches work, but `uv` is faster for CI.
+
+### Azure Provisioning
+
+- Running `azd provision` creates real Azure resources that incur costs.
+- The infrastructure creates:
+  - Azure OpenAI account with `gpt-4o` deployment (capacity: 30)
+  - Text embedding deployment `text-embedding-3-small` (capacity: 30)
+- The postprovision hook automatically creates the `.env` file.
+- **Always run `azd down`** when done to avoid ongoing charges.
+
+### File Organization
+
+- Spanish translations are in `spanish/` directory with their own README and scripts.
+- Spanish scripts are functionally identical to English versions, just translated.
+- Both English and Spanish directories have their own `rag_ingested_chunks.json` files.
+
+### Common Errors and Solutions
+
+**Error: `ImportError: No module named 'pymupdf4llm'`**
+- Solution: Install RAG dependencies: `python -m pip install -r requirements-rag.txt`
+
+**Error: `KeyError: 'AZURE_OPENAI_ENDPOINT'`**
+- Solution: Your `.env` file is missing required Azure variables, or `API_HOST` is set to `azure` but you haven't configured Azure. Switch to GitHub Models or configure Azure properly.
+
+**Error: `openai.APIError: content_filter`**
+- This is expected behavior for `chat_safety.py` - it's demonstrating content filtering.
+- The script catches this error and prints a message.
+
+**Error: Function calling not supported**
+- Solution: Use a model that supports tools. For GitHub Models, use `gpt-4o`, `gpt-4o-mini`, or another compatible model from the list above.
+
+**Error: `azd` command not found**
+- Solution: Install Azure Developer CLI: https://aka.ms/install-azd
+
+## Agent Workflow Recommendations
+
+When making code changes:
+
+1. **Always install dependencies first**: `python -m pip install -r requirements-dev.txt`
+2. **Run linters before making changes** to understand baseline: `ruff check .` and `black . --check`
+3. **Make minimal, surgical changes** to the relevant scripts.
+4. **Run linters again after changes**: `ruff check .` and `black .` (auto-fix)
+5. **Manually test the changed script** with GitHub Models:
+   ```bash
+   export GITHUB_TOKEN=$YOUR_TOKEN
+   python your_modified_script.py
+   ```
+6. **Check that Spanish translations are updated** if applicable.
+
+## Trust These Instructions
+
+These instructions have been validated by:
+- Reviewing all documentation (README.md, CONTRIBUTING.md)
+- Examining all configuration files (pyproject.toml, .pre-commit-config.yaml, azure.yaml)
+- Analyzing all CI/CD workflows (.github/workflows/)
+- Inspecting all infrastructure files (infra/)
+- Testing environment setup and linting commands
+- Verifying dependency installation processes
+
+**If you encounter discrepancies between these instructions and the actual repository state**, the repository may have been updated. In that case:
+1. Re-examine the relevant documentation or configuration files
+2. Update these instructions if needed
+3. Otherwise, trust these instructions and only explore further if they are incomplete or proven incorrect
PATCH

echo "Gold patch applied."
