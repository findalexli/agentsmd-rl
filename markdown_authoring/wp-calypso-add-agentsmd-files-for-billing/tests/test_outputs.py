"""Behavioral checks for wp-calypso-add-agentsmd-files-for-billing (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/wp-calypso")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- client/dashboard/me/billing-purchases — billing & purchase management' in text, "expected to find: " + '- client/dashboard/me/billing-purchases — billing & purchase management'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- client/me/purchases — purchase management' in text, "expected to find: " + '- client/me/purchases — purchase management'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('AGENTS.md')
    assert '- client/my-sites/checkout — checkout flow' in text, "expected to find: " + '- client/my-sites/checkout — checkout flow'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert '- Prefer `@wordpress/components` over custom UI primitives (Button, Modal, Card, etc.). Avoid `__experimental*` components unless existing usage in codebase.' in text, "expected to find: " + '- Prefer `@wordpress/components` over custom UI primitives (Button, Modal, Card, etc.). Avoid `__experimental*` components unless existing usage in codebase.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert 'React + TypeScript application clients for WordPress.com. For repo-level context, see root `AGENTS.md`.' in text, "expected to find: " + 'React + TypeScript application clients for WordPress.com. For repo-level context, see root `AGENTS.md`.'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('client/AGENTS.md')
    assert 'page.js routing. Dashboard (`client/dashboard/`) uses TanStack Query + TanStack Router.' in text, "expected to find: " + 'page.js routing. Dashboard (`client/dashboard/`) uses TanStack Query + TanStack Router.'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/AGENTS.md')
    assert '- **me/billing-purchases/** — Billing & purchase management (cancel flows, payment methods, DataViews)' in text, "expected to find: " + '- **me/billing-purchases/** — Billing & purchase management (cancel flows, payment methods, DataViews)'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/AGENTS.md')
    assert '## Sub-area Guides' in text, "expected to find: " + '## Sub-area Guides'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/me/billing-purchases/AGENTS.md')
    assert '6. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never call ' in text, "expected to find: " + '6. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never call '[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/me/billing-purchases/AGENTS.md')
    assert '| Flow Type            | When                                                          | API Call                            |' in text, "expected to find: " + '| Flow Type            | When                                                          | API Call                            |'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/me/billing-purchases/AGENTS.md')
    assert '| `REMOVE`             | Expired, grace-period, or (not refundable AND auto-renew off) | `removePurchaseMutation()` (DELETE) |' in text, "expected to find: " + '| `REMOVE`             | Expired, grace-period, or (not refundable AND auto-renew off) | `removePurchaseMutation()` (DELETE) |'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('client/dashboard/me/billing-purchases/CLAUDE.md')
    assert 'client/dashboard/me/billing-purchases/CLAUDE.md' in text, "expected to find: " + 'client/dashboard/me/billing-purchases/CLAUDE.md'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('client/me/purchases/AGENTS.md')
    assert '9. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never query' in text, "expected to find: " + '9. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never query'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('client/me/purchases/AGENTS.md')
    assert '├── remove-purchase/                # Remove flow (expired items, DELETE API) — separate from cancel' in text, "expected to find: " + '├── remove-purchase/                # Remove flow (expired items, DELETE API) — separate from cancel'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('client/me/purchases/AGENTS.md')
    assert '├── purchases-list-in-dataviews/    # Modern DataViews list (retrofitted into Redux architecture)' in text, "expected to find: " + '├── purchases-list-in-dataviews/    # Modern DataViews list (retrofitted into Redux architecture)'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('client/me/purchases/CLAUDE.md')
    assert 'client/me/purchases/CLAUDE.md' in text, "expected to find: " + 'client/me/purchases/CLAUDE.md'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('client/my-sites/checkout/AGENTS.md')
    assert '10. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never quer' in text, "expected to find: " + '10. **Siteless purchases** — Some products (Akismet, Jetpack, Marketplace) use temporary sites (`siteless.{jetpack|akismet|marketplace.wp|a4a}.com`). Guard with `isTemporarySitePurchase()`. Never quer'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('client/my-sites/checkout/AGENTS.md')
    assert '1. **Payment method component** — `src/payment-methods/{name}.tsx`, export `create{Name}PaymentMethod()` returning a `PaymentMethod` object (`{ id, paymentProcessorId, label, activeContent, submitButt' in text, "expected to find: " + '1. **Payment method component** — `src/payment-methods/{name}.tsx`, export `create{Name}PaymentMethod()` returning a `PaymentMethod` object (`{ id, paymentProcessorId, label, activeContent, submitButt'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('client/my-sites/checkout/AGENTS.md')
    assert "6. **Slug mapping** — Add bidirectional mapping in `packages/wpcom-checkout/src/translate-payment-method-names.ts` (e.g., `'pix'` ↔ `'WPCOM_Billing_Ebanx_Redirect_Brazil_Pix'`)" in text, "expected to find: " + "6. **Slug mapping** — Add bidirectional mapping in `packages/wpcom-checkout/src/translate-payment-method-names.ts` (e.g., `'pix'` ↔ `'WPCOM_Billing_Ebanx_Redirect_Brazil_Pix'`)"[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('client/my-sites/checkout/CLAUDE.md')
    assert 'client/my-sites/checkout/CLAUDE.md' in text, "expected to find: " + 'client/my-sites/checkout/CLAUDE.md'[:80]

