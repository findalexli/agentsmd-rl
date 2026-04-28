"""Behavioral checks for aiconfigurator-feat-add-claude-rules-for (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/aiconfigurator")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator-development.md')
    assert '- **Dynamo profiler** (https://github.com/ai-dynamo/dynamo/tree/main/components/src/dynamo/profiler) -- profiler feeds data that generator consumes; schema changes propagate' in text, "expected to find: " + '- **Dynamo profiler** (https://github.com/ai-dynamo/dynamo/tree/main/components/src/dynamo/profiler) -- profiler feeds data that generator consumes; schema changes propagate'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator-development.md')
    assert '| `src/aiconfigurator/generator/rendering/engine.py` | High | Context building + template rendering; changes affect ALL backends and versions |' in text, "expected to find: " + '| `src/aiconfigurator/generator/rendering/engine.py` | High | Context building + template rendering; changes affect ALL backends and versions |'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator-development.md')
    assert '| `src/aiconfigurator/generator/module_bridge.py` | Medium | SDK/profiler bridge; field name mismatches break the profiler -> generator flow |' in text, "expected to find: " + '| `src/aiconfigurator/generator/module_bridge.py` | Medium | SDK/profiler bridge; field name mismatches break the profiler -> generator flow |'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/config_schema.md')
    assert '| `src/aiconfigurator/generator/config/deployment_config.yaml` | Input schema: ~54 params, defaults, constraints |' in text, "expected to find: " + '| `src/aiconfigurator/generator/config/deployment_config.yaml` | Input schema: ~54 params, defaults, constraints |'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/config_schema.md')
    assert '| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Unified param -> backend CLI flag mapping |' in text, "expected to find: " + '| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Unified param -> backend CLI flag mapping |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/config_schema.md')
    assert '| `src/aiconfigurator/generator/rendering/schemas.py` | Schema validation, default application |' in text, "expected to find: " + '| `src/aiconfigurator/generator/rendering/schemas.py` | Schema validation, default application |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/cross_module_impact.md')
    assert '| 2. Templates | `src/aiconfigurator/generator/config/backend_templates/<backend>/` | Version-specific templates if CLI changed |' in text, "expected to find: " + '| 2. Templates | `src/aiconfigurator/generator/config/backend_templates/<backend>/` | Version-specific templates if CLI changed |'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/cross_module_impact.md')
    assert '| 1. Schema | `src/aiconfigurator/generator/config/deployment_config.yaml` | Define the param, default, backend support |' in text, "expected to find: " + '| 1. Schema | `src/aiconfigurator/generator/config/deployment_config.yaml` | Define the param, default, backend support |'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/cross_module_impact.md')
    assert '| 1. Version matrix | `src/aiconfigurator/generator/config/backend_version_matrix.yaml` | Map Dynamo -> backend version |' in text, "expected to find: " + '| 1. Version matrix | `src/aiconfigurator/generator/config/backend_version_matrix.yaml` | Map Dynamo -> backend version |'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/debugging.md')
    assert '| Missing parameter in one backend | #579 | Rule not added | `.rule` file for that backend |' in text, "expected to find: " + '| Missing parameter in one backend | #579 | Rule not added | `.rule` file for that backend |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/debugging.md')
    assert '- Generator produces wrong output (invalid CLI args, missing config blocks, wrong values)' in text, "expected to find: " + '- Generator produces wrong output (invalid CLI args, missing config blocks, wrong values)'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/debugging.md')
    assert 'The generator has 6 stages. A bug can originate at any stage but manifests at the output.' in text, "expected to find: " + 'The generator has 6 stages. A bug can originate at any stage but manifests at the output.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/guard_rails.md')
    assert '| `build_config` nesting is version-dependent | SILENT | Pre-1.2.0rc5: inside `build_config`. Post-1.2.0rc5: top-level. Wrong placement silently ignored. |' in text, "expected to find: " + '| `build_config` nesting is version-dependent | SILENT | Pre-1.2.0rc5: inside `build_config`. Post-1.2.0rc5: top-level. Wrong placement silently ignored. |'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/guard_rails.md')
    assert '| `cache_transceiver_config` lifecycle | CRASH | Absent pre-1.0.0rc4. In engine YAML 1.0.0rc4-1.3.0rc1. In CLI `--override-engine-args` post-1.3.0rc5. |' in text, "expected to find: " + '| `cache_transceiver_config` lifecycle | CRASH | Absent pre-1.0.0rc4. In engine YAML 1.0.0rc4-1.3.0rc1. In CLI `--override-engine-args` post-1.3.0rc5. |'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/guard_rails.md')
    assert '| Template variables must be top-level keys | SILENT | `engine.py` flattens context; nested paths like `build_config.max_batch_size` are undefined. |' in text, "expected to find: " + '| Template variables must be top-level keys | SILENT | `engine.py` flattens context; nested paths like `build_config.max_batch_size` are undefined. |'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/new_backend_version.md')
    assert 'coordinated changes across multiple files. Getting any step wrong results in deployment' in text, "expected to find: " + 'coordinated changes across multiple files. Getting any step wrong results in deployment'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/new_backend_version.md')
    assert "didn't change, the existing template works fine. The version fallback logic handles it." in text, "expected to find: " + "didn't change, the existing template works fine. The version fallback logic handles it."[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/new_backend_version.md')
    assert 'Adding a new backend version is one of the most frequent generator tasks. It involves' in text, "expected to find: " + 'Adding a new backend version is one of the most frequent generator tasks. It involves'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/rule_authoring.md')
    assert 'agg max_num_tokens = ((max_batch_size + SlaConfig.isl + 1500 + tokens_per_block - 1) // tokens_per_block) * tokens_per_block' in text, "expected to find: " + 'agg max_num_tokens = ((max_batch_size + SlaConfig.isl + 1500 + tokens_per_block - 1) // tokens_per_block) * tokens_per_block'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/rule_authoring.md')
    assert '| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Parameter backend support |' in text, "expected to find: " + '| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Parameter backend support |'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/rule_authoring.md')
    assert '| `src/aiconfigurator/generator/rule_plugin/benchmark/*.rule` | Benchmark rules per backend |' in text, "expected to find: " + '| `src/aiconfigurator/generator/rule_plugin/benchmark/*.rule` | Benchmark rules per backend |'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/template_authoring.md')
    assert '- **New version templates**: Copy the closest prior version, modify. NEVER edit prior versions.' in text, "expected to find: " + '- **New version templates**: Copy the closest prior version, modify. NEVER edit prior versions.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/template_authoring.md')
    assert '| `src/aiconfigurator/generator/rendering/engine.py` | Template rendering + context building |' in text, "expected to find: " + '| `src/aiconfigurator/generator/rendering/engine.py` | Template rendering + context building |'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/template_authoring.md')
    assert '| `src/aiconfigurator/generator/config/backend_version_matrix.yaml` | Version compatibility |' in text, "expected to find: " + '| `src/aiconfigurator/generator/config/backend_version_matrix.yaml` | Version compatibility |'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/testing.md')
    assert 'runtime in CI, silent regressions, and test coverage gaps. This reference defines' in text, "expected to find: " + 'runtime in CI, silent regressions, and test coverage gaps. This reference defines'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/testing.md')
    assert 'Generator testing has unique challenges: combinatorial output space, no backend' in text, "expected to find: " + 'Generator testing has unique challenges: combinatorial output space, no backend'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/rules/generator/testing.md')
    assert '- Template/rule/schema change (output-affecting): Integration + golden snapshot' in text, "expected to find: " + '- Template/rule/schema change (output-affecting): Integration + golden snapshot'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This file adds an explicit guard for generator rule edits.' in text, "expected to find: " + 'This file adds an explicit guard for generator rule edits.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `aiconfigurator/.claude/rules/generator-development.md`' in text, "expected to find: " + '- `aiconfigurator/.claude/rules/generator-development.md`'[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- `aiconfigurator/src/aiconfigurator/generator/**`' in text, "expected to find: " + '- `aiconfigurator/src/aiconfigurator/generator/**`'[:80]

