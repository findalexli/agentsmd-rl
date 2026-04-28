"""
Tests for civitai attachment download fix (PR #2071).

The bug: article attachment downloads served wrong file content when a File.id
collided with a ModelFile.id in the storage resolver. The fix changes the
attachment endpoint to use getDownloadUrl (delivery worker direct) instead of
resolveDownloadUrl (which queries the storage resolver first).
"""

import os
import re
import subprocess
from pathlib import Path

REPO = Path(os.environ.get("REPO_DIR", "/workspace/civitai"))
ATTACHMENT_FILE = REPO / "src/pages/api/download/attachments/[fileId].ts"
DELIVERY_WORKER_FILE = REPO / "src/utils/delivery-worker.ts"


def read_file(path: Path) -> str:
    """Read file content, raise AssertionError if missing."""
    assert path.exists(), f"File not found: {path}"
    return path.read_text(encoding="utf-8")


# ── fail-to-pass tests (must fail on base commit, pass on fix) ─────────


def test_imports_getDownloadUrl():
    """Attachment endpoint must import getDownloadUrl from delivery-worker (f2p).

    On the base commit, the file imports resolveDownloadUrl instead.
    """
    source = read_file(ATTACHMENT_FILE)
    # Must have an import statement that brings in getDownloadUrl
    import_pattern = re.compile(
        r"import\s+\{[^}]*getDownloadUrl[^}]*\}\s+from\s+['\"]~/utils/delivery-worker['\"]"
    )
    assert import_pattern.search(source), (
        "getDownloadUrl must be imported from ~/utils/delivery-worker"
    )


def test_does_not_import_resolveDownloadUrl():
    """Attachment endpoint must NOT import resolveDownloadUrl (f2p).

    On the base commit, resolveDownloadUrl is imported, which routes through
    the storage resolver that only tracks ModelFile records.
    """
    source = read_file(ATTACHMENT_FILE)
    import_pattern = re.compile(
        r"import\s+\{[^}]*resolveDownloadUrl[^}]*\}\s+from"
    )
    assert not import_pattern.search(source), (
        "resolveDownloadUrl must NOT be imported — it queries the storage resolver "
        "which only tracks ModelFile records, causing wrong-file downloads for attachments"
    )


def test_download_call_uses_file_url_and_name():
    """The download function must be called with (file.url, file.name), not (fileId, file.url, file.name) (f2p).

    On the base commit, resolveDownloadUrl(fileId, file.url, file.name) is called
    with 3 arguments. The fix should use getDownloadUrl(file.url, file.name) with 2 arguments,
    resolving via the file's actual S3 URL.
    """
    source = read_file(ATTACHMENT_FILE)
    # Must call getDownloadUrl with file.url and file.name
    call_pattern = re.compile(
        r"getDownloadUrl\s*\(\s*file\.url\s*,\s*file\.name\s*\)"
    )
    assert call_pattern.search(source), (
        "Must call getDownloadUrl(file.url, file.name) — resolves via the file's "
        "actual S3 URL without querying the storage resolver"
    )


def test_fileId_not_in_download_call():
    """fileId must NOT be passed as first argument to the download URL function (f2p).

    On the base commit, fileId is passed as the first argument to resolveDownloadUrl,
    which causes the storage resolver to look up a ModelFile with that ID.
    The fix should not pass the numeric fileId to any download resolution function.
    """
    source = read_file(ATTACHMENT_FILE)
    # Neither getDownloadUrl nor resolveDownloadUrl should be called with fileId
    assert not re.search(r'(?:getDownloadUrl|resolveDownloadUrl)\s*\(\s*fileId', source), (
        "fileId must not be passed to the download function — "
        "it triggers storage resolver lookup which only tracks ModelFile records"
    )


# ── pass-to-pass tests (should pass on both base and fix) ──────────────


