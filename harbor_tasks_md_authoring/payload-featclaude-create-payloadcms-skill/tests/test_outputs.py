"""Behavioral checks for payload-featclaude-create-payloadcms-skill (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/payload")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/SKILL.md')
    assert 'description: Use when working with Payload CMS projects, payload.config.ts, collections, fields, hooks, access control, or Payload API. Provides TypeScript patterns and examples for Payload 3.x develo' in text, "expected to find: " + 'description: Use when working with Payload CMS projects, payload.config.ts, collections, fields, hooks, access control, or Payload API. Provides TypeScript patterns and examples for Payload 3.x develo'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/SKILL.md')
    assert '| Task                     | Solution                                  | Details                                                                                                                        ' in text, "expected to find: " + '| Task                     | Solution                                  | Details                                                                                                                        '[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/SKILL.md')
    assert '| Auto-generate slugs      | `slugField()`                             | [FIELDS.md#slug-field-helper](reference/FIELDS.md#slug-field-helper)                                                           ' in text, "expected to find: " + '| Auto-generate slugs      | `slugField()`                             | [FIELDS.md#slug-field-helper](reference/FIELDS.md#slug-field-helper)                                                           '[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md')
    assert 'Advanced access control patterns including context-aware access, time-based restrictions, factory functions, and production templates.' in text, "expected to find: " + 'Advanced access control patterns including context-aware access, time-based restrictions, factory functions, and production templates.'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md')
    assert '**Note**: Requires your server to pass IP address via headers (common with proxies/load balancers).' in text, "expected to find: " + '**Note**: Requires your server to pass IP address via headers (common with proxies/load balancers).'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ACCESS-CONTROL-ADVANCED.md')
    assert '13. **Handle Errors Gracefully**: Access functions should return `false` on error, not throw' in text, "expected to find: " + '13. **Handle Errors Gracefully**: Access functions should return `false` on error, not throw'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ACCESS-CONTROL.md')
    assert 'For advanced access control patterns including context-aware access, time-based restrictions, subscription-based access, factory functions, configuration templates, debugging tips, and performance opt' in text, "expected to find: " + 'For advanced access control patterns including context-aware access, time-based restrictions, subscription-based access, factory functions, configuration templates, debugging tips, and performance opt'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ACCESS-CONTROL.md')
    assert '1. **Local API Default**: Access control is **skipped by default** in Local API (`overrideAccess: true`). When passing a `user` parameter, you almost always want to set `overrideAccess: false` to resp' in text, "expected to find: " + '1. **Local API Default**: Access control is **skipped by default** in Local API (`overrideAccess: true`). When passing a `user` parameter, you almost always want to set `overrideAccess: false` to resp'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ACCESS-CONTROL.md')
    assert "**Why this matters**: If you pass `user` without `overrideAccess: false`, the operation runs with admin privileges regardless of the user's actual permissions. This is a common security mistake." in text, "expected to find: " + "**Why this matters**: If you pass `user` without `overrideAccess: false`, the operation runs with admin privileges regardless of the user's actual permissions. This is a common security mistake."[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ADAPTERS.md')
    assert '**Critical**: When performing nested operations in hooks, always pass `req` to maintain transaction context. Failing to do so breaks atomicity and can cause partial updates.' in text, "expected to find: " + '**Critical**: When performing nested operations in hooks, always pass `req` to maintain transaction context. Failing to do so breaks atomicity and can cause partial updates.'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ADAPTERS.md')
    assert 'Payload automatically uses transactions for all-or-nothing database operations. Pass `req` to include operations in the same transaction.' in text, "expected to find: " + 'Payload automatically uses transactions for all-or-nothing database operations. Pass `req` to include operations in the same transaction.'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ADAPTERS.md')
    assert '**Note**: MongoDB requires replicaset for transactions. SQLite requires `transactionOptions: {}` to enable.' in text, "expected to find: " + '**Note**: MongoDB requires replicaset for transactions. SQLite requires `transactionOptions: {}` to enable.'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ADVANCED.md')
    assert '- **[All Commonly-Used Types](https://github.com/payloadcms/payload/blob/main/packages/payload/src/index.ts)** - Check here first for commonly used types and interfaces. All core types are exported fr' in text, "expected to find: " + '- **[All Commonly-Used Types](https://github.com/payloadcms/payload/blob/main/packages/payload/src/index.ts)** - Check here first for commonly used types and interfaces. All core types are exported fr'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ADVANCED.md')
    assert '- **[Lexical Types](https://github.com/payloadcms/payload/blob/main/packages/richtext-lexical/src/exports/server/index.ts)** - Lexical editor configuration' in text, "expected to find: " + '- **[Lexical Types](https://github.com/payloadcms/payload/blob/main/packages/richtext-lexical/src/exports/server/index.ts)** - Lexical editor configuration'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/ADVANCED.md')
    assert '- **[Database Adapter Types](https://github.com/payloadcms/payload/blob/main/packages/payload/src/database/types.ts)** - Base adapter interface' in text, "expected to find: " + '- **[Database Adapter Types](https://github.com/payloadcms/payload/blob/main/packages/payload/src/database/types.ts)** - Base adapter interface'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/COLLECTIONS.md')
    assert 'Payload maintains version history and supports draft/publish workflows.' in text, "expected to find: " + 'Payload maintains version history and supports draft/publish workflows.'[:80]


def test_signal_16():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/COLLECTIONS.md')
    assert 'return `${baseUrl}/api/preview?slug=${slug}&collection=${collection}`' in text, "expected to find: " + 'return `${baseUrl}/api/preview?slug=${slug}&collection=${collection}`'[:80]


def test_signal_17():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/COLLECTIONS.md')
    assert 'draft: true, // Saves as draft, skips required field validation' in text, "expected to find: " + 'draft: true, // Saves as draft, skips required field validation'[:80]


def test_signal_18():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/FIELDS.md')
    assert 'Join fields create reverse relationships, allowing you to access related documents from the "other side" of a relationship.' in text, "expected to find: " + 'Join fields create reverse relationships, allowing you to access related documents from the "other side" of a relationship.'[:80]


def test_signal_19():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/FIELDS.md')
    assert 'Point fields store geographic coordinates with automatic 2dsphere indexing for geospatial queries.' in text, "expected to find: " + 'Point fields store geographic coordinates with automatic 2dsphere indexing for geospatial queries.'[:80]


def test_signal_20():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/FIELDS.md')
    assert 'export const link: LinkType = ({ appearances, disableLabel = false, overrides = {} } = {}) => {' in text, "expected to find: " + 'export const link: LinkType = ({ appearances, disableLabel = false, overrides = {} } = {}) => {'[:80]


def test_signal_21():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/HOOKS.md')
    assert '- Pass `req` to nested operations for transaction safety (see [ADAPTERS.md#threading-req-through-operations](ADAPTERS.md#threading-req-through-operations))' in text, "expected to find: " + '- Pass `req` to nested operations for transaction safety (see [ADAPTERS.md#threading-req-through-operations](ADAPTERS.md#threading-req-through-operations))'[:80]


def test_signal_22():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/HOOKS.md')
    assert 'export const revalidateDelete: CollectionAfterDeleteHook<Page> = ({ doc, req: { context } }) => {' in text, "expected to find: " + 'export const revalidateDelete: CollectionAfterDeleteHook<Page> = ({ doc, req: { context } }) => {'[:80]


def test_signal_23():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/HOOKS.md')
    assert "import type { CollectionAfterChangeHook, CollectionAfterDeleteHook } from 'payload'" in text, "expected to find: " + "import type { CollectionAfterChangeHook, CollectionAfterDeleteHook } from 'payload'"[:80]


def test_signal_24():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/QUERIES.md')
    assert "**Important**: Local API bypasses access control by default (`overrideAccess: true`). When passing a `user` parameter, you must explicitly set `overrideAccess: false` to respect that user's permission" in text, "expected to find: " + "**Important**: Local API bypasses access control by default (`overrideAccess: true`). When passing a `user` parameter, you must explicitly set `overrideAccess: false` to respect that user's permission"[:80]


def test_signal_25():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/QUERIES.md')
    assert 'This is critical for MongoDB replica sets and Postgres. See [ADAPTERS.md#threading-req-through-operations](ADAPTERS.md#threading-req-through-operations) for details.' in text, "expected to find: " + 'This is critical for MongoDB replica sets and Postgres. See [ADAPTERS.md#threading-req-through-operations](ADAPTERS.md#threading-req-through-operations) for details.'[:80]


def test_signal_26():
    """Distinctive line from gold patch must be present."""
    text = _read('.claude/skills/payload-cms/reference/QUERIES.md')
    assert 'When performing operations in hooks or nested operations, pass the `req` parameter to maintain transaction context:' in text, "expected to find: " + 'When performing operations in hooks or nested operations, pass the `req` parameter to maintain transaction context:'[:80]

