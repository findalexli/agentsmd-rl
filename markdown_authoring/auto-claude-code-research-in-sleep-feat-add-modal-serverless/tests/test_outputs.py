"""Behavioral checks for auto-claude-code-research-in-sleep-feat-add-modal-serverless (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/auto-claude-code-research-in-sleep")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/experiment-bridge/SKILL.md')
    assert '- **Modal lifecycle.** If using `gpu: modal`, no cleanup is needed — Modal auto-scales to zero after each run. But always show cost estimates before running and verify the spending limit is set at htt' in text, "expected to find: " + '- **Modal lifecycle.** If using `gpu: modal`, no cleanup is needed — Modal auto-scales to zero after each run. But always show cost estimates before running and verify the spending limit is set at htt'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-experiment/SKILL.md')
    assert '- **Modal cost awareness**: Modal auto-scales to zero — no idle billing. When reporting results from Modal runs, note the actual execution time and estimated cost (time * $/hr from the GPU tier used).' in text, "expected to find: " + '- **Modal cost awareness**: Modal auto-scales to zero — no idle billing. When reporting results from Modal runs, note the actual execution time and estimated cost (time * $/hr from the GPU tier used).'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-experiment/SKILL.md')
    assert "Modal apps auto-terminate when done — if it's not in the list, it already finished. Check results via `modal volume ls <volume>` or local output." in text, "expected to find: " + "Modal apps auto-terminate when done — if it's not in the list, it already finished. Check results via `modal volume ls <volume>` or local output."[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/monitor-experiment/SKILL.md')
    assert 'modal app logs <app>   # Stream logs from a running app' in text, "expected to find: " + 'modal app logs <app>   # Stream logs from a running app'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run-experiment/SKILL.md')
    assert '> **Modal setup**: Run `pip install modal && modal setup`. Bind a payment method at https://modal.com/settings (NEVER through CLI) to unlock the full $30/month free tier (without card: $5/month only).' in text, "expected to find: " + '> **Modal setup**: Run `pip install modal && modal setup`. Bind a payment method at https://modal.com/settings (NEVER through CLI) to unlock the full $30/month free tier (without card: $5/month only).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run-experiment/SKILL.md')
    assert '**Modal detection:** If `CLAUDE.md` has `gpu: modal` or a `## Modal` section, the entire deployment is handled by `/serverless-modal`. Jump to **Step 4: Deploy (Modal)** — Steps 2-3 are not needed (Mo' in text, "expected to find: " + '**Modal detection:** If `CLAUDE.md` has `gpu: modal` or a `## Modal` section, the entire deployment is handled by `/serverless-modal`. Jump to **Step 4: Deploy (Modal)** — Steps 2-3 are not needed (Mo'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/run-experiment/SKILL.md')
    assert 'description: Deploy and run ML experiments on local, remote, Vast.ai, or Modal serverless GPU. Use when user says "run experiment", "deploy to server", "跑实验", or needs to launch training jobs.' in text, "expected to find: " + 'description: Deploy and run ML experiments on local, remote, Vast.ai, or Modal serverless GPU. Use when user says "run experiment", "deploy to server", "跑实验", or needs to launch training jobs.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/serverless-modal/SKILL.md')
    assert '> **Cost protection**: After `modal setup`, go to https://modal.com/settings in your browser (NEVER through CLI) → bind a payment method to unlock $30/month free tier (without card: only $5/month). Th' in text, "expected to find: " + '> **Cost protection**: After `modal setup`, go to https://modal.com/settings in your browser (NEVER through CLI) → bind a payment method to unlock $30/month free tier (without card: only $5/month). Th'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/serverless-modal/SKILL.md')
    assert 'description: "Run GPU workloads on Modal — training, fine-tuning, inference, batch processing. Zero-config serverless: no SSH, no Docker, auto scale-to-zero. Use when user says \\"modal run\\", \\"modal ' in text, "expected to find: " + 'description: "Run GPU workloads on Modal — training, fine-tuning, inference, batch processing. Zero-config serverless: no SSH, no Docker, auto scale-to-zero. Use when user says \\"modal run\\", \\"modal '[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/serverless-modal/SKILL.md')
    assert '> **SECURITY WARNING**: Always bind your card and set spending limits directly on https://modal.com/settings in your browser. NEVER enter payment information, card numbers, or billing details through ' in text, "expected to find: " + '> **SECURITY WARNING**: Always bind your card and set spending limits directly on https://modal.com/settings in your browser. NEVER enter payment information, card numbers, or billing details through '[:80]

