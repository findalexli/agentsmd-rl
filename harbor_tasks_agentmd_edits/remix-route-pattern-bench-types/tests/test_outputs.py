"""
Task: remix-route-pattern-bench-types
Repo: remix-run/remix @ 3921f065331f6b28e0c29750f1e757a4e09feebc
PR:   11045

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import json
from pathlib import Path

REPO = "/workspace/remix"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / structure checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Package JSON files must be valid JSON."""
    bench_pkg = Path(REPO) / "packages/route-pattern/bench/package.json"
    rp_pkg = Path(REPO) / "packages/route-pattern/package.json"
    # Both must parse without errors
    json.loads(bench_pkg.read_text())
    json.loads(rp_pkg.read_text())


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_runtime_benchmarks_in_src():
    """Runtime benchmark files must be in bench/src/ subdirectory."""
    src_dir = Path(REPO) / "packages/route-pattern/bench/src"
    assert src_dir.is_dir(), "bench/src/ directory must exist"
    bench_files = list(src_dir.glob("*.bench.ts"))
    assert len(bench_files) >= 4, (
        f"Expected at least 4 .bench.ts files in bench/src/, found {len(bench_files)}: "
        f"{[f.name for f in bench_files]}"
    )
    expected = {"comparison.bench.ts", "href.bench.ts", "pathological.bench.ts", "simple.bench.ts"}
    actual = {f.name for f in bench_files}
    assert expected.issubset(actual), (
        f"Missing benchmark files in bench/src/: {expected - actual}"
    )


# [pr_diff] fail_to_pass
def test_type_benchmarks_exist():
    """Type benchmark files must exist in bench/types/ with @ark/attest imports."""
    types_dir = Path(REPO) / "packages/route-pattern/bench/types"
    assert types_dir.is_dir(), "bench/types/ directory must exist"
    expected_files = ["href.ts", "join.ts", "new.ts", "params.ts"]
    for fname in expected_files:
        fpath = types_dir / fname
        assert fpath.exists(), f"bench/types/{fname} must exist"
        content = fpath.read_text()
        assert "@ark/attest" in content, (
            f"bench/types/{fname} must import from @ark/attest"
        )
        assert "bench(" in content, (
            f"bench/types/{fname} must use bench() from attest"
        )


# [pr_diff] fail_to_pass
def test_type_bench_covers_key_apis():
    """Type benchmarks must cover href, join, params, and constructor APIs."""
    types_dir = Path(REPO) / "packages/route-pattern/bench/types"
    assert types_dir.is_dir(), "bench/types/ directory must exist"
    ts_files = list(types_dir.glob("*.ts"))
    assert len(ts_files) >= 1, "bench/types/ must contain at least one .ts file"
    all_content = ""
    for fpath in ts_files:
        all_content += fpath.read_text()
    # Check key API types are benchmarked
    assert "HrefArgs" in all_content, "Type benchmarks should cover HrefArgs"
    assert "Join" in all_content, "Type benchmarks should cover Join type"
    assert "Params" in all_content, "Type benchmarks should cover Params type"
    assert "RoutePattern" in all_content, "Type benchmarks should cover RoutePattern"


# [pr_diff] fail_to_pass
def test_bench_types_script():
    """bench/package.json must have a bench:types script."""
    pkg = json.loads(
        (Path(REPO) / "packages/route-pattern/bench/package.json").read_text()
    )
    scripts = pkg.get("scripts", {})
    assert "bench:types" in scripts, (
        "bench/package.json must have a 'bench:types' script"
    )


# [pr_diff] fail_to_pass
def test_attest_dependency_moved():
    """@ark/attest must be in bench devDeps, not route-pattern devDeps."""
    bench_pkg = json.loads(
        (Path(REPO) / "packages/route-pattern/bench/package.json").read_text()
    )
    rp_pkg = json.loads(
        (Path(REPO) / "packages/route-pattern/package.json").read_text()
    )
    # Must be in bench devDependencies
    bench_dev = bench_pkg.get("devDependencies", {})
    assert "@ark/attest" in bench_dev, (
        "@ark/attest must be a devDependency of the bench package"
    )
    # Must NOT be in route-pattern devDependencies
    rp_dev = rp_pkg.get("devDependencies", {})
    assert "@ark/attest" not in rp_dev, (
        "@ark/attest must be removed from route-pattern devDependencies"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — AGENTS.md compliance
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass
