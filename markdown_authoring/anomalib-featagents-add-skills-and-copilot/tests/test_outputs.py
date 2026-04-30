"""Behavioral checks for anomalib-featagents-add-skills-and-copilot (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/anomalib")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/benchmark-and-docs-refresh/SKILL.md')
    assert 'description: Run or continue model benchmarks, collect measured results, and refresh README/docs benchmark sections from generated artifacts. Use when benchmark tables in model docs need to be created' in text, "expected to find: " + 'description: Run or continue model benchmarks, collect measured results, and refresh README/docs benchmark sections from generated artifacts. Use when benchmark tables in model docs need to be created'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/benchmark-and-docs-refresh/SKILL.md')
    assert 'Use this skill to update benchmark sections in model documentation from real benchmark outputs.' in text, "expected to find: " + 'Use this skill to update benchmark sections in model documentation from real benchmark outputs.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/benchmark-and-docs-refresh/SKILL.md')
    assert 'If a README only contains placeholders, replace only the rows supported by measured results.' in text, "expected to find: " + 'If a README only contains placeholders, replace only the rows supported by measured results.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/docs-changelog/SKILL.md')
    assert '- Review the nearest documentation surface, not just the edited Python file: `README.md`, docs under `docs/source/markdown/`, model-specific `README.md`, examples, or reference pages.' in text, "expected to find: " + '- Review the nearest documentation surface, not just the edited Python file: `README.md`, docs under `docs/source/markdown/`, model-specific `README.md`, examples, or reference pages.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/docs-changelog/SKILL.md')
    assert '- Purely internal changes may not need a changelog entry, but reviewers should call out missing entries for behavior, API, docs, or user workflow changes.' in text, "expected to find: " + '- Purely internal changes may not need a changelog entry, but reviewers should call out missing entries for behavior, API, docs, or user workflow changes.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/docs-changelog/SKILL.md')
    assert '- For tensors, arrays, batches, or structured outputs, ask reviewers to document shapes or field expectations when they matter for correct usage.' in text, "expected to find: " + '- For tensors, arrays, batches, or structured outputs, ask reviewers to document shapes or field expectations when they matter for correct usage.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/model-doc-sync/SKILL.md')
    assert '- If the docs page is a lightweight API/reference page, still ensure it does not contradict README claims about architecture, benchmarks, or results.' in text, "expected to find: " + '- If the docs page is a lightweight API/reference page, still ensure it does not contradict README claims about architecture, benchmarks, or results.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/model-doc-sync/SKILL.md')
    assert '- Many model docs pages act as reference wrappers around module docs, so keep them aligned with the README without forcing full duplication.' in text, "expected to find: " + '- Many model docs pages act as reference wrappers around module docs, so keep them aligned with the README without forcing full duplication.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/model-doc-sync/SKILL.md')
    assert '- Prefer repository-consistent image references such as `/docs/source/images/<model>/...` when the README already uses that pattern.' in text, "expected to find: " + '- Prefer repository-consistent image references such as `/docs/source/images/<model>/...` when the README already uses that pattern.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/model-sample-image-export/SKILL.md')
    assert 'description: Export, validate, and publish model sample-result images into docs/source/images and reference them from README/docs pages. Use when model sample images are missing, outdated, or suspecte' in text, "expected to find: " + 'description: Export, validate, and publish model sample-result images into docs/source/images and reference them from README/docs pages. Use when model sample images are missing, outdated, or suspecte'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/model-sample-image-export/SKILL.md')
    assert '- if no suitable completed checkpoint, benchmark output, or other traceable run artifact exists, schedule a few runs to generate trustworthy sample images' in text, "expected to find: " + '- if no suitable completed checkpoint, benchmark output, or other traceable run artifact exists, schedule a few runs to generate trustworthy sample images'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/model-sample-image-export/SKILL.md')
    assert 'If you have fewer than 3 trustworthy images, train the model on a few more categories to generate more sample images.' in text, "expected to find: " + 'If you have fewer than 3 trustworthy images, train the model on a few more categories to generate more sample images.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/models-data/SKILL.md')
    assert '- Training side effects such as checkpointing, timing, compression, or visualization should follow the callback-based patterns already present in `src/anomalib/callbacks/`.' in text, "expected to find: " + '- Training side effects such as checkpointing, timing, compression, or visualization should follow the callback-based patterns already present in `src/anomalib/callbacks/`.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/models-data/SKILL.md')
    assert "- Data should move through anomalib's typed dataclass system rather than ad hoc dictionaries where the library already has structured item/batch types." in text, "expected to find: " + "- Data should move through anomalib's typed dataclass system rather than ad hoc dictionaries where the library already has structured item/batch types."[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/models-data/SKILL.md')
    assert '- `src/anomalib/data/dataclasses/generic.py` is the main reference for `FieldDescriptor`, typed fields, update behavior, and batch/item patterns.' in text, "expected to find: " + '- `src/anomalib/data/dataclasses/generic.py` is the main reference for `FieldDescriptor`, typed fields, update behavior, and batch/item patterns.'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-workflow/SKILL.md')
    assert "- Security-sensitive changes should be reviewed with the repo's CI security tooling in mind: Bandit, CodeQL, Semgrep, Zizmor, Trivy, and Dependabot." in text, "expected to find: " + "- Security-sensitive changes should be reviewed with the repo's CI security tooling in mind: Bandit, CodeQL, Semgrep, Zizmor, Trivy, and Dependabot."[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-workflow/SKILL.md')
    assert "- Review feedback should align with the project's configured checks in `pyproject.toml` and `.pre-commit-config.yaml`." in text, "expected to find: " + "- Review feedback should align with the project's configured checks in `pyproject.toml` and `.pre-commit-config.yaml`."[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/pr-workflow/SKILL.md')
    assert '- Be stricter when a PR changes CLI entrypoints, workflows, deployment, inferencers, or user-facing public APIs.' in text, "expected to find: " + '- Be stricter when a PR changes CLI entrypoints, workflows, deployment, inferencers, or user-facing public APIs.'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/python-docstrings/SKILL.md')
    assert '- Document constructor arguments in the class docstring rather than in a separate `__init__` docstring.' in text, "expected to find: " + '- Document constructor arguments in the class docstring rather than in a separate `__init__` docstring.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/python-docstrings/SKILL.md')
    assert '- Use doctest-style `Example` blocks with `>>>` when examples help clarify usage.' in text, "expected to find: " + '- Use doctest-style `Example` blocks with `>>>` when examples help clarify usage.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/python-docstrings/SKILL.md')
    assert '- arguments, returns, or intentionally raised exceptions are undocumented;' in text, "expected to find: " + '- arguments, returns, or intentionally raised exceptions are undocumented;'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/python-style/SKILL.md')
    assert '- Prefer repository-established typing patterns such as `X | None`, `type[...]`, `Sequence[...]`, `TypeVar`, and `Generic` where they fit.' in text, "expected to find: " + '- Prefer repository-established typing patterns such as `X | None`, `type[...]`, `Sequence[...]`, `TypeVar`, and `Generic` where they fit.'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/python-style/SKILL.md')
    assert '- Flag vague escape hatches such as unnecessary `Any`, broad untyped `**kwargs`, or type suppressions that hide real issues.' in text, "expected to find: " + '- Flag vague escape hatches such as unnecessary `Any`, broad untyped `**kwargs`, or type suppressions that hide real issues.'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/python-style/SKILL.md')
    assert '- Flag debug prints, dead code, commented-out code, and magic values that should be named constants or config.' in text, "expected to find: " + '- Flag debug prints, dead code, commented-out code, and magic values that should be named constants or config.'[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing/SKILL.md')
    assert '- For tensor-heavy logic, ensure tests assert the properties that matter: shapes, values, reconstruction behavior, errors, or invariants.' in text, "expected to find: " + '- For tensor-heavy logic, ensure tests assert the properties that matter: shapes, values, reconstruction behavior, errors, or invariants.'[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing/SKILL.md')
    assert '- If the change touches CLI/config/model loading or pipeline orchestration, review whether a higher-level test is also needed.' in text, "expected to find: " + '- If the change touches CLI/config/model loading or pipeline orchestration, review whether a higher-level test is also needed.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/testing/SKILL.md')
    assert 'Use this skill to decide what test coverage is required and whether existing tests still prove the intended behavior.' in text, "expected to find: " + 'Use this skill to decide what test coverage is required and whether existing tests still prove the intended behavior.'[:80]


def test_signal_27():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/third-party-code/SKILL.md')
    assert '- Do not add third-party-derived code unless its license allows redistribution and modification compatible with this repository.' in text, "expected to find: " + '- Do not add third-party-derived code unless its license allows redistribution and modification compatible with this repository.'[:80]


def test_signal_28():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/third-party-code/SKILL.md')
    assert "- Keep the anomalib-side copyright/SPDX notice pattern when the repository's existing third-party examples do so." in text, "expected to find: " + "- Keep the anomalib-side copyright/SPDX notice pattern when the repository's existing third-party examples do so."[:80]


def test_signal_29():
    """Distinctive line from gold patch must be present."""
    text = _read('.agents/skills/third-party-code/SKILL.md')
    assert 'Use this skill when reviewing or generating code that is copied from, adapted from, or substantially based on an' in text, "expected to find: " + 'Use this skill when reviewing or generating code that is copied from, adapted from, or substantially based on an'[:80]


def test_signal_30():
    """Distinctive line from gold patch must be present."""
    text = _read('.cursor/rules/python_docstrings.mdc')
    assert '.cursor/rules/python_docstrings.mdc' in text, "expected to find: " + '.cursor/rules/python_docstrings.mdc'[:80]


def test_signal_31():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- Treat `src/anomalib/`, `application/`, `tests/`, `docs/`, `.github/`, and relevant `.agents/skills/` files as first-class review surfaces.' in text, "expected to find: " + '- Treat `src/anomalib/`, `application/`, `tests/`, `docs/`, `.github/`, and relevant `.agents/skills/` files as first-class review surfaces.'[:80]


def test_signal_32():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert '- If a change touches `application/`, note that Anomalib Studio has some separate tooling and config from the root project.' in text, "expected to find: " + '- If a change touches `application/`, note that Anomalib Studio has some separate tooling and config from the root project.'[:80]


def test_signal_33():
    """Distinctive line from gold patch must be present."""
    text = _read('.github/copilot-instructions.md')
    assert 'Prefer the repository-local skills under `.agents/skills/` instead of embedding all review policy here.' in text, "expected to find: " + 'Prefer the repository-local skills under `.agents/skills/` instead of embedding all review policy here.'[:80]

