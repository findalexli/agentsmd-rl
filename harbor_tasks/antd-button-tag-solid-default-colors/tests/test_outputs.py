"""
Test suite for antd Button and Tag solid variant default colors.

This tests that the code changes add the correct logic for default colors.
"""

import subprocess
import os

REPO = "/workspace/ant-design"


def test_button_solid_default_code():
    """Button.tsx should contain logic for solid variant default color."""
    button_file = os.path.join(REPO, "components/button/Button.tsx")
    with open(button_file, "r") as f:
        content = f.read()

    # Check that there's logic for variant === 'solid'
    assert "if (variant === 'solid')" in content, "Button.tsx missing direct variant='solid' check"


def test_button_context_solid_default_code():
    """Button.tsx should contain logic for contextVariant solid default color."""
    button_file = os.path.join(REPO, "components/button/Button.tsx")
    with open(button_file, "r") as f:
        content = f.read()

    # Check that there's logic for contextVariant === 'solid'
    assert "if (contextVariant === 'solid')" in content, "Button.tsx missing contextVariant='solid' check"


def test_tag_solid_default_code():
    """Tag useColor.ts should contain logic for solid variant default color."""
    tag_file = os.path.join(REPO, "components/tag/hooks/useColor.ts")
    with open(tag_file, "r") as f:
        content = f.read()

    # Check that there's logic for nextVariant === 'solid' and nextColor === undefined
    assert "nextVariant === 'solid'" in content, "useColor.ts missing nextVariant === 'solid' check"
    assert "nextColor === undefined" in content, "useColor.ts missing nextColor === undefined check"


def test_tag_uses_nextcolor_for_preset():
    """Tag useColor.ts should use nextColor for isPresetColor check."""
    tag_file = os.path.join(REPO, "components/tag/hooks/useColor.ts")
    with open(tag_file, "r") as f:
        content = f.read()

    assert "isPresetColor(nextColor)" in content, "useColor.ts should use nextColor for isPresetColor"


def test_tag_uses_nextcolor_for_status():
    """Tag useColor.ts should use nextColor for isPresetStatusColor check."""
    tag_file = os.path.join(REPO, "components/tag/hooks/useColor.ts")
    with open(tag_file, "r") as f:
        content = f.read()

    assert "isPresetStatusColor(nextColor)" in content, "useColor.ts should use nextColor for isPresetStatusColor"


def test_button_returns_primary_for_solid():
    """Button.tsx should return ['primary', variant] for solid variant."""
    button_file = os.path.join(REPO, "components/button/Button.tsx")
    with open(button_file, "r") as f:
        content = f.read()

    # Should return ['primary', variant] or ['primary', contextVariant]
    assert "['primary', variant]" in content or "['primary', contextVariant]" in content, \
        "Button.tsx should return 'primary' as default color for solid variant"


def test_tag_returns_default_for_solid():
    """Tag useColor.ts should set nextColor = 'default' for solid variant."""
    tag_file = os.path.join(REPO, "components/tag/hooks/useColor.ts")
    with open(tag_file, "r") as f:
        content = f.read()

    assert "nextColor = 'default'" in content, "useColor.ts should set nextColor = 'default' for solid variant"


def test_repo_typescript_compiles():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "tsc"],
        capture_output=True, text=True, timeout=600, cwd=REPO, env={
            **os.environ,
            "NODE_OPTIONS": "--max-old-space-size=4096"
        }
    )
    assert r.returncode == 0, f"TypeScript compilation failed:\n{r.stderr[-500:]}"


def test_button_structure_preserved():
    """Button.tsx should maintain its basic component structure."""
    button_file = os.path.join(REPO, "components/button/Button.tsx")
    with open(button_file, "r") as f:
        content = f.read()

    # Basic structure checks
    assert "React.forwardRef" in content, "Button should use forwardRef"
    assert "InternalCompoundedButton" in content or "const Button" in content, "Button should define component"
    assert "variant" in content, "Button should handle variant prop"
    assert "color" in content, "Button should handle color prop"


def test_repo_lint_passes():
    """Repo's ESLint checks pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:script"],
        capture_output=True, text=True, timeout=300, cwd=REPO
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}"


def test_repo_button_tests_pass():
    """Repo's Button component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=button/__tests__/index", "--maxWorkers=1", "--silent"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env={
            **os.environ,
            "CI": "true",
            "SKIP_SEMANTIC": "1"
        }
    )
    assert r.returncode == 0, f"Button tests failed:\n{r.stderr[-500:]}"


def test_repo_tag_tests_pass():
    """Repo's Tag component tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=tag/__tests__/index", "--maxWorkers=1", "--silent"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env={
            **os.environ,
            "CI": "true",
            "SKIP_SEMANTIC": "1"
        }
    )
    assert r.returncode == 0, f"Tag tests failed:\n{r.stderr[-500:]}"
