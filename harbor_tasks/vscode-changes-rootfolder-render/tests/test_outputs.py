"""
Task: vscode-changes-rootfolder-render
Repo: microsoft/vscode @ 3c51a00d738294aa6e113b87e38b8ea770fbf9ee

Fix: Add root folder rendering to Changes View tree, support workspace
files without git repos, and add 'none' change type for unchanged files.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/sessions/contrib/changes/browser/changesView.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_root_type_added():
    """ChangeType should include 'root' type or IChangesRootItem interface."""
    src = Path(TARGET).read_text()
    assert "IChangesRootItem" in src or "'root'" in src, \
        "Should define IChangesRootItem or root type"


def test_none_change_type():
    """ChangeType should include 'none' for unchanged files."""
    src = Path(TARGET).read_text()
    assert "'none'" in src, "ChangeType should include 'none'"


def test_is_changes_root_item():
    """isChangesRootItem type guard function should exist."""
    src = Path(TARGET).read_text()
    assert "isChangesRootItem" in src, \
        "isChangesRootItem function should be defined"


def test_build_tree_children_accepts_root_info():
    """buildTreeChildren should accept optional treeRootInfo parameter."""
    src = Path(TARGET).read_text()
    assert "treeRootInfo" in src, \
        "buildTreeChildren should accept treeRootInfo"


def test_workspace_files_observable():
    """activeSessionWorkspaceFilesObs should be defined for non-git workspaces."""
    src = Path(TARGET).read_text()
    assert "activeSessionWorkspaceFilesObs" in src or "WorkspaceFiles" in src, \
        "Should have workspace files observable"


def test_render_root_element():
    """renderRootElement method should exist for rendering root folder."""
    src = Path(TARGET).read_text()
    assert "renderRootElement" in src, \
        "renderRootElement method should be defined"


def test_file_service_injected():
    """IFileService should be injected for collecting workspace files."""
    src = Path(TARGET).read_text()
    assert "IFileService" in src, \
        "IFileService should be imported/injected"
