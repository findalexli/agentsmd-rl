#!/usr/bin/env python3
"""
Verifier for TanStack Router PR #7066: preserve scroll position after SSR hash hydration.
"""

import os
import subprocess
import sys

REPO = "/workspace/router"
os.chdir(REPO)

def run_cmd(cmd, timeout=600):
    if isinstance(cmd, list) and any('@tanstack' in str(c) for c in cmd):
        if cmd[0] == 'pnpm' and '--filter' in cmd:
            bash_cmd = ' '.join(cmd)
            r = subprocess.run(['bash', '-c', bash_cmd], capture_output=True, text=True, timeout=timeout, cwd=REPO)
            return r
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO)
    return r

def test_typescript_compiles():
    r = run_cmd(['bash', '-c', 'pnpm --filter @tanstack/router-core run test:types'], timeout=300)
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-1000:]}"
    print("  [PASS] TypeScript compiles")

def test_build_succeeds():
    r = run_cmd(['bash', '-c', 'pnpm --filter @tanstack/router-core run build'], timeout=300)
    assert r.returncode == 0, f"Build failed:\n{r.stderr[-1000:]}"
    print("  [PASS] router-core builds")

def test_unit_tests_pass():
    r = run_cmd(['bash', '-c', 'pnpm --filter @tanstack/router-core run test:unit -- --run'], timeout=300)
    assert r.returncode == 0, f"Unit tests failed:\n{r.stderr[-1000:]}"
    print("  [PASS] router-core unit tests pass")

def test_resolvedlocation_fix_in_source():
    """
    CORE FIX TEST (f2p): In the non-SPA SSR hydration path, resolvedLocation must be
    set to the current location state before the early return.

    Without this fix, later preload/invalidation cycles detect a false location
    change and re-trigger hash scrolling.
    """
    with open("packages/router-core/src/ssr/ssr-client.ts") as f:
        src = f.read()

    # The fix must add resolvedLocation.setState in the non-SPA block
    assert "resolvedLocation.setState" in src, (
        "resolvedLocation.setState not found in ssr-client.ts"
    )

    # Extract the non-SPA block using a simpler approach:
    # Find the block starting with "!hasSsrFalseMatches && !isSpaMode" and
    # ending with the first "return routeChunkPromise" that follows it.
    lines = src.split('\n')
    block_start = -1
    block_end = -1

    for i, line in enumerate(lines):
        if '!hasSsrFalseMatches && !isSpaMode' in line:
            block_start = i
        if block_start >= 0 and 'return routeChunkPromise' in line:
            block_end = i
            break

    assert block_start >= 0 and block_end > block_start, (
        "Could not find non-SPA SSR block ending with return routeChunkPromise"
    )

    block_text = '\n'.join(lines[block_start:block_end + 1])

    assert 'resolvedLocation.setState' in block_text, (
        "Fix missing: resolvedLocation.setState not found in non-SPA SSR block. "
        "Without this, later preload/invalidation cycles re-trigger hash scrolling."
    )
    assert 'later load cycles' in block_text or 'preloads' in block_text or 'invalidations' in block_text, (
        "Fix context comment missing — should explain why resolvedLocation is being set"
    )

    print("  [PASS] resolvedLocation fix is present in non-SPA SSR hydration path")

def test_spa_mode_path_unchanged():
    """SPA mode hydration path must remain intact."""
    with open("packages/router-core/src/ssr/ssr-client.ts") as f:
        src = f.read()

    assert 'if (isSpaMode)' in src, "SPA mode check should be preserved"
    assert 'loadPromise.then' in src, "loadPromise.then should be preserved"

    lines = src.split('\n')
    in_spa_block = False
    brace_count = 0
    found_open_brace = False
    spa_lines = []

    for i, line in enumerate(lines):
        if 'if (isSpaMode)' in line:
            in_spa_block = True
        if in_spa_block:
            spa_lines.append(line)
            if '{' in line:
                found_open_brace = True
                brace_count += line.count('{') - line.count('}')
            if '}' in line:
                brace_count -= line.count('}') - line.count('{')
                if found_open_brace and brace_count <= 0:
                    break

    spa_text = '\n'.join(spa_lines)
    assert 'resolvedLocation.setState' in spa_text, "SPA mode should set resolvedLocation"
    print("  [PASS] SPA mode hydration path is intact")

