"""
Tests for ant-design Popconfirm icon semantic support.

This validates that the Popconfirm component properly supports classNames.icon
and styles.icon for semantic styling of the confirmation icon element.
"""

import subprocess
import os
import json

REPO = "/workspace/ant-design"


def test_repo_jest_popconfirm():
    """Jest tests pass for popconfirm component (pass_to_pass)."""
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns=components/popconfirm/__tests__", "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    assert result.returncode == 0, f"Jest tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_popconfirm_semantic_type_has_icon():
    """PopconfirmSemanticType includes icon in classNames (fail_to_pass)."""
    index_path = os.path.join(REPO, "components/popconfirm/index.tsx")
    with open(index_path, "r") as f:
        content = f.read()

    # The fix should add icon to the PopconfirmSemanticType
    assert "classNames?" in content and "icon?: string" in content, (
        "PopconfirmSemanticType must include 'icon?: string' in classNames"
    )
    assert "styles?" in content and "icon?: React.CSSProperties" in content, (
        "PopconfirmSemanticType must include 'icon?: React.CSSProperties' in styles"
    )


def test_purepanel_applies_classnames_icon():
    """PurePanel applies classNames?.icon to icon span (fail_to_pass)."""
    purepanel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")
    with open(purepanel_path, "r") as f:
        content = f.read()

    # The icon span should use clsx with classNames?.icon
    assert "classNames?.icon" in content, (
        "PurePanel must apply classNames?.icon to the icon element"
    )


def test_purepanel_applies_styles_icon():
    """PurePanel applies styles?.icon to icon span (fail_to_pass)."""
    purepanel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")
    with open(purepanel_path, "r") as f:
        content = f.read()

    # The icon span should apply styles?.icon
    assert "styles?.icon" in content, (
        "PurePanel must apply styles?.icon to the icon element"
    )


def test_icon_element_uses_clsx():
    """Icon element uses clsx to combine classes (fail_to_pass)."""
    purepanel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")
    with open(purepanel_path, "r") as f:
        content = f.read()

    # Should use clsx to combine the base class with classNames?.icon
    # Looking for pattern like: clsx(`${prefixCls}-message-icon`, classNames?.icon)
    assert "clsx(" in content and "message-icon" in content and "classNames?.icon" in content, (
        "Icon element should use clsx to combine base class with classNames?.icon"
    )


def test_popconfirm_type_exported():
    """PopconfirmSemanticType is properly exported (fail_to_pass)."""
    index_path = os.path.join(REPO, "components/popconfirm/index.tsx")
    with open(index_path, "r") as f:
        content = f.read()

    # Type should be exported and define its own structure (not just alias PopoverSemanticAllType)
    assert "export type PopconfirmSemanticType = {" in content, (
        "PopconfirmSemanticType must be a distinct type definition, not an alias"
    )


def test_imports_from_popover_updated():
    """PurePanel imports types from popconfirm index (fail_to_pass)."""
    purepanel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")
    with open(purepanel_path, "r") as f:
        content = f.read()

    # Should import PopconfirmSemanticAllType from '.', not PopoverSemanticAllType from '../popover'
    assert "PopconfirmSemanticAllType" in content, (
        "PurePanel should use PopconfirmSemanticAllType"
    )


def test_overlay_props_use_popconfirm_types():
    """OverlayProps uses PopconfirmSemanticAllType (fail_to_pass)."""
    purepanel_path = os.path.join(REPO, "components/popconfirm/PurePanel.tsx")
    with open(purepanel_path, "r") as f:
        content = f.read()

    # OverlayProps should reference PopconfirmSemanticAllType, not PopoverSemanticAllType
    # Check that it's using the correct type for classNames and styles
    lines = content.split('\n')
    in_overlay_props = False
    found_correct_type = False

    for line in lines:
        if "export interface OverlayProps" in line:
            in_overlay_props = True
        if in_overlay_props:
            if "PopconfirmSemanticAllType" in line and ("classNames" in line or "styles" in line):
                found_correct_type = True
                break
            if line.strip() == "}" and in_overlay_props:
                break

    assert found_correct_type, (
        "OverlayProps should use PopconfirmSemanticAllType for classNames and styles types"
    )


def test_repo_lint_popconfirm():
    """Lint passes for popconfirm files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/popconfirm/index.tsx", "components/popconfirm/PurePanel.tsx",
         "--no-error-on-unmatched-pattern"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # ESLint exit code 0 = no errors, 1 = errors found
    assert result.returncode == 0, f"ESLint errors:\n{result.stdout}\n{result.stderr}"


def test_repo_biome_lint():
    """Biome lint passes for popconfirm files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/popconfirm/index.tsx", "components/popconfirm/PurePanel.tsx"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome lint errors:\n{result.stdout}\n{result.stderr}"


def test_icon_semantic_integration():
    """Icon semantic props are properly typed in the component chain (fail_to_pass)."""
    # Check that PopconfirmSemanticType properly extends PopoverSemanticType
    index_path = os.path.join(REPO, "components/popconfirm/index.tsx")
    with open(index_path, "r") as f:
        content = f.read()

    # Should import PopoverSemanticType (not PopoverSemanticAllType)
    assert "PopoverSemanticType" in content, (
        "Should import PopoverSemanticType from popover"
    )

    # Should extend it with icon properties
    assert "PopoverSemanticType['classNames']" in content or "PopoverSemanticType[" in content, (
        "PopconfirmSemanticType should extend PopoverSemanticType with icon"
    )
