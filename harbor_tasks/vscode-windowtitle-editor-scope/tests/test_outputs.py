"""
Task: vscode-windowtitle-editor-scope
Repo: microsoft/vscode @ c2016b08f5d48a676858f04907c2b1c10ab03a44

Fix: Scope the editor service in BrowserTitlebarPart to its own editor
groups container, preventing the main window title from showing editors
that were moved to auxiliary windows.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/browser/parts/titlebar/titlebarPart.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_service_collection_imported():
    """ServiceCollection should be imported for creating scoped services."""
    src = Path(TARGET).read_text()
    assert "ServiceCollection" in src, \
        "ServiceCollection should be imported"


def test_scoped_editor_service_created():
    """A scoped editor service should be created with createScoped."""
    src = Path(TARGET).read_text()
    assert "createScoped" in src, \
        "Should call editorService.createScoped"


def test_child_instantiation_service():
    """Should create child instantiation service with scoped editor service."""
    src = Path(TARGET).read_text()
    assert "createChild" in src, \
        "Should call instantiationService.createChild"


def test_editor_service_in_service_collection():
    """IEditorService should be overridden in the child service collection."""
    src = Path(TARGET).read_text()
    assert "IEditorService" in src and "ServiceCollection" in src, \
        "Should put IEditorService in ServiceCollection"


def test_instantiation_service_field():
    """instantiationService should be a field (protected readonly)."""
    src = Path(TARGET).read_text()
    assert "protected readonly instantiationService" in src or \
           "protected instantiationService" in src or \
           "readonly instantiationService: IInstantiationService" in src, \
        "instantiationService should be a protected/readonly field"


def test_active_group_editor_check():
    """Should use editorGroupsContainer.activeGroup.activeEditor instead of editorService.activeEditor."""
    src = Path(TARGET).read_text()
    assert "editorGroupsContainer.activeGroup.activeEditor" in src or \
           "this.editorGroupsContainer.activeGroup.activeEditor" in src, \
        "Should check activeGroup.activeEditor instead of editorService.activeEditor"
