"""
Task: next.js-add-nextplaywright-package-with-instant
Repo: vercel/next.js @ 0f851c5ecd1872a209595770c5fe8b2b24274715
PR:   90470

Extract the instant navigation testing API into a standalone @next/playwright
package, and add a README documenting the API, usage examples, and the
cookie-based protocol.

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
import re
from pathlib import Path

REPO = "/workspace/next.js"
PKG = Path(REPO) / "packages" / "next-playwright"
INDEX_TS = PKG / "src" / "index.ts"
PKG_JSON = PKG / "package.json"
README = PKG / "README.md"
ROOT_TSCONFIG = Path(REPO) / "tsconfig.json"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_root_tsconfig_valid_json():
    """Root tsconfig.json must remain valid JSON (with comments stripped)."""
    raw = ROOT_TSCONFIG.read_text()
    # tsconfig allows // comments and trailing commas — strip them
    stripped = re.sub(r'//.*', '', raw)
    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
    data = json.loads(stripped)
    assert "compilerOptions" in data, "tsconfig.json must have compilerOptions"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_package_json_structure():
    """@next/playwright package.json must exist with correct name and dist fields."""
    assert PKG_JSON.exists(), (
        f"Expected package.json at {PKG_JSON.relative_to(REPO)}"
    )
    data = json.loads(PKG_JSON.read_text())
    assert data.get("name") == "@next/playwright", (
        f"package.json name should be '@next/playwright', got '{data.get('name')}'"
    )
    # Must point to compiled output
    main = data.get("main", "")
    types = data.get("types", "")
    assert "dist" in main or "dist" in types, (
        "package.json main or types should reference dist/ directory"
    )


# [pr_diff] fail_to_pass
def test_instant_function_exported():
    """index.ts must export an async function named 'instant' that takes page + callback."""
    assert INDEX_TS.exists(), (
        f"Expected source file at {INDEX_TS.relative_to(REPO)}"
    )
    content = INDEX_TS.read_text()
    # Must export the function (either 'export async function instant' or 'export function instant')
    assert re.search(r'export\s+(async\s+)?function\s+instant', content), (
        "index.ts must export a function named 'instant'"
    )
    # Function must accept a page-like object and a callback
    assert "page" in content.lower() or "Page" in content, (
        "instant() must accept a page parameter"
    )
    # Must be generic or accept a callback function
    assert "=>" in content or "Promise" in content, (
        "instant() must work with async callbacks"
    )


# [pr_diff] fail_to_pass
def test_instant_cookie_protocol():
    """instant() must use the 'next-instant-navigation-testing' cookie to control navigation."""
    content = INDEX_TS.read_text()
    assert "next-instant-navigation-testing" in content, (
        "instant() must use the 'next-instant-navigation-testing' cookie name "
        "to match the Next.js navigation lock protocol"
    )
    # Must set the cookie (document.cookie = ...)
    assert "document.cookie" in content, (
        "instant() must set/clear cookies via document.cookie"
    )
    # Must clear the cookie after callback (max-age=0 or equivalent)
    assert "max-age=0" in content or "max-age: 0" in content or "expires=" in content.lower(), (
        "instant() must clear the cookie after the callback completes"
    )


# [pr_diff] fail_to_pass
def test_instant_cleanup_on_error():
    """instant() must clean up the cookie even if the callback throws (try/finally)."""
    content = INDEX_TS.read_text()
    assert "finally" in content, (
        "instant() must use try/finally to ensure cookie cleanup on error"
    )
    # The finally block should contain the cookie clearing
    finally_idx = content.index("finally")
    after_finally = content[finally_idx:]
    assert "cookie" in after_finally or "max-age" in after_finally or "COOKIE" in after_finally, (
        "The finally block must clear the cookie"
    )


# [pr_diff] fail_to_pass
def test_tsconfig_path_mapping():
    """Root tsconfig.json must map '@next/playwright' to the package source."""
    raw = ROOT_TSCONFIG.read_text()
    stripped = re.sub(r'//.*', '', raw)
    stripped = re.sub(r',\s*([}\]])', r'\1', stripped)
    data = json.loads(stripped)
    paths = data.get("compilerOptions", {}).get("paths", {})
    assert "@next/playwright" in paths, (
        "Root tsconfig.json must have a path alias for '@next/playwright'"
    )
    targets = paths["@next/playwright"]
    assert any("next-playwright" in t for t in targets), (
        "The @next/playwright path alias must point to the next-playwright package"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
