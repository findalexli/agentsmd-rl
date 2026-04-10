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
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"
PKG = Path(REPO) / "packages" / "next-playwright"
INDEX_TS = PKG / "src" / "index.ts"
PKG_JSON = PKG / "package.json"
README = PKG / "README.md"
ROOT_TSCONFIG = Path(REPO) / "tsconfig.json"


def _strip_json_comments(raw: str) -> str:
    """Strip // comments and trailing commas from JSON (tsconfig style)."""
    stripped = re.sub(r"//.*", "", raw)
    stripped = re.sub(r",\s*([}\]])", r"\1", stripped)
    return stripped


# -----------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# -----------------------------------------------------------------------------

# [static] pass_to_pass
def test_root_tsconfig_valid_json():
    """Root tsconfig.json must remain valid JSON (with comments stripped)."""
    raw = ROOT_TSCONFIG.read_text()
    stripped = _strip_json_comments(raw)
    data = json.loads(stripped)
    assert "compilerOptions" in data, "tsconfig.json must have compilerOptions"


# [static] pass_to_pass - validates monorepo structure (file read only)
def test_repo_package_json_valid():
    """Repo root package.json must be valid and define workspaces (pass_to_pass)."""
    root_pkg_json = Path(REPO) / "package.json"
    assert root_pkg_json.exists(), "Root package.json must exist"
    data = json.loads(root_pkg_json.read_text())
    # Must be a monorepo with workspaces
    assert "workspaces" in data, "Root package.json must define workspaces"
    workspaces = data.get("workspaces", [])
    assert "packages/*" in workspaces, "Workspaces must include packages/*"
    # Must have standard scripts
    scripts = data.get("scripts", {})
    assert "test-types" in scripts, "package.json must have test-types script"
    assert "typescript" in scripts, "package.json must have typescript script"


# [static] pass_to_pass - validates existing packages structure (file read only)
def test_existing_packages_have_valid_structure():
    """Existing packages in monorepo must have valid structure (pass_to_pass)."""
    packages_dir = Path(REPO) / "packages"
    assert packages_dir.exists(), "packages/ directory must exist"
    # Core 'next' package must exist with package.json
    next_pkg_json = packages_dir / "next" / "package.json"
    assert next_pkg_json.exists(), "packages/next/package.json must exist"
    data = json.loads(next_pkg_json.read_text())
    assert data.get("name") == "next", "Core package must be named 'next'"
    # Check that at least the core 'next' package has valid tsconfig
    next_pkg_tsconfig = packages_dir / "next" / "tsconfig.json"
    if next_pkg_tsconfig.exists():
        raw = next_pkg_tsconfig.read_text()
        stripped = _strip_json_comments(raw)
        data = json.loads(stripped)
        assert "compilerOptions" in data, "packages/next/tsconfig.json must have compilerOptions"


# [repo_tests] pass_to_pass - runs actual CI command
def test_repo_tsconfig_valid():
    """Repo TypeScript config is valid via tsc --showConfig (pass_to_pass)."""
    r = subprocess.run(
        ["tsc", "--showConfig"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"tsc --showConfig failed:\n{r.stderr}"
    # Verify output contains expected config
    assert "compilerOptions" in r.stdout, "tsc --showConfig output must contain compilerOptions"


# -----------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# -----------------------------------------------------------------------------

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
def test_package_compiles():
    """Package TypeScript compiles without errors (tsc --noEmit)."""
    # This is the key behavioral test: the package must actually compile
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", str(PKG / "tsconfig.json")],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_instant_function_exported():
    """index.ts must export an async function named 'instant' that takes page + callback."""
    assert INDEX_TS.exists(), (
        f"Expected source file at {INDEX_TS.relative_to(REPO)}"
    )
    content = INDEX_TS.read_text()
    # Must export the function (either 'export async function instant' or 'export function instant')
    assert re.search(r"export\s+(async\s+)?function\s+instant", content), (
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
    assert (
        "max-age=0" in content
        or "max-age: 0" in content
        or "expires=" in content.lower()
    ), "instant() must clear the cookie after the callback completes"


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
    assert (
        "cookie" in after_finally or "max-age" in after_finally or "COOKIE" in after_finally
    ), "The finally block must clear the cookie"


# [pr_diff] fail_to_pass
def test_tsconfig_path_mapping():
    """Root tsconfig.json must map '@next/playwright' to the package source."""
    raw = ROOT_TSCONFIG.read_text()
    stripped = _strip_json_comments(raw)
    data = json.loads(stripped)
    paths = data.get("compilerOptions", {}).get("paths", {})
    assert "@next/playwright" in paths, (
        "Root tsconfig.json must have a path alias for '@next/playwright'"
    )
    targets = paths["@next/playwright"]
    assert any("next-playwright" in t for t in targets), (
        "The @next/playwright path alias must point to the next-playwright package"
    )


# [pr_diff] fail_to_pass
def test_path_mapping_resolves():
    """Path mapping must actually resolve to the package source file."""
    raw = ROOT_TSCONFIG.read_text()
    stripped = _strip_json_comments(raw)
    data = json.loads(stripped)
    paths = data.get("compilerOptions", {}).get("paths", {})
    targets = paths.get("@next/playwright", [])

    for target in targets:
        resolved = Path(REPO) / target.replace(".ts", "").replace("./", "")
        # The path should point somewhere in packages/next-playwright
        assert "next-playwright" in str(resolved), (
            f"Path alias target '{target}' does not point to next-playwright package"
        )


# -----------------------------------------------------------------------------
# Fail-to-pass (agent_config) — README documentation tests
# -----------------------------------------------------------------------------

# [agent_config] fail_to_pass — packages/next-playwright/README.md @ base_commit
def test_readme_documentation():
    """README.md documents the instant() testing helper with usage examples."""
    assert README.exists(), "README.md must exist in the package"
    content = README.read_text()
    # Must mention instant()
    assert "instant" in content.lower(), "README must document the instant() function"
    # Must have code examples
    assert "```ts" in content or "```typescript" in content, (
        "README must include TypeScript code examples"
    )
    # Must mention cookie protocol
    assert "cookie" in content.lower(), (
        "README must explain the cookie-based protocol"
    )


# [agent_config] fail_to_pass — packages/next-playwright/README.md @ base_commit
def test_readme_cookie_protocol_explained():
    """README.md explains the cookie-based protocol so others can replicate it."""
    content = README.read_text()
    # Must explain how it works
    assert "how it works" in content.lower() or "design" in content.lower(), (
        "README must explain how the cookie mechanism works"
    )
    # Must show the cookie name
    assert "next-instant-navigation-testing" in content, (
        "README must document the exact cookie name used by the protocol"
    )
