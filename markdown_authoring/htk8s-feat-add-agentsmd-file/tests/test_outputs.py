"""Behavioral checks for htk8s-feat-add-agentsmd-file (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/htk8s")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert 'This project uses `kustomize` to manage Kubernetes manifests. The core manifests are located in the `base` directory, and environment-specific configurations (overlays) are in the `overlays` directory' in text, "expected to find: " + 'This project uses `kustomize` to manage Kubernetes manifests. The core manifests are located in the `base` directory, and environment-specific configurations (overlays) are in the `overlays` directory'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '-   **Never edit the `install_*.yaml` files directly.** These files are auto-generated, and your changes will be overwritten the next time the `update-manifests.sh` script is run.' in text, "expected to find: " + '-   **Never edit the `install_*.yaml` files directly.** These files are auto-generated, and your changes will be overwritten the next time the `update-manifests.sh` script is run.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '2.  **Regenerate the Install Manifests**: After you have made your changes to the base manifests, you **MUST** run the following script to regenerate the final install manifests:' in text, "expected to find: " + '2.  **Regenerate the Install Manifests**: After you have made your changes to the base manifests, you **MUST** run the following script to regenerate the final install manifests:'[:80]

