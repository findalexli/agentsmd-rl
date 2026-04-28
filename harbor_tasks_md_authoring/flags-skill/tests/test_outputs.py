"""Behavioral checks for flags-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/flags")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/SKILL.md')
    assert 'The Flags SDK (`flags` npm package) is a feature flags toolkit for Next.js and SvelteKit. It turns each feature flag into a callable function, works with any flag provider via adapters, and keeps page' in text, "expected to find: " + 'The Flags SDK (`flags` npm package) is a feature flags toolkit for Next.js and SvelteKit. It turns each feature flag into a callable function, works with any flag provider via adapters, and keeps page'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/SKILL.md')
    assert '- **[references/providers.md](references/providers.md)**: All provider adapters — Vercel, Edge Config, Statsig, LaunchDarkly, PostHog, GrowthBook, Hypertune, Flagsmith, Reflag, Split, Optimizely, Open' in text, "expected to find: " + '- **[references/providers.md](references/providers.md)**: All provider adapters — Vercel, Edge Config, Statsig, LaunchDarkly, PostHog, GrowthBook, Hypertune, Flagsmith, Reflag, Split, Optimizely, Open'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/SKILL.md')
    assert 'Use precompute to keep pages static while using feature flags. Middleware evaluates flags and encodes results into the URL via rewrite. The page reads precomputed values instead of re-evaluating.' in text, "expected to find: " + 'Use precompute to keep pages static while using feature flags. Middleware evaluates flags and encodes results into the URL via rewrite. The page reads precomputed values instead of re-evaluating.'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/api.md')
    assert 'Creates an App Router route handler for `/.well-known/vercel/flags`. Auto-verifies access and adds version header.' in text, "expected to find: " + 'Creates an App Router route handler for `/.well-known/vercel/flags`. Auto-verifies access and adds version header.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/api.md')
    assert '| Parameter       | Type                                               | Description          |' in text, "expected to find: " + '| Parameter       | Type                                               | Description          |'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/api.md')
    assert '| `options.secret`| `string`                                           | `FLAGS_SECRET`       |' in text, "expected to find: " + '| `options.secret`| `string`                                           | `FLAGS_SECRET`       |'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/nextjs.md')
    assert 'The `hasAuthCookieFlag` checks cookie existence without authenticating. Two shells get prerendered — one for each auth state — served statically with no layout shift.' in text, "expected to find: " + 'The `hasAuthCookieFlag` checks cookie existence without authenticating. Two shells get prerendered — one for each auth state — served statically with no layout shift.'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/nextjs.md')
    assert '`identify` receives normalized `headers` and `cookies` that work across App Router, Pages Router, and Middleware.' in text, "expected to find: " + '`identify` receives normalized `headers` and `cookies` that work across App Router, Pages Router, and Middleware.'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/nextjs.md')
    assert 'Keep pages static while using feature flags. Middleware evaluates flags and encodes results into the URL.' in text, "expected to find: " + 'Keep pages static while using feature flags. Middleware evaluates flags and encodes results into the URL.'[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/providers.md')
    assert "import { createSource, flagFallbacks, vercelFlagDefinitions, type Context, type FlagValues } from './generated/hypertune';" in text, "expected to find: " + "import { createSource, flagFallbacks, vercelFlagDefinitions, type Context, type FlagValues } from './generated/hypertune';"[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/providers.md')
    assert 'Disabled by default (middleware prefetch would cause premature exposures). Enable explicitly:' in text, "expected to find: " + 'Disabled by default (middleware prefetch would cause premature exposures). Enable explicitly:'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/providers.md')
    assert 'Set `GROWTHBOOK_EDGE_CONNECTION_STRING` or `EXPERIMENTATION_CONFIG` (Vercel Marketplace).' in text, "expected to find: " + 'Set `GROWTHBOOK_EDGE_CONNECTION_STRING` or `EXPERIMENTATION_CONFIG` (Vercel Marketplace).'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/sveltekit.md')
    assert 'The `x-visitorId` header ensures the visitor ID is available even on the first request before the cookie is set.' in text, "expected to find: " + 'The `x-visitorId` header ensures the visitor ID is available even on the first request before the cookie is set.'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/sveltekit.md')
    assert '- Middleware has access to cookies and private env vars; `reroute` runs on client and must defer to server' in text, "expected to find: " + '- Middleware has access to cookies and private env vars; `reroute` runs on client and must defer to server'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('skills/flags-sdk/references/sveltekit.md')
    assert 'Extract `identify` as a named function and reuse across flags. Calls are deduped by function identity:' in text, "expected to find: " + 'Extract `identify` as a named function and reuse across flags. Calls are deduped by function identity:'[:80]

