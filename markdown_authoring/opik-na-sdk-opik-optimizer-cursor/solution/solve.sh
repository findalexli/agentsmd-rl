#!/usr/bin/env bash
set -euo pipefail

cd /workspace/opik

# Idempotency guard
if grep -qF "- Opik Optimizer SDK: `sdks/opik_optimizer/.cursor/rules/` (`architecture.mdc`, " "AGENTS.md" && grep -qF "Each algorithm sits in its own package (`evolutionary_optimizer/`, `few_shot_bay" "sdks/opik_optimizer/.cursor/rules/architecture.mdc" && grep -qF "- Split new logic into focused modules when a file grows beyond ~300 lines or mi" "sdks/opik_optimizer/.cursor/rules/code-structure.mdc" && grep -qF "- Test-only dependencies live in `tests/test_requirements.txt` (e.g. `pytest`, `" "sdks/opik_optimizer/.cursor/rules/dependencies.mdc" && grep -qF "- Update `README.md`, notebooks under `notebooks/`, and docs under `docs/` whene" "sdks/opik_optimizer/.cursor/rules/documentation-style.mdc" && grep -qF "- Interactions with Opik (`opik.api_objects.optimization.Optimization`) can rais" "sdks/opik_optimizer/.cursor/rules/error-handling.mdc" && grep -qF "- Include context such as `optimization_id`, `iteration`, `best_score`, or `popu" "sdks/opik_optimizer/.cursor/rules/logging.mdc" && grep -qF "- Seed randomness where behaviour depends on stochastic operators (`random.seed`" "sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc" && grep -qF "- Co-locate tests with the feature they exercise. For a new optimizer, add unit " "sdks/opik_optimizer/.cursor/rules/test-organization.mdc"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -5,6 +5,7 @@
 - Backend: `apps/opik-backend/.cursor/rules/` (e.g., `tech_stack.mdc`, `code_quality.mdc`, `api_design.mdc`).
 - Frontend: `apps/opik-frontend/.cursor/rules/` (`tech-stack.mdc`, `code-quality.mdc`, `unit-testing.mdc`).
 - Python SDK: `sdks/python/.cursor/rules/` (`code-structure.mdc`, `test-best-practices.mdc`, `documentation-style.mdc`).
+- Opik Optimizer SDK: `sdks/opik_optimizer/.cursor/rules/` (`architecture.mdc`, `code-structure.mdc`, `dependencies.mdc`, `documentation-style.mdc`, `error-handling.mdc`, `logging.mdc`, `test-best-practices.mdc`, `test-organization.mdc`).
 - TypeScript SDK: `sdks/typescript/.cursor/rules/` (`overview.mdc`, `code-structure.mdc`, `test-best-practices.mdc`).
 
 ## Project Structure & Module Organization
@@ -20,6 +21,7 @@
 - Backend build/tests: `mvn verify` in `apps/opik-backend`; respect `apps/opik-backend/.cursor/rules/code_quality.mdc`.
 - Frontend checks: `npm install`, `npm lint`, `npm test`, `npm build`; follow `apps/opik-frontend/.cursor/rules/code-quality.mdc`, `apps/opik-frontend/.cursor/rules/unit-testing.mdc`.
 - Python SDK: `pip install -e .[dev]`, `ruff check`, `pytest`; align with `sdks/python/.cursor/rules/test-best-practices.mdc`.
+- Opik Optimizer SDK: `make install-dev`, `make test`, `make precommit` from `sdks/opik_optimizer`; follow the optimizer rules in `sdks/opik_optimizer/.cursor/rules/` (architecture, code structure, dependencies, testing).
 - TypeScript SDK: `npm install`, `npm lint`, `npm test`; observe `sdks/typescript/.cursor/rules/code-structure.mdc`.
 
 ## Coding Style & Naming Conventions
