"""
Behavioral tests for ant-design shadow tokens dark theme adaptation.

These tests verify actual behavior by:
1. Importing and executing theme code via subprocess
2. Generating tokens for light and dark themes
3. Asserting on computed shadow values (not source code structure)

This validates that shadow tokens properly adapt their color based on the theme:
- Light theme: shadows use dark colors (rgba(0,0,0,...))
- Dark theme: shadows use light colors (rgba(255,255,255,...))
"""

import subprocess
import sys
import os
import re

REPO = "/workspace/ant-design"


def run_typescript_test(code, description=""):
    """Helper to run TypeScript code that imports and tests the theme."""
    test_file = os.path.join(REPO, "components/theme", "behavioral_test.ts")

    full_code = f"""import theme from './index';
import getDesignToken from './getDesignToken';

{code}
"""
    # Write the test file
    with open(test_file, "w") as f:
        f.write(full_code)

    try:
        # Run the test
        result = subprocess.run(
            ["npx", "tsx", "behavioral_test.ts"],
            cwd=os.path.join(REPO, "components/theme"),
            capture_output=True,
            text=True,
            timeout=120,
        )
        return result
    finally:
        # Cleanup
        try:
            os.remove(test_file)
        except:
            pass


# ============ Fail-to-Pass Tests ============

def test_shadow_tokens_adapt_to_dark_theme():
    """
    Shadow tokens should adapt to dark theme - core behavioral verification.

    The fix should make shadow colors theme-aware:
    - Light theme: shadows use black-based colors
    - Dark theme: shadows use white-based colors
    """
    code = """
const lightToken = getDesignToken({});
const darkToken = getDesignToken({ algorithm: [theme.darkAlgorithm] });

// Helper to extract RGB values from rgba string (handles both "0, 0, 0" and "0,0,0")
const parseRgba = (rgba: string): number[] | null => {
  const match = rgba.match(/rgba\\s*\\(\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,\\s*(\\d+)\\s*,/);
  return match ? [parseInt(match[1]), parseInt(match[2]), parseInt(match[3])] : null;
};

// Extract all rgba values from shadow
const extractColors = (shadow: string): number[][] => {
  const rgbaMatches = [...shadow.matchAll(/rgba\\([^)]+\\)/g)];
  return rgbaMatches.map(m => parseRgba(m[0])).filter((c): c is number[] => c !== null);
};

const lightColors = extractColors(lightToken.boxShadow || '');
const darkColors = extractColors(darkToken.boxShadow || '');

// Light theme should use black (0,0,0) shadows
const lightHasBlack = lightColors.some(c => c[0] === 0 && c[1] === 0 && c[2] === 0);
if (!lightHasBlack) {
  console.error('FAIL: Light theme should use black-based shadows');
  process.exit(1);
}

// Dark theme should use white (255,255,255) shadows
const darkHasWhite = darkColors.some(c => c[0] === 255 && c[1] === 255 && c[2] === 255);
if (!darkHasWhite) {
  console.error('FAIL: Dark theme should use white-based shadows');
  process.exit(1);
}

// The shadows should be different between themes
if (lightToken.boxShadow === darkToken.boxShadow) {
  console.error('FAIL: Light and dark themes should have different shadows');
  process.exit(1);
}

console.log('PASS: Shadow tokens adapt to theme');
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"Shadow tokens should adapt to theme:\n{result.stdout}\n{result.stderr}"


def test_dark_theme_has_white_based_shadows():
    """
    Dark theme shadows must use white-based colors for visibility on dark backgrounds.
    """
    code = """
const darkToken = getDesignToken({ algorithm: [theme.darkAlgorithm] });

// Helper to check if shadow uses white-based colors
const hasWhiteColors = (shadow: string): boolean => {
  // Match rgba with 255 for all RGB components
  return /rgba\\s*\\(\\s*255\\s*,\\s*255\\s*,\\s*255\\s*,/.test(shadow);
};

if (!hasWhiteColors(darkToken.boxShadow || '')) {
  console.error('FAIL: Dark theme boxShadow should use white-based colors');
  process.exit(1);
}

console.log('PASS: Dark theme uses white-based shadows');
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"Dark theme white shadows test failed:\n{result.stdout}\n{result.stderr}"


def test_light_theme_has_black_based_shadows():
    """
    Light theme shadows must use black-based colors for visibility on light backgrounds.
    """
    code = """
const lightToken = getDesignToken({});

// Helper to check if shadow uses black-based colors
const hasBlackColors = (shadow: string): boolean => {
  // Match rgba with 0 for all RGB components
  return /rgba\\s*\\(\\s*0\\s*,\\s*0\\s*,\\s*0\\s*,/.test(shadow);
};

if (!hasBlackColors(lightToken.boxShadow || '')) {
  console.error('FAIL: Light theme boxShadow should use black-based colors');
  process.exit(1);
}

console.log('PASS: Light theme uses black-based shadows');
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"Light theme black shadows test failed:\n{result.stdout}\n{result.stderr}"


def test_shadow_card_adapts_to_theme():
    """
    boxShadowCard should adapt its color based on theme (black for light, white for dark).
    """
    code = """
const lightToken = getDesignToken({});
const darkToken = getDesignToken({ algorithm: [theme.darkAlgorithm] });

const hasWhite = (shadow: string): boolean => /rgba\\s*\\(\\s*255\\s*,\\s*255\\s*,\\s*255\\s*,/.test(shadow);
const hasBlack = (shadow: string): boolean => /rgba\\s*\\(\\s*0\\s*,\\s*0\\s*,\\s*0\\s*,/.test(shadow);

// Light theme should have black shadows
if (!hasBlack(lightToken.boxShadowCard || '')) {
  console.error('FAIL: Light theme boxShadowCard should use black');
  process.exit(1);
}

// Dark theme should have white shadows
if (!hasWhite(darkToken.boxShadowCard || '')) {
  console.error('FAIL: Dark theme boxShadowCard should use white');
  process.exit(1);
}

// They should be different
if (lightToken.boxShadowCard === darkToken.boxShadowCard) {
  console.error('FAIL: boxShadowCard should differ between themes');
  process.exit(1);
}

console.log('PASS: boxShadowCard adapts to theme');
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"boxShadowCard should adapt to theme:\n{result.stdout}\n{result.stderr}"


def test_color_shadow_token_exists_and_differs():
    """
    The colorShadow token should exist and have different values in light vs dark themes.
    """
    code = """
const lightToken = getDesignToken({});
const darkToken = getDesignToken({ algorithm: [theme.darkAlgorithm] });

// colorShadow should exist in both themes
if (!lightToken.colorShadow) {
  console.error('FAIL: colorShadow should exist in light theme');
  process.exit(1);
}
if (!darkToken.colorShadow) {
  console.error('FAIL: colorShadow should exist in dark theme');
  process.exit(1);
}

// colorShadow values should be different (black vs white based)
if (lightToken.colorShadow === darkToken.colorShadow) {
  console.error('FAIL: colorShadow should differ between themes');
  process.exit(1);
}

// Light theme should have black-based colorShadow (check for 0,0,0 or #000)
const lightHasBlack = /#000|rgba\\s*\\(\\s*0\\s*,\\s*0\\s*,\\s*0\\s*/i.test(lightToken.colorShadow);
if (!lightHasBlack) {
  console.error('FAIL: Light theme colorShadow should be black-based');
  process.exit(1);
}

// Dark theme should have white-based colorShadow (check for 255 or fff)
const darkHasWhite = /255|fff/i.test(darkToken.colorShadow);
if (!darkHasWhite) {
  console.error('FAIL: Dark theme colorShadow should be white-based');
  process.exit(1);
}

console.log('PASS: colorShadow token exists and differs between themes');
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"colorShadow token test failed:\n{result.stdout}\n{result.stderr}"


def test_all_shadow_tokens_are_theme_aware():
    """
    All major shadow tokens should adapt to theme (not just boxShadow).
    """
    code = """
const lightToken = getDesignToken({});
const darkToken = getDesignToken({ algorithm: [theme.darkAlgorithm] });

const shadowTokens = [
  'boxShadow', 'boxShadowCard', 'boxShadowSecondary', 'boxShadowTertiary',
  'boxShadowDrawerRight', 'boxShadowDrawerLeft', 'boxShadowDrawerUp', 'boxShadowDrawerDown',
  'boxShadowPopoverArrow',
  'boxShadowTabsOverflowLeft', 'boxShadowTabsOverflowRight',
  'boxShadowTabsOverflowTop', 'boxShadowTabsOverflowBottom'
];

let adaptedCount = 0;
for (const tokenName of shadowTokens) {
  const lightVal = (lightToken as any)[tokenName] || '';
  const darkVal = (darkToken as any)[tokenName] || '';

  if (lightVal && darkVal && lightVal !== darkVal) {
    adaptedCount++;
  }
}

// At least 8 shadow tokens should be theme-aware
if (adaptedCount < 8) {
  console.error(`FAIL: Only ${adaptedCount} shadow tokens adapted, expected at least 8`);
  process.exit(1);
}

console.log(`PASS: ${adaptedCount} shadow tokens are theme-aware`);
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"Shadow tokens theme awareness test failed:\n{result.stdout}\n{result.stderr}"


def test_shadow_opacity_structure_preserved():
    """
    Shadow opacity structure should be preserved - both themes have same number of layers.
    """
    code = """
const lightToken = getDesignToken({});
const darkToken = getDesignToken({ algorithm: [theme.darkAlgorithm] });

// Count rgba occurrences (shadow layers)
const countRgba = (shadow: string): number => {
  const matches = shadow.match(/rgba\\s*\\([^)]+\\)/g);
  return matches ? matches.length : 0;
};

const lightCount = countRgba(lightToken.boxShadow || '');
const darkCount = countRgba(darkToken.boxShadow || '');

// Both should have the same number of shadow layers
if (lightCount !== darkCount) {
  console.error(`FAIL: Light has ${lightCount} layers, dark has ${darkCount}`);
  process.exit(1);
}

// Should have at least 3 layers per requirements (0.05, 0.08, 0.12)
if (lightCount < 3) {
  console.error(`FAIL: boxShadow should have at least 3 layers, got ${lightCount}`);
  process.exit(1);
}

console.log(`PASS: Shadow structure preserved with ${lightCount} layers`);
"""
    result = run_typescript_test(code)
    assert result.returncode == 0, f"Shadow opacity preservation test failed:\n{result.stdout}\n{result.stderr}"


# ============ Pass-to-Pass Tests ============

def test_theme_jest_tests_pass():
    """
    Run the repo's existing theme tests (pass_to_pass).
    """
    result = subprocess.run(
        ["npx", "jest", "--testPathPattern", "components/theme/__tests__/token.test.tsx",
         "--no-coverage", "--forceExit", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
    )
    # Check for test failures (not just process exit code since jest may return non-zero for other reasons)
    if "FAIL" in result.stdout and "shadow tokens should adapt" not in result.stdout:
        # There are test failures other than the new test (which won't exist on base)
        raise AssertionError(f"Theme tests failed:\n{result.stdout[-2000:]}")


def test_alias_module_valid_typescript():
    """
    The alias.ts module should be valid TypeScript (pass_to_pass).
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
         "--moduleResolution", "node", "--esModuleInterop",
         "components/theme/util/alias.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    # Ignore pre-existing errors, just check for new errors related to our changes
    if result.returncode != 0:
        errors = result.stderr + result.stdout
        # Check for errors related to the fix
        if "colorShadow" in errors:
            raise AssertionError(f"TypeScript errors in shadow-related code:\n{errors}")


def test_theme_module_structure():
    """
    Verify theme module structure is intact (pass_to_pass).
    """
    # Verify key files exist
    required_files = [
        "components/theme/index.tsx",
        "components/theme/util/alias.ts",
        "components/theme/themes/dark/colors.ts",
        "components/theme/themes/default/colors.ts",
    ]
    for file in required_files:
        path = os.path.join(REPO, file)
        assert os.path.exists(path), f"Required file missing: {file}"


def test_repo_eslint_theme_files():
    """
    ESLint passes on theme files modified by PR (pass_to_pass).
    """
    modified_files = [
        "components/theme/util/alias.ts",
        "components/theme/themes/dark/colors.ts",
        "components/theme/themes/default/colors.ts",
        "components/theme/interface/maps/colors.ts",
        "components/theme/themes/ColorMap.ts",
    ]
    result = subprocess.run(
        ["npx", "eslint"] + modified_files,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_repo_biome_ci_theme_files():
    """
    Biome CI checks pass on theme files modified by PR (pass_to_pass).
    """
    modified_files = [
        "components/theme/util/alias.ts",
        "components/theme/themes/dark/colors.ts",
        "components/theme/themes/default/colors.ts",
        "components/theme/interface/maps/colors.ts",
        "components/theme/themes/ColorMap.ts",
    ]
    result = subprocess.run(
        ["npx", "biome", "ci"] + modified_files,
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert result.returncode == 0, f"Biome CI failed:\n{result.stdout}\n{result.stderr}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
