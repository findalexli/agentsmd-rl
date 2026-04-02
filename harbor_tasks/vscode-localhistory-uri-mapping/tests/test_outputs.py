"""
Task: vscode-localhistory-uri-mapping
Repo: microsoft/vscode @ 8c61afa3677cb13ce3071eac5326312fc4d2193a

Fix: findLocalHistoryEntry must map vscode-local-history scheme URIs back to
the original file URI before calling getEntries, so that local history commands
work when triggered from a diff editor.

AST-only because: TypeScript cannot be imported into Python; VS Code has
massive dep graph. All checks use file content inspection via subprocess/read.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = Path(REPO) / "src/vs/workbench/contrib/localHistory/browser/localHistoryCommands.ts"


def _read() -> str:
    return TARGET.read_text(encoding="utf-8")


def _extract_function(src: str) -> str:
    """Extract the body of the findLocalHistoryEntry function."""
    marker = "findLocalHistoryEntry("
    start = src.find(marker)
    assert start != -1, "findLocalHistoryEntry not found in file"
    brace_start = src.index("{", start)
    depth = 0
    i = brace_start
    while i < len(src):
        if src[i] == "{":
            depth += 1
        elif src[i] == "}":
            depth -= 1
            if depth == 0:
                return src[brace_start : i + 1]
        i += 1
    return src[brace_start:]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — URI scheme mapping
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_scheme_check_in_findLocalHistoryEntry():
    """findLocalHistoryEntry must check for LocalHistoryFileSystemProvider.SCHEMA before querying history."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    assert "LocalHistoryFileSystemProvider.SCHEMA" in func, (
        "findLocalHistoryEntry does not check uri.scheme against "
        "LocalHistoryFileSystemProvider.SCHEMA"
    )


# [pr_diff] fail_to_pass
def test_uri_remapped_via_fromLocalHistoryFileSystem():
    """findLocalHistoryEntry must call fromLocalHistoryFileSystem to remap the URI."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    assert "fromLocalHistoryFileSystem" in func, (
        "fromLocalHistoryFileSystem not found in findLocalHistoryEntry; "
        "URI is not being remapped from the vscode-local-history scheme"
    )


# [pr_diff] fail_to_pass
def test_getEntries_not_called_with_descriptor_uri_directly():
    """getEntries must not be called with descriptor.uri — it must use the (possibly remapped) variable."""
    # AST-only because: TypeScript file, cannot be imported
    # Base commit: getEntries(descriptor.uri, CancellationToken.None)
    # After fix:   let uri = descriptor.uri; ... getEntries(uri, CancellationToken.None)
    func = _extract_function(_read())
    assert "getEntries(descriptor.uri," not in func, (
        "getEntries is still called with descriptor.uri directly. "
        "The fix should reassign to a local 'uri' variable that may be remapped."
    )


# [pr_diff] fail_to_pass
def test_associatedResource_used_for_original_uri():
    """The fix must use .associatedResource to extract the original file URI from the local history URI."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    assert "associatedResource" in func, (
        ".associatedResource not found in findLocalHistoryEntry; "
        "the fix must call fromLocalHistoryFileSystem(uri).associatedResource to get the original file URI"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_getEntries_still_called_in_function():
    """getEntries must still be called inside findLocalHistoryEntry after the fix."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    assert "getEntries(" in func, (
        "getEntries call is missing from findLocalHistoryEntry — fix accidentally removed core logic"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md @ 8c61afa3677cb13ce3071eac5326312fc4d2193a
def test_uses_schema_constant_not_hardcoded_string():
    """The fix must use LocalHistoryFileSystemProvider.SCHEMA constant, not a hardcoded string literal."""
    # AST-only because: TypeScript file, cannot be imported
    # copilot-instructions.md line ~162: "Do not use magic strings; use constants"
    func = _extract_function(_read())
    # Allow the string in comments only; reject it in code lines
    code_lines = [
        ln for ln in func.splitlines()
        if not ln.strip().startswith("//") and not ln.strip().startswith("*")
    ]
    code = "\n".join(code_lines)
    assert '"vscode-local-history"' not in code, (
        "Hardcoded 'vscode-local-history' string literal found in findLocalHistoryEntry. "
        "Use LocalHistoryFileSystemProvider.SCHEMA constant instead."
    )
