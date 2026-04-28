"""Behavioral checks for unity-cli-loop-fix-correct-skillmd-file-format (markdown_authoring task).

Each test asserts that a distinctive literal from the gold patch appears
in the target tier-1 file after the agent runs.
"""
from __future__ import annotations

from pathlib import Path

REPO = Path("/workspace/unity-cli-loop")


def _read(path: str) -> str:
    p = REPO / path
    assert p.is_file(), f"{p} does not exist"
    return p.read_text(encoding="utf-8", errors="replace")


def test_signal_00():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-project-info/SKILL.md')
    assert 'description: "Get Unity project information via uloop CLI. Use when you need to: (1) Check Unity Editor version, (2) Get project settings and platform info, (3) Retrieve project metadata for diagnosti' in text, "expected to find: " + 'description: "Get Unity project information via uloop CLI. Use when you need to: (1) Check Unity Editor version, (2) Get project settings and platform info, (3) Retrieve project metadata for diagnosti'[:80]


def test_signal_01():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Cli~/src/skills/skill-definitions/cli-only/uloop-get-version/SKILL.md')
    assert 'description: "Get Unity and project information via uloop CLI. Use when you need to verify Unity version, check project settings (ProductName, CompanyName, Version), or troubleshoot environment issues' in text, "expected to find: " + 'description: "Get Unity and project information via uloop CLI. Use when you need to verify Unity version, check project settings (ProductName, CompanyName, Version), or troubleshoot environment issues'[:80]


def test_signal_02():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/CaptureWindow/SKILL.md')
    assert 'description: "Take a screenshot of Unity Editor windows and save as PNG image. Use when you need to: (1) Screenshot the Game View, Scene View, Console, Inspector, or other windows, (2) Capture current' in text, "expected to find: " + 'description: "Take a screenshot of Unity Editor windows and save as PNG image. Use when you need to: (1) Screenshot the Game View, Scene View, Console, Inspector, or other windows, (2) Capture current'[:80]


def test_signal_03():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/ClearConsole/SKILL.md')
    assert 'description: "Clear Unity console logs via uloop CLI. Use when you need to: (1) Clear the console before running tests, (2) Start a fresh debugging session, (3) Clean up log output for better readabil' in text, "expected to find: " + 'description: "Clear Unity console logs via uloop CLI. Use when you need to: (1) Clear the console before running tests, (2) Start a fresh debugging session, (3) Clean up log output for better readabil'[:80]


def test_signal_04():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/Compile/SKILL.md')
    assert 'description: "Compile Unity project via uloop CLI. Use when you need to: (1) Verify C# code compiles successfully after editing scripts, (2) Check for compile errors or warnings, (3) Validate script c' in text, "expected to find: " + 'description: "Compile Unity project via uloop CLI. Use when you need to: (1) Verify C# code compiles successfully after editing scripts, (2) Check for compile errors or warnings, (3) Validate script c'[:80]


def test_signal_05():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/ControlPlayMode/SKILL.md')
    assert 'description: "Control Unity Editor play mode via uloop CLI. Use when you need to: (1) Start play mode for testing, (2) Stop play mode after testing, (3) Pause play mode for debugging."' in text, "expected to find: " + 'description: "Control Unity Editor play mode via uloop CLI. Use when you need to: (1) Start play mode for testing, (2) Stop play mode after testing, (3) Pause play mode for debugging."'[:80]


def test_signal_06():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/ExecuteDynamicCode/SKILL.md')
    assert 'description: "Execute C# code dynamically in Unity Editor via uloop CLI. Use for editor automation: (1) Prefab/material wiring and AddComponent operations, (2) Reference wiring with SerializedObject, ' in text, "expected to find: " + 'description: "Execute C# code dynamically in Unity Editor via uloop CLI. Use for editor automation: (1) Prefab/material wiring and AddComponent operations, (2) Reference wiring with SerializedObject, '[:80]


def test_signal_07():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/ExecuteMenuItem/SKILL.md')
    assert 'description: "Execute Unity MenuItem via uloop CLI. Use when you need to: (1) Trigger menu commands programmatically, (2) Automate editor actions (save, build, refresh), (3) Run custom menu items defi' in text, "expected to find: " + 'description: "Execute Unity MenuItem via uloop CLI. Use when you need to: (1) Trigger menu commands programmatically, (2) Automate editor actions (save, build, refresh), (3) Run custom menu items defi'[:80]


