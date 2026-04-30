"""
Task: remix-feat-define-mime-type
Repo: remix-run/remix @ 9c05f82591c422ffc958bd61deb1b29c181ae225
PR:   remix-run/remix#10921

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import os
import subprocess
import tempfile
from pathlib import Path

REPO = Path("/workspace/remix")
MIME_LIB = REPO / "packages/mime/src/lib"


def _run_ts(code: str) -> subprocess.CompletedProcess:
    """Write a temp .ts file and run with node --experimental-strip-types."""
    fd, path = tempfile.mkstemp(suffix=".ts", dir=str(MIME_LIB))
    try:
        with os.fdopen(fd, "w") as f:
            f.write(code)
        return subprocess.run(
            ["node", "--experimental-strip-types", path],
            capture_output=True,
            text=True,
            cwd=str(MIME_LIB),
            timeout=30,
        )
    finally:
        os.unlink(path)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_define_mime_type_registers_custom_ext():
    """defineMimeType registers a new extension and detectMimeType finds it."""
    r = _run_ts(
        """
import { defineMimeType, resetMimeTypes } from './define-mime-type.ts'
import { detectMimeType } from './detect-mime-type.ts'

resetMimeTypes()
defineMimeType({ extensions: 'myformat', mimeType: 'application/x-myformat' })

if (detectMimeType('myformat') !== 'application/x-myformat')
    throw new Error('custom ext not detected: ' + detectMimeType('myformat'))
if (detectMimeType('file.myformat') !== 'application/x-myformat')
    throw new Error('custom ext with filename not detected')
"""
    )
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_define_mime_type_overrides_builtin():
    """defineMimeType overrides a built-in MIME type mapping."""
    r = _run_ts(
        """
import { defineMimeType, resetMimeTypes } from './define-mime-type.ts'
import { detectMimeType } from './detect-mime-type.ts'

resetMimeTypes()
if (detectMimeType('ts') !== 'video/mp2t')
    throw new Error('builtin ts should be video/mp2t')

defineMimeType({ extensions: 'ts', mimeType: 'text/typescript' })
if (detectMimeType('ts') !== 'text/typescript')
    throw new Error('override not applied: ' + detectMimeType('ts'))
"""
    )
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_define_mime_type_custom_compressible():
    """defineMimeType compressible option overrides default heuristics."""
    r = _run_ts(
        """
import { defineMimeType, resetMimeTypes } from './define-mime-type.ts'
import { isCompressibleMimeType } from './is-compressible-mime-type.ts'

resetMimeTypes()
// Mark a non-compressible-by-heuristic type as compressible
defineMimeType({ extensions: 'myext', mimeType: 'application/x-myformat', compressible: true })
if (!isCompressibleMimeType('application/x-myformat'))
    throw new Error('should be compressible')

// Mark a compressible-by-heuristic type as non-compressible
resetMimeTypes()
defineMimeType({ extensions: 'html', mimeType: 'text/html', compressible: false })
if (isCompressibleMimeType('text/html'))
    throw new Error('should not be compressible')
"""
    )
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# [pr_diff] fail_to_pass
def test_define_mime_type_custom_charset():
    """defineMimeType charset option overrides default charset heuristics."""
    r = _run_ts(
        """
import { defineMimeType, resetMimeTypes } from './define-mime-type.ts'
import { mimeTypeToContentType } from './mime-type-to-content-type.ts'

resetMimeTypes()
// Add charset to a type that normally doesn't get one
defineMimeType({ extensions: 'myext', mimeType: 'application/x-myformat', charset: 'utf-8' })

const result1 = mimeTypeToContentType('application/x-myformat')
if (result1 !== 'application/x-myformat; charset=utf-8')
    throw new Error('expected charset utf-8, got: ' + result1)

// Custom non-utf-8 charset
resetMimeTypes()
defineMimeType({ extensions: 'myext', mimeType: 'application/x-myformat', charset: 'iso-8859-1' })

const result2 = mimeTypeToContentType('application/x-myformat')
if (result2 !== 'application/x-myformat; charset=iso-8859-1')
    throw new Error('expected charset iso-8859-1, got: ' + result2)
