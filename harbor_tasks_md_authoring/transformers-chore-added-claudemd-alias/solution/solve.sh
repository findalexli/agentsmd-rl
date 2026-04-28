#!/usr/bin/env bash
set -euo pipefail

cd /workspace/transformers

# Idempotency guard
if grep -qF "2) The newer method is to add a file named `modular_<name>.py` in the model dire" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,113 +1,14 @@
-# AGENTS.md Guide for Hugging Face Transformers
+## Useful commands
+- `make style`: runs formatters and linters, necessary to pass code style checks
+- `make fix-repo`: auto-fixes copies, modular conversions, doc TOCs, docstrings in addition to the `make style` fixes
+- `make check-repo` — CI-style consistency checks
+- Many tests are marked as 'slow' and skipped by default in the CI. To run them, use: `RUN_SLOW=1 pytest ...`
 
-You are a contributor-focused assistant for this repo. Prioritize small, reviewable changes and help users succeed with CI.
+`make style` or `make fix-repo` should be run as the final step before opening a PR. The CI will run `make check-repo` and fail if any issues are found.
 
-**New Contributors: See [CONTRIBUTING.md](CONTRIBUTING.md) for complete setup and workflow details.**
+## Copies and Modular Models
 
-**Commands (Run Early)**
-- Style/format: `make style`
-- Repo checks: `make check-repo`
-- Auto-fix repo consistency: `make fix-repo`
-- Core tests: `make test`
-- Examples tests: `make test-examples`
+We try to avoid direct inheritance between model-specific files in `src/transformers/models/`. We have two mechanisms to manage the resulting code duplication:
 
