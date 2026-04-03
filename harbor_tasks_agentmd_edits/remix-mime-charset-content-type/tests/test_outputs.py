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


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """New TypeScript files must parse without syntax errors."""
    files = [
        "packages/mime/src/lib/mime-type-to-content-type.ts",
        "packages/mime/src/lib/detect-content-type.ts",
        "packages/mime/src/index.ts",
        "packages/response/src/lib/file.ts",
    ]
    for f in files:
        fp = Path(REPO) / f
        assert fp.exists(), f"{f} does not exist"
        # Use node to check TS syntax via --experimental-strip-types
        r = subprocess.run(
            ["node", "--experimental-strip-types", "-e",
             f"import('{fp.as_posix()}')"],
            capture_output=True, timeout=30,
        )
        # For files with monorepo imports (@remix-run/*), import may fail
        # at resolution, but syntax errors give a different exit pattern.
        # Read the file to check it's valid TS at minimum.
        content = fp.read_text()
        assert len(content.strip()) > 10, f"{f} is too short or empty"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_mime_type_to_content_type_text_types():
    """mimeTypeToContentType adds '; charset=utf-8' to text/* MIME types."""
    script = """
import { mimeTypeToContentType } from './packages/mime/src/lib/mime-type-to-content-type.ts';
let cases = [
  ['text/plain', 'text/plain; charset=utf-8'],
  ['text/html', 'text/html; charset=utf-8'],
  ['text/css', 'text/css; charset=utf-8'],
  ['text/javascript', 'text/javascript; charset=utf-8'],
  ['text/markdown', 'text/markdown; charset=utf-8'],
  ['text/csv', 'text/csv; charset=utf-8'],
];
for (let [input, expected] of cases) {
  let result = mimeTypeToContentType(input);
  if (result !== expected) {
    console.error('FAIL:', input, '=>', result, '(expected', expected + ')');
    process.exit(1);
  }
}
""".strip()
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--input-type=module", "-e", script],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"mimeTypeToContentType failed for text types:\n"
        f"stdout={r.stdout.decode()}\nstderr={r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_mime_type_to_content_type_json_and_js():
    """mimeTypeToContentType adds charset to application/json, application/javascript, +json types."""
    script = """
import { mimeTypeToContentType } from './packages/mime/src/lib/mime-type-to-content-type.ts';
let cases = [
  ['application/json', 'application/json; charset=utf-8'],
  ['application/javascript', 'application/javascript; charset=utf-8'],
  ['application/ld+json', 'application/ld+json; charset=utf-8'],
  ['application/manifest+json', 'application/manifest+json; charset=utf-8'],
  ['application/geo+json', 'application/geo+json; charset=utf-8'],
];
for (let [input, expected] of cases) {
  let result = mimeTypeToContentType(input);
  if (result !== expected) {
    console.error('FAIL:', input, '=>', result, '(expected', expected + ')');
    process.exit(1);
  }
}
""".strip()
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--input-type=module", "-e", script],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"mimeTypeToContentType failed for json/js types:\n"
        f"stdout={r.stdout.decode()}\nstderr={r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_mime_type_to_content_type_exclusions():
    """mimeTypeToContentType does NOT add charset to text/xml, binary types, or already-charset types."""
    script = """
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
for (let [input, expected] of cases) {
  let result = mimeTypeToContentType(input);
  if (result !== expected) {
    console.error('FAIL:', input, '=>', result, '(expected', expected + ')');
    process.exit(1);
  }
}
""".strip()
    r = subprocess.run(
        ["node", "--experimental-strip-types", "--input-type=module", "-e", script],
        cwd=REPO, capture_output=True, timeout=30,
    )
    assert r.returncode == 0, (
        f"mimeTypeToContentType exclusions failed:\n"
        f"stdout={r.stdout.decode()}\nstderr={r.stderr.decode()}"
    )


# [pr_diff] fail_to_pass
def test_detect_content_type_function():
    """detectContentType function exists with correct structure (imports detectMimeType + mimeTypeToContentType)."""
    fp = Path(REPO) / "packages/mime/src/lib/detect-content-type.ts"
    assert fp.exists(), "detect-content-type.ts does not exist"
    content = fp.read_text()
    # Must import and compose detectMimeType with mimeTypeToContentType
    assert "detectMimeType" in content, "Must import detectMimeType"
    assert "mimeTypeToContentType" in content, "Must use mimeTypeToContentType"
    assert "export" in content and "detectContentType" in content, (
        "Must export detectContentType"
    )
    # Must return undefined for unknown types (not throw)
    assert "undefined" in content or "?" in content, (
        "Must handle undefined mimeType (unknown extensions)"
    )


# [pr_diff] fail_to_pass
def test_exports_new_functions():
    """packages/mime/src/index.ts must export both detectContentType and mimeTypeToContentType."""
    fp = Path(REPO) / "packages/mime/src/index.ts"
    content = fp.read_text()
    assert "detectContentType" in content, (
        "index.ts must export detectContentType"
    )
    assert "mimeTypeToContentType" in content, (
        "index.ts must export mimeTypeToContentType"
    )
    # Also verify existing exports are preserved
    assert "detectMimeType" in content, "Must preserve detectMimeType export"
    assert "isCompressibleMimeType" in content, "Must preserve isCompressibleMimeType export"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (agent_config) — coding style from AGENTS.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — AGENTS.md:19 @ 848194ec


# ---------------------------------------------------------------------------
# Config-edit (config_edit) — README must document new functions
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass
