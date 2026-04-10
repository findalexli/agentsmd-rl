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


# [repo_tests] pass_to_pass - validates key config files are valid JSON
def test_package_json_valid():
    """Root package.json is valid JSON (pass_to_pass)."""
    pkg_file = REPO / "package.json"
    data = json.loads(pkg_file.read_text())
    assert "name" in data, "package.json must have a name field"
    assert "workspaces" in data, "package.json must define workspaces"


# [repo_tests] pass_to_pass - validates Prettier formatting on key files
def test_prettier_formatting_configs():
    """Key config files follow Prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "tsconfig.json", "package.json"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates tsconfig paths are valid
def test_tsconfig_paths_valid():
    """Root tsconfig.json paths resolve to existing files (pass_to_pass)."""
    tsconfig = REPO / "tsconfig.json"
    data = json.loads(tsconfig.read_text())

    paths = data.get("compilerOptions", {}).get("paths", {})
    for alias, targets in paths.items():
        for target in targets:
            target_path = REPO / target
            assert target_path.exists() or target_path.parent.exists(), \
                f"tsconfig path alias '{alias}' -> '{target}' does not resolve to existing file/dir"


# [repo_tests] pass_to_pass - validates repo structure integrity
def test_packages_directory_structure():
    """Packages directory structure is intact (pass_to_pass)."""
    packages_dir = REPO / "packages"
    assert packages_dir.exists(), "packages/ directory must exist"

    # Check core packages exist
    core_packages = ["next"]
    for pkg in core_packages:
        pkg_path = packages_dir / pkg
        assert pkg_path.exists(), f"Core package '{pkg}' must exist"
        assert (pkg_path / "package.json").exists(), f"{pkg}/package.json must exist"


# [repo_tests] pass_to_pass - validates test infrastructure
def test_test_lib_structure():
    """Test library infrastructure is intact (pass_to_pass)."""
    test_lib = REPO / "test" / "lib"
    assert test_lib.exists(), "test/lib directory must exist"

    # Check core test utility files exist
    key_files = ["next-test-utils.ts", "next-webdriver.ts"]
    for f in key_files:
        assert (test_lib / f).exists(), f"test/lib/{f} must exist"

    # Check e2e-utils directory exists with its index.ts
    e2e_utils = test_lib / "e2e-utils"
    assert e2e_utils.exists(), "test/lib/e2e-utils directory must exist"
    assert (e2e_utils / "index.ts").exists(), "test/lib/e2e-utils/index.ts must exist"


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
def test_playwright_package_json_valid():
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


# [repo_tests] pass_to_pass - validates e2e test for instant navigation exists at base commit
def test_instant_navigation_test_file_exists():
    """Instant navigation test file exists at base commit (pass_to_pass)."""
    test_file = REPO / "test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts"
    assert test_file.exists(), "instant-navigation-testing-api.test.ts must exist at base commit"


# [repo_tests] pass_to_pass - validates core next package exists
def test_next_package_structure():
    """Core next package structure is intact (pass_to_pass)."""
    next_pkg = REPO / "packages/next"
    assert next_pkg.exists(), "packages/next must exist"
    assert (next_pkg / "package.json").exists(), "packages/next/package.json must exist"

    # Check src directory exists (dist is built, not present at base commit)
    assert (next_pkg / "src").exists(), "packages/next/src must exist"


# [repo_tests] pass_to_pass - validates all root config files are valid JSON/YAML
def test_root_config_files_valid():
    """Root configuration files are valid and parseable (pass_to_pass)."""
    # JSON files should be valid
    json_files = ["package.json", "tsconfig.json"]
    for f in json_files:
        path = REPO / f
        if path.exists():
            content = path.read_text()
            data = json.loads(content)
            assert data is not None, f"{f} must contain valid JSON"


# [repo_tests] pass_to_pass - validates Prettier formatting on workflow files
def test_prettier_formatting_workflows():
    """GitHub workflow files follow Prettier formatting (pass_to_pass)."""
    workflows_dir = REPO / ".github/workflows"
    if workflows_dir.exists():
        # Check formatting on a subset of workflow files
        workflow_files = list(workflows_dir.glob("*.yml"))[:3]
        if workflow_files:
            r = subprocess.run(
                ["npx", "prettier", "--check"] + [str(f.relative_to(REPO)) for f in workflow_files],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO,
            )
            assert r.returncode == 0, f"Prettier check failed on workflow files:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates Cargo.toml is valid TOML
def test_cargo_toml_valid():
    """Cargo.toml is valid and parseable (pass_to_pass)."""
    cargo_toml = REPO / "Cargo.toml"
    if cargo_toml.exists():
        content = cargo_toml.read_text()
        # Basic TOML validation - check for required sections
        assert "[workspace]" in content, "Cargo.toml must have [workspace] section"
        assert "members" in content, "Cargo.toml must have members in workspace"


# [repo_tests] pass_to_pass - validates test directory structure
def test_e2e_directory_structure():
    """E2E test directory structure is intact (pass_to_pass)."""
    e2e_dir = REPO / "test/e2e"
    assert e2e_dir.exists(), "test/e2e directory must exist"

    app_dir = e2e_dir / "app-dir"
    assert app_dir.exists(), "test/e2e/app-dir directory must exist"

    # Check the instant-navigation-testing-api directory exists
    instant_test_dir = app_dir / "instant-navigation-testing-api"
    assert instant_test_dir.exists(), "instant-navigation-testing-api directory must exist"
    assert (instant_test_dir / "app").exists(), "instant-navigation-testing-api/app directory must exist"
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


# [repo_tests] pass_to_pass - validates key config files are valid JSON
def test_package_json_valid():
    """Root package.json is valid JSON (pass_to_pass)."""
    pkg_file = REPO / "package.json"
    data = json.loads(pkg_file.read_text())
    assert "name" in data, "package.json must have a name field"
    assert "workspaces" in data, "package.json must define workspaces"


# [repo_tests] pass_to_pass - validates Prettier formatting on key files
def test_prettier_formatting_configs():
    """Key config files follow Prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "tsconfig.json", "package.json"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates tsconfig paths are valid
