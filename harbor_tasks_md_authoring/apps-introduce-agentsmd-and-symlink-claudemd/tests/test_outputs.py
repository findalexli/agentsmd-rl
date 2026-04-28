"""Behavioral checks for apps-introduce-agentsmd-and-symlink-claudemd (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/apps")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Use Cases**: Webhook handlers delegate to use case classes that contain business logic. Use cases extend `BaseUseCase` for shared config loading patterns.' in text, "expected to find: " + '**Use Cases**: Webhook handlers delegate to use case classes that contain business logic. Use cases extend `BaseUseCase` for shared config loading patterns.'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**Monorepo Architecture**: This is a Turborepo-managed monorepo containing Saleor Apps built with Next.js, TypeScript, and modern development tooling.' in text, "expected to find: " + '**Monorepo Architecture**: This is a Turborepo-managed monorepo containing Saleor Apps built with Next.js, TypeScript, and modern development tooling.'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '**External APIs**: Payment providers (Stripe, NP Atobarai), tax services (AvaTax), CMS systems, etc. wrapped in domain-specific client classes' in text, "expected to find: " + '**External APIs**: Payment providers (Stripe, NP Atobarai), tax services (AvaTax), CMS systems, etc. wrapped in domain-specific client classes'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('CLAUDE.md')
    assert 'CLAUDE.md' in text, "expected to find: " + 'CLAUDE.md'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/smtp/AGENTS.md')
    assert 'This is a Saleor SMTP Application that handles email notifications for e-commerce events. It integrates with Saleor API via webhooks and sends transactional emails using SMTP configuration.' in text, "expected to find: " + 'This is a Saleor SMTP Application that handles email notifications for e-commerce events. It integrates with Saleor API via webhooks and sends transactional emails using SMTP configuration.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/smtp/AGENTS.md')
    assert 'All API endpoints use tRPC routers defined in `*.router.ts` files. Protected procedures require authentication via `protectedClientProcedure` (valid Saleor token).' in text, "expected to find: " + 'All API endpoints use tRPC routers defined in `*.router.ts` files. Protected procedures require authentication via `protectedClientProcedure` (valid Saleor token).'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/smtp/AGENTS.md')
    assert 'Located in `/src/modules/smtp/configuration/`, manages email templates and SMTP settings per event type. Configurations are stored in DynamoDB/APL.' in text, "expected to find: " + 'Located in `/src/modules/smtp/configuration/`, manages email templates and SMTP settings per event type. Configurations are stored in DynamoDB/APL.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/smtp/CLAUDE.md')
    assert 'apps/smtp/CLAUDE.md' in text, "expected to find: " + 'apps/smtp/CLAUDE.md'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('apps/smtp/CLAUDE.md')
    assert 'apps/smtp/CLAUDE.md' in text, "expected to find: " + 'apps/smtp/CLAUDE.md'[:80]

