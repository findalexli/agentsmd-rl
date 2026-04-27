"""Behavioral checks for pinme-docs-optimize-skill-documentation (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/pinme")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pinme-api/SKILL.md')
    assert 'description: Use this skill when a PinMe project (Worker TypeScript) needs to integrate email sending (send_email) or LLM API calls (chat/completions). Guides AI to generate correct Worker TS code.' in text, "expected to find: " + 'description: Use this skill when a PinMe project (Worker TypeScript) needs to integrate email sending (send_email) or LLM API calls (chat/completions). Guides AI to generate correct Worker TS code.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pinme-api/SKILL.md')
    assert "> `project_name` is parsed from the Worker's subdomain — see example below. For available models, refer to [PinMe LLM Supported Models](https://openrouter.ai/models) (OpenAI-compatible format)." in text, "expected to find: " + "> `project_name` is parsed from the Worker's subdomain — see example below. For available models, refer to [PinMe LLM Supported Models](https://openrouter.ai/models) (OpenAI-compatible format)."[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pinme-api/SKILL.md')
    assert '> `API_KEY` is the sole credential for the Worker to call PinMe platform APIs. When `BASE_URL` is not set, it defaults to `https://pinme.dev`.' in text, "expected to find: " + '> `API_KEY` is the sole credential for the Worker to call PinMe platform APIs. When `BASE_URL` is not set, it defaults to `https://pinme.dev`.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pinme/SKILL.md')
    assert 'description: Use this skill when the user mentions "pinme", or needs to upload files, store to IPFS, create/publish/deploy websites or full-stack services (including frontend pages, backend APIs, data' in text, "expected to find: " + 'description: Use this skill when the user mentions "pinme", or needs to upload files, store to IPFS, create/publish/deploy websites or full-stack services (including frontend pages, backend APIs, data'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pinme/SKILL.md')
    assert 'Zero-config deployment tool: upload static files to IPFS, or create and deploy full-stack web projects (React+Vite + Cloudflare Worker + D1 database). Workers also support sending emails via the PinMe' in text, "expected to find: " + 'Zero-config deployment tool: upload static files to IPFS, or create and deploy full-stack web projects (React+Vite + Cloudflare Worker + D1 database). Workers also support sending emails via the PinMe'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/pinme/SKILL.md')
    assert "`pinme create` generates a working Hello World template (includes frontend page + backend API routes + database schema). **Modify the template** to match the user's business logic — do not write from " in text, "expected to find: " + "`pinme create` generates a working Hello World template (includes frontend page + backend API routes + database schema). **Modify the template** to match the user's business logic — do not write from "[:80]

