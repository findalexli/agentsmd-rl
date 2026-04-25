"""
Test harness for mantinedev/mantine#8522 - SSR fix for Tooltip and related components

The PR fixes SSR errors in Next.js App Router where components like Tooltip,
Popover.Target, HoverCard.Target, and MenuTarget fail because children can be
a React Lazy type that lacks a props field and cannot be used with cloneElement.

The fix introduces getSingleElementChild which uses Children.toArray to handle
these cases properly.
"""

import subprocess
import os
import sys

REPO = "/workspace/mantine"
os.chdir(REPO)


def run(cmd, **kwargs):
    result = subprocess.run(cmd, **kwargs)
    return result


def test_get_single_element_child_file_exists():
    """The getSingleElementChild utility file was created."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/core/utils/get-single-element-child/get-single-element-child.ts"
    )
    assert os.path.exists(path), f"getSingleElementChild file should exist at {path}"
    with open(path) as f:
        content = f.read()
    assert "Children.toArray" in content, "Should use Children.toArray"
    assert "export function getSingleElementChild" in content, "Should export the function"


def test_core_package_exports():
    """The core package exports getSingleElementChild."""
    index_path = os.path.join(REPO, "packages/@mantine/core/src/core/utils/index.ts")
    with open(index_path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "getSingleElementChild should be exported from core utils"


def test_popover_target_uses_fix():
    """PopoverTarget component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/Popover/PopoverTarget/PopoverTarget.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "PopoverTarget should use getSingleElementChild"


def test_tooltip_uses_fix():
    """Tooltip component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/Tooltip/Tooltip.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "Tooltip should use getSingleElementChild"


def test_tooltip_floating_uses_fix():
    """TooltipFloating component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/Tooltip/TooltipFloating/TooltipFloating.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "TooltipFloating should use getSingleElementChild"


def test_menu_target_uses_fix():
    """MenuTarget component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/Menu/MenuTarget/MenuTarget.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "MenuTarget should use getSingleElementChild"


def test_hovercard_target_uses_fix():
    """HoverCardTarget component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/HoverCard/HoverCardTarget/HoverCardTarget.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "HoverCardTarget should use getSingleElementChild"


def test_combobox_target_uses_fix():
    """ComboboxTarget component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/Combobox/ComboboxTarget/ComboboxTarget.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "ComboboxTarget should use getSingleElementChild"


def test_combobox_events_target_uses_fix():
    """ComboboxEventsTarget component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/Combobox/ComboboxEventsTarget/ComboboxEventsTarget.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "ComboboxEventsTarget should use getSingleElementChild"


def test_focus_trap_uses_fix():
    """FocusTrap component uses getSingleElementChild."""
    path = os.path.join(
        REPO,
        "packages/@mantine/core/src/components/FocusTrap/FocusTrap.tsx"
    )
    with open(path) as f:
        content = f.read()
    assert "getSingleElementChild" in content, "FocusTrap should use getSingleElementChild"


def test_tooltip_tests_pass():
    """Tooltip tests pass (pass_to_pass - repo's own tests)."""
    r = run(
        ["npm", "run", "jest", "--", "--testPathPatterns", "Tooltip", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Tooltip tests failed:\n{r.stdout[-500:]}"


def test_popover_tests_pass():
    """Popover tests pass (pass_to_pass - repo's own tests)."""
    r = run(
        ["npm", "run", "jest", "--", "--testPathPatterns", "Popover", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Popover tests failed:\n{r.stdout[-500:]}"


def test_menu_tests_pass():
    """Menu tests pass (pass_to_pass - repo's own tests)."""
    r = run(
        ["npm", "run", "jest", "--", "--testPathPatterns", "Menu.test", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Menu tests failed:\n{r.stdout[-500:]}"


def test_combobox_tests_pass():
    """Combobox tests pass (pass_to_pass - repo's own tests)."""
    r = run(
        ["npm", "run", "jest", "--", "--testPathPatterns", "Combobox.test", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"Combobox tests failed:\n{r.stdout[-500:]}"


def test_hovercard_tests_pass():
    """HoverCard tests pass (pass_to_pass - repo's own tests)."""
    r = run(
        ["npm", "run", "jest", "--", "--testPathPatterns", "HoverCard.test", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert r.returncode == 0, f"HoverCard tests failed:\n{r.stdout[-500:]}"


def test_repo_typecheck():
    """TypeScript typecheck passes (pass_to_pass)."""
    r = run(
        ["npx", "tsc", "--noEmit"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_eslint():
    """ESLint passes on packages (pass_to_pass)."""
    r = run(
        ["npx", "eslint", "packages", "--cache"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=600
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    tests = [
        test_get_single_element_child_file_exists,
        test_core_package_exports,
        test_popover_target_uses_fix,
        test_tooltip_uses_fix,
        test_tooltip_floating_uses_fix,
        test_menu_target_uses_fix,
        test_hovercard_target_uses_fix,
        test_combobox_target_uses_fix,
        test_combobox_events_target_uses_fix,
        test_focus_trap_uses_fix,
        test_tooltip_tests_pass,
        test_popover_tests_pass,
        test_menu_tests_pass,
        test_combobox_tests_pass,
        test_hovercard_tests_pass,
        test_repo_typecheck,
        test_repo_eslint,
    ]

    failed = []
    for test in tests:
        print(f"Running {test.__name__}...", end=" ")
        try:
            test()
            print("PASSED")
        except Exception as e:
            print(f"FAILED: {e}")
            failed.append(test.__name__)

    if failed:
        print(f"\n{len(failed)} tests failed:")
        for name in failed:
            print(f"  - {name}")
        sys.exit(1)
    else:
        print("\nAll tests passed!")
        sys.exit(0)