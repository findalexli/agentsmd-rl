"""Tests for remix-run/remix#11019: route-pattern href benchmark name."""

import subprocess
from pathlib import Path

REPO = Path("/workspace/remix")


def test_bench_name_is_git_derived():
    """Benchmark name is derived from git branch/commit, not hardcoded 'bench'."""
    bench_file = REPO / "packages" / "route-pattern" / "bench" / "href.bench.ts"
    content = bench_file.read_text()

    # The benchName at module level must be dynamically computed,
    # not a hardcoded 'bench' string literal (the original code)
    bench_name_lines = [
        l for l in content.split("\n")
        if "benchName" in l and "=" in l and not l.strip().startswith("//")
    ]
    for line in bench_name_lines:
        # Strip comments to check the actual code
        code = line.split("//")[0]
        # benchName should call a function, not assign a string literal
        assert (
            "'bench'" not in code
        ), f"benchName should be computed dynamically, got: {line.strip()}"

    # Must import execSync from child_process
    assert "child_process" in content, "Should import from child_process module"
    assert "execSync" in content, "Should use execSync"

    # Must use git rev-parse to obtain branch and commit info
    assert "rev-parse" in content, "Should use git rev-parse commands"

    # Must handle git command failures (try/catch with fallback to 'bench')
    assert "catch" in content, "Should handle git command failures"
    assert (
        "return 'bench'" in content or 'return "bench"' in content
    ), "Should fallback to 'bench' on error"

    # Behavioral: verify git commands work in this repo
    r = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r.returncode == 0, f"git rev-parse --short HEAD failed: {r.stderr}"
    short_sha = r.stdout.strip()
    assert len(short_sha) >= 7, f"Expected >=7 char short commit hash, got: `{short_sha}`"

    r2 = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True, timeout=10, cwd=REPO,
    )
    assert r2.returncode == 0, f"git rev-parse --abbrev-ref HEAD failed: {r2.stderr}"
    branch = r2.stdout.strip()
    assert branch, "Branch name must be non-empty"


def test_benchmark_names_are_git_derived():
    """Running vitest bench produces git-derived names, not literal 'bench'."""
    import re
    vitest_candidates = sorted(
        (REPO / "node_modules" / ".pnpm").glob("vitest@*/node_modules/vitest/vitest.mjs")
    )
    assert vitest_candidates, "vitest.mjs not found in pnpm store"
    vitest_bin = str(vitest_candidates[0])

    r = subprocess.run(
        ["node", vitest_bin, "bench", "--run", "packages/route-pattern/bench/href.bench.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, (
        f"Benchmark failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-500:]}\nstderr: {r.stderr[-500:]}"
    )

    # Parse BENCH Summary section (vitest bench outputs to stdout+stderr)
    combined = r.stdout + r.stderr
    clean = re.sub(r'\x1b\[[0-9;]*m', '', combined)

    lines = clean.split('\n')
    summary_idx = None
    for i, line in enumerate(lines):
        if 'BENCH' in line and 'Summary' in line:
            summary_idx = i
            break

    assert summary_idx is not None, f"Could not find BENCH Summary in output:\n{clean[-1000:]}"

    summary_lines = [l.strip() for l in lines[summary_idx + 1:] if l.strip()]
    route_pattern_lines = [
        l for l in summary_lines if 'route-pattern/bench/href.bench.ts' in l
    ]

    assert route_pattern_lines, (
        f"No route-pattern benchmark lines in summary:\n"
        f"{chr(10).join(summary_lines[:20])}"
    )

    for line in route_pattern_lines:
        bench_name = line.split(' - ')[0].strip()
        assert bench_name != 'bench', (
            f"Benchmark name should be git-derived, got: '{bench_name}'"
        )
        # Verify format: contains parenthesized commit hash (e.g., "main (a2245ea)")
        assert '(' in bench_name and ')' in bench_name, (
            f"Benchmark name should contain parenthesized commit, got: '{bench_name}'"
        )
        m = re.search(r'\(([a-f0-9]+)\)', bench_name)
        assert m, f"Expected parenthesized commit hash in: '{bench_name}'"
        assert len(m.group(1)) >= 7, (
            f"Short commit hash should be >= 7 chars, got: '{m.group(1)}'"
        )


def test_package_typecheck():
    """TypeScript type-check passes for the route-pattern package."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/route-pattern", "run", "typecheck"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_format_check():
    """Prettier formatting check passes."""
    r = subprocess.run(
        ["pnpm", "run", "format:check"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Format check failed:\n{r.stderr[-500:]}"


# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_lint():
    """pass_to_pass | CI job 'check' → step 'Lint'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm lint'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Lint' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_typecheck():
    """pass_to_pass | CI job 'check' → step 'Typecheck'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm typecheck'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Typecheck' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_check_check_change_files():
    """pass_to_pass | CI job 'check' → step 'Check change files'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm changes:validate'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check change files' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")


def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests' (scoped to affected package)"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm --filter @remix-run/route-pattern run test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
