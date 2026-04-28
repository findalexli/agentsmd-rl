"""Behavioral checks for autorag-research-add-agent-skills-for-plugin (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/autorag-research")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-generation-plugin/SKILL.md')
    assert '**Custom parameters:** Add fields to your config class and pass them via `get_pipeline_kwargs()` → accept them in the pipeline constructor.' in text, "expected to find: " + '**Custom parameters:** Add fields to your config class and pass them via `get_pipeline_kwargs()` → accept them in the pipeline constructor.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-generation-plugin/SKILL.md')
    assert '- `self._service` — `GenerationPipelineService` (use `self._service.get_chunk_contents(chunk_ids)`, `self._get_query_text(query_id)`)' in text, "expected to find: " + '- `self._service` — `GenerationPipelineService` (use `self._service.get_chunk_contents(chunk_ids)`, `self._get_query_text(query_id)`)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-generation-plugin/SKILL.md')
    assert '- `self._retrieval_pipeline` — composed retrieval pipeline (use `await self._retrieval_pipeline._retrieve_by_id(query_id, top_k)`)' in text, "expected to find: " + '- `self._retrieval_pipeline` — composed retrieval pipeline (use `await self._retrieval_pipeline._retrieve_by_id(query_id, top_k)`)'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-ingestor-plugin/SKILL.md')
    assert 'The generated `pyproject.toml` registers the `autorag_research.ingestors` entry point. The `@register_ingestor` decorator handles automatic CLI parameter extraction from `__init__` type hints.' in text, "expected to find: " + 'The generated `pyproject.toml` registers the `autorag_research.ingestors` entry point. The `@register_ingestor` decorator handles automatic CLI parameter extraction from `__init__` type hints.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-ingestor-plugin/SKILL.md')
    assert '- `IngestorTestVerifier` — runs all configured checks: count verification, format validation, retrieval relation checks, generation_gt checks, content hash verification' in text, "expected to find: " + '- `IngestorTestVerifier` — runs all configured checks: count verification, format validation, retrieval relation checks, generation_gt checks, content hash verification'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-ingestor-plugin/SKILL.md')
    assert '**`self.service`** is injected after construction via `set_service()`. Read existing ingestors for exact service method signatures.' in text, "expected to find: " + '**`self.service`** is injected after construction via `set_service()`. Read existing ingestors for exact service method signatures.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-metric-plugin/SKILL.md')
    assert "This is critical for multi-hop queries where multiple evidence pieces are needed. Your metric must handle this structure correctly — don't just flatten it into a single set unless your metric semantic" in text, "expected to find: " + "This is critical for multi-hop queries where multiple evidence pieces are needed. Your metric must handle this structure correctly — don't just flatten it into a single set unless your metric semantic"[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-metric-plugin/SKILL.md')
    assert 'Use the `@metric` decorator (per-input) or `@metric_loop` decorator (batch) from `autorag_research.evaluation.metrics.util`. Both validate that required fields are non-None before calling.' in text, "expected to find: " + 'Use the `@metric` decorator (per-input) or `@metric_loop` decorator (batch) from `autorag_research.evaluation.metrics.util`. Both validate that required fields are non-None before calling.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-metric-plugin/SKILL.md')
    assert 'The generated config class just needs `get_metric_func()` to return your metric function. If your metric takes extra kwargs, override `get_metric_kwargs()`.' in text, "expected to find: " + 'The generated config class just needs `get_metric_func()` to return your metric function. If your metric takes extra kwargs, override `get_metric_kwargs()`.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-retrieval-plugin/SKILL.md')
    assert '**Custom parameters:** Add fields to your config class and pass them via `get_pipeline_kwargs()` → accept them in the pipeline constructor. See `bm25.py` for a real example.' in text, "expected to find: " + '**Custom parameters:** Add fields to your config class and pass them via `get_pipeline_kwargs()` → accept them in the pipeline constructor. See `bm25.py` for a real example.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-retrieval-plugin/SKILL.md')
    assert 'Read the generated `pipeline.py`, `pyproject.toml`, YAML config, and test file to understand the structure.' in text, "expected to find: " + 'Read the generated `pipeline.py`, `pyproject.toml`, YAML config, and test file to understand the structure.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/create-retrieval-plugin/SKILL.md')
    assert '- `_retrieve_by_id(query_id, top_k)` — retrieve using query ID (query exists in DB with stored embedding)' in text, "expected to find: " + '- `_retrieve_by_id(query_id, top_k)` — retrieve using query ID (query exists in DB with stored embedding)'[:80]

