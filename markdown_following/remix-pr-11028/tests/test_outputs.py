import subprocess
import os
import textwrap

REPO = '/workspace/remix'

def _run_ts(script: str) -> subprocess.CompletedProcess:
    """Write a temp .ts file and run it with tsx inside the repo."""
    path = '/tmp/_harbor_test.ts'
    with open(path, 'w') as f:
        f.write(script)
    env = os.environ.copy()
    return subprocess.run(
        ['npx', 'tsx', path],
        capture_output=True, text=True, timeout=60,
        cwd=REPO, env=env,
    )


def test_route_pattern_match_has_params_meta():
    """RoutePattern.match() returns paramsMeta on the result (fail_to_pass)."""
    script = textwrap.dedent('''\
    import { RoutePattern } from "@remix-run/route-pattern"

    let pattern = new RoutePattern("/users/:id")
    let result = pattern.match("https://example.com/users/123")
    if (!result) throw new Error("no match")

    // paramsMeta must exist with hostname and pathname
    if (!("paramsMeta" in result)) throw new Error("result.paramsMeta is missing")
    if (!result.paramsMeta.hostname) throw new Error("result.paramsMeta.hostname is missing")
    if (!result.paramsMeta.pathname) throw new Error("result.paramsMeta.pathname is missing")

    // Verify pathname contains the matched param
    let pathnameEntries = result.paramsMeta.pathname
    if (pathnameEntries.length !== 1) throw new Error("expected 1 pathname entry, got " + pathnameEntries.length)
    let entry = pathnameEntries[0]
    if (entry.name !== "id") throw new Error("expected param name 'id', got '" + entry.name + "'")
    if (entry.value !== "123") throw new Error("expected param value '123', got '" + entry.value + "'")

    console.log("OK")
    ''')
    r = _run_ts(script)
    assert r.returncode == 0, f"RoutePattern.paramsMeta test failed:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"


def test_trie_matcher_match_has_params_meta():
    """TrieMatcher.match() returns paramsMeta on the result (fail_to_pass)."""
    script = textwrap.dedent('''\
    import { TrieMatcher, RoutePattern } from "@remix-run/route-pattern"

    let matcher = new TrieMatcher<string>()
    matcher.add(new RoutePattern("/users/:id"), "user-data")
    let result = matcher.match("https://example.com/users/123")

    if (!result) throw new Error("no match")
    if (!("paramsMeta" in result)) throw new Error("result.paramsMeta is missing")
    if (!result.paramsMeta.hostname) throw new Error("result.paramsMeta.hostname is missing")
    if (!result.paramsMeta.pathname) throw new Error("result.paramsMeta.pathname is missing")

    // Verify pathname contains the matched param
    let pathnameEntries = result.paramsMeta.pathname
    if (pathnameEntries.length !== 1) throw new Error("expected 1 pathname entry, got " + pathnameEntries.length)
    let entry = pathnameEntries[0]
    if (entry.name !== "id") throw new Error("expected param name 'id', got '" + entry.name + "'")
    if (entry.value !== "123") throw new Error("expected param value '123', got '" + entry.value + "'")

    console.log("OK")
    ''')
    r = _run_ts(script)
    assert r.returncode == 0, f"TrieMatcher.paramsMeta test failed:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"


def test_specificity_compare_uses_params_meta():
    """compare() from specificity.ts accesses paramsMeta on match objects (fail_to_pass)."""
    script = textwrap.dedent('''\
    import { compare } from "@remix-run/route-pattern/specificity"

    // Build a minimal mock that has paramsMeta but NOT meta.
    // compare() reads .paramsMeta internally, so if the implementation
    // still uses the old property name this will throw TypeError.
    // compare() also accesses .pattern.ast.search and .url.hostname,
    // so those must be present too.
    let mockPattern: any = { ast: { search: new Map() } }

    let mock: any = {
      pattern: mockPattern,
      url: new URL("https://example.com/b"),
      params: {},
      paramsMeta: { hostname: [], pathname: [] },
    }

    let result = compare(mock, mock)
    if (result !== 0) throw new Error("compare should return 0 for equal matches, got " + result)

    // Also test with non-empty metadata to exercise the full comparison path.
    // Same URL so compare() proceeds past the URL equality guard,
    // but different pattern objects so it enters hostname/pathname comparison.
    let pathnameDataA = [{ name: "id", type: ":", value: "1", begin: 7, end: 8 }]
    let pathnameDataB = [{ name: "id", type: ":", value: "2", begin: 7, end: 8 }]

    let mockA: any = {
      pattern: { ast: { search: new Map() } },
      url: new URL("https://example.com/posts"),
      params: {},
      paramsMeta: { hostname: [], pathname: pathnameDataA },
    }
    let mockB: any = {
      pattern: { ast: { search: new Map() } },  // different object
      url: new URL("https://example.com/posts"),
      params: {},
      paramsMeta: { hostname: [], pathname: pathnameDataB },
    }

    // compare() should run hostname + pathname comparison without throwing
    let resultAB = compare(mockA, mockB)
    console.log("OK compare result:", resultAB)
    ''')
    r = _run_ts(script)
    assert r.returncode == 0, f"Specificity.compare test failed:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}"


def test_repo_tests_pass():
    """Existing route-pattern test suite passes (pass_to_pass)."""
    r = subprocess.run(
        ['pnpm', '--filter', '@remix-run/route-pattern', 'run', 'test'],
        capture_output=True, text=True, timeout=120,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Repo tests failed:\nSTDERR: {r.stderr[-800:]}\nSTDOUT: {r.stdout[-500:]}"

# === CI-mined tests (taskforge.ci_check_miner) ===
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

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")