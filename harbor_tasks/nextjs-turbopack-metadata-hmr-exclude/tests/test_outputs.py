"""
Task: nextjs-turbopack-metadata-hmr-exclude
Repo: vercel/next.js @ 9a0214a12f1ed1901c4b01e84073ab854848eea0
PR:   92034

Tests verify that Turbopack's hot reloader excludes metadata routes
(manifest.ts, robots.ts, sitemap.ts, icon.tsx, etc.) from server HMR,
so their caches are properly invalidated on file changes.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
import subprocess
from pathlib import Path

REPO = "/workspace/next.js"

HOT_RELOADER = Path(REPO) / "packages/next/src/server/dev/hot-reloader-turbopack.ts"


def _extract_uses_server_hmr_block(src: str) -> str | None:
    """Extract the usesServerHmr assignment block from the source."""
    match = re.search(
        r"const\s+usesServerHmr\s*=\s*([\s\S]*?)(?=\n\s*\n|\nconst |\nlet |\nfor )",
        src,
    )
    return match.group(0) if match else None


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file validity
# ---------------------------------------------------------------------------


# [static] pass_to_pass
def test_syntax_valid():
    """hot-reloader-turbopack.ts exists and has substantial content."""
    assert HOT_RELOADER.exists(), "hot-reloader-turbopack.ts does not exist"
    content = HOT_RELOADER.read_text()
    line_count = len(content.splitlines())
    assert line_count > 400, (
        f"hot-reloader-turbopack.ts has only {line_count} lines, expected >400"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_metadata_route_hmr_exclusion():
    """usesServerHmr must exclude metadata routes via isMetadataRoute check.

    Uses node to parse the source and verify the usesServerHmr expression
    includes a metadata route exclusion guard.
    """
    r = subprocess.run(
        [
            "node",
            "-e",
            """
const fs = require('fs');
const src = fs.readFileSync(
    'packages/next/src/server/dev/hot-reloader-turbopack.ts',
    'utf8'
);

// Find the usesServerHmr assignment block
const match = src.match(/const\\s+usesServerHmr\\s*=[\\s\\S]*?(?=\\n\\s*\\n|\\nconst |\\nlet |\\nfor )/);
if (!match) {
    console.error('Could not find usesServerHmr assignment');
    process.exit(1);
}
const expr = match[0];

// Check for metadata route exclusion (isMetadataRoute or isMetadataRouteFile or metadata keyword check)
const hasMetadataCheck =
    expr.includes('isMetadataRoute') ||
    expr.includes('isMetadataRouteFile') ||
    (expr.includes('metadata') && (expr.includes('route') || expr.includes('Route')));

if (!hasMetadataCheck) {
    console.error('usesServerHmr does not exclude metadata routes');
    console.error('Expression found:', expr);
    process.exit(1);
}

// The exclusion must be negated (metadata routes should NOT use server HMR)
if (expr.includes('isMetadataRoute') || expr.includes('isMetadataRouteFile')) {
    if (!expr.includes('!isMetadataRoute') && !expr.includes('!isMetadataRouteFile')) {
        console.error('Metadata route check must be negated (metadata routes should be excluded)');
        process.exit(1);
    }
}

console.log('OK: usesServerHmr properly excludes metadata routes');
""",
        ],
        cwd=REPO,
        capture_output=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"usesServerHmr metadata route exclusion check failed:\n"
        f"{r.stdout.decode()}\n{r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_is_metadata_route_imported():
    """isMetadataRoute must be imported in hot-reloader-turbopack.ts.

    The fix requires importing isMetadataRoute (not just isMetadataRouteFile)
    from the metadata route module to check routes in the usesServerHmr guard.
    """
    src = HOT_RELOADER.read_text()

    # Check for import of isMetadataRoute (distinct from isMetadataRouteFile)
    # Accept various import styles:
    #   import { isMetadataRoute } from ...
    #   import { isMetadataRoute, isMetadataRouteFile } from ...
    #   import { isMetadataRouteFile, isMetadataRoute } from ...
    has_import = bool(
        re.search(r"import\s+\{[^}]*\bisMetadataRoute\b[^}]*\}", src)
    )

    # Also accept: const { isMetadataRoute } = require(...)
    has_require = bool(
        re.search(r"(?:const|let|var)\s+\{[^}]*\bisMetadataRoute\b[^}]*\}\s*=\s*require", src)
    )

    assert has_import or has_require, (
        "hot-reloader-turbopack.ts must import isMetadataRoute "
        "(not just isMetadataRouteFile) from the metadata route module"
    )


# [pr_diff] fail_to_pass
def test_entry_page_extracted():
    """The page/route from splitEntryKey must be available for the metadata route check.

    The fix needs the page (or route) from splitEntryKey(key) to pass to
    isMetadataRoute. This can be via destructuring or property access.
    """
    src = HOT_RELOADER.read_text()

    # Accept multiple patterns:
    # 1. Destructured: const { type: entryType, page: entryPage } = splitEntryKey(key)
    # 2. Property access: splitEntryKey(key).page
    # 3. Separate variable: const entryPage = splitEntryKey(key).page

    # Check pattern 1: page in destructuring
    split_match = re.search(
        r"(?:const|let|var)\s+\{([^}]*)\}\s*=\s*splitEntryKey\s*\(",
        src,
    )
    destructured_page = False
    if split_match:
        destructured_page = bool(re.search(r"\bpage\b", split_match.group(1)))

    # Check pattern 2/3: .page accessed from splitEntryKey
    property_access = bool(re.search(r"splitEntryKey\s*\([^)]*\)\s*\.\s*page", src))

    assert destructured_page or property_access, (
        "The page property from splitEntryKey must be extracted "
        "(via destructuring or property access) for the metadata route check"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff) — regression checks
# ---------------------------------------------------------------------------


# [pr_diff] pass_to_pass
def test_server_hmr_preserves_app_entry_check():
    """usesServerHmr must still require entryType === 'app' for non-metadata routes."""
    src = HOT_RELOADER.read_text()
    block = _extract_uses_server_hmr_block(src)
    assert block is not None, "Could not find usesServerHmr assignment"

    # The condition must still include the app entry type check
    assert "entryType" in block and "'app'" in block, (
        "usesServerHmr must still check entryType === 'app'. "
        f"Found: {block}"
    )


# [pr_diff] pass_to_pass
def test_server_hmr_preserves_edge_exclusion():
    """usesServerHmr must still exclude edge runtime endpoints."""
    src = HOT_RELOADER.read_text()
    block = _extract_uses_server_hmr_block(src)
    assert block is not None, "Could not find usesServerHmr assignment"

    # The condition must still exclude edge endpoints
    assert "'edge'" in block, (
        "usesServerHmr must still exclude edge runtime endpoints. "
        f"Found: {block}"
    )
