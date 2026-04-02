"""
Task: vscode-titlebar-scoped-editor-service
Repo: microsoft/vscode @ bb01c58f40788bb80f069f73613f13c12af7566a
PR:   N/A (inverse of #306699 which introduced the scoped service)

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

The fix removes an unnecessary scoped IEditorService from BrowserTitlebarPart,
simplifying DI injection and fixing a stale active-editor check.
"""

import re
from pathlib import Path

REPO = "/workspace/vscode"
FILE = Path(REPO) / "src/vs/workbench/browser/parts/titlebar/titlebarPart.ts"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core structural changes from the fix
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
# AST-only because: TypeScript source, cannot execute without tsc compilation
def test_servicecollection_import_removed():
    """ServiceCollection import must be removed — it was only used for the scoped child service."""
    content = FILE.read_text()
    assert "ServiceCollection" not in content, (
        "ServiceCollection should be removed from imports: the scoped child instantiation "
        "service that required it has been eliminated"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript source, cannot execute without tsc compilation
def test_scoped_editor_service_removed():
    """createScoped() call must be removed — titlebar should use the injected editorService directly."""
    content = FILE.read_text()
    assert "createScoped" not in content, (
        "editorService.createScoped() should not be called in the titlebar; "
        "the scoped editor service added unnecessary indirection"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript source, cannot execute without tsc compilation
def test_active_editor_check_uses_editor_service():
    """Active editor check must use editorService.activeEditor, not editorGroupsContainer.activeGroup.activeEditor."""
    content = FILE.read_text()
    # Old pattern: this.editorGroupsContainer.activeGroup.activeEditor !== undefined
    assert "editorGroupsContainer.activeGroup.activeEditor" not in content, (
        "Should not check active editor via editorGroupsContainer.activeGroup.activeEditor "
        "(can return stale results in multi-group configs)"
    )
    # New pattern must be present
    assert "editorService.activeEditor" in content, (
        "Should check active editor via this.editorService.activeEditor "
        "(canonical IEditorService API)"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript source, cannot execute without tsc compilation
def test_instantiation_service_assignment_removed():
    """The manual this.instantiationService = this._register(...createChild...) assignment must be gone."""
    content = FILE.read_text()
    # Base commit has: this.instantiationService = this._register(instantiationService.createChild(
    assert "this.instantiationService = this._register(" not in content, (
        "Constructor should not manually assign this.instantiationService via createChild(); "
        "instantiationService should be injected directly via 'protected readonly' constructor param"
    )


# [pr_diff] fail_to_pass
# AST-only because: TypeScript source, cannot execute without tsc compilation
def test_editor_service_constructor_param_private_readonly():
    """editorService constructor parameter must be declared 'private readonly' (not a bare local)."""
    content = FILE.read_text()
    # After fix: @IEditorService private readonly editorService: IEditorService
    assert re.search(
        r"@IEditorService\s+private\s+readonly\s+editorService", content
    ), (
        "The @IEditorService constructor parameter should be 'private readonly editorService' "
        "so it is stored directly on the instance without needing a scoped wrapper"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — file integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
# AST-only because: TypeScript source, cannot execute without tsc compilation
def test_file_exists_and_non_trivial():
    """titlebarPart.ts must exist and still contain the BrowserTitlebarPart class."""
    assert FILE.exists(), "titlebarPart.ts must exist"
    content = FILE.read_text()
    assert len(content) > 10_000, (
        f"File appears truncated or emptied ({len(content)} chars); "
        "BrowserTitlebarPart implementation must remain intact"
    )
    assert "class BrowserTitlebarPart" in content, (
        "BrowserTitlebarPart class definition must still be present"
    )
    assert "IEditorService" in content, (
        "IEditorService import/usage must still exist in the file"
    )
