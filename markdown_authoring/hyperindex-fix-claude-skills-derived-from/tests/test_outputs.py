"""Behavioral checks for hyperindex-fix-claude-skills-derived-from (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/hyperindex")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md')
    assert '**Entity relationships** — schema uses entity references; handlers use the `_id` suffix that codegen adds:' in text, "expected to find: " + '**Entity relationships** — schema uses entity references; handlers use the `_id` suffix that codegen adds:'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md')
    assert '// WRONG:  { collection_id: String! } in schema  ← _id belongs in handlers, not schema' in text, "expected to find: " + '// WRONG:  { collection_id: String! } in schema  ← _id belongs in handlers, not schema'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/.claude/skills/indexing-handler-syntax/SKILL.md')
    assert '// Handler:  { token0_id: token0.id }  ← codegen adds _id; NEVER write "token0" here' in text, "expected to find: " + '// Handler:  { token0_id: token0.id }  ← codegen adds _id; NEVER write "token0" here'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md')
    assert '- **Never write `pool_id: String!` in the schema when using `@derivedFrom(field: "pool")`.** The schema field must be `pool: Pool!`; the `_id` is a codegen artifact for handlers only' in text, "expected to find: " + '- **Never write `pool_id: String!` in the schema when using `@derivedFrom(field: "pool")`.** The schema field must be `pool: Pool!`; the `_id` is a codegen artifact for handlers only'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md')
    assert '- In TypeScript handlers, set this relationship using the `_id` suffix: `pool_id: poolEntity.id` — codegen transforms `pool: Pool!` → `pool_id` in the TypeScript type' in text, "expected to find: " + '- In TypeScript handlers, set this relationship using the `_id` suffix: `pool_id: poolEntity.id` — codegen transforms `pool: Pool!` → `pool_id` in the TypeScript type'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/.claude/skills/indexing-schema/SKILL.md')
    assert '- The `field` argument must match the **schema field name** on the child entity — which is the entity reference name (`"pool"`), **not** `"pool_id"`' in text, "expected to find: " + '- The `field` argument must match the **schema field name** on the child entity — which is the entity reference name (`"pool"`), **not** `"pool_id"`'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/AGENTS.md')
    assert '- **Entity references in schema, `_id` in handlers** — Schema uses `collection: NftCollection!` (entity reference, no `_id`). Handlers use `collection_id: value` (codegen adds `_id`). `@derivedFrom(fi' in text, "expected to find: " + '- **Entity references in schema, `_id` in handlers** — Schema uses `collection: NftCollection!` (entity reference, no `_id`). Handlers use `collection_id: value` (codegen adds `_id`). `@derivedFrom(fi'[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('packages/cli/templates/static/shared/CLAUDE.md')
    assert '- Schema uses entity references (`collection: NftCollection!`); handlers use `_id` suffix (`collection_id: value`); never add `_id` to schema field names' in text, "expected to find: " + '- Schema uses entity references (`collection: NftCollection!`); handlers use `_id` suffix (`collection_id: value`); never add `_id` to schema field names'[:80]

