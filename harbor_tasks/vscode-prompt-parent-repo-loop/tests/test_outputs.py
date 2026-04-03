"""
Task: vscode-prompt-parent-repo-loop
Repo: microsoft/vscode @ 68cb51843c3f0f4e551479f825d18c954e88c778

Fix: Prevent infinite loop in findParentRepoFolders when walking up
directory tree by checking for filesystem root (fixed-point of dirname)
and deduplicating the termination conditions.

All checks must pass for reward = 1. Any failure = reward 0.
"""

from pathlib import Path

REPO = "/workspace/vscode"
TARGET = f"{REPO}/src/vs/workbench/contrib/chat/common/promptSyntax/utils/promptFilesLocator.ts"


def test_file_exists():
    """Target file must exist."""
    assert Path(TARGET).exists()


def test_while_true_loop():
    """Should use while(true) instead of do-while for clearer termination."""
    src = Path(TARGET).read_text()
    assert "while (true)" in src or "while(true)" in src, \
        "Should use while(true) loop"


def test_dirname_fixed_point_check():
    """Should check for dirname fixed-point (filesystem root)."""
    src = Path(TARGET).read_text()
    assert "isEqual(current, parent)" in src, \
        "Should check if dirname(current) == current (filesystem root)"


def test_root_path_check():
    """Should check for root path '/'."""
    src = Path(TARGET).read_text()
    assert "current.path === '/'" in src or "path === '/'" in src, \
        "Should check for root path '/'"


def test_seen_set_check():
    """Should check seen set to prevent revisiting."""
    src = Path(TARGET).read_text()
    assert "seen.has(parent)" in src, \
        "Should check seen set for parent"


def test_break_instead_of_dowhile():
    """Should use break statement to exit loop."""
    src = Path(TARGET).read_text()
    # Find the while(true) and verify there's a break
    in_loop = False
    has_break = False
    for line in src.split('\n'):
        if 'while (true)' in line or 'while(true)' in line:
            in_loop = True
        if in_loop and 'break' in line:
            has_break = True
            break
    assert has_break, "Should have break statement in while(true) loop"


def test_dirname_called_inside_loop():
    """dirname should be called inside the loop (moved from do-while condition)."""
    src = Path(TARGET).read_text()
    # The parent should be computed inside the loop body
    assert "const parent = dirname(current)" in src or \
           "parent = dirname(current)" in src, \
        "dirname(current) should be computed inside loop body"