def test_signal_08():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/FindGameObjects/SKILL.md')
    assert 'description: "Find GameObjects with search criteria via uloop CLI. Use when you need to: (1) Locate GameObjects by name pattern, (2) Find objects by tag or layer, (3) Search for objects with specific ' in text, "expected to find: " + 'description: "Find GameObjects with search criteria via uloop CLI. Use when you need to: (1) Locate GameObjects by name pattern, (2) Find objects by tag or layer, (3) Search for objects with specific '[:80]


def test_signal_09():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/FocusUnityWindow/SKILL.md')
    assert 'description: "Bring Unity Editor window to front via uloop CLI. Use when you need to: (1) Focus Unity Editor before capturing screenshots, (2) Ensure Unity window is visible for visual checks, (3) Bri' in text, "expected to find: " + 'description: "Bring Unity Editor window to front via uloop CLI. Use when you need to: (1) Focus Unity Editor before capturing screenshots, (2) Ensure Unity window is visible for visual checks, (3) Bri'[:80]


def test_signal_10():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/GetHierarchy/SKILL.md')
    assert 'description: "Get Unity Hierarchy structure via uloop CLI. Use when you need to: (1) Inspect scene structure and GameObject tree, (2) Find GameObjects and their parent-child relationships, (3) Check c' in text, "expected to find: " + 'description: "Get Unity Hierarchy structure via uloop CLI. Use when you need to: (1) Inspect scene structure and GameObject tree, (2) Find GameObjects and their parent-child relationships, (3) Check c'[:80]


def test_signal_11():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/GetLogs/SKILL.md')
    assert 'description: "Get Unity Console output including errors, warnings, and Debug.Log messages. Use when you need to: (1) Check for compile errors or runtime exceptions after code changes, (2) See what Deb' in text, "expected to find: " + 'description: "Get Unity Console output including errors, warnings, and Debug.Log messages. Use when you need to: (1) Check for compile errors or runtime exceptions after code changes, (2) See what Deb'[:80]


def test_signal_12():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/GetMenuItems/SKILL.md')
    assert 'description: "Retrieve Unity MenuItems via uloop CLI. Use when you need to: (1) Discover available menu commands in Unity Editor, (2) Find menu paths for automation, (3) Prepare for executing menu ite' in text, "expected to find: " + 'description: "Retrieve Unity MenuItems via uloop CLI. Use when you need to: (1) Discover available menu commands in Unity Editor, (2) Find menu paths for automation, (3) Prepare for executing menu ite'[:80]


def test_signal_13():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/RunTests/SKILL.md')
    assert 'description: "Execute Unity Test Runner via uloop CLI. Use when you need to: (1) Run unit tests (EditMode tests), (2) Run integration tests (PlayMode tests), (3) Verify code changes don\'t break existi' in text, "expected to find: " + 'description: "Execute Unity Test Runner via uloop CLI. Use when you need to: (1) Run unit tests (EditMode tests), (2) Run integration tests (PlayMode tests), (3) Verify code changes don\'t break existi'[:80]


def test_signal_14():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/UnitySearch/SKILL.md')
    assert 'description: "Search Unity project via uloop CLI. Use when you need to: (1) Find assets by name or type (scenes, prefabs, scripts, materials), (2) Search for project resources using Unity\'s search sys' in text, "expected to find: " + 'description: "Search Unity project via uloop CLI. Use when you need to: (1) Find assets by name or type (scenes, prefabs, scripts, materials), (2) Search for project resources using Unity\'s search sys'[:80]


def test_signal_15():
    """Distinctive line from gold patch must be present."""
    text = _read('Packages/src/Editor/Api/McpTools/UnitySearchProviderDetails/SKILL.md')
    assert 'description: "Get Unity Search provider details via uloop CLI. Use when you need to: (1) Discover available search providers, (2) Understand search capabilities and filters, (3) Configure searches wit' in text, "expected to find: " + 'description: "Get Unity Search provider details via uloop CLI. Use when you need to: (1) Discover available search providers, (2) Understand search capabilities and filters, (3) Configure searches wit'[:80]

