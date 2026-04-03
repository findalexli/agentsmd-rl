"""
Task: nextjs-turbo-tasks-readme-rustdoc
Repo: vercel/next.js @ a5f36eb27d68bdf5b7acf3299a8c8083e2329ec9
PR:   91120

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/next.js"
LIB_RS = Path(REPO) / "turbopack" / "crates" / "turbo-tasks" / "src" / "lib.rs"
README = Path(REPO) / "turbopack" / "crates" / "turbo-tasks" / "README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """lib.rs retains valid Rust crate attributes and module declarations."""
    content = LIB_RS.read_text()
    # Must still have feature attributes (basic structural check)
    assert "#![feature(trivial_bounds)]" in content, \
        "lib.rs is missing expected #![feature(trivial_bounds)] attribute"
    # Must still declare the backend module
    assert "pub mod backend;" in content, \
        "lib.rs is missing 'pub mod backend;' declaration"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code changes in lib.rs
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README.md creation with proper content
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — anti-stub and structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_lib_rs_retains_module_structure():
    """lib.rs must still declare its public modules (not gutted by the refactor)."""
    content = LIB_RS.read_text()
    # Key modules that must still be declared
    for mod_name in ["backend", "display", "event", "graph"]:
        assert f"pub mod {mod_name};" in content, \
            f"lib.rs must still declare 'pub mod {mod_name};'"
