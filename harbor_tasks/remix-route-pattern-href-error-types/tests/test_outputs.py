import subprocess

REPO = '/workspace/remix/packages/route-pattern'


def _run_node(script: str) -> subprocess.CompletedProcess:
    r = subprocess.run(
        ['node', '--disable-warning=ExperimentalWarning', '-e', script],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f'Node script failed:\nSTDOUT: {r.stdout}\nSTDERR: {r.stderr}'
    return r


def test_nameless_wildcard_hostname_error_type():
    """Nameless wildcard in hostname throws nameless-wildcard error, not missing-params."""
    script = '''
    import { RoutePattern } from './src/lib/route-pattern.ts'
    import { HrefError } from './src/lib/route-pattern/href.ts'
    let pattern = new RoutePattern('://*.example.com/path')
    try {
        pattern.href()
        process.stdout.write('NO_ERROR')
    } catch (e) {
        if (e instanceof HrefError) {
            process.stdout.write('TYPE:' + e.details.type)
        } else {
            process.stdout.write('OTHER:' + e.message)
        }
    }
    '''
    r = _run_node(script)
    assert 'TYPE:nameless-wildcard' in r.stdout, f'Expected nameless-wildcard, got: {r.stdout}'
    assert 'TYPE:missing-params' not in r.stdout, f'Got wrong error type: {r.stdout}'


def test_nameless_wildcard_pathname_error_type():
    """Nameless wildcard in pathname throws nameless-wildcard error, not missing-params."""
    script = '''
    import { RoutePattern } from './src/lib/route-pattern.ts'
    import { HrefError } from './src/lib/route-pattern/href.ts'
    let pattern = new RoutePattern('/files/*')
    try {
        pattern.href()
        process.stdout.write('NO_ERROR')
    } catch (e) {
        if (e instanceof HrefError) {
            process.stdout.write('TYPE:' + e.details.type)
        } else {
            process.stdout.write('OTHER:' + e.message)
        }
    }
    '''
    r = _run_node(script)
    assert 'TYPE:nameless-wildcard' in r.stdout, f'Expected nameless-wildcard, got: {r.stdout}'
    assert 'TYPE:missing-params' not in r.stdout, f'Got wrong error type: {r.stdout}'


def test_missing_params_error_message_format():
    """Missing-params error message uses colon, quotes param names, omits variant listing."""
    script = '''
    import { RoutePattern } from './src/lib/route-pattern.ts'
    import { HrefError } from './src/lib/route-pattern/href.ts'
    let pattern = new RoutePattern('https://example.com/:id')
    try {
        pattern.href()
        process.stdout.write('NO_ERROR')
    } catch (e) {
        if (e instanceof HrefError) {
            process.stdout.write(e.toString())
        }
    }
    '''
    r = _run_node(script)
    assert "missing param(s):" in r.stdout, (
        f"Expected 'missing param(s):' in error message, got: {r.stdout}"
    )
    assert "'id'" in r.stdout, (
        f"Expected quoted 'id' in error message, got: {r.stdout}"
    )
    assert 'Pathname variants:' not in r.stdout, (
        f"Old variant listing should not appear, got: {r.stdout}"
    )


def test_missing_search_params_error_message_format():
    """Missing search params error uses colon after 'param(s)'."""
    script = '''
    import { RoutePattern } from './src/lib/route-pattern.ts'
    import { HrefError } from './src/lib/route-pattern/href.ts'
    let pattern = new RoutePattern('https://example.com/search?q=')
    let error = new HrefError({
        type: 'missing-search-params',
        pattern,
        missingParams: ['q'],
        searchParams: {},
    })
    process.stdout.write(error.toString())
    '''
    r = _run_node(script)
    assert "missing required search param(s):" in r.stdout, (
        f"Expected 'missing required search param(s):' with colon, got: {r.stdout}"
    )
    assert "'q'" in r.stdout, (
        f"Expected quoted 'q' in error message, got: {r.stdout}"
    )


def test_valid_href_still_works():
    """Valid href() calls with all required params still work correctly."""
    script = '''
    import { RoutePattern } from './src/lib/route-pattern.ts'
    let p1 = new RoutePattern('/posts/:id')
    let r1 = p1.href({ id: '42' })
    process.stdout.write('R1:' + r1)

    let p2 = new RoutePattern('://example.com/path')
    let r2 = p2.href()
    process.stdout.write('|R2:' + r2)

    let p3 = new RoutePattern('://:sub.example.com/path')
    let r3 = p3.href({ sub: 'api' })
    process.stdout.write('|R3:' + r3)
    '''
    r = _run_node(script)
    assert 'R1:/posts/42' in r.stdout
    assert 'R2:https://example.com/path' in r.stdout
    assert 'R3:https://api.example.com/path' in r.stdout


def test_repo_test_suite():
    """Full test suite for route-pattern passes."""
    r = subprocess.run(
        ['node', '--disable-warning=ExperimentalWarning', '--test'],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f'Test suite failed:\nSTDERR: {r.stderr[-1000:]}\nSTDOUT: {r.stdout[-1000:]}'

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_run_tests():
    """pass_to_pass | CI job 'test' → step 'Run tests'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm test'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Run tests' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_build_build_packages():
    """pass_to_pass | CI job 'build' → step 'Build packages'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm build'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Build packages' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_format_format():
    """pass_to_pass | CI job 'format' → step 'Format'"""
    r = subprocess.run(
        ["bash", "-lc", 'pnpm format'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Format' failed (returncode={r.returncode}):\n"
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

# === PR-added f2p tests (taskforge.test_patch_miner) ===
def test_pr_added_throws_for_nameless_wildcard():
    """fail_to_pass | PR added test 'throws for nameless wildcard' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for nameless wildcard" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for nameless wildcard" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for nameless wildcard" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "throws for nameless wildcard" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'throws for nameless wildcard' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_excludes_nameless_wildcard_from_params():
    """fail_to_pass | PR added test 'excludes nameless wildcard from params' in 'packages/route-pattern/src/lib/route-pattern.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "excludes nameless wildcard from params" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern.test.ts" -t "excludes nameless wildcard from params" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "excludes nameless wildcard from params" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern.test.ts" -t "excludes nameless wildcard from params" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'excludes nameless wildcard from params' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_shows_pattern():
    """fail_to_pass | PR added test 'shows pattern' in 'packages/route-pattern/src/lib/route-pattern/href.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows pattern" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows pattern" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows pattern" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows pattern" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'shows pattern' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_pr_added_shows_missing_param_pattern_and_params():
    """fail_to_pass | PR added test 'shows missing param, pattern, and params' in 'packages/route-pattern/src/lib/route-pattern/href.test.ts' (vitest_or_jest)"""
    r = subprocess.run(
        ["bash", "-lc", '(pnpm vitest run "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows missing param, pattern, and params" 2>&1 || npx vitest run "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows missing param, pattern, and params" 2>&1 || pnpm jest "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows missing param, pattern, and params" 2>&1 || npx jest "packages/route-pattern/src/lib/route-pattern/href.test.ts" -t "shows missing param, pattern, and params" 2>&1) | tail -50'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"PR-added test 'shows missing param, pattern, and params' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")