-**Environment Setup**
-If the environment is not yet set up:
-1. Requires Python 3.10+ but 3.10 recommended as the minimal supported Python
-2. Install dev dependencies: `uv pip install -e ".[dev]"` or  `pip install -e ".[dev]"` if `uv` is unavailable
-3. Verify install with `make check-repo`
-
-**Quick Start**
-- Prefer the smallest change that fixes the issue.
-- Use `rg` to locate files; avoid broad file reads.
-- If you touched copied code, modular files, docs TOCs, or docstrings, run `make fix-repo`.
-- Otherwise, run `make style` before you finish.
-
-**Example Flows**
-- Small code change: edit -> `make style` -> targeted `pytest ...`
-- Modular/copies change: edit source/modular -> `make fix-repo` -> targeted `pytest ...`
-- Docs change: edit -> `make fix-repo` -> (optional) doc build
-
-**Repo Map**
-- `src/transformers`: core library code.
-- `src/transformers/models`: per-model implementations.
-- `tests`: core tests and model tests.
-- `docs/source/en`: documentation sources (MDX-like Markdown).
-
-**Boundaries**
-- Always: keep diffs minimal, follow existing patterns, prefer targeted tests.
-- Ask first: adding dependencies, modifying CI, changing public APIs, large refactors.
-- Never: edit generated modeling files when a `modular_<name>.py` exists.
-- Dependencies: see [CONTRIBUTING.md#do-you-want-to-add-documentation](CONTRIBUTING.md) for adding new dependencies (ask maintainers first).
-
-**Tech Stack**
-- Python package with PyTorch focus; tests run with `pytest`, formatting via `ruff`.
-- Docs built with `doc-builder` (see `docs/README.md`).
-
-**Copies and Modular Models**
-- If a file has `# Copied from ...`, change the source and run `make fix-repo` to propagate.
-- If a model has `modular_<name>.py`, do not edit generated `modeling_*.py` files directly. Edit modular and run `make fix-repo` (or `python utils/modular_model_converter.py <name>`).
-- Files with `This file was automatically generated from` in second line are generated.
-- Protobuf files, ending with `_pb2.py` are also generated.
-
-**Adding Models the Modular Way**
-Modular Transformers lets you add models by inheriting from existing models, significantly reducing code:
-- pick a CamelCase unique name for model and use it everywhere. All modules should be prefixed with that name following PEP8 convention.
-- Create a `modular_<name>.py` file in `src/transformers/models/<name>/`
-- Import and inherit from similar models (e.g., `class MyModelConfig(LlamaConfig)`)
-- Only define what changes: new attributes, modified layers, different behavior
-- Run `python utils/modular_model_converter.py <name>` to generate standard files
-- Run `make check-repo` to verify the conversion and check for issues
-- The linter automatically unravels inheritance, flattens dependencies, and copies required functions
-
-Key patterns:
-- `super().__init__(...)` unravels parent body; add `del self.attribute` after to remove unwanted attributes
-- `class MyClass(ParentClass): pass` copies parent definition exactly with renamed references
-- Import functions directly (e.g., `from ..llama.modeling_llama import eager_attention_forward`)
-- Docstring variables set to `None` reuse parent docstrings automatically
-- Override methods only when logic changes; decorators inherit unless you specify new ones
-
-See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for full guide with Olmo2 example.
-
-**Testing (smallest relevant set)**
-- Targeted model tests: `pytest tests/models/<name>/test_modeling_<name>.py`
-- Tokenizers/processors: `pytest tests/models/<name>/test_tokenization_<name>.py` or `test_processing_<name>.py`
-- Examples: `make test-examples`
-- Full suite: `make test`
-- Slow tests: `RUN_SLOW=1 pytest ...`
-
-**CI Test Selection**
-- CI runs only tests impacted by the diff.
-- Reproduce locally: `python utils/tests_fetcher.py`
-- Run list: `python -m pytest -n 8 --dist=loadfile -rA -s $(cat test_list.txt)`
-
-**Docs Notes**
-- Docs use MDX-like syntax; keep formatting minimal and consistent.
-- Adding a doc requires updating the Toc tree with `make check-repo`.
-- Local docs build uses `doc-builder` and dev extras in `docs/README.md`.
-
-**Makefile Truth**
-- `make style` runs ruff format/check plus repo formatters.
-- `make check-repo` runs CI-style consistency checks.
-- `make fix-repo` auto-fixes copies, modular conversions, doc TOCs, doctest lists, and docstrings.
-
-**Git Workflow**
-- Keep PRs small; avoid unrelated refactors and sweeping reformatting.
-- When uncertain, prefer targeted changes and ask before widening scope.
-- See [CONTRIBUTING.md#create-a-pull-request](CONTRIBUTING.md#create-a-pull-request) for full PR workflow.
-
-**Troubleshooting**
-- `make style` failures: read output carefully—most are auto-fixed, some need manual fixes. Common: import ordering, docstring formatting.
-- `make check-repo` failures: check specific error message. If it mentions copies/modular/TOC/docstrings, run `make fix-repo`.
-- Test failures: check test output for assertion errors. Verify changes didn't break existing behavior.
-- Import errors after install: ensure you ran `pip install -e ".[dev]"` with `-e` flag for editable mode.
-- Slow tests timing out: use `RUN_SLOW=1` environment variable only when needed.
-
-**Common Errors**
-- "import failed, unprotected imports": you added an import without proper guards. Check `__init__.py` patterns.
-- "modular conversion failed": modular file has syntax errors. Run `python utils/modular_model_converter.py <name>` to debug.
-- "copies check failed": edited a `# Copied from ...` file directly. Edit the source file instead and run `make fix-repo`.
-- "doc TOC check failed": added a doc without updating `docs/source/en/_toctree.yml`. Add your file there.
-
-**Output Example**
-- Good: "Edited `src/transformers/models/bert/modeling_bert.py`, ran `make style`, ran `pytest tests/models/bert/test_modeling_bert.py`."
+1) The older method is to mark classes or functions with `# Copied from ...`. Copies are kept in sync by `make fix-repo`. Do not edit a `# Copied from` block, as it will be reverted by `make fix-repo`. Ideally you should edit the code it's copying from and propagate the change, but you can break the `# Copied from` link if needed.
+2) The newer method is to add a file named `modular_<name>.py` in the model directory. `modular` files **can** inherit from other models. `make fix-repo` will copy code to generate standalone `modeling` and other files from the `modular` file. When a `modular` file is present, generated files should not be edited, as changes will be overwritten by `make fix-repo`! Instead, edit the `modular` file. See [docs/source/en/modular_transformers.md](docs/source/en/modular_transformers.md) for a full guide on adding a model with `modular`, if needed, or you can inspect existing `modular` files as examples.
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
PATCH

echo "Gold patch applied."
