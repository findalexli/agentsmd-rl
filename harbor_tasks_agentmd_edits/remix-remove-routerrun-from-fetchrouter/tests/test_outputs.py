"""
Task: remix-remove-routerrun-from-fetchrouter
Repo: remix-run/remix @ 783fa46240191001e0ee2084297b5c81d78b3545
PR:   11071

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"

ROUTER_TS = f"{REPO}/packages/fetch-router/src/lib/router.ts"
ROUTER_TEST_TS = f"{REPO}/packages/fetch-router/src/lib/router.test.ts"
FETCH_ROUTER_README = f"{REPO}/packages/fetch-router/README.md"
BOOKSTORE_README = f"{REPO}/demos/bookstore/README.md"
CHANGE_FILE = f"{REPO}/packages/fetch-router/.changes/minor.router-run.md"


def _run_node(code: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Execute JavaScript code via Node in the repo directory."""
    script = Path(REPO) / "_eval_tmp.mjs"
    script.write_text(code)
    try:
        return subprocess.run(
            ["node", str(script)],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
        )
    finally:
        script.unlink(missing_ok=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — router.run removed from source code
# ---------------------------------------------------------------------------

def test_router_run_removed_from_source():
    """Router interface and createRouter must not contain run() method."""
    r = _run_node("""
import { readFileSync } from 'node:fs';

const src = readFileSync('packages/fetch-router/src/lib/router.ts', 'utf8');

// Extract the Router interface body
const iface = src.match(/export\\s+interface\\s+Router\\s*\\{([\\s\\S]*?)\\n\\}/);
if (!iface) {
  console.error('ERROR: Router interface not found');
  process.exit(1);
}

// Check for run method declarations in the interface
if (/^\\s+run\\s*[<(]/m.test(iface[1])) {
  console.error('ERROR: Router interface still declares run() method');
  process.exit(1);
}

// Check for async run implementation anywhere in the file
if (/async\\s+run\\s*[<(]/m.test(src)) {
  console.error('ERROR: createRouter still has async run() implementation');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"router.run() not fully removed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_router_run_tests_and_imports_removed():
    """Test file must not contain router.run() tests or createStorageKey import."""
    r = _run_node("""
import { readFileSync } from 'node:fs';

const src = readFileSync('packages/fetch-router/src/lib/router.test.ts', 'utf8');

if (src.includes("describe('router.run()")) {
  console.error('ERROR: test file still has router.run() describe block');
  process.exit(1);
}

if (/router\\.run\\s*\\(/m.test(src)) {
  console.error('ERROR: test file still calls router.run()');
  process.exit(1);
}

if (src.includes('createStorageKey')) {
  console.error('ERROR: test file still imports createStorageKey');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"router.run() tests not removed: {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_change_file_deleted():
    """The unreleased change file for router.run must be removed."""
    assert not Path(CHANGE_FILE).exists(), \
        "packages/fetch-router/.changes/minor.router-run.md should be deleted"


def test_readme_router_run_section_removed():
    """fetch-router README must not have 'Running Code In Request Context' section."""
    r = _run_node("""
import { readFileSync } from 'node:fs';

const content = readFileSync('packages/fetch-router/README.md', 'utf8');

if (content.includes('### Running Code In Request Context')) {
  console.error('ERROR: README still has "Running Code In Request Context" section');
  process.exit(1);
}

if (/router\\.run\\s*\\(/m.test(content)) {
  console.error('ERROR: README still has router.run() code examples');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"README still references router.run(): {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


def test_bookstore_readme_no_router_run():
    """Bookstore demo README must not reference router.run()."""
    r = _run_node("""
import { readFileSync } from 'node:fs';

const content = readFileSync('demos/bookstore/README.md', 'utf8');

if (/router\\.run\\(\\)/m.test(content)) {
  console.error('ERROR: bookstore README still mentions router.run()');
  process.exit(1);
}

if (content.includes('#running-code-in-request-context')) {
  console.error('ERROR: bookstore README still links to removed section');
  process.exit(1);
}

console.log('PASS');
""")
    assert r.returncode == 0, f"bookstore README still references router.run(): {r.stderr}\n{r.stdout}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — preserved functionality
# ---------------------------------------------------------------------------

def test_syntax_check():
    """Modified TypeScript files must be non-empty with balanced braces."""
    for path in [ROUTER_TS, ROUTER_TEST_TS]:
        src = Path(path).read_text()
        assert len(src.strip()) > 0, f"{path} is empty"
        assert src.count("{") == src.count("}"), f"{path} has unbalanced braces"


def test_router_fetch_still_in_interface():
    """The Router interface must still declare fetch()."""
    src = Path(ROUTER_TS).read_text()
    assert "fetch(" in src, \
        "Router interface must still have fetch() method"


def test_router_map_still_in_interface():
    """The Router interface must still declare map()."""
    src = Path(ROUTER_TS).read_text()
    assert "map(" in src or "mapRoutes" in src, \
        "Router interface must still have map() method"


def test_fetch_router_readme_still_has_content():
    """fetch-router README must still document core features."""
    content = Path(FETCH_ROUTER_README).read_text()
    assert "router.fetch" in content, "README must still document router.fetch"
    assert "## Features" in content, "README must still have Features section"
    assert "## Usage" in content, "README must still have Usage section"
