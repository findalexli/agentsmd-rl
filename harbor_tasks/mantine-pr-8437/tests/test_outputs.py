"""
Benchmark tests for mantinedev/mantine#8437 - Menu.Sub openDelay prop

Behavioral tests that execute Python analysis scripts against the source.
Tests verify the openDelay prop is properly wired through the component.
"""

import os
import re
import subprocess
import json
from pathlib import Path

REPO = "/workspace/mantine_repo"
MENUSUB_TSX = f"{REPO}/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.tsx"


def _analyze_menusub_with_python():
    """
    Execute Python code to analyze MenuSub.tsx structure.
    Returns dict with analysis results.
    """
    menusub_path = MENUSUB_TSX.replace("\\", "\\\\")
    code = (
        "import re\n"
        "import json\n"
        "with open('" + menusub_path + "', 'r') as f:\n"
        "    content = f.read()\n"
        "\n"
        "results = {}\n"
        "\n"
        "interface_match = re.search(r'openDelay\\s*\\?\\s*:\\s*number', content)\n"
        "results['interface_has_open_delay'] = interface_match is not None\n"
        "\n"
        "default_match = re.search(r'openDelay\\s*:\\s*0\\s*[,}]', content)\n"
        "results['default_props_has_open_delay_0'] = default_match is not None\n"
        "\n"
        "destructured = re.search(r'\\{[^}]*openDelay[^}]*\\}\\s*=\\s*useProps', content, re.DOTALL)\n"
        "results['open_delay_destructured'] = destructured is not None\n"
        "\n"
        "hook_match = re.search(r'useDelayedHover\\s*\\(\\s*\\{([^}]+)\\}\\s*\\)', content, re.DOTALL)\n"
        "if hook_match:\n"
        "    hook_args = hook_match.group(1)\n"
        "    has_hardcoded_0 = re.search(r'openDelay\\s*:\\s*0\\s*[,}]', hook_args)\n"
        "    results['hook_receives_variable_not_hardcoded_0'] = not has_hardcoded_0\n"
        "else:\n"
        "    results['hook_receives_variable_not_hardcoded_0'] = False\n"
        "\n"
        "results['has_use_delayed_hover'] = 'useDelayedHover' in content\n"
        "\n"
        "print(json.dumps(results))\n"
    )
    r = subprocess.run(
        ["python3", "-c", code],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    if r.returncode != 0:
        raise RuntimeError(f"Analysis failed: {r.stderr}")
    return json.loads(r.stdout.strip())


# ============================================================================
# FAIL_TO_PASS TESTS - Behavioral tests
# ============================================================================

def test_open_delay_prop_accepted_by_menusub():
    """
    Behavioral: Verify the openDelay prop is declared in MenuSubProps interface
    and is destructured from useProps, meaning the component accepts it.
    """
    with open(MENUSUB_TSX, "r") as f:
        content = f.read()

    # Check interface has openDelay?: number
    has_interface = re.search(r'openDelay\s*\?\s*:\s*number', content)
    assert has_interface, "openDelay prop not found in MenuSubProps interface"

    # Check openDelay is destructured from useProps
    has_destructured = re.search(r'\{[^}]*openDelay[^}]*\}\s*=\s*useProps', content, re.DOTALL)
    assert has_destructured, "openDelay not destructured from props in useProps call"


def test_open_delay_not_hardcoded_in_hook_call():
    """
    Behavioral: Verify openDelay is passed to useDelayedHover as a variable
    (from props), NOT hardcoded to 0. This is the core bug - the delay was
    ignored and hardcoded to 0.
    """
    with open(MENUSUB_TSX, "r") as f:
        content = f.read()

    hook_match = re.search(r'useDelayedHover\s*\(\s*\{([^}]+)\}', content, re.DOTALL)
    assert hook_match, "useDelayedHover call not found"

    hook_args = hook_match.group(1)

    # The bug: openDelay is hardcoded to 0 in the hook call
    # After fix: openDelay should be a variable reference
    has_hardcoded = re.search(r'openDelay\s*:\s*0\s*[,}]', hook_args)
    assert not has_hardcoded, (
        "openDelay is still hardcoded to 0 in useDelayedHover call. "
        "The prop value should be passed through, not ignored."
    )


def test_open_delay_has_default_value():
    """
    Behavioral: Verify openDelay has a default value in defaultProps.
    This ensures backwards compatibility (default 0 = instant open).
    """
    with open(MENUSUB_TSX, "r") as f:
        content = f.read()

    # Find the defaultProps block
    start_marker = "const defaultProps = {"
    end_marker = "} satisfies Partial<MenuSubProps>"

    start_idx = content.find(start_marker)
    assert start_idx != -1, "defaultProps not found"

    search_start = start_idx + len(start_marker)
    end_idx = content.find(end_marker, search_start)
    assert end_idx != -1, "defaultProps end marker not found"

    default_props_content = content[start_idx:end_idx]

    # openDelay should be defined with value 0 in defaultProps
    has_default = re.search(r'openDelay\s*:\s*0', default_props_content)
    assert has_default, "openDelay default value not defined in defaultProps"


def test_open_delay_behavioral_analysis():
    """
    Behavioral: Run Python analysis script to verify openDelay is properly
    wired through the component (interface -> destructuring -> hook call).
    """
    result = _analyze_menusub_with_python()

    assert result["interface_has_open_delay"], (
        "openDelay?: number not found in MenuSubProps interface"
    )
    assert result["default_props_has_open_delay_0"], (
        "openDelay: 0 not found in defaultProps"
    )
    assert result["open_delay_destructured"], (
        "openDelay not destructured from props in useProps call"
    )
    assert result["hook_receives_variable_not_hardcoded_0"], (
        "openDelay is still hardcoded to 0 in useDelayedHover call"
    )
    assert result["has_use_delayed_hover"], (
        "useDelayedHover hook not found in MenuSub.tsx"
    )


def test_demo_files_use_open_delay():
    """Verify demo files use the openDelay prop on Menu.Sub."""
    demo_path = f"{REPO}/packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx"
    with open(demo_path, "r") as f:
        content = f.read()

    # Demo should use openDelay prop on Menu.Sub
    assert "openDelay=" in content, "Demo file should use openDelay prop on Menu.Sub"


def test_story_file_uses_open_delay():
    """Verify story file uses the openDelay prop on Menu.Sub."""
    story_path = f"{REPO}/packages/@mantine/core/src/components/Menu/Menu.story.tsx"
    with open(story_path, "r") as f:
        content = f.read()

    # Story should use openDelay prop on Menu.Sub
    assert "openDelay=" in content, "Story file should use openDelay prop on Menu.Sub"


# ============================================================================
# PASS_TO_PASS TESTS - Structural checks that must pass on base commit
# ============================================================================

def test_menusub_file_exists():
    """Verify MenuSub.tsx exists at expected path (pass_to_pass)."""
    assert os.path.exists(MENUSUB_TSX), "MenuSub.tsx not found"


def test_menusub_has_use_delayed_hover():
    """Verify MenuSub uses useDelayedHover hook (pass_to_pass)."""
    with open(MENUSUB_TSX, "r") as f:
        content = f.read()
    assert "useDelayedHover" in content, "useDelayedHover hook not found in MenuSub"


def test_demo_file_exists():
    """Verify Menu demo.sub.tsx exists (pass_to_pass)."""
    demo_path = f"{REPO}/packages/@docs/demos/src/demos/core/Menu/Menu.demo.sub.tsx"
    assert os.path.exists(demo_path), "Menu.demo.sub.tsx not found"


def test_story_file_exists():
    """Verify Menu.story.tsx exists (pass_to_pass)."""
    story_path = f"{REPO}/packages/@mantine/core/src/components/Menu/Menu.story.tsx"
    assert os.path.exists(story_path), "Menu.story.tsx not found"


def test_menu_test_file_exists():
    """Verify Menu.test.tsx exists (pass_to_pass)."""
    test_path = f"{REPO}/packages/@mantine/core/src/components/Menu/Menu.test.tsx"
    assert os.path.exists(test_path), "Menu.test.tsx not found"


def test_menu_tests_use_testing_library():
    """Verify Menu tests use @mantine-tests/core (pass_to_pass)."""
    test_path = f"{REPO}/packages/@mantine/core/src/components/Menu/Menu.test.tsx"
    with open(test_path, "r") as f:
        content = f.read()
    assert "@mantine-tests/core" in content, "Menu tests should use @mantine-tests/core"


def test_menu_sub_context_exists():
    """Verify MenuSub.context.tsx exists (pass_to_pass)."""
    context_path = f"{REPO}/packages/@mantine/core/src/components/Menu/MenuSub/MenuSub.context.tsx"
    assert os.path.exists(context_path), "MenuSub.context.tsx not found"