diff --git a/sdks/opik_optimizer/.cursor/rules/architecture.mdc b/sdks/opik_optimizer/.cursor/rules/architecture.mdc
@@ -0,0 +1,79 @@
+---
+description: Core architecture and design patterns for Opik Optimizer SDK
+globs: sdks/opik_optimizer/src/opik_optimizer/**/*
+alwaysApply: false
+---
+# Opik Optimizer Architecture
+
+The optimizer SDK layers iterative search loops on top of Opik's evaluation stack. Keep orchestration, evaluation, and presentation concerns separate so optimizers stay composable and easy to extend.
+
+## Key Components
+
+- `BaseOptimizer` (`base_optimizer.py`): shared lifecycle hooks, LiteLLM cache bootstrap, rate limiting, Opik optimisation tracking, history management (`OptimizationRound`), and `OptimizationResult` construction.
+- `OptimizableAgent` (`optimizable_agent.py`): wraps LiteLLM agents, attaches the active optimizer, throttles `_llm_complete`, and pushes optimisation ids into Opik spans via `opik_context`. Treat this class as the boundary for provider-specific behaviour.
+- `task_evaluator.evaluate` (`task_evaluator.py`): funnels evaluations through `opik.evaluation.evaluator`, handling sampling, threading, multi-metric objectives, and optimisation id tagging.
+- `OptimizationResult` (`optimization_result.py`): normalised result object containing final prompt, score, metadata, baseline metrics, LiteLLM/tool counters, and helpers for chaining optimizers.
+- Support modules (`optimization_config/`, `_throttle.py`, `cache_config.py`, `reporting_utils.py`, `logging_config.py`, `multi_metric_objective.py`) provide prompt structures, rate limiting, caching, console output, logging setup, and multi-metric aggregation.
+
+## Package Layout
+
+Each algorithm sits in its own package (`evolutionary_optimizer/`, `few_shot_bayesian_optimizer/`, `gepa_optimizer/`, `hierarchical_reflective_optimizer/`, `meta_prompt_optimizer/`, `mipro_optimizer/`, `parameter_optimizer/`). Keep algorithm-specific helpers, prompts, and operators inside the corresponding package. Cross-cutting utilities belong at the root (`optimization_config/`, `utils/`, `mcp_utils/`, `metrics/`). Production code must never import from `tests/`.
+
+## Execution Flow
+
+1. `optimize_prompt` (or `optimize_mcp`) validates inputs with `_validate_optimization_inputs`, seeds counters, and may start an Opik optimisation run (`self.opik_client.create_optimization`) storing the id on `self.current_optimization_id`.
+2. Subclasses generate candidate prompts or parameter sets via helper modules (mutation ops, prompt planners, MCP workflows).
+3. Candidate scoring flows `_evaluate_prompt` -> `evaluate_prompt` -> `task_evaluator.evaluate`. The evaluator enforces sampling, threading, LiteLLM throttling, and attaches optimisation ids using `opik_context.update_current_trace`.
+4. Progress reporting runs through `reporting_utils` context managers while `_add_to_history` captures `OptimizationRound` snapshots.
+5. The run returns an `OptimizationResult` built by the subclass or helper, including baseline metrics, final scores, metadata, and LiteLLM/tool counters.
+
+Keep iteration logic free of side effects beyond the explicit history, reporting, and Opik telemetry work so optimizations remain resumable and testable.
+
+## API Contract
+
+All optimizers must expose a consistent prompt-optimisation method and return the shared result object:
+
+```python
+from collections.abc import Callable
+from opik import Dataset
+from opik_optimizer.optimization_config import chat_prompt
+from opik_optimizer import optimization_result
+from opik_optimizer.optimizable_agent import OptimizableAgent
+
+class BaseOptimizer:
+    def optimize_prompt(
+        self,
+        prompt: chat_prompt.ChatPrompt,
+        dataset: Dataset,
+        metric: Callable[[dict[str, object], str], object],
+        experiment_config: dict[str, object] | None = None,
+        n_samples: int | None = None,
+        auto_continue: bool = False,
+        agent_class: type[OptimizableAgent] | None = None,
+        project_name: str = "Optimization",
+        **kwargs: object,
+    ) -> optimization_result.OptimizationResult: ...
+```
+
+`OptimizationResult` provides fields such as `optimizer`, `prompt`, `score`, `metric_name`, `optimization_id`, `initial_prompt`, `initial_score`, `details`, `history`, `llm_calls`, and `tool_calls`. Interface guarantees are exercised in `tests/unit/test_optimization_result.py` and the e2e suite under `tests/e2e/optimizers/`, which instantiate multiple optimizers to confirm they produce compatible signatures and result structures.
+
+## Boundaries and Dependencies
+
+- Production code must not import from `tests/`.
+- Optimizer packages may import from `base_optimizer`, shared utilities, and siblings within the same package. Avoid reaching into unrelated optimizer packages.
+- Provider glue belongs in `integrations/` and must guard imports so the default install stays lightweight.
+- `datasets/` exposes deterministic sample datasets for demos/tests; omit benchmark-only assets from runtime packages.
+
+## Caching, Throttling, and Telemetry
+
+- Use `_throttle.get_rate_limiter_for_current_opik_installation` and decorators such as `@rate_limited` for outbound LiteLLM calls instead of ad-hoc sleep loops.
+- `cache_config.initialize_cache()` configures a shared LiteLLM disk cache under `~/.litellm_cache`. If an optimizer needs different behaviour, add configuration knobs rather than mutating global state.
+- Tag Opik traces through `opik_context.update_current_trace` so optimisation ids surface in logs and UI.
+
+## Adding a New Optimizer
+
+1. Create a new package under `src/opik_optimizer/` with an `__init__.py` that re-exports the public class.
+2. Subclass `BaseOptimizer` and implement `optimize_prompt` (and optionally `optimize_mcp`). Extract helper modules for mutation, selection, or reporting to keep the main loop readable.
+3. Reuse `reporting_utils` context managers for console output and populate `OptimizationResult` with baseline, final metrics, metadata, and counters.
+4. Document new configuration knobs in `optimization_config/` and update README/docs/notebooks.
+5. Add unit coverage for helper modules plus a lightweight e2e test under `tests/e2e/optimizers/` running on a tiny dataset to prove the interface contract.
diff --git a/sdks/opik_optimizer/.cursor/rules/code-structure.mdc b/sdks/opik_optimizer/.cursor/rules/code-structure.mdc
@@ -0,0 +1,61 @@
+---
+description: Import organization, module layout, and access control for Opik Optimizer SDK
+globs: sdks/opik_optimizer/src/opik_optimizer/**/*
+alwaysApply: false
+---
+# Opik Optimizer Code Structure
+
+Keep modules small, explicit, and aligned with the optimizer architecture so contributors can navigate the SDK quickly.
+
+## Imports
+
+- Order imports as: standard library -> third-party -> Opik/Opik Optimizer modules.
+- Use absolute imports when referencing other packages inside `opik_optimizer` (`from opik_optimizer.optimization_config import chat_prompt`). Reserve relative imports for local siblings within the same package.
+- Guard optional dependencies (for example, `gepa`, `langgraph`, `torch`) inside functions or `try/except ImportError` blocks so the base install works without extras.
+
+## Directory Layout
+
+```
+src/opik_optimizer/
+├── base_optimizer.py
+├── optimization_result.py
+├── optimizable_agent.py
+├── optimization_config/
+├── datasets/
+├── utils/
+├── metrics/
+├── integrations/
+├── {optimizer}/
+│   ├── __init__.py
+│   ├── {optimizer}.py
+│   ├── operators/
+│   ├── prompts.py
+│   └── reporting.py
+└── mcp_utils/
+```
+
+- Replace `{optimizer}` with concrete packages such as `evolutionary_optimizer`, `meta_prompt_optimizer`, `parameter_optimizer`, etc. A healthy default layout for each optimizer package is:
+  - `{optimizer}.py`: the public class that subclasses `BaseOptimizer` and orchestrates the run.
+  - `operators/`: submodules such as `mutation_ops.py`, `selection_ops.py`, `population_ops.py`, and `evaluation_ops.py` that keep genetic/search behaviours isolated.
+  - `prompts.py`: canned prompt templates or helpers used to seed candidates.
+  - `reporting.py`: helpers that wrap `reporting_utils` context managers to print progress, capture baselines, and surface final summaries. Keep console output centralised here so the optimizer file focuses on control flow.
+- Split new logic into focused modules when a file grows beyond ~300 lines or mixes concerns (for example, extraction of mutation operators, prompt planners, evaluation helpers, or style utilities). Prefer creating a dedicated submodule over adding yet another helper to the main optimizer file.
+
+- Keep algorithm-specific helpers (mutation ops, prompts, stage planners) inside the corresponding optimizer package.
+- Shared utilities that are reused across optimizers live in top-level directories (`utils/`, `optimization_config/`, `metrics/`, `mcp_utils/`). Do not introduce generic `helpers.py` dumps.
+
+## Public Surface
+
+- Re-export public optimizers from package `__init__.py` files so users can import with `from opik_optimizer import EvolutionaryOptimizer`.
+- Keep internal helpers private with a leading underscore or by omitting them from `__all__`.
+
+## Module State and Configuration
+
+- Avoid work at import time beyond constant definition and lightweight configuration (`initialize_cache()` is triggered inside `BaseOptimizer`, not at module load).
+- Store configurable defaults as uppercase constants near the top of the module (for example, `DEFAULT_POPULATION_SIZE`).
+- When you need mutable shared state (caches, counters), encapsulate it in a dedicated module (`cache_config`, `_throttle`) rather than scattering globals.
+
+## Typing and Data Structures
+
+- Type annotate public methods and helper functions. Use `pydantic.BaseModel`, dataclasses, or TypedDicts for structured data exchanged between modules (for example, `OptimizationResult`, prompt variants).
+- Prefer immutable structures (tuples, frozen dataclasses) for candidate representations passed between operators to avoid accidental mutation.
diff --git a/sdks/opik_optimizer/.cursor/rules/dependencies.mdc b/sdks/opik_optimizer/.cursor/rules/dependencies.mdc
@@ -0,0 +1,39 @@
+---
+description: Dependency management and versioning for Opik Optimizer SDK
+globs: sdks/opik_optimizer/**/*
+alwaysApply: false
+---
+# Opik Optimizer Dependencies
+
+Manage dependencies deliberately so the optimizer package remains lightweight while still supporting advanced optimisers and integrations.
+
+## Runtime Dependencies
+
+- Declared in `sdks/opik_optimizer/setup.py`. Core packages include `litellm`, `opik`, `optuna`, `deap`, `diskcache`, `pydantic`, `pandas`, `pyrate-limiter`, `hf_xet`, `ujson`, `tqdm`, and `rich`.
+- Honour `python_requires=">=3.10,<3.14"` - new language features must keep Python 3.10 compatibility.
+- Keep heavyweight or niche integrations (for example, `gepa`, `langgraph`) in extras (`extras_require["dev"]`) or feature-specific requirements. Guard imports so base users are prompted with a clear installation hint.
+
+## Test and Dev Requirements
+
+- Test-only dependencies live in `tests/test_requirements.txt` (e.g. `pytest`, `pytest-asyncio`, `pytest-cov`, `orderly_set==5.3.2`, `gepa>=0.0.7`). Update this file when tests rely on new packages and document pins inline.
+- Notebooks and benchmarks may have their own requirements; prefer per-tool requirements files over bloating runtime dependencies.
+
+## Adding or Updating Dependencies
+
+1. Confirm the standard library or existing dependencies cannot cover the use case.
+2. Add the package to `setup.py` (and `tests/test_requirements.txt` when applicable) with a justified version range. Reference upstream issues in comments when applying tight pins.
+3. Guard imports in code using `try/except ImportError` with actionable error messages (`"Install opik-optimizer[dev]"`).
+4. Run unit and e2e tests to verify the new dependency behaves as expected across optimizers.
+5. Update documentation (README, notebooks) mentioning new installation steps or extras.
+
+## Tooling and Checks
+
+- Static typing: `pyproject.toml` configures `mypy` (see `[tool.mypy]`). Run `make test` equivalent before merging; optimizers should keep type coverage high.
+- Formatting and lint hooks: `.pre-commit-config.yaml` provides the hook set. Run `make precommit` (which executes `pre-commit run --all-files`) locally or install the hooks with `pre-commit install`.
+- Task shortcuts: `sdks/opik_optimizer/Makefile` exposes `make install`, `make install-dev`, `make test`, `make precommit`, and `make build`. Keep these targets working whenever dependencies change.
+
+## Security and Licensing
+
+- Prefer actively maintained libraries compatible with Apache 2.0.
+- Do not commit API keys, private indexes, or credentials alongside dependency updates.
+- Monitor `litellm`, `optuna`, and provider SDK releases: breaking changes often require upper bounds or compatibility shims.
diff --git a/sdks/opik_optimizer/.cursor/rules/documentation-style.mdc b/sdks/opik_optimizer/.cursor/rules/documentation-style.mdc
@@ -0,0 +1,34 @@
+---
+description: Documentation standards and code style for Opik Optimizer SDK
+globs: sdks/opik_optimizer/src/opik_optimizer/**/*
+alwaysApply: false
+---
+# Opik Optimizer Documentation Style
+
+Keep docs lightweight and point back to the architecture rule for shared signatures and component overviews. Use documentation to clarify behaviour, configuration, and examples rather than restating code.
+
+## Docstrings and Type Hints
+
+- Provide docstrings for public classes, lifecycle hooks (`optimize_prompt`, `_initialize_population`, `_evaluate_prompt`), and complex helpers. Start with a one-line summary followed by behaviour/side-effect details.
+- Rely on type hints to document parameters; docstrings should explain semantics, expected ranges, and side effects (for example, background evaluations or Opik trace tagging).
+- Use `pydantic` model field descriptions when exposing configuration objects to users.
+
+## Examples and Guides
+
+- Update `README.md`, notebooks under `notebooks/`, and docs under `docs/` whenever you add a new optimizer or surface area. Demonstrate minimal reproducible examples using datasets from `opik_optimizer.datasets`. Additionally, update the Fern docs in `apps/opik-documentation/documentation/fern/docs/agent_optimization` when public APIs change.
+- Keep code snippets executable: import from `opik_optimizer`, configure provider keys via environment variables, and run on small datasets to limit cost.
+- When features depend on optional extras, show the installation command (`pip install opik-optimizer[dev]`) alongside the example.
+
+## Rich Output and CLI Messaging
+
+- `OptimizationResult.__str__` and `reporting_utils` rely on Rich. When adding new console sections, use Rich markup strings and keep plain-text fallbacks sensible for notebook and CLI users.
+- Avoid direct `print` statements in optimizers; emit structured data through reporting helpers or logging.
+
+## Release Notes
+
+- Mention new configuration flags, dependency changes, and required environment variables in release notes or changelog entries.
+- Cross-link to relevant docs or notebooks so users can follow up with detailed examples.
+
+## API Spec
+
+- Run `scripts/generate_fern_docs.py` to refresh Fern docs when you add or modify public classes. Ensure imports stay valid so the doc build succeeds.
diff --git a/sdks/opik_optimizer/.cursor/rules/error-handling.mdc b/sdks/opik_optimizer/.cursor/rules/error-handling.mdc
@@ -0,0 +1,30 @@
+---
+description: Exception handling and failure management for Opik Optimizer SDK
+globs: sdks/opik_optimizer/src/opik_optimizer/**/*
+alwaysApply: false
+---
+# Opik Optimizer Error Handling
+
+Optimizers make heavy use of third-party services and background evaluations. Surface actionable errors while keeping optimisation runs resilient.
+
+## Validation
+
+- `_validate_optimization_inputs` should raise `ValueError` with descriptive messages when prompts, datasets, or metrics are invalid. Mirror this pattern in new optimizers before any remote calls occur.
+- Configuration parsing (for example, `optimization_config` models, MCP configs) should use `pydantic.ValidationError` or custom exceptions that describe which field failed.
+
+## Remote Calls and Retries
+
+- Interactions with Opik (`opik.api_objects.optimization.Optimization`) can raise `ApiError`. Catch these at the boundary, log a warning, and continue without optimisation tracking when possible so the user can still receive results.
+- For LiteLLM calls, use `_throttle.rate_limited` or the shared rate limiter instead of ad-hoc sleep loops. When retries are required, limit attempts and propagate the final error with context.
+- When evaluation fails for a candidate, decide whether to penalise, skip, or abort. Log the failure at `warning` level with the candidate summary and propagate the exception only if the optimizer cannot continue safely.
+
+## Task Evaluation
+
+- `task_evaluator.evaluate` already guards against empty datasets and metric failures by returning 0.0 and marking scores as failed. When extending it, keep error handling consistent and avoid leaking provider-specific exceptions.
+- When a metric is a `MultiMetricObjective`, ensure the returned `ScoreResult` list preserves the underlying metrics so downstream consumers can diagnose failures.
+
+## Logging and Result Surfacing
+
+- Use `logging.getLogger(__name__)` and include optimisation ids or candidate identifiers in log messages to aid debugging.
+- Populate `OptimizationResult.details` with failure metadata (for example, skipped candidates, retry counts) when it helps users understand degraded results.
+- Never log API keys, raw dataset contents, or PII. Truncate long prompts and outputs before logging.
diff --git a/sdks/opik_optimizer/.cursor/rules/logging.mdc b/sdks/opik_optimizer/.cursor/rules/logging.mdc
@@ -0,0 +1,31 @@
+---
+description: Logging patterns and verbosity guidelines for Opik Optimizer SDK
+globs: sdks/opik_optimizer/src/opik_optimizer/**/*
+alwaysApply: false
+---
+# Opik Optimizer Logging
+
+Use consistent logging so optimisation runs can be monitored locally and inside Opik traces.
+
+## Logger Setup
+
+- Declare a module-level logger with `logger = logging.getLogger(__name__)`.
+- Call `logging_config.setup_logging()` (or expect callers to do so) before emitting logs; it wires the Rich handler and propagates `OPIK_LOG_LEVEL` overrides.
+- Access progress bars via `opik.environment.get_tqdm_for_current_environment()` instead of printing raw status lines.
+
+## Log Levels
+
+- `INFO`: High-level lifecycle events (start/end of optimisation, generation summaries, baseline scores).
+- `DEBUG`: Candidate details, mutation operator choices, retry diagnostics. Wrap expensive formatting in `if logger.isEnabledFor(logging.DEBUG)`.
+- `WARNING`: Recoverable issues (failed candidate evaluation, throttled requests, Opik API hiccups).
+- `ERROR`: Failures that abort the optimisation run.
+
+## Structured Messages
+
+- Include context such as `optimization_id`, `iteration`, `best_score`, or `population_size` in log messages. Prefer keyword arguments or formatted dicts over concatenated strings for readability.
+- When logging prompts or outputs, truncate to a reasonable length and avoid leaking secrets.
+
+## Reporting vs Logging
+
+- Reserve logging for machine-readable diagnostics. Use `reporting_utils` context managers for user-facing console output; they already respect the `verbose` flag.
+- Avoid mixing `print` statements with logging. If temporary prints are necessary during debugging, remove them before committing.
diff --git a/sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc b/sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc
@@ -0,0 +1,31 @@
+---
+description: Test naming conventions and performance guidelines for Opik Optimizer SDK
+globs: sdks/opik_optimizer/tests/**/*
+alwaysApply: false
+---
+# Opik Optimizer Test Best Practices
+
+The test suite is pytest-based and aims to keep optimizers deterministic, fast, and affordable.
+
+## Determinism and Isolation
+
+- Seed randomness where behaviour depends on stochastic operators (`random.seed`, `numpy.random.seed`). Many optimizers accept a `seed` parameter - set it explicitly in tests. Our default value for seed is "42".
+- Reset global state (LiteLLM cache, logging configuration, environment variables) with fixtures or `monkeypatch` as seen in `tests/unit/test_logging_config.py`.
+- Avoid touching the real LiteLLM cache directory in unit tests; point cache-dependent code to a temporary directory when practical.
+
+## Fast Feedback
+
+- Configure optimizers with tiny populations, low iteration counts, and reduced thread pools. Unit tests should replace LiteLLM calls with fakes or patches so they run offline.
+- Prefer dataset stubs from `tests/unit` or `opik_optimizer.datasets.tiny_test()` for smoke coverage.
+- Use parametrisation to cover edge cases without introducing nested loops.
+
+## Assertions
+
+- Assert both positive paths (best score improves, result shape) and failure handling (invalid config, evaluation failure fallback).
+- When verifying prompts or histories, rely on helper models (for example, `OptimizationResult`) and compare essential fields rather than entire nested structures.
+- Use `caplog` to assert log-level behaviour in logging-sensitive code.
+
+## External Services
+
+- End-to-end tests may require provider credentials (for example, `OPENAI_API_KEY`). Guard them with explicit failure messages so contributors understand the prerequisite before running the suite.
+- When adding a new e2e test, document any required environment variables in the test docstring.
diff --git a/sdks/opik_optimizer/.cursor/rules/test-organization.mdc b/sdks/opik_optimizer/.cursor/rules/test-organization.mdc
@@ -0,0 +1,26 @@
+---
+description: Test organization and patterns for Opik Optimizer SDK
+globs: sdks/opik_optimizer/tests/**/*
+alwaysApply: false
+---
+# Opik Optimizer Test Organization
+
+Tests live under `sdks/opik_optimizer/tests` and mirror the package structure so contributors can find coverage quickly.
+
+## Layout
+
+- `test_setup.py`: ensures `src/` is on the import path for the test suite.
+- `unit/`: deterministic tests for helpers, configuration models, mutation operators, logging config, MCP utilities, etc. Subdirectories (like `unit/mcp/`) group related helper modules.
+- `e2e/optimizers/`: high-level runs for each optimizer family with reduced populations/iterations. These tests may require provider keys.
+- `test_requirements.txt`: pinned list of packages needed to run the suite locally or in CI.
+
+## Markers and Configuration
+
+- `pytest.ini` defines an `integration` marker for slower scenarios and filters noisy warnings. Tag new long-running tests accordingly.
+- Keep new fixtures in the closest `conftest.py` (prefer local fixtures over globals). Autouse fixtures should document the state they reset.
+
+## Adding Tests
+
+- Co-locate tests with the feature they exercise. For a new optimizer, add unit coverage for operators/helpers under `tests/unit/<optimizer>/` and an e2e smoke test under `tests/e2e/optimizers/`.
+- Use descriptive test names (for example, `test_evolutionary_optimizer__improves_score`), and include docstrings when context is not obvious.
+- Skip e2e tests gracefully when required environment variables or credentials are missing, and mention the requirement at the top of the file.
PATCH

echo "Gold patch applied."
