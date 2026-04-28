"""Behavioral checks for browser-use-improve-model-docs (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/browser-use")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/open-source/references/models.md')
    assert 'Requires `~/.oci/config` setup and `pip install "browser-use[oci]"`. [Available models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/imported-models.htm). Auth types: `API_KEY`, `INSTANCE_' in text, "expected to find: " + 'Requires `~/.oci/config` setup and `pip install "browser-use[oci]"`. [Available models](https://docs.oracle.com/en-us/iaas/Content/generative-ai/imported-models.htm). Auth types: `API_KEY`, `INSTANCE_'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/open-source/references/models.md')
    assert '**Env:** `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` | [Available models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)' in text, "expected to find: " + '**Env:** `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_API_KEY` | [Available models](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/open-source/references/models.md')
    assert '**Env:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` | [Available models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)' in text, "expected to find: " + '**Env:** `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION` | [Available models](https://docs.aws.amazon.com/bedrock/latest/userguide/model-ids.html)'[:80]

