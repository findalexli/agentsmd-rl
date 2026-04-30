import subprocess
import os

REPO = "/workspace/remix"
FETCH_ROUTER = os.path.join(REPO, "packages/fetch-router")
SRC_LIB = os.path.join(FETCH_ROUTER, "src/lib")


def _write_test_file(filename, code):
    """Write a test file into the fetch-router src/lib directory."""
    path = os.path.join(SRC_LIB, filename)
    with open(path, "w") as f:
        f.write(code)
    return path


def _run_node_test(filename, code, timeout=60):
    """Write a Node.js test file and run it with the Node test runner."""
    path = _write_test_file(filename, code)
    try:
        r = subprocess.run(
            ["node", "--disable-warning=ExperimentalWarning", "--test", path],
            cwd=FETCH_ROUTER,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return r
    finally:
        if os.path.exists(path):
            os.unlink(path)


def test_context_router_accessible():
    """context.router is set on the request context during router.fetch()."""
    code = """\
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { createRouter } from './router.ts'

describe('context.router', () => {
  it('is set on the request context during fetch', async () => {
    let router = createRouter()
    let capturedRouter = null
    router.get('/', (ctx) => {
      capturedRouter = ctx.router
      return new Response('ok')
    })
    let response = await router.fetch('https://example.com/')
    assert.strictEqual(response.status, 200)
    assert.strictEqual(
      capturedRouter,
      router,
      'context.router must be the router instance'
    )
  })
})
"""
    r = _run_node_test("_hb_router_accessible.test.ts", code)
    assert r.returncode == 0, (
        f"context.router accessible test failed (exit {r.returncode}):\\n"
        f"STDERR: {r.stderr[-2000:]}\\n"
        f"STDOUT: {r.stdout[-2000:]}"
    )


def test_context_router_throws():
    """Accessing context.router when not set via fetch() throws an error."""
    code = """\
import { describe, it } from 'node:test'
import assert from 'node:assert/strict'
import { RequestContext } from './request-context.ts'

describe('context.router', () => {
  it('throws when router is not set', () => {
    let ctx = new RequestContext(new Request('https://example.com/'))
    assert.throws(
      () => { let _ = ctx.router },
      { message: /No router found/ }
    )
  })

  it('does not throw when accessed within a real fetch', async () => {
    let { createRouter } = await import('./router.ts')
    let router = createRouter()
    router.get('/', (ctx) => {
      let r = ctx.router
      if (r !== router) throw new Error('context.router !== router')
      return new Response('ok')
    })
    let response = await router.fetch('https://example.com/')
    assert.strictEqual(response.status, 200)
  })
})
"""
    r = _run_node_test("_hb_router_throws.test.ts", code)
    assert r.returncode == 0, (
        f"context.router throws test failed (exit {r.returncode}):\\n"
        f"STDERR: {r.stderr[-2000:]}\\n"
        f"STDOUT: {r.stdout[-2000:]}"
    )


def test_existing_tests():
    """Existing fetch-router test suite passes."""
    r = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test"],
        cwd=FETCH_ROUTER,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Existing tests failed (exit {r.returncode}):\\n"
        f"STDERR: {r.stderr[-2000:]}\\n"
        f"STDOUT: {r.stdout[-2000:]}"
    )


def test_typecheck():
    """TypeScript type checking passes for fetch-router package."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/fetch-router", "run", "typecheck"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        f"Typecheck failed (exit {r.returncode}):\\n"
        f"STDERR: {r.stderr[-2000:]}\\n"
        f"STDOUT: {r.stdout[-2000:]}"
    )

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