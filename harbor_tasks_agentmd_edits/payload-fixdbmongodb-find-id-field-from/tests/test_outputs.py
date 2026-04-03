"""
Task: payload-fixdbmongodb-find-id-field-from
Repo: payloadcms/payload @ 5ebda61c74724cf68d2b1b1dc9886dde5f55b0ff
PR:   15110

MongoDB adapter ignores custom ID fields nested inside tabs/groups.
CLAUDE.md needs test cleanup best-practices documented.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/payload"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files must exist and not be empty/truncated."""
    files = [
        "packages/db-mongodb/src/models/buildSchema.ts",
        "packages/db-mongodb/src/models/buildCollectionSchema.ts",
        "packages/payload/src/fields/hooks/afterRead/promise.ts",
        "packages/payload/src/fields/hooks/afterRead/traverseFields.ts",
        "packages/payload/src/fields/hooks/afterRead/index.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} must exist"
        content = p.read_text()
        assert len(content) > 200, f"{f} appears truncated"
        # Basic balance check: braces should be roughly balanced
        assert abs(content.count("{") - content.count("}")) < 5, \
            f"{f} has unbalanced braces — likely a syntax error"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_buildschema_searches_flattened_for_id():
    """buildSchema must use flattenedFields to find custom ID fields nested in tabs/groups."""
    src = (Path(REPO) / "packages/db-mongodb/src/models/buildSchema.ts").read_text()

    # 1. The function must accept a flattenedFields parameter
    assert "flattenedFields" in src, \
        "buildSchema should accept a flattenedFields parameter"

    # 2. flattenedFields must be used in the ID-finding logic, not just declared
    # The fix: `const fieldsToSearch = flattenedFields || schemaFields`
    # then: `fieldsToSearch.find(... field.name === 'id' ...)`
    # We check that flattenedFields appears in the logic that searches for the ID field
    id_search_pattern = re.compile(
        r"flattenedFields.*\bfind\b.*\bid\b"
        r"|"
        r"\bfind\b.*\bid\b.*flattenedFields"
        r"|"
        r"flattenedFields\s*\|\|.*\bfind\b",
        re.DOTALL
    )
    # Look in the section between allowIDField check and _id assignment
    allow_id_idx = src.find("allowIDField")
    id_field_idx = src.find("_id:", allow_id_idx) if allow_id_idx != -1 else -1
    if allow_id_idx != -1 and id_field_idx != -1:
        search_section = src[allow_id_idx:id_field_idx]
        assert "flattenedFields" in search_section, \
            "flattenedFields should be used in the ID field search logic (between allowIDField and _id assignment)"
    else:
        # Fallback: just verify the pattern exists somewhere
        assert id_search_pattern.search(src), \
            "flattenedFields should be connected to the ID field search logic"


# [pr_diff] fail_to_pass
def test_collection_schema_passes_flattened():
    """buildCollectionSchema must pass flattenedFields to buildSchema."""
    src = (Path(REPO) / "packages/db-mongodb/src/models/buildCollectionSchema.ts").read_text()
    assert "flattenedFields" in src, \
        "buildCollectionSchema should pass flattenedFields to the schema builder"
    # Verify it references collection.flattenedFields (the actual data source)
    assert re.search(r"collection\s*\.\s*flattenedFields", src), \
        "Should read flattenedFields from the collection config"


# [pr_diff] fail_to_pass
def test_afterread_preserves_hidden_toplevel_id():
    """afterRead hook must not strip hidden custom ID fields at the top level."""
    src = (Path(REPO) / "packages/payload/src/fields/hooks/afterRead/promise.ts").read_text()

    # 1. Must introduce a concept of field depth
    assert "fieldDepth" in src or "field_depth" in src or "depth" in src.lower(), \
        "promise.ts should track field nesting depth"

    # 2. Must have logic connecting ID fields to depth for the hidden-field check
    # The fix adds: `const isTopLevelIDField = fieldAffectsDataResult && field.name === 'id' && fieldDepth === 0`
    # and uses it in the condition: `!showHiddenFields && !isTopLevelIDField`
    # Check that the hidden-field removal block has an exception for top-level ID
    hidden_section = ""
    lines = src.split("\n")
    for i, line in enumerate(lines):
        if "hidden" in line and "field" in line.lower():
            # Grab surrounding context
            start = max(0, i - 3)
            end = min(len(lines), i + 10)
            hidden_section += "\n".join(lines[start:end])
    assert hidden_section, "Should have hidden field handling logic"

    # The key: the hidden-field deletion must NOT apply to top-level ID fields
    # Look for depth-related guard near the hidden+delete logic
    delete_region_start = src.find("delete siblingDoc")
    if delete_region_start == -1:
        delete_region_start = src.find("delete ")
    assert delete_region_start != -1, "Should have field deletion logic"

    # Find the condition block that gates the deletion
    # Look backwards from delete for the if-block
    pre_delete = src[max(0, delete_region_start - 600):delete_region_start]
    assert ("depth" in pre_delete.lower() or "topLevel" in pre_delete or
            "TopLevel" in pre_delete or "top_level" in pre_delete or
            "isTopLevel" in pre_delete), \
        "Hidden field deletion should be gated by a depth/top-level check to preserve custom IDs"


# [pr_diff] fail_to_pass

    # Also verify the entry point initializes it
    index_src = (Path(REPO) / "packages/payload/src/fields/hooks/afterRead/index.ts").read_text()
    assert "fieldDepth" in index_src or "field_depth" in index_src, \
        "afterRead entry point should initialize fieldDepth"


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — CLAUDE.md update
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass

    # 1. Must mention tests being self-contained or cleaning up
    assert ("clean up" in content_lower or "cleanup" in content_lower or
            "self-contained" in content_lower or "clean after" in content_lower), \
        "CLAUDE.md should document that tests must clean up after themselves"

    # 2. Must mention afterEach or equivalent cleanup pattern
    assert ("aftereach" in content_lower or "after_each" in content_lower or
            "after each" in content_lower), \
        "CLAUDE.md should mention afterEach for test cleanup"

    # 3. Must mention tracking created resources for cleanup
    assert ("created" in content_lower and
            ("id" in content_lower or "resource" in content_lower or "track" in content_lower)), \
        "CLAUDE.md should mention tracking created resources/IDs for cleanup"

    # 4. Must have guidance on test naming or behavior focus
    assert ("descriptive" in content_lower or "should" in content_lower or
            "one test" in content_lower or "focused" in content_lower), \
        "CLAUDE.md should include test naming or focus guidelines"