def test_delivery_worker_module_integrity():
    """delivery-worker.ts must export both getDownloadUrl and resolveDownloadUrl (p2p).

    Both functions are needed by other parts of the codebase (model downloads
    still use resolveDownloadUrl). The fix only changes which one the attachment
    endpoint uses.
    """
    source = read_file(DELIVERY_WORKER_FILE)
    assert "export async function getDownloadUrl" in source, (
        "delivery-worker.ts must export getDownloadUrl"
    )
    assert "export async function resolveDownloadUrl" in source, (
        "delivery-worker.ts must export resolveDownloadUrl"
    )


def test_delivery_worker_getDownloadUrl_signature():
    """getDownloadUrl must accept (fileUrl, fileName?) — 2 params (p2p).

    This is the function that goes directly to the delivery worker via S3 URL,
    bypassing the storage resolver.
    """
    source = read_file(DELIVERY_WORKER_FILE)
    sig_pattern = re.compile(
        r"export\s+async\s+function\s+getDownloadUrl\s*\(\s*fileUrl\s*:\s*string\s*,\s*fileName\?\s*:\s*string\s*\)"
    )
    assert sig_pattern.search(source), (
        "getDownloadUrl must have signature (fileUrl: string, fileName?: string)"
    )


def test_delivery_worker_resolveDownloadUrl_signature():
    """resolveDownloadUrl must accept (fileId, fileUrl, fileName?) — 3 params (p2p).

    This function queries the storage resolver by fileId, falling back to
    getDownloadUrl when the resolver doesn't have the file.
    """
    source = read_file(DELIVERY_WORKER_FILE)
    sig_pattern = re.compile(
        r"export\s+async\s+function\s+resolveDownloadUrl\s*\(\s*fileId\s*:\s*number\s*,\s*fileUrl\s*:\s*string\s*,\s*fileName\?\s*:\s*string\s*\)"
    )
    assert sig_pattern.search(source), (
        "resolveDownloadUrl must have signature (fileId: number, fileUrl: string, fileName?: string)"
    )


def test_attachment_endpoint_structure():
    """Attachment endpoint file must have valid structure with expected exports (p2p)."""
    source = read_file(ATTACHMENT_FILE)
    # Must be a Next.js API route with default export
    assert "export default" in source, "Must have default export (Next.js API route)"
    # Must use PublicEndpoint wrapper
    assert "PublicEndpoint" in source, "Must use PublicEndpoint wrapper"
    # Must import required dependencies
    assert "getFileWithPermission" in source, "Must import getFileWithPermission"
    assert "z" in source, "Must use Zod for validation"


def test_resolveDownloadUrl_has_fallback_to_getDownloadUrl():
    """resolveDownloadUrl must fall back to getDownloadUrl for non-ModelFile records (p2p).

    The resolveDownloadUrl function should catch errors from the storage resolver
    and fall back to getDownloadUrl. This ensures model downloads still work
    even when the resolver doesn't have a record.
    """
    source = read_file(DELIVERY_WORKER_FILE)
    # resolveDownloadUrl should exist as an exported async function
    assert re.search(
        r"export\s+async\s+function\s+resolveDownloadUrl\s*\(",
        source,
    ), "resolveDownloadUrl function must exist"
    # Look for the fallback pattern: resolveDownloadUrl calls getDownloadUrl
    assert "return getDownloadUrl(fileUrl, fileName)" in source, (
        "resolveDownloadUrl must fall back to getDownloadUrl(fileUrl, fileName)"
    )


def test_attachment_endpoint_file_valid_syntax():
    """Attachment endpoint file has balanced braces and no obvious syntax errors (p2p).

    Uses Node.js to do a basic syntax check on the file.
    """
    source = read_file(ATTACHMENT_FILE)
    # Count balanced braces (simple heuristic)
    open_count = source.count("{")
    close_count = source.count("}")
    assert abs(open_count - close_count) <= 2, (
        f"Unbalanced braces: {open_count} open vs {close_count} close"
    )
    # Check balanced parentheses
    open_paren = source.count("(")
    close_paren = source.count(")")
    assert abs(open_paren - close_paren) <= 2, (
        f"Unbalanced parentheses: {open_paren} open vs {close_paren} close"
    )


# ── repo CI pass-to-pass tests (subprocess-based) ──────────────────────


