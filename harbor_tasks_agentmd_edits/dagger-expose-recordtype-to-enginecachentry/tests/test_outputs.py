"""
Task: dagger-expose-recordtype-to-enginecachentry
Repo: dagger/dagger @ 267017813dfa4a570c29b516288eef01b6fcf100
PR:   #11899

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/dagger"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------


def test_record_type_field_in_struct():
    """EngineCacheEntry struct must have a RecordType string field with proper tags."""
    src = Path(f"{REPO}/core/engine.go").read_text()

    # Find the EngineCacheEntry struct block
    match = re.search(
        r"type\s+EngineCacheEntry\s+struct\s*\{(.*?)\}",
        src,
        re.DOTALL,
    )
    assert match, "EngineCacheEntry struct not found in core/engine.go"
    struct_body = match.group(1)

    # Must have RecordType field of type string
    assert re.search(r"\bRecordType\s+string\b", struct_body), (
        "EngineCacheEntry must have a RecordType field of type string"
    )

    # Must have field:"true" tag to expose via GraphQL
    record_type_line = [
        line for line in struct_body.splitlines()
        if "RecordType" in line
    ]
    assert record_type_line, "RecordType field line not found"
    line = record_type_line[0]
    assert 'field:"true"' in line, (
        'RecordType field must have `field:"true"` struct tag'
    )
    assert "doc:" in line, (
        "RecordType field must have a doc struct tag"
    )


def test_gc_populates_record_type():
    """engine/server/gc.go must populate RecordType from the cache record."""
    src = Path(f"{REPO}/engine/server/gc.go").read_text()

    # The field must be assigned in the struct literal
    assert re.search(r"RecordType:\s+.*[Rr]ecord[Tt]ype", src), (
        "gc.go must assign RecordType from the record's RecordType field"
    )



    # Find the EngineCacheEntry type block
    match = re.search(
        r"type\s+EngineCacheEntry\s*\{(.*?)\}",
        schema,
        re.DOTALL,
    )
    assert match, "EngineCacheEntry type not found in schema.graphqls"
    type_body = match.group(1)

    # Must have recordType field of type String
    assert re.search(r"\brecordType\b.*String", type_body), (
        "EngineCacheEntry must have a recordType: String field in GraphQL schema"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CONTRIBUTING.md update tests
# ---------------------------------------------------------------------------



    # The playground section should reference engine-dev
    assert "engine-dev" in content and "playground" in content, (
        "CONTRIBUTING.md must reference 'engine-dev' for the playground command"
    )
    # Old command pattern should not be present
    assert "dagger call playground terminal" not in content, (
        "CONTRIBUTING.md should not have the old 'dagger call playground terminal' command"
    )



    # Old test commands should not be present
    assert "`dagger call test all`" not in content, (
        "CONTRIBUTING.md should not reference old 'dagger call test all' command"
    )
    assert "`dagger call test list`" not in content, (
        "CONTRIBUTING.md should not reference old 'dagger call test list' command"
    )
    assert "`dagger call test-sdks`" not in content, (
        "CONTRIBUTING.md should not reference old 'dagger call test-sdks' command"
    )

    # Updated commands should reference engine-dev for specific tests
    assert "engine-dev" in content and "test" in content, (
        "CONTRIBUTING.md must use 'engine-dev' for test commands"
    )



    # Old generate command should not be present
    assert "`dagger call generate`" not in content, (
        "CONTRIBUTING.md should not reference old 'dagger call generate' command"
    )

    # Old lint command should not be present
    assert "`dagger call lint`" not in content, (
        "CONTRIBUTING.md should not reference old 'dagger call lint' command"
    )
