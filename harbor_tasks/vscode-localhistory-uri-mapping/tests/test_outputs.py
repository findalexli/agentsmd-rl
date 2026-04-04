"""
Task: vscode-localhistory-uri-mapping
Repo: microsoft/vscode @ 8c61afa3677cb13ce3071eac5326312fc4d2193a
PR:   306147

Fix: findLocalHistoryEntry must map vscode-local-history scheme URIs back to
the original file URI before calling getEntries, so that local history commands
work when triggered from a diff editor.

AST-only because: TypeScript cannot be imported into Python; VS Code has
massive dep graph. All checks use file content inspection.
"""

import re
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


def _code_lines(func_body: str) -> str:
    """Return only non-comment code lines from a function body."""
    lines = []
    for ln in func_body.splitlines():
        stripped = ln.strip()
        if stripped.startswith("//") or stripped.startswith("*") or stripped.startswith("/*"):
            continue
        lines.append(ln)
    return "\n".join(lines)


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
        "the fix must call fromLocalHistoryFileSystem(uri).associatedResource "
        "to get the original file URI"
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
        "getEntries call is missing from findLocalHistoryEntry — "
        "fix accidentally removed core logic"
    )


# [static] pass_to_pass
def test_function_signature_unchanged():
    """findLocalHistoryEntry function signature must not be altered."""
    # AST-only because: TypeScript file, cannot be imported
    src = _read()
    sig_pattern = (
        r"export\s+async\s+function\s+findLocalHistoryEntry\s*\("
        r"\s*workingCopyHistoryService\s*:\s*IWorkingCopyHistoryService\s*,"
        r"\s*descriptor\s*:\s*ITimelineCommandArgument\s*\)"
    )
    assert re.search(sig_pattern, src), (
        "findLocalHistoryEntry function signature has been altered; "
        "only the body should change"
    )


# ---------------------------------------------------------------------------
# Config-derived (agent_config)
# ---------------------------------------------------------------------------

# [agent_config] fail_to_pass — .github/copilot-instructions.md:140 @ 8c61afa
def test_uses_schema_constant_not_hardcoded_string():
    """The fix must use LocalHistoryFileSystemProvider.SCHEMA constant, not a hardcoded string literal."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    code = _code_lines(func)
    # Check multiple possible hardcoded variants
    for variant in ['"vscode-local-history"', "'vscode-local-history'"]:
        assert variant not in code, (
            f"Hardcoded {variant} string literal found in findLocalHistoryEntry. "
            "Use LocalHistoryFileSystemProvider.SCHEMA constant instead."
        )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:131 @ 8c61afa
def test_no_then_chains_in_fix():
    """Fix must use async/await, not .then() chains for the new getEntries call."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    code = _code_lines(func)
    # The getEntries call should use await, not .then()
    assert ".then(" not in code, (
        "Found .then() chain in findLocalHistoryEntry. "
        "Prefer async/await over Promise.then() per copilot-instructions.md."
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:140 @ 8c61afa
def test_no_any_unknown_in_fix():
    """Fix must not introduce any/unknown type annotations."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    code = _code_lines(func)
    # Check for explicit 'any' or 'unknown' type annotations in the function
    any_pattern = re.compile(r":\s*any\b|as\s+any\b")
    unknown_pattern = re.compile(r":\s*unknown\b|as\s+unknown\b")
    assert not any_pattern.search(code), (
        "Found 'any' type annotation in findLocalHistoryEntry. "
        "Do not use any/unknown unless absolutely necessary."
    )
    assert not unknown_pattern.search(code), (
        "Found 'unknown' type annotation in findLocalHistoryEntry. "
        "Do not use any/unknown unless absolutely necessary."
    )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:72 @ 8c61afa
def test_uses_tabs_not_spaces():
    """New lines added by the fix must use tabs for indentation, not spaces."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    lines = func.splitlines()
    for ln in lines:
        stripped = ln.lstrip()
        if not stripped or stripped.startswith("//") or stripped.startswith("*"):
            continue
        leading = ln[: len(ln) - len(ln.lstrip())]
        if leading:
            assert "\t" in leading and "    " not in leading, (
                f"Found space-indented line in findLocalHistoryEntry: {ln!r}. "
                "VS Code uses tabs, not spaces."
            )


# [agent_config] pass_to_pass — .github/copilot-instructions.md:113 @ 8c61afa
def test_conditionals_have_curly_braces():
    """if/else blocks in the fix must use curly braces."""
    # AST-only because: TypeScript file, cannot be imported
    func = _extract_function(_read())
    code = _code_lines(func)
    # Find if statements not followed by { on same line
    for ln in code.splitlines():
        stripped = ln.strip()
        if re.match(r"^(if|else if)\s*\(.*\)\s*$", stripped):
            assert False, (
                f"Found if/else without curly brace on same line: {stripped!r}. "
                "Always surround conditional bodies with curly braces."
            )
