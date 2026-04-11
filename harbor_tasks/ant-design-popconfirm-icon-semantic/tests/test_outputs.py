"""
Test file for ant-design Popconfirm icon semantic support PR #57528
Tests that classNames.icon and styles.icon are properly supported in Popconfirm component.
"""

import subprocess
import re
import os

REPO = "/workspace/ant-design"


def test_icon_classnames_applied():
    """
    Fail-to-pass: Verify that classNames?.icon is applied to the icon span element.
    The fix should apply clsx to combine the base class with classNames?.icon.
    """
    pure_panel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")

    with open(pure_panel_path, "r") as f:
        content = f.read()

    # Check that classNames?.icon is being used with clsx in the icon span
    assert "classNames?.icon" in content, "classNames?.icon should be referenced in PurePanel.tsx"

    # Check that clsx is used to combine the base class with classNames?.icon
    pattern = r'className=\{clsx\(`\$\{prefixCls\}-message-icon`,\s*classNames\?\.icon\)\}'
    assert re.search(pattern, content), "icon span should use clsx to apply classNames?.icon"


def test_icon_styles_applied():
    """
    Fail-to-pass: Verify that styles?.icon is applied to the icon span element.
    """
    pure_panel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")

    with open(pure_panel_path, "r") as f:
        content = f.read()

    # Check that styles?.icon is being applied to the icon span
    assert "styles?.icon" in content, "styles?.icon should be referenced in PurePanel.tsx"

    # Check the icon span has style={styles?.icon}
    pattern = r'style=\{styles\?\.icon\}'
    assert re.search(pattern, content), "icon span should have style={styles?.icon}"


def test_type_definition_includes_icon():
    """
    Fail-to-pass: Verify that PopconfirmSemanticType includes icon field in type definition.
    """
    index_path = os.path.join(REPO, "components/popconfirm/index.tsx")

    with open(index_path, "r") as f:
        content = f.read()

    # Check for PopconfirmSemanticType definition with icon field in classNames
    assert "PopconfirmSemanticType" in content, "PopconfirmSemanticType should be defined"

    # Check that icon is defined in classNames
    pattern = r'classNames\?.*icon\?:\s*string'
    assert re.search(pattern, content, re.DOTALL), "classNames should include icon?: string"

    # Check that icon is defined in styles
    pattern = r'styles\?.*icon\?:\s*React\.CSSProperties'
    assert re.search(pattern, content, re.DOTALL), "styles should include icon?: React.CSSProperties"


def test_overlay_props_use_correct_type():
    """
    Fail-to-pass: Verify that OverlayProps uses PopconfirmSemanticAllType instead of PopoverSemanticAllType.
    """
    pure_panel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")

    with open(pure_panel_path, "r") as f:
        content = f.read()

    # Should use PopconfirmSemanticAllType, not PopoverSemanticAllType
    assert "PopconfirmSemanticAllType" in content, "Should import PopconfirmSemanticAllType"

    # OverlayProps classNames and styles should reference PopconfirmSemanticAllType
    pattern = r'classNames\?:\s*PopconfirmSemanticAllType\[\'classNames\'\]'
    assert re.search(pattern, content), "OverlayProps.classNames should use PopconfirmSemanticAllType['classNames']"

    pattern = r'styles\?:\s*PopconfirmSemanticAllType\[\'styles\'\]'
    assert re.search(pattern, content), "OverlayProps.styles should use PopconfirmSemanticAllType['styles']"


def test_semantic_demo_updated():
    """
    Fail-to-pass: Verify that demo/_semantic.tsx includes icon in the semantics list.
    """
    demo_path = os.path.join(REPO, "components/popconfirm/demo/_semantic.tsx")

    with open(demo_path, "r") as f:
        content = f.read()

    # Check that icon is documented in the semantics array
    assert '{ name: \'icon\'' in content, "demo/_semantic.tsx should include icon in semantics list"


def test_repo_lint_biome():
    """Repo's Biome lint passes (pass_to_pass)."""
    r = subprocess.run(
        ["npm", "run", "lint:biome"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome lint failed:\n{r.stderr[-500:]}"


def test_repo_lint_eslint_popconfirm():
    """Repo's ESLint passes on popconfirm component (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "components/popconfirm", "--cache"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"


def test_semantic_test_file_updated():
    """
    Fail-to-pass: Verify that semantic.test.tsx includes icon in test assertions.
    """
    test_path = os.path.join(REPO, "components/popconfirm/__tests__/semantic.test.tsx")

    with open(test_path, "r") as f:
        content = f.read()

    # Check that the test file includes icon in classNames tests
    assert "icon: 'custom-icon'" in content, "semantic.test.tsx should test icon classNames"

    # Check that icon style is tested
    assert "icon: { color:" in content, "semantic.test.tsx should test icon styles"

    # Check for dynamic icon testing in function-based test
    assert "icon: 'dynamic-icon'" in content, "semantic.test.tsx should test dynamic icon classNames"


def test_repo_tests_node():
    """Repo's node tests pass (pass_to_pass)."""
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    r = subprocess.run(
        ["npm", "run", "test:node"],
        capture_output=True, text=True, timeout=180, cwd=REPO, env=env
    )
    assert r.returncode == 0, f"Node tests failed:\n{r.stderr[-1000:]}"


def test_repo_format_biome():
    """Repo's Biome format check passes on popconfirm (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "biome", "format", "components/popconfirm"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Biome format check failed:\n{r.stderr[-500:]}"