def test_tsconfig_paths_valid():
    """Root tsconfig.json paths resolve to existing files (pass_to_pass)."""
    tsconfig = REPO / "tsconfig.json"
    data = json.loads(tsconfig.read_text())

    paths = data.get("compilerOptions", {}).get("paths", {})
    for alias, targets in paths.items():
        for target in targets:
            target_path = REPO / target
            assert target_path.exists() or target_path.parent.exists(), \
                f"tsconfig path alias '{alias}' -> '{target}' does not resolve to existing file/dir"


# [repo_tests] pass_to_pass - validates repo structure integrity
def test_packages_directory_structure():
    """Packages directory structure is intact (pass_to_pass)."""
    packages_dir = REPO / "packages"
    assert packages_dir.exists(), "packages/ directory must exist"

    # Check core packages exist
    core_packages = ["next"]
    for pkg in core_packages:
        pkg_path = packages_dir / pkg
        assert pkg_path.exists(), f"Core package '{pkg}' must exist"
        assert (pkg_path / "package.json").exists(), f"{pkg}/package.json must exist"


# [repo_tests] pass_to_pass - validates test infrastructure
def test_test_lib_structure():
    """Test library infrastructure is intact (pass_to_pass)."""
    test_lib = REPO / "test" / "lib"
    assert test_lib.exists(), "test/lib directory must exist"

    # Check core test utility files exist
    key_files = ["next-test-utils.ts", "next-webdriver.ts"]
    for f in key_files:
        assert (test_lib / f).exists(), f"test/lib/{f} must exist"

    # Check e2e-utils directory exists with its index.ts
    e2e_utils = test_lib / "e2e-utils"
    assert e2e_utils.exists(), "test/lib/e2e-utils directory must exist"
    assert (e2e_utils / "index.ts").exists(), "test/lib/e2e-utils/index.ts must exist"


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
def test_playwright_package_json_valid():
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


# [repo_tests] pass_to_pass - validates e2e test for instant navigation exists at base commit
def test_instant_navigation_test_file_exists():
    """Instant navigation test file exists at base commit (pass_to_pass)."""
    test_file = REPO / "test/e2e/app-dir/instant-navigation-testing-api/instant-navigation-testing-api.test.ts"
    assert test_file.exists(), "instant-navigation-testing-api.test.ts must exist at base commit"


# [repo_tests] pass_to_pass - validates core next package exists
def test_next_package_structure():
    """Core next package structure is intact (pass_to_pass)."""
    next_pkg = REPO / "packages/next"
    assert next_pkg.exists(), "packages/next must exist"
    assert (next_pkg / "package.json").exists(), "packages/next/package.json must exist"

    # Check src directory exists (dist is built, not present at base commit)
    assert (next_pkg / "src").exists(), "packages/next/src must exist"


# [repo_tests] pass_to_pass - validates all root config files are valid JSON/YAML
def test_root_config_files_valid():
    """Root configuration files are valid and parseable (pass_to_pass)."""
    # JSON files should be valid
    json_files = ["package.json", "tsconfig.json"]
    for f in json_files:
        path = REPO / f
        if path.exists():
            content = path.read_text()
            data = json.loads(content)
            assert data is not None, f"{f} must contain valid JSON"


# [repo_tests] pass_to_pass - validates Prettier formatting on workflow files
def test_prettier_formatting_workflows():
    """GitHub workflow files follow Prettier formatting (pass_to_pass)."""
    workflows_dir = REPO / ".github/workflows"
    if workflows_dir.exists():
        # Check formatting on a subset of workflow files
        workflow_files = list(workflows_dir.glob("*.yml"))[:3]
        if workflow_files:
            r = subprocess.run(
                ["npx", "prettier", "--check"] + [str(f.relative_to(REPO)) for f in workflow_files],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=REPO,
            )
            assert r.returncode == 0, f"Prettier check failed on workflow files:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates Cargo.toml is valid TOML
def test_cargo_toml_valid():
    """Cargo.toml is valid and parseable (pass_to_pass)."""
    cargo_toml = REPO / "Cargo.toml"
    if cargo_toml.exists():
        content = cargo_toml.read_text()
        # Basic TOML validation - check for required sections
        assert "[workspace]" in content, "Cargo.toml must have [workspace] section"
        assert "members" in content, "Cargo.toml must have members in workspace"


# [repo_tests] pass_to_pass - validates test directory structure
def test_e2e_directory_structure():
    """E2E test directory structure is intact (pass_to_pass)."""
    e2e_dir = REPO / "test/e2e"
    assert e2e_dir.exists(), "test/e2e directory must exist"

    app_dir = e2e_dir / "app-dir"
    assert app_dir.exists(), "test/e2e/app-dir directory must exist"

    # Check the instant-navigation-testing-api directory exists
    instant_test_dir = app_dir / "instant-navigation-testing-api"
    assert instant_test_dir.exists(), "instant-navigation-testing-api directory must exist"
    assert (instant_test_dir / "app").exists(), "instant-navigation-testing-api/app directory must exist"



# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) - actual CI commands from the repo
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass - runs check-error-codes script via node
def test_repo_check_error_codes():
    """Error codes check passes (pass_to_pass)."""
    r = subprocess.run(
        ["node", "packages/next/check-error-codes.js"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"check-error-codes failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - runs alex lint on markdown files
def test_repo_alex_lint():
    """Alex linting passes on contributing guide (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "alex", "contributing.md"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Alex lint failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates tsconfig.json structure via node
def test_repo_tsconfig_typescript_parse():
    """tsconfig.json has required structure via Node validation (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e",
         "const cfg = require('./tsconfig.json'); " +
         "if (!cfg.compilerOptions) { " +
         "  console.error('Missing compilerOptions'); process.exit(1); " +
         "} " +
         "if (!cfg.include || cfg.include.length === 0) { " +
         "  console.error('Missing include'); process.exit(1); " +
         "} " +
         "console.log('tsconfig.json validated successfully');"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"tsconfig.json validation failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates GitHub workflows follow Prettier formatting
def test_repo_workflow_prettier():
    """GitHub workflow files follow Prettier formatting (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", ".github/workflows/build_and_test.yml"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Workflow prettier check failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass - validates package.json scripts section exists
def test_repo_package_json_scripts():
    """package.json has required scripts section (pass_to_pass)."""
    r = subprocess.run(
        ["node", "-e",
         "const pkg = require('./package.json'); " +
         "if (!pkg.scripts || !pkg.scripts['test-unit']) { " +
         "  console.error('Missing test-unit script'); process.exit(1); " +
         "} " +
         "if (!pkg.scripts['lint-typescript']) { " +
         "  console.error('Missing lint-typescript script'); process.exit(1); " +
         "} " +
         "console.log('package.json scripts validated');"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"package.json scripts check failed:\n{r.stderr[-500:]}"