def test_scroll_restoration_preserved():
    """The fix does not break existing scroll restoration behavior."""
    hash_scroll_path = "packages/router-core/src/hash-scroll.ts"
    assert os.path.exists(hash_scroll_path), "hash-scroll.ts not found"
    with open(hash_scroll_path) as f:
        content = f.read()
    assert 'handleHashScroll' in content
    print("  [PASS] Scroll restoration code is intact")

def test_no_router_load_in_non_spa_block():
    """
    The non-SPA SSR block should NOT call router.load() — all data came from server.
    The only reference to router.load() in the block is in a comment.
    """
    with open("packages/router-core/src/ssr/ssr-client.ts") as f:
        src = f.read()

    lines = src.split('\n')
    block_start = -1
    block_end = -1

    for i, line in enumerate(lines):
        if '!hasSsrFalseMatches && !isSpaMode' in line:
            block_start = i
        if block_start >= 0 and 'return routeChunkPromise' in line:
            block_end = i
            break

    assert block_start >= 0 and block_end > block_start

    block_text = '\n'.join(lines[block_start:block_end + 1])
    code_lines = [l for l in block_text.split('\n') if not l.strip().startswith('//')]
    code_block = '\n'.join(code_lines)

    assert 'router.load()' not in code_block, "router.load() should not be called in non-SPA SSR block"
    print("  [PASS] No router.load() call in non-SPA SSR block (as expected)")

def test_repo_eslint():
    """Repo's linter passes on router-core (pass_to_pass)."""
    r = run_cmd(['bash', '-c', 'CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:test:eslint --skipRemoteCache'], timeout=300)
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-1000:]}"
    print("  [PASS] router-core ESLint passes")

def test_repo_build_check():
    """Router-core package passes build verification (publint/attw) (pass_to_pass)."""
    r = run_cmd(['bash', '-c', 'CI=1 NX_DAEMON=false pnpm nx run @tanstack/router-core:test:build --skipRemoteCache'], timeout=300)
    assert r.returncode == 0, f"Build check failed:\n{r.stderr[-1000:]}"
    print("  [PASS] router-core build check passes")

def test_ssr_client_file_has_no_tabs():
    """SSR client source file uses spaces, not tabs (pass_to_pass)."""
    ssr_client_path = "packages/router-core/src/ssr/ssr-client.ts"
    with open(ssr_client_path) as f:
        content = f.read()
    assert '\t' not in content, "ssr-client.ts contains tab characters"
    print("  [PASS] ssr-client.ts uses spaces, not tabs")

if __name__ == "__main__":
    tests = [
        test_typescript_compiles,
        test_build_succeeds,
        test_unit_tests_pass,
        test_resolvedlocation_fix_in_source,
        test_spa_mode_path_unchanged,
        test_scroll_restoration_preserved,
        test_no_router_load_in_non_spa_block,
        test_repo_eslint,
        test_repo_build_check,
        test_ssr_client_file_has_no_tabs,
    ]

    failed = 0
    for t in tests:
        try:
            print(f"\nRunning: {t.__doc__}")
            t()
        except AssertionError as e:
            print(f"  [FAIL] {e}")
            failed += 1
        except Exception as e:
            print(f"  [ERROR] {e}")
            failed += 1

    print(f"\n{'='*60}")
    print(f"Results: {len(tests) - failed}/{len(tests)} passed")
    reward = 1 if failed == 0 else 0
    print(f"Reward: {reward}")

    try:
        with open("/logs/verifier/reward.txt", "w") as f:
            f.write(str(reward))
    except Exception:
        with open("/tmp/reward.txt", "w") as f:
            f.write(str(reward))

    sys.exit(failed)