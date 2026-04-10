"""
Test that shadow tokens correctly adapt to dark theme.

This test file verifies that:
1. The colorShadow token exists and is properly typed
2. Dark theme uses light-colored shadows (rgba(255,255,255,...))
3. Light theme uses dark-colored shadows (rgba(0,0,0,...))
4. Shadow colors are derived from the colorShadow token
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/ant-design"


def test_colorShadow_token_exists_in_interface():
    """
    The ColorNeutralMapToken interface should have colorShadow property.

    This is a structural check that verifies the token interface is correct.
    """
    colors_interface = os.path.join(REPO, "components/theme/interface/maps/colors.ts")

    with open(colors_interface, 'r') as f:
        content = f.read()

    # Check that colorShadow is defined in the interface
    assert "colorShadow" in content, f"colorShadow should be defined in ColorNeutralMapToken interface in {colors_interface}"

    # Check that it's properly documented as @internal
    assert "@internal" in content, f"colorShadow should be marked as @internal in {colors_interface}"


def test_colorShadow_in_dark_colors():
    """
    Dark theme colors.ts should define colorShadow with white as default.
    """
    dark_colors = os.path.join(REPO, "components/theme/themes/dark/colors.ts")

    with open(dark_colors, 'r') as f:
        content = f.read()

    # Check colorShadow parameter exists in generateNeutralColorPalettes
    assert "shadowColor?:" in content, f"generateNeutralColorPalettes should accept shadowColor parameter in {dark_colors}"

    # Check that colorShadow is set from shadowColor or defaults to white
    assert "colorShadow = shadowColor ||" in content or "const colorShadow =" in content, \
        f"colorShadow should be set from shadowColor parameter in {dark_colors}"

    # Check that colorShadow is returned
    assert "colorShadow," in content, f"colorShadow should be returned from generateNeutralColorPalettes in {dark_colors}"


def test_colorShadow_in_default_colors():
    """
    Default (light) theme colors.ts should define colorShadow with black as default.
    """
    default_colors = os.path.join(REPO, "components/theme/themes/default/colors.ts")

    with open(default_colors, 'r') as f:
        content = f.read()

    # Check colorShadow parameter exists in generateNeutralColorPalettes
    assert "shadowColor?:" in content, f"generateNeutralColorPalettes should accept shadowColor parameter in {default_colors}"

    # Check that colorShadow is set from shadowColor or defaults to black
    assert "colorShadow = shadowColor ||" in content or "const colorShadow =" in content, \
        f"colorShadow should be set from shadowColor parameter in {default_colors}"

    # Check that colorShadow is returned
    assert "colorShadow," in content, f"colorShadow should be returned from generateNeutralColorPalettes in {default_colors}"


def test_generateNeutralColorMap_signature():
    """
    ColorMap.ts should have updated type signature for GenerateNeutralColorMap.
    """
    color_map = os.path.join(REPO, "components/theme/themes/ColorMap.ts")

    with open(color_map, 'r') as f:
        content = f.read()

    # Check that GenerateNeutralColorMap accepts shadowColor parameter
    assert "shadowColor?:" in content, f"GenerateNeutralColorMap type should accept shadowColor parameter in {color_map}"


def test_alias_uses_colorShadow():
    """
    The alias.ts file should use colorShadow to derive shadow colors.

    This is the key test - after the fix, alias.ts should:
    1. Read colorShadow from mergedToken
    2. Create a FastColor from it
    3. Use getShadowColor helper with alpha multipliers
    """
    alias_file = os.path.join(REPO, "components/theme/util/alias.ts")

    with open(alias_file, 'r') as f:
        content = f.read()

    # Check that FastColor is used with colorShadow
    assert "new FastColor(mergedToken.colorShadow)" in content or "new FastColor(mergedToken.colorShadow" in content, \
        f"alias.ts should create FastColor from mergedToken.colorShadow in {alias_file}"

    # Check that getShadowColor helper exists
    assert "getShadowColor" in content, f"alias.ts should have getShadowColor helper function in {alias_file}"

    # Check that boxShadow uses getShadowColor
    assert "${getShadowColor(" in content or "getShadowColor(" in content, \
        f"alias.ts should use getShadowColor for shadow token generation in {alias_file}"


def test_shadow_tokens_use_dynamic_color():
    """
    All shadow tokens in alias.ts should use the dynamic shadow color, not hardcoded rgba(0,0,0,...).

    Before the fix, shadows were hardcoded like:
      boxShadow: `0 6px 16px 0 rgba(0, 0, 0, 0.08),...`

    After the fix, they should use:
      boxShadow: `0 6px 16px 0 ${getShadowColor(0.08)},...`
    """
    alias_file = os.path.join(REPO, "components/theme/util/alias.ts")

    with open(alias_file, 'r') as f:
        content = f.read()

    # Find boxShadow definitions and check they don't have hardcoded rgba(0,0,0
    shadow_tokens = [
        "boxShadow",
        "boxShadowSecondary",
        "boxShadowTertiary",
        "boxShadowPopoverArrow",
        "boxShadowCard",
        "boxShadowDrawerRight",
        "boxShadowDrawerLeft",
        "boxShadowDrawerUp",
        "boxShadowDrawerDown",
        "boxShadowTabsOverflowLeft",
        "boxShadowTabsOverflowRight",
        "boxShadowTabsOverflowTop",
        "boxShadowTabsOverflowBottom",
    ]

    for token in shadow_tokens:
        # Find the token definition in the file
        pattern = rf"{token}:\s*[`\"']"
        matches = list(re.finditer(pattern, content))

        if matches:
            # Get a snippet after the match to check if it uses getShadowColor
            for match in matches:
                start = match.end()
                snippet = content[start:start+200]

                # Should NOT have hardcoded rgba(0, 0, 0 - this indicates the old buggy code
                has_hardcoded_black = "rgba(0, 0, 0" in snippet or "rgba(0,0,0" in snippet

                if has_hardcoded_black:
                    assert False, f"{token} should not use hardcoded rgba(0,0,0,...) in {alias_file}. Found: {snippet[:100]}"


def test_repo_theme_unit_tests():
    """
    Run the repository's theme token unit tests specifically.

    This test runs the existing test file at components/theme/__tests__/token.test.tsx
    which should include tests for shadow tokens.

    pass_to_pass: Repository's theme token unit tests continue to pass.
    """
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=token.test",
         "--testNamePattern=shadow", "--no-coverage",
         "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Repository theme shadow tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_repo_theme_all_tests():
    """
    Run all theme-related Jest tests.

    This ensures the theme module tests continue to pass (pass_to_pass).
    """
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=theme",
         "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    assert result.returncode == 0, f"Repository theme tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_repo_typescript_typecheck():
    """
    Run TypeScript typecheck on the repository.

    This ensures no type errors are introduced (pass_to_pass).
    """
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"

    result = subprocess.run(
        ["npm", "run", "tsc"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env
    )

    assert result.returncode == 0, f"TypeScript typecheck failed:\n{result.stderr[-500:]}"


def test_npm_lint_theme():
    """
    Run the repo's lint check on theme files.

    pass_to_pass: ESLint on theme files passes without errors.
    """
    result = subprocess.run(
        ["npm", "run", "lint:script", "--", "--no-cache", "components/theme/"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    assert result.returncode == 0, f"Lint check failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"




def test_repo_node_tests():
    """
    Run the repository's Node.js/SSR tests.

    This tests server-side rendering of components, ensuring the fix
    doesn't break SSR compatibility (pass_to_pass).
    """
    env = os.environ.copy()
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"

    result = subprocess.run(
        ["npm", "run", "test:node"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env=env
    )

    assert result.returncode == 0, f"Node.js tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_repo_dropdown_demo_tests():
    """
    Run dropdown component demo tests.

    This tests dropdown demo rendering with snapshots (pass_to_pass).
    The gold patch modifies dropdown snapshots for shadow color fixes.
    """
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=dropdown/__tests__/demo-extend.test",
         "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Dropdown demo tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_repo_menu_demo_tests():
    """
    Run menu component demo tests.

    This tests menu demo rendering with snapshots (pass_to_pass).
    The gold patch modifies menu snapshots for shadow color fixes.
    """
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "--no-cache",
         "--testPathPatterns=menu/__tests__/demo-extend.test",
         "--maxWorkers=1"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=180
    )

    assert result.returncode == 0, f"Menu demo tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
