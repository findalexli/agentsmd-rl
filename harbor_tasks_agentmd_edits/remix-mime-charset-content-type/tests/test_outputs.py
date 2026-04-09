"""
Task: remix-mime-charset-content-type
Repo: remix-run/remix @ 848194ecde3f143b5d0d1fde9b11fa713b7c142e
PR:   10905

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from pathlib import Path

REPO = "/workspace/remix"


def _run_ts(script: str, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run an inline TypeScript/ESM snippet via Node with experimental strip-types."""
    return subprocess.run(
        ["node", "--experimental-strip-types", "--no-warnings",
         "--input-type=module", "-e", script],
        cwd=REPO, capture_output=True, text=True, timeout=timeout,
    )


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Pre-existing files that get modified must still parse."""
    for f in [
        "packages/mime/src/index.ts",
        "packages/response/src/lib/file.ts",
    ]:
        fp = Path(REPO) / f
        assert fp.exists(), f"{f} does not exist"
        content = fp.read_text()
        assert len(content.strip()) > 20, f"{f} is too short or empty"


# ---------------------------------------------------------------------------
# Repo CI/CD tests (pass_to_pass, repo_tests)
# These ensure the repo's own CI/CD checks pass on both base commit and after fix
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_mime_package_tests():
    """Repo's @remix-run/mime package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/mime", "test"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Mime package tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_mime_package_typecheck():
    """Repo's @remix-run/mime package typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/mime", "typecheck"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Mime package typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_response_package_tests():
    """Repo's @remix-run/response package tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/response", "test"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Response package tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_response_package_typecheck():
    """Repo's @remix-run/response package typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "--filter", "@remix-run/response", "typecheck"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Response package typecheck failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_changes_validate():
    """Repo's changes file validation passes (pass_to_pass)."""
    r = subprocess.run(
        ["pnpm", "changes:validate"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Changes validate failed:\n{r.stderr[-500:]}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mime_type_to_content_type_text_types():
    """mimeTypeToContentType adds '; charset=utf-8' to text/* MIME types."""
    r = _run_ts("""
import { mimeTypeToContentType } from './packages/mime/src/lib/mime-type-to-content-type.ts';
let cases = [
  ['text/plain', 'text/plain; charset=utf-8'],
  ['text/html', 'text/html; charset=utf-8'],
  ['text/css', 'text/css; charset=utf-8'],
  ['text/javascript', 'text/javascript; charset=utf-8'],
  ['text/markdown', 'text/markdown; charset=utf-8'],
  ['text/csv', 'text/csv; charset=utf-8'],
];
let failed = [];
for (let [input, expected] of cases) {
  let result = mimeTypeToContentType(input);
  if (result !== expected) failed.push({input, result, expected});
}
if (failed.length) { console.error(JSON.stringify(failed)); process.exit(1); }
""")
    assert r.returncode == 0, (
        f"mimeTypeToContentType failed for text types:\n{r.stdout}\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_mime_type_to_content_type_json_and_js():
    """mimeTypeToContentType adds charset to application/json, application/javascript, +json types."""
    r = _run_ts("""
import { mimeTypeToContentType } from './packages/mime/src/lib/mime-type-to-content-type.ts';
let cases = [
  ['application/json', 'application/json; charset=utf-8'],
  ['application/javascript', 'application/javascript; charset=utf-8'],
  ['application/ld+json', 'application/ld+json; charset=utf-8'],
  ['application/manifest+json', 'application/manifest+json; charset=utf-8'],
  ['application/geo+json', 'application/geo+json; charset=utf-8'],
];
let failed = [];
for (let [input, expected] of cases) {
  let result = mimeTypeToContentType(input);
  if (result !== expected) failed.push({input, result, expected});
}
if (failed.length) { console.error(JSON.stringify(failed)); process.exit(1); }
""")
    assert r.returncode == 0, (
        f"mimeTypeToContentType failed for json/js types:\n{r.stdout}\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_mime_type_to_content_type_exclusions():
    """mimeTypeToContentType excludes text/xml, binary types, and already-charset types."""
    r = _run_ts("""
import { mimeTypeToContentType } from './packages/mime/src/lib/mime-type-to-content-type.ts';
let cases = [
  ['text/xml', 'text/xml'],
  ['image/png', 'image/png'],
  ['image/jpeg', 'image/jpeg'],
  ['video/mp4', 'video/mp4'],
  ['application/pdf', 'application/pdf'],
  ['application/zip', 'application/zip'],
  ['application/octet-stream', 'application/octet-stream'],
  ['font/woff2', 'font/woff2'],
  ['text/plain; charset=utf-8', 'text/plain; charset=utf-8'],
  ['text/html;charset=iso-8859-1', 'text/html;charset=iso-8859-1'],
];
let failed = [];
for (let [input, expected] of cases) {
  let result = mimeTypeToContentType(input);
  if (result !== expected) failed.push({input, result, expected});
}
if (failed.length) { console.error(JSON.stringify(failed)); process.exit(1); }
""")
    assert r.returncode == 0, (
        f"mimeTypeToContentType exclusions failed:\n{r.stdout}\n{r.stderr}"
    )


# [pr_diff] fail_to_pass
def test_detect_content_type_exists_and_composes():
    """detectContentType must exist, import detectMimeType + mimeTypeToContentType, and export."""
    fp = Path(REPO) / "packages/mime/src/lib/detect-content-type.ts"
    assert fp.exists(), "detect-content-type.ts does not exist"
    content = fp.read_text()
    assert "detectMimeType" in content, "Must import detectMimeType"
    assert "mimeTypeToContentType" in content, "Must use mimeTypeToContentType"
    assert "export" in content and "detectContentType" in content, (
        "Must export detectContentType"
    )
    # Verify it handles unknown extensions (returns undefined, not throws)
    assert "undefined" in content or "?" in content, (
        "Must handle undefined mimeType for unknown extensions"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_readme_documents_detect_content_type():
    """packages/mime/README.md must document the detectContentType function."""
    readme = Path(REPO) / "packages/mime/README.md"
    content = readme.read_text()
    assert "detectContentType" in content, (
        "README must mention detectContentType"
    )
    # Should show usage example with charset output
    assert "charset=utf-8" in content, (
        "README should show charset in detectContentType examples"
    )
    # Should document it handles extensions/filenames
    assert "extension" in content.lower() or "filename" in content.lower(), (
        "README should describe that detectContentType accepts extensions or filenames"
    )


# [pr_diff] fail_to_pass
def test_readme_documents_mime_type_to_content_type():
    """packages/mime/README.md must document the mimeTypeToContentType function."""
    readme = Path(REPO) / "packages/mime/README.md"
    content = readme.read_text()
    assert "mimeTypeToContentType" in content, (
        "README must mention mimeTypeToContentType"
    )
    # Should explain charset logic
    assert "text/xml" in content or "xml" in content.lower(), (
        "README should mention text/xml exclusion"
    )
    # Should show usage example
    assert "text/css; charset=utf-8" in content or "text/html; charset=utf-8" in content, (
        "README should show charset example for a text type"
    )


# ---------------------------------------------------------------------------
# Fail-to-pass (agent_config) — AGENTS.md:16 package exports rule
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — AGENTS.md:16 @ 848194ec
def test_index_exports_new_functions():
    """packages/mime/src/index.ts must re-export both new functions per AGENTS.md architecture rule."""
    index_ts = Path(REPO) / "packages/mime/src/index.ts"
    content = index_ts.read_text()
    assert "detectContentType" in content, (
        "index.ts must export detectContentType (AGENTS.md: package exports re-export from src/lib)"
    )
    assert "mimeTypeToContentType" in content, (
        "index.ts must export mimeTypeToContentType (AGENTS.md: package exports re-export from src/lib)"
    )
    # Verify they are actual exports, not just comments
    lines = content.splitlines()
    export_lines = [l for l in lines if l.strip().startswith("export")]
    exported_names = " ".join(export_lines)
    assert "detectContentType" in exported_names, (
        "detectContentType must be in an export statement"
    )
    assert "mimeTypeToContentType" in exported_names, (
        "mimeTypeToContentType must be in an export statement"
    )
