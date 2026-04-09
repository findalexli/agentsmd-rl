"""
Task: nextjs-playwright-instant-testing-package
Repo: vercel/next.js @ 0f851c5ecd1872a209595770c5fe8b2b24274715
PR:   90470

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
from pathlib import Path

REPO = Path("/workspace/next.js")


def _run(cmd, **kwargs):
    return subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=60, **kwargs)


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression check
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_tsconfig_valid_json():
    """Root tsconfig.json remains valid JSON."""
    tsconfig = REPO / "tsconfig.json"
    data = json.loads(tsconfig.read_text())
    assert "compilerOptions" in data, "Root tsconfig must have compilerOptions"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_package_typescript_compiles():
    """The @next/playwright package must compile without TypeScript errors."""
    pkg_dir = REPO / "packages/next-playwright"
    index_ts = pkg_dir / "src/index.ts"
    assert index_ts.exists(), "packages/next-playwright/src/index.ts must exist"

    # Create a temp tsconfig that adds DOM lib for document.cookie
    tmp_config = pkg_dir / "tsconfig.check.json"
    tmp_config.write_text(json.dumps({
        "extends": "./tsconfig.json",
        "compilerOptions": {"lib": ["es2019", "dom"]}
    }))
    try:
        r = _run(["tsc", "--noEmit", "-p", "packages/next-playwright/tsconfig.check.json"])
        assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr}\n{r.stdout}"
    finally:
        tmp_config.unlink(missing_ok=True)


# [pr_diff] fail_to_pass
def test_package_exports_instant():
    """Package must export the instant() function with cookie-based protocol."""
    index_ts = REPO / "packages/next-playwright/src/index.ts"
    assert index_ts.exists(), "packages/next-playwright/src/index.ts must exist"
    content = index_ts.read_text()
    assert "export async function instant" in content, \
        "Package must export an async function named 'instant'"
    assert "document.cookie" in content, \
        "instant() must use cookie-based protocol to control navigation"
    assert "max-age=0" in content, \
        "instant() must clear the cookie in the cleanup phase"
    assert "try" in content and "finally" in content, \
        "instant() must use try/finally for guaranteed cleanup"


# [pr_diff] fail_to_pass
def test_package_json_valid():
    """package.json must define @next/playwright with correct configuration."""
    pkg_json = REPO / "packages/next-playwright/package.json"
    assert pkg_json.exists(), "packages/next-playwright/package.json must exist"
    data = json.loads(pkg_json.read_text())
    assert data.get("name") == "@next/playwright", \
        "Package name must be @next/playwright"
    assert data.get("main") == "dist/index.js", \
        "Main entry must point to dist/index.js"
    assert data.get("types") == "dist/index.d.ts", \
        "Types entry must point to dist/index.d.ts"


# [pr_diff] fail_to_pass
def test_test_file_imports_package():
    """The instant navigation test must import instant() from @next/playwright."""
    test_file = REPO / "test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts"
    assert test_file.exists(), "Test file must exist"
    content = test_file.read_text()
    assert "from '@next/playwright'" in content, \
        "Test file must import from the @next/playwright package"
    assert "import { instant }" in content, \
        "Test file must import the instant function"


# [pr_diff] fail_to_pass
def test_inline_implementation_removed():
    """The old inline instant() implementation must be removed from the test file."""
    test_file = REPO / "test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts"
    content = test_file.read_text()
    assert "const INSTANT_COOKIE = 'next-instant-navigation-testing'" not in content, \
        "Inline INSTANT_COOKIE constant should be removed from the test file"


# [pr_diff] fail_to_pass
def test_root_tsconfig_has_alias():
    """Root tsconfig.json must include path alias for @next/playwright."""
    tsconfig = REPO / "tsconfig.json"
    content = tsconfig.read_text()
    assert "@next/playwright" in content, \
        "Root tsconfig must have path alias for @next/playwright"
    assert "next-playwright/src/index.ts" in content, \
        "Path alias must point to the package source file"


# ---------------------------------------------------------------------------
# Config/documentation tests (pr_diff) — README.md content
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_instant_navigation():
    """README.md must document instant() testing helper with key concepts."""
    readme = REPO / "packages/next-playwright/README.md"
    assert readme.exists(), "packages/next-playwright/README.md must exist"
    content = readme.read_text()
    assert "instant" in content.lower(), \
        "README must describe the instant navigation concept"
    assert "cookie" in content.lower(), \
        "README must explain the cookie-based mechanism"
    assert "cache" in content.lower() or "cached" in content.lower(), \
        "README must describe the caching/prefetching behavior"
    assert "Playwright" in content, \
        "README must reference Playwright as the testing framework"


# [pr_diff] fail_to_pass
def test_readme_has_usage_examples():
    """README.md must include TypeScript code examples showing instant() usage."""
    readme = REPO / "packages/next-playwright/README.md"
    content = readme.read_text()
    assert "```ts" in content or "```typescript" in content, \
        "README must include TypeScript code examples"
    assert "await instant" in content, \
        "README must show the instant() usage pattern"
    assert "page.goto" in content or "page.click" in content, \
        "README examples should demonstrate page navigation patterns"


# [pr_diff] fail_to_pass
def test_readme_documents_design():
    """README.md must explain the design and how the cookie protocol works."""
    readme = REPO / "packages/next-playwright/README.md"
    content = readme.read_text()
    assert "next-instant-navigation-testing" in content, \
        "README must document the cookie name used by the protocol"
    assert "design" in content.lower() or "how it works" in content.lower(), \
        "README must have a section explaining the design or mechanism"