"""
    )
    assert r.returncode == 0, f"Failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — config/documentation update tests
# ---------------------------------------------------------------------------


# [pr_diff] fail_to_pass
def test_readme_documents_define_mime_type():
    """README.md must document the new defineMimeType function."""
    readme = REPO / "packages/mime/README.md"
    content = readme.read_text()
    lower = content.lower()
    assert "definemimetype" in lower, "README should mention defineMimeType"
    # Should describe what it does (register/custom/override)
    has_register = "register" in lower
    has_custom = "custom" in lower
    has_override = "override" in lower
    assert has_register or has_custom or has_override, (
        "README should describe what defineMimeType does (register/custom/override)"
    )


# [pr_diff] fail_to_pass
def test_readme_shows_api_options():
    """README must document extensions, mimeType, and at least one optional parameter."""
    readme = REPO / "packages/mime/README.md"
    lower = readme.read_text().lower()
    assert "extensions" in lower, "README should document the extensions option"
    assert "mimetype" in lower, "README should document the mimeType option"
    has_compressible = "compressible" in lower
    has_charset = "charset" in lower
    assert has_compressible or has_charset, (
        "README should document at least one optional parameter (compressible or charset)"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — regression checks
# ---------------------------------------------------------------------------


# [repo_tests] pass_to_pass
def test_existing_detect_mime_type_works():
    """detectMimeType still works for built-in types after the change."""
    r = _run_ts(
        """
import { detectMimeType } from './detect-mime-type.ts'

if (detectMimeType('txt') !== 'text/plain')
    throw new Error('txt should be text/plain')
if (detectMimeType('html') !== 'text/html')
    throw new Error('html should be text/html')
if (detectMimeType('json') !== 'application/json')
    throw new Error('json should be application/json')
if (detectMimeType('unknown_ext_xyz') !== undefined)
    throw new Error('unknown should be undefined')
"""
    )
    assert r.returncode == 0, f"Regression: {r.stderr}"


# [repo_tests] pass_to_pass
def test_existing_content_type_functions_work():
    """isCompressibleMimeType and mimeTypeToContentType still work for builtins."""
    r = _run_ts(
        """
import { isCompressibleMimeType } from './is-compressible-mime-type.ts'
import { mimeTypeToContentType } from './mime-type-to-content-type.ts'

// Compressible checks
if (!isCompressibleMimeType('text/html'))
    throw new Error('text/html should be compressible')
if (!isCompressibleMimeType('application/json'))
    throw new Error('application/json should be compressible')
if (isCompressibleMimeType('image/png'))
    throw new Error('image/png should not be compressible')

// Content-Type with charset
const ct1 = mimeTypeToContentType('text/html')
if (!ct1.includes('charset'))
    throw new Error('text/html content-type should include charset')

// Content-Type without charset
const ct2 = mimeTypeToContentType('image/png')
if (ct2.includes('charset'))
    throw new Error('image/png content-type should not include charset')

// text/xml exception (no charset added)
const ct3 = mimeTypeToContentType('text/xml')
if (ct3 !== 'text/xml')
    throw new Error('text/xml should not have charset, got: ' + ct3)
"""
    )
    assert r.returncode == 0, f"Regression: {r.stderr}"


# [repo_tests] pass_to_pass
def test_repo_detect_mime_type_tests_pass():
    """detect-mime-type.ts unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test", "src/lib/detect-mime-type.test.ts"],
        capture_output=True,
        text=True,
        cwd=str(REPO / "packages/mime"),
        timeout=60,
    )
    assert r.returncode == 0, f"detect-mime-type tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_is_compressible_mime_type_tests_pass():
    """is-compressible-mime-type.ts unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test", "src/lib/is-compressible-mime-type.test.ts"],
        capture_output=True,
        text=True,
        cwd=str(REPO / "packages/mime"),
        timeout=60,
    )
    assert r.returncode == 0, f"is-compressible-mime-type tests failed:\n{r.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_repo_mime_type_to_content_type_tests_pass():
    """mime-type-to-content-type.ts unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["node", "--disable-warning=ExperimentalWarning", "--test", "src/lib/mime-type-to-content-type.test.ts"],
        capture_output=True,
        text=True,
        cwd=str(REPO / "packages/mime"),
        timeout=60,
    )
    assert r.returncode == 0, f"mime-type-to-content-type tests failed:\n{r.stderr[-500:]}"
