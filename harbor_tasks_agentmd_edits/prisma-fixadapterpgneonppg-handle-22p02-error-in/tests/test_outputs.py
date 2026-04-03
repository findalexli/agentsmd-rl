"""
Task: prisma-fixadapterpgneonppg-handle-22p02-error-in
Repo: prisma/prisma @ 857400baec117a7acd8be8799fa285d146329a33
PR:   28849

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/prisma"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_check():
    """Modified TypeScript files exist and are non-empty."""
    files = [
        "packages/driver-adapter-utils/src/types.ts",
        "packages/adapter-pg/src/errors.ts",
        "packages/adapter-neon/src/errors.ts",
        "packages/adapter-ppg/src/errors.ts",
        "packages/client-engine-runtime/src/user-facing-error.ts",
    ]
    for f in files:
        p = Path(REPO) / f
        assert p.exists(), f"{f} does not exist"
        content = p.read_text()
        assert len(content) > 100, f"{f} is suspiciously small"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_mapped_error_type_includes_invalid_input():
    """MappedError type in driver-adapter-utils must include InvalidInputValue kind."""
    content = (Path(REPO) / "packages/driver-adapter-utils/src/types.ts").read_text()
    assert "InvalidInputValue" in content, \
        "MappedError should include InvalidInputValue kind"
    # Verify it's a proper kind declaration, not just a comment
    assert re.search(r"kind:\s*['\"]InvalidInputValue['\"]", content), \
        "InvalidInputValue should be declared as a kind in the MappedError type"
    # Verify the variant has a message field
    after_kind = content.split("InvalidInputValue")[1]
    block = after_kind[:after_kind.index("}") + 1]
    assert "message" in block, \
        "InvalidInputValue variant should have a message field"


# [pr_diff] fail_to_pass
def test_adapter_pg_maps_22p02():
    """adapter-pg must map PostgreSQL error code 22P02 to InvalidInputValue."""
    content = (Path(REPO) / "packages/adapter-pg/src/errors.ts").read_text()
    assert "22P02" in content, "adapter-pg should handle error code 22P02"
    idx = content.index("22P02")
    after = content[idx:idx + 300]
    assert "InvalidInputValue" in after, \
        "22P02 should map to InvalidInputValue kind"


# [pr_diff] fail_to_pass
def test_adapter_neon_maps_22p02():
    """adapter-neon must map PostgreSQL error code 22P02 to InvalidInputValue."""
    content = (Path(REPO) / "packages/adapter-neon/src/errors.ts").read_text()
    assert "22P02" in content, "adapter-neon should handle error code 22P02"
    idx = content.index("22P02")
    after = content[idx:idx + 300]
    assert "InvalidInputValue" in after, \
        "22P02 should map to InvalidInputValue kind"


# [pr_diff] fail_to_pass
def test_adapter_ppg_maps_22p02():
    """adapter-ppg must map PostgreSQL error code 22P02 to InvalidInputValue."""
    content = (Path(REPO) / "packages/adapter-ppg/src/errors.ts").read_text()
    assert "22P02" in content, "adapter-ppg should handle error code 22P02"
    idx = content.index("22P02")
    after = content[idx:idx + 300]
    assert "InvalidInputValue" in after, \
        "22P02 should map to InvalidInputValue kind"


# [pr_diff] fail_to_pass
def test_runtime_maps_invalid_input_to_p2007():
    """user-facing-error.ts must map InvalidInputValue to Prisma error code P2007."""
    content = (Path(REPO) / "packages/client-engine-runtime/src/user-facing-error.ts").read_text()
    assert "InvalidInputValue" in content, \
        "user-facing-error.ts should handle InvalidInputValue kind"
    assert "P2007" in content, \
        "user-facing-error.ts should map to P2007 error code"
    # Verify they're associated: InvalidInputValue near P2007
    idx = content.index("InvalidInputValue")
    window = content[max(0, idx - 50):idx + 150]
    assert "P2007" in window, \
        "InvalidInputValue and P2007 should be associated in getErrorCode"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — AGENTS.md documentation updates
# ---------------------------------------------------------------------------


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