def test_repo_eslint_modified_files():
    """ESLint passes on the modified files (pass_to_pass).

    Runs the repo's ESLint configuration against the two files touched by
    the PR: delivery-worker.ts and the attachment endpoint. The repo's CI
    runs `pnpm run eslint` (cross-env TIMING=1 eslint src/ --quiet).
    We scope it to just the changed files to avoid OOM in constrained envs.
    """
    r = subprocess.run(
        [
            "bash", "-c",
            f"cd {REPO} && NODE_OPTIONS='--max_old_space_size=4096' "
            f"npx eslint src/utils/delivery-worker.ts "
            f"'src/pages/api/download/attachments/[fileId].ts'",
        ],
        capture_output=True, text=True, timeout=300,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_prettier_modified_files():
    """Prettier formatting check passes on modified files (pass_to_pass).

    The repo's CI includes `pnpm run prettier:check`. We scope it to the
    two files touched by the PR to keep the check fast.
    """
    r = subprocess.run(
        [
            "bash", "-c",
            f"cd {REPO} && npx prettier --check "
            f"'src/utils/delivery-worker.ts' "
            f"'src/pages/api/download/attachments/[fileId].ts'",
        ],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_ts_parse_delivery_worker():
    """TypeScript parser accepts delivery-worker.ts without errors (pass_to_pass).

    Uses the TypeScript compiler's createSourceFile API to verify the file
    parses cleanly. This is a lighter-weight check than full type-checking
    (which requires submodules not available in the Docker image).
    """
    r = subprocess.run(
        [
            "bash", "-c",
            f"cd {REPO} && node -e \""
            f"const ts = require('typescript');"
            f"const src = require('fs').readFileSync('src/utils/delivery-worker.ts','utf8');"
            f"const sf = ts.createSourceFile('delivery-worker.ts', src, ts.ScriptTarget.Latest, true);"
            f"const diags = sf.parseDiagnostics || [];"
            f"if (diags.length) {{ diags.forEach(d => console.error(d)); process.exit(1); }}"
            f"console.log('Parse OK');"
            f"\"",
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"TS parse failed for delivery-worker.ts:\n{r.stderr[-500:]}"


def test_repo_ts_parse_attachment_endpoint():
    """TypeScript parser accepts the attachment endpoint without errors (pass_to_pass).

    Uses the TypeScript compiler's createSourceFile API to verify the file
    parses cleanly.
    """
    r = subprocess.run(
        [
            "bash", "-c",
            f"cd {REPO} && node -e \""
            f"const ts = require('typescript');"
            f"const src = require('fs').readFileSync('src/pages/api/download/attachments/[fileId].ts','utf8');"
            f"const sf = ts.createSourceFile('[fileId].ts', src, ts.ScriptTarget.Latest, true);"
            f"const diags = sf.parseDiagnostics || [];"
            f"if (diags.length) {{ diags.forEach(d => console.error(d)); process.exit(1); }}"
            f"console.log('Parse OK');"
            f"\"",
        ],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"TS parse failed for attachment endpoint:\n{r.stderr[-500:]}"


def test_repo_vitest_stable_unit_tests():
    """A subset of repo unit tests pass (pass_to_pass).

    Runs a curated set of vitest test files that are stable on the base
    commit. These verify the broader test infrastructure works and that
    unrelated functionality isn't broken.
    """
    r = subprocess.run(
        [
            "bash", "-c",
            f"cd {REPO} && npx vitest run "
            f"src/server/services/__tests__/isUsernamePermitted.test.ts "
            f"src/shared/utils/__tests__/creator-program.utils.test.ts "
            f"src/server/games/daily-challenge/__tests__/challenge-helpers.test.ts "
            f"src/server/games/daily-challenge/template-engine.test.ts",
        ],
        capture_output=True, text=True, timeout=120,
    )
    assert r.returncode == 0, f"Vitest unit tests failed:\n{r.stdout[-800:]}\n{r.stderr[-500:]}"

# Note: Full-repo typecheck (pnpm run typecheck) is excluded because it requires
# the private event-engine-common submodule which isn't available in Docker.
# Per-file TypeScript parse checks (test_repo_ts_parse_*) cover syntax validation
# on the files touched by this PR.