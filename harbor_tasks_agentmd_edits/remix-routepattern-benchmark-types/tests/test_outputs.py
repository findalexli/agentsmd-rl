"""
Task: remix-routepattern-benchmark-types
Repo: remix-run/remix @ 3921f065331f6b28e0c29750f1e757a4e09feebc
PR:   11045

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------


def test_readme_documents_type_benchmarks():
    """bench/README.md must document type benchmarks with ArkType Attest."""
    readme = Path(REPO) / "packages/route-pattern/bench/README.md"
    content = readme.read_text().lower()
    # Must distinguish between runtime and type benchmarks
    assert "type benchmark" in content, \
        "README should have a Type benchmarks section"
    assert "attest" in content, \
        "README should mention ArkType Attest for type benchmarking"


def test_readme_has_run_command_for_types():
    """bench/README.md must document how to run type benchmarks."""
    readme = Path(REPO) / "packages/route-pattern/bench/README.md"
    content = readme.read_text()
    # Must include a command to run type benchmarks
    assert "node" in content.lower() and "types" in content.lower(), \
        "README should show a node command for running type benchmarks"
    # Must mention the types/ directory
    assert "types/" in content, \
        "README should reference the types/ directory"


def test_readme_distinguishes_runtime_benchmarks():
    """bench/README.md must differentiate runtime vs type benchmarks."""
    readme = Path(REPO) / "packages/route-pattern/bench/README.md"
    content = readme.read_text()
    # The heading should now say "Runtime benchmarks", not just "Run benchmarks"
    assert "runtime" in content.lower(), \
        "README should label runtime benchmarks distinctly from type benchmarks"
    # Should reference src/ directory for runtime benchmarks
    assert "src/" in content, \
        "README should reference the src/ directory for runtime benchmarks"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — code tests: type benchmark files
# ---------------------------------------------------------------------------


def test_type_benchmarks_test_href():
    """A type benchmark file must test RoutePattern href and HrefArgs."""
    types_dir = Path(REPO) / "packages/route-pattern/bench/types"
    assert types_dir.is_dir(), "types/ directory must exist"
    # Find a file that tests href functionality
    href_content = ""
    for f in types_dir.glob("*.ts"):
        text = f.read_text()
        if "href" in text.lower() and "attest" in text.lower():
            href_content = text
            break
    assert href_content, "No type benchmark file tests href/HrefArgs"
    assert "RoutePattern" in href_content, \
        "Type benchmark should use RoutePattern class"
    assert "bench(" in href_content, \
        "Type benchmark should use @ark/attest bench() function"
    assert ".types(" in href_content, \
        "Type benchmark should assert type instantiation counts"


def test_type_benchmarks_test_params():
    """A type benchmark file must test RoutePattern params and Params type."""
    types_dir = Path(REPO) / "packages/route-pattern/bench/types"
    assert types_dir.is_dir(), "types/ directory must exist"
    # Find a file that tests params functionality
    params_content = ""
    for f in types_dir.glob("*.ts"):
        text = f.read_text()
        if "params" in text.lower() and "attest" in text.lower():
            params_content = text
            break
    assert params_content, "No type benchmark file tests params/Params"
    assert "match" in params_content, \
        "Params benchmark should test pattern.match() method"
    assert "bench(" in params_content, \
        "Type benchmark should use @ark/attest bench() function"


def test_bench_package_has_types_script():
    """bench/package.json must have a bench:types script."""
    pkg_path = Path(REPO) / "packages/route-pattern/bench/package.json"
    pkg = json.loads(pkg_path.read_text())
    scripts = pkg.get("scripts", {})
    assert "bench:types" in scripts, \
        "bench/package.json must have a bench:types script"


def test_bench_package_has_attest_dep():
    """bench/package.json must have @ark/attest as a devDependency."""
    pkg_path = Path(REPO) / "packages/route-pattern/bench/package.json"
    pkg = json.loads(pkg_path.read_text())
    dev_deps = pkg.get("devDependencies", {})
    assert "@ark/attest" in dev_deps, \
        "bench/package.json must have @ark/attest in devDependencies"


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------


def test_existing_bench_deps_maintained():
    """Existing bench dependencies (vitest, path-to-regexp) still present."""
    pkg_path = Path(REPO) / "packages/route-pattern/bench/package.json"
    pkg = json.loads(pkg_path.read_text())
    deps = pkg.get("dependencies", {})
    dev_deps = pkg.get("devDependencies", {})
    assert "vitest" in dev_deps, "vitest devDependency must be preserved"
    assert "path-to-regexp" in deps, "path-to-regexp dependency must be preserved"
    assert "@remix-run/route-pattern" in deps, \
        "@remix-run/route-pattern dependency must be preserved"


def test_attest_moved_to_bench_subpackage():
    """@ark/attest removed from route-pattern/package.json (moved to bench)."""
    pkg_path = Path(REPO) / "packages/route-pattern/package.json"
    pkg = json.loads(pkg_path.read_text())
    dev_deps = pkg.get("devDependencies", {})
    assert "@ark/attest" not in dev_deps, \
        "@ark/attest should be removed from route-pattern devDependencies (moved to bench)"


def test_route_pattern_package_json_valid():
    """packages/route-pattern/package.json core fields preserved."""
    pkg_path = Path(REPO) / "packages/route-pattern/package.json"
    pkg = json.loads(pkg_path.read_text())
    assert pkg.get("name") == "@remix-run/route-pattern", \
        "Package name must be preserved"
    assert "exports" in pkg, "exports field must be preserved"
