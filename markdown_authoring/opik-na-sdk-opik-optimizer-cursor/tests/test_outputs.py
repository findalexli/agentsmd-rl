"""Behavioral checks for opik-na-sdk-opik-optimizer-cursor (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/opik")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Opik Optimizer SDK: `sdks/opik_optimizer/.cursor/rules/` (`architecture.mdc`, `code-structure.mdc`, `dependencies.mdc`, `documentation-style.mdc`, `error-handling.mdc`, `logging.mdc`, `test-best-pra' in text, "expected to find: " + '- Opik Optimizer SDK: `sdks/opik_optimizer/.cursor/rules/` (`architecture.mdc`, `code-structure.mdc`, `dependencies.mdc`, `documentation-style.mdc`, `error-handling.mdc`, `logging.mdc`, `test-best-pra'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- Opik Optimizer SDK: `make install-dev`, `make test`, `make precommit` from `sdks/opik_optimizer`; follow the optimizer rules in `sdks/opik_optimizer/.cursor/rules/` (architecture, code structure, de' in text, "expected to find: " + '- Opik Optimizer SDK: `make install-dev`, `make test`, `make precommit` from `sdks/opik_optimizer`; follow the optimizer rules in `sdks/opik_optimizer/.cursor/rules/` (architecture, code structure, de'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/architecture.mdc')
    assert 'Each algorithm sits in its own package (`evolutionary_optimizer/`, `few_shot_bayesian_optimizer/`, `gepa_optimizer/`, `hierarchical_reflective_optimizer/`, `meta_prompt_optimizer/`, `mipro_optimizer/`' in text, "expected to find: " + 'Each algorithm sits in its own package (`evolutionary_optimizer/`, `few_shot_bayesian_optimizer/`, `gepa_optimizer/`, `hierarchical_reflective_optimizer/`, `meta_prompt_optimizer/`, `mipro_optimizer/`'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/architecture.mdc')
    assert '`OptimizationResult` provides fields such as `optimizer`, `prompt`, `score`, `metric_name`, `optimization_id`, `initial_prompt`, `initial_score`, `details`, `history`, `llm_calls`, and `tool_calls`. I' in text, "expected to find: " + '`OptimizationResult` provides fields such as `optimizer`, `prompt`, `score`, `metric_name`, `optimization_id`, `initial_prompt`, `initial_score`, `details`, `history`, `llm_calls`, and `tool_calls`. I'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/architecture.mdc')
    assert '- Support modules (`optimization_config/`, `_throttle.py`, `cache_config.py`, `reporting_utils.py`, `logging_config.py`, `multi_metric_objective.py`) provide prompt structures, rate limiting, caching,' in text, "expected to find: " + '- Support modules (`optimization_config/`, `_throttle.py`, `cache_config.py`, `reporting_utils.py`, `logging_config.py`, `multi_metric_objective.py`) provide prompt structures, rate limiting, caching,'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/code-structure.mdc')
    assert '- Split new logic into focused modules when a file grows beyond ~300 lines or mixes concerns (for example, extraction of mutation operators, prompt planners, evaluation helpers, or style utilities). P' in text, "expected to find: " + '- Split new logic into focused modules when a file grows beyond ~300 lines or mixes concerns (for example, extraction of mutation operators, prompt planners, evaluation helpers, or style utilities). P'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/code-structure.mdc')
    assert '- `reporting.py`: helpers that wrap `reporting_utils` context managers to print progress, capture baselines, and surface final summaries. Keep console output centralised here so the optimizer file foc' in text, "expected to find: " + '- `reporting.py`: helpers that wrap `reporting_utils` context managers to print progress, capture baselines, and surface final summaries. Keep console output centralised here so the optimizer file foc'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/code-structure.mdc')
    assert '- Use absolute imports when referencing other packages inside `opik_optimizer` (`from opik_optimizer.optimization_config import chat_prompt`). Reserve relative imports for local siblings within the sa' in text, "expected to find: " + '- Use absolute imports when referencing other packages inside `opik_optimizer` (`from opik_optimizer.optimization_config import chat_prompt`). Reserve relative imports for local siblings within the sa'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/dependencies.mdc')
    assert '- Test-only dependencies live in `tests/test_requirements.txt` (e.g. `pytest`, `pytest-asyncio`, `pytest-cov`, `orderly_set==5.3.2`, `gepa>=0.0.7`). Update this file when tests rely on new packages an' in text, "expected to find: " + '- Test-only dependencies live in `tests/test_requirements.txt` (e.g. `pytest`, `pytest-asyncio`, `pytest-cov`, `orderly_set==5.3.2`, `gepa>=0.0.7`). Update this file when tests rely on new packages an'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/dependencies.mdc')
    assert '- Keep heavyweight or niche integrations (for example, `gepa`, `langgraph`) in extras (`extras_require["dev"]`) or feature-specific requirements. Guard imports so base users are prompted with a clear ' in text, "expected to find: " + '- Keep heavyweight or niche integrations (for example, `gepa`, `langgraph`) in extras (`extras_require["dev"]`) or feature-specific requirements. Guard imports so base users are prompted with a clear '[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/dependencies.mdc')
    assert '- Formatting and lint hooks: `.pre-commit-config.yaml` provides the hook set. Run `make precommit` (which executes `pre-commit run --all-files`) locally or install the hooks with `pre-commit install`.' in text, "expected to find: " + '- Formatting and lint hooks: `.pre-commit-config.yaml` provides the hook set. Run `make precommit` (which executes `pre-commit run --all-files`) locally or install the hooks with `pre-commit install`.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/documentation-style.mdc')
    assert '- Update `README.md`, notebooks under `notebooks/`, and docs under `docs/` whenever you add a new optimizer or surface area. Demonstrate minimal reproducible examples using datasets from `opik_optimiz' in text, "expected to find: " + '- Update `README.md`, notebooks under `notebooks/`, and docs under `docs/` whenever you add a new optimizer or surface area. Demonstrate minimal reproducible examples using datasets from `opik_optimiz'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/documentation-style.mdc')
    assert '- Provide docstrings for public classes, lifecycle hooks (`optimize_prompt`, `_initialize_population`, `_evaluate_prompt`), and complex helpers. Start with a one-line summary followed by behaviour/sid' in text, "expected to find: " + '- Provide docstrings for public classes, lifecycle hooks (`optimize_prompt`, `_initialize_population`, `_evaluate_prompt`), and complex helpers. Start with a one-line summary followed by behaviour/sid'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/documentation-style.mdc')
    assert 'Keep docs lightweight and point back to the architecture rule for shared signatures and component overviews. Use documentation to clarify behaviour, configuration, and examples rather than restating c' in text, "expected to find: " + 'Keep docs lightweight and point back to the architecture rule for shared signatures and component overviews. Use documentation to clarify behaviour, configuration, and examples rather than restating c'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/error-handling.mdc')
    assert '- Interactions with Opik (`opik.api_objects.optimization.Optimization`) can raise `ApiError`. Catch these at the boundary, log a warning, and continue without optimisation tracking when possible so th' in text, "expected to find: " + '- Interactions with Opik (`opik.api_objects.optimization.Optimization`) can raise `ApiError`. Catch these at the boundary, log a warning, and continue without optimisation tracking when possible so th'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/error-handling.mdc')
    assert '- `task_evaluator.evaluate` already guards against empty datasets and metric failures by returning 0.0 and marking scores as failed. When extending it, keep error handling consistent and avoid leaking' in text, "expected to find: " + '- `task_evaluator.evaluate` already guards against empty datasets and metric failures by returning 0.0 and marking scores as failed. When extending it, keep error handling consistent and avoid leaking'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/error-handling.mdc')
    assert '- When evaluation fails for a candidate, decide whether to penalise, skip, or abort. Log the failure at `warning` level with the candidate summary and propagate the exception only if the optimizer can' in text, "expected to find: " + '- When evaluation fails for a candidate, decide whether to penalise, skip, or abort. Log the failure at `warning` level with the candidate summary and propagate the exception only if the optimizer can'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/logging.mdc')
    assert '- Include context such as `optimization_id`, `iteration`, `best_score`, or `population_size` in log messages. Prefer keyword arguments or formatted dicts over concatenated strings for readability.' in text, "expected to find: " + '- Include context such as `optimization_id`, `iteration`, `best_score`, or `population_size` in log messages. Prefer keyword arguments or formatted dicts over concatenated strings for readability.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/logging.mdc')
    assert '- Reserve logging for machine-readable diagnostics. Use `reporting_utils` context managers for user-facing console output; they already respect the `verbose` flag.' in text, "expected to find: " + '- Reserve logging for machine-readable diagnostics. Use `reporting_utils` context managers for user-facing console output; they already respect the `verbose` flag.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/logging.mdc')
    assert '- Call `logging_config.setup_logging()` (or expect callers to do so) before emitting logs; it wires the Rich handler and propagates `OPIK_LOG_LEVEL` overrides.' in text, "expected to find: " + '- Call `logging_config.setup_logging()` (or expect callers to do so) before emitting logs; it wires the Rich handler and propagates `OPIK_LOG_LEVEL` overrides.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc')
    assert '- Seed randomness where behaviour depends on stochastic operators (`random.seed`, `numpy.random.seed`). Many optimizers accept a `seed` parameter - set it explicitly in tests. Our default value for se' in text, "expected to find: " + '- Seed randomness where behaviour depends on stochastic operators (`random.seed`, `numpy.random.seed`). Many optimizers accept a `seed` parameter - set it explicitly in tests. Our default value for se'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc')
    assert '- End-to-end tests may require provider credentials (for example, `OPENAI_API_KEY`). Guard them with explicit failure messages so contributors understand the prerequisite before running the suite.' in text, "expected to find: " + '- End-to-end tests may require provider credentials (for example, `OPENAI_API_KEY`). Guard them with explicit failure messages so contributors understand the prerequisite before running the suite.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/test-best-practices.mdc')
    assert '- Configure optimizers with tiny populations, low iteration counts, and reduced thread pools. Unit tests should replace LiteLLM calls with fakes or patches so they run offline.' in text, "expected to find: " + '- Configure optimizers with tiny populations, low iteration counts, and reduced thread pools. Unit tests should replace LiteLLM calls with fakes or patches so they run offline.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/test-organization.mdc')
    assert '- Co-locate tests with the feature they exercise. For a new optimizer, add unit coverage for operators/helpers under `tests/unit/<optimizer>/` and an e2e smoke test under `tests/e2e/optimizers/`.' in text, "expected to find: " + '- Co-locate tests with the feature they exercise. For a new optimizer, add unit coverage for operators/helpers under `tests/unit/<optimizer>/` and an e2e smoke test under `tests/e2e/optimizers/`.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/test-organization.mdc')
    assert '- `unit/`: deterministic tests for helpers, configuration models, mutation operators, logging config, MCP utilities, etc. Subdirectories (like `unit/mcp/`) group related helper modules.' in text, "expected to find: " + '- `unit/`: deterministic tests for helpers, configuration models, mutation operators, logging config, MCP utilities, etc. Subdirectories (like `unit/mcp/`) group related helper modules.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('sdks/opik_optimizer/.cursor/rules/test-organization.mdc')
    assert '- Skip e2e tests gracefully when required environment variables or credentials are missing, and mention the requirement at the top of the file.' in text, "expected to find: " + '- Skip e2e tests gracefully when required environment variables or credentials are missing, and mention the requirement at the top of the file.'[:80]

