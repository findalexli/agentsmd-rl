"""
Tests for civitai/civitai#2071:
Article attachment downloads were serving wrong file content when a File.id
collided with a ModelFile.id in the storage resolver's file_locations table.

The fix bypasses the storage resolver and uses the delivery worker directly
for attachment downloads, since it resolves via the file's actual S3 URL
rather than by ID.
"""
import subprocess
import os
import re
import json

REPO = os.environ.get("REPO", "/workspace/civitai_repo")
TARGET_FILE = "src/pages/api/download/attachments/[fileId].ts"


def get_source(file_path):
    with open(os.path.join(REPO, file_path), "r") as f:
        return f.read()


def run_tsquery(query_code, extra_args=None):
    """Run a TypeScript AST query, return parsed JSON results."""
    script = f"""
const ts = require('typescript');
const fs = require('fs');
const filePath = '{REPO}/{TARGET_FILE}';
const source = fs.readFileSync(filePath, 'utf8');
const sf = ts.createSourceFile('file.ts', source, ts.ScriptTarget.Latest, true);
{query_code}
"""
    cmd = ["node", "-e", script]
    if extra_args:
        cmd.extend(extra_args)
    r = subprocess.run(
        cmd,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=30,
    )
    if r.returncode != 0:
        return [{"error": r.stderr}]
    try:
        return json.loads(r.stdout.strip())
    except json.JSONDecodeError:
        return [{"raw": r.stdout, "error": "parse error"}]


# ---------------------------------------------------------------------------
# Fail-to-pass tests (f2p): these MUST fail on base commit, pass after fix
# ---------------------------------------------------------------------------

def test_uses_getdownloadurl_not_resolve():
    """Attachment endpoint must import getDownloadUrl, not resolveDownloadUrl.

    The storage resolver only tracks ModelFile records, not File table records
    (article attachments). Using resolveDownloadUrl causes ID collision bugs.
    """
    src = get_source(TARGET_FILE)
    # Must import getDownloadUrl
    assert "getDownloadUrl" in src, \
        "getDownloadUrl must be imported from delivery-worker"
    # Must NOT have resolveDownloadUrl imported from delivery-worker
    import_pattern = r"import\s*{[^}]*resolveDownloadUrl[^}]*}\s*from\s*['\"]~/utils/delivery-worker['\"]"
    assert not re.search(import_pattern, src), \
        "resolveDownloadUrl must not be imported from delivery-worker in attachment endpoint"


def test_no_fileid_based_resolution():
    """The endpoint must NOT call any function that uses fileId as first argument.

    The bug is that resolveDownloadUrl(fileId, ...) goes through the storage
    resolver which matches by ID — causing wrong file content on ID collisions.
    Any correct fix will call a function that does NOT take fileId as an arg.
    """
    query_code = r"""
const results = [];
function visitor(node) {
  if (ts.isCallExpression(node)) {
    const expr = node.expression.getText();
    if (expr.includes('DownloadUrl') && node.arguments.length > 0) {
      const args = node.arguments.map(a => a.getText());
      results.push({func: expr, args: args, nArgs: node.arguments.length});
    }
  }
  ts.forEachChild(node, visitor);
}
visitor(sf);
process.stdout.write(JSON.stringify(results));
"""
    results = run_tsquery(query_code)
    error = next((r for r in results if "error" in r), None)
    if error:
        raise AssertionError(f"TS query failed: {error['error']}")

    # Filter to calls where fileId is the first argument (the buggy pattern)
    fileId_calls = [r for r in results if r['args'] and r['args'][0] == 'fileId']
    assert len(fileId_calls) == 0, \
        f"Endpoint still calls a function with fileId as first arg: {fileId_calls}"


def test_call_signature_two_args():
    """The URL resolution call must take (url, name) — two args, not three.

    resolveDownloadUrl(fileId, url, name) uses 3 args and ID-based resolution.
    getDownloadUrl(url, name) uses 2 args and URL-based resolution.
    Any correct fix will use 2 args with URL+name (whether destructured or not).
    """
    query_code = r"""
const results = [];
function visitor(node) {
  if (ts.isCallExpression(node)) {
    const expr = node.expression.getText();
    if (expr.includes('DownloadUrl') && node.arguments.length >= 2) {
      const args = node.arguments.map(a => a.getText());
      results.push({func: expr, args: args, nArgs: node.arguments.length});
    }
  }
  ts.forEachChild(node, visitor);
}
visitor(sf);
process.stdout.write(JSON.stringify(results));
"""
    results = run_tsquery(query_code)
    error = next((r for r in results if "error" in r), None)
    if error:
        raise AssertionError(f"TS query failed: {error['error']}")

    # Filter to download URL calls (not tracker calls)
    download_calls = [r for r in results if 'Tracker' not in r['func']]
    assert len(download_calls) > 0, "No download URL calls found"

    for call in download_calls:
        assert call['nArgs'] == 2, \
            f"Download URL call must use 2 args (url, name), not {call['nArgs']}: {call['func']}({call['args']})"

    for call in download_calls:
        assert 'getDownloadUrl' in call['func'], \
            f"Must call getDownloadUrl, not {call['func']}"


def test_file_compiles_typescript():
    """The modified endpoint must compile without TypeScript errors."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", TARGET_FILE],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # TypeScript may have project-wide errors unrelated to our change.
    # Only fail if there are errors in the target file itself.
    errors_in_file = [
        line for line in r.stderr.split('\n')
        if TARGET_FILE in line and 'error TS' in line
    ]
    assert len(errors_in_file) == 0, \
        f"TypeScript errors in {TARGET_FILE}:\n" + '\n'.join(errors_in_file)


# ---------------------------------------------------------------------------
# Pass-to-pass tests (p2p): verify delivery-worker module exports needed fn
# ---------------------------------------------------------------------------

def test_delivery_worker_exports_getdownloadurl():
    """The delivery-worker module must export getDownloadUrl (used by the fix)."""
    worker_src = get_source("src/utils/delivery-worker.ts")
    assert "export" in worker_src and "getDownloadUrl" in worker_src, \
        "delivery-worker.ts must export getDownloadUrl function"


# ---------------------------------------------------------------------------
# Pass-to-pass tests (p2p): repo CI commands that must pass on base commit
# ---------------------------------------------------------------------------

def test_prettier_attachment_endpoint():
    """Attachment endpoint follows repo code style (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/pages/api/download/attachments/[fileId].ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}"


def test_prettier_delivery_worker():
    """Delivery worker module follows repo code style (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "src/utils/delivery-worker.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}"


def test_repo_unit_tests_pass():
    """Repo's unit test suite passes on base commit (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "vitest", "run",
         "src/server/services/__tests__/isUsernamePermitted.test.ts",
         "src/server/services/__tests__/redeemableCode.service.test.ts",
         "src/server/games/daily-challenge/__tests__/challenge-helpers.test.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, f"Unit tests failed:\n{r.stdout[-1000:]}"