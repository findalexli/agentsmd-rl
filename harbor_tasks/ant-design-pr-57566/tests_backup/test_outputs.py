"""
Tests for ant-design Typography ellipsis performance optimization.

The fix ensures that native ellipsis measurement (isEleEllipsis) is only called
when tooltip is configured, avoiding expensive reflows in dense table scenarios.
"""
import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/antd")
TYPOGRAPHY_BASE = REPO / "components" / "typography" / "Base" / "index.tsx"


def read_file(path: Path) -> str:
    """Read file contents."""
    return path.read_text(encoding="utf-8")


# =============================================================================
# FAIL-TO-PASS TESTS: These should fail on base commit, pass after fix
# =============================================================================


def test_needNativeEllipsisMeasure_variable_exists():
    """
    Verify that the needNativeEllipsisMeasure variable exists and is defined
    based on both cssEllipsis and tooltipProps.title.

    Before fix: This variable doesn't exist - isEleEllipsis is called unconditionally
    After fix: needNativeEllipsisMeasure = cssEllipsis && !!tooltipProps.title
    """
    content = read_file(TYPOGRAPHY_BASE)

    # Check that the variable is defined correctly
    assert "needNativeEllipsisMeasure" in content, \
        "needNativeEllipsisMeasure variable should exist in Typography Base component"

    # Check the specific definition pattern
    pattern = r"needNativeEllipsisMeasure\s*=\s*cssEllipsis\s*&&\s*!!\s*tooltipProps\.title"
    match = re.search(pattern, content)
    assert match is not None, \
        "needNativeEllipsisMeasure should be defined as 'cssEllipsis && !!tooltipProps.title'"


def test_isEleEllipsis_gated_by_needNativeEllipsisMeasure():
    """
    Verify that isEleEllipsis call is gated by needNativeEllipsisMeasure.

    Before fix: if (enableEllipsis && cssEllipsis && textEle)
    After fix: if (enableEllipsis && needNativeEllipsisMeasure && textEle)
    """
    content = read_file(TYPOGRAPHY_BASE)

    # The condition for calling isEleEllipsis should include needNativeEllipsisMeasure
    # Pattern: if (enableEllipsis && needNativeEllipsisMeasure && textEle)
    pattern = r"if\s*\(\s*enableEllipsis\s*&&\s*needNativeEllipsisMeasure\s*&&\s*textEle\s*\)"
    match = re.search(pattern, content)
    assert match is not None, \
        "isEleEllipsis should be gated by needNativeEllipsisMeasure instead of cssEllipsis"


def test_useEffect_dependency_includes_needNativeEllipsisMeasure():
    """
    Verify that useEffect dependencies include needNativeEllipsisMeasure.

    Before fix: dependencies include cssEllipsis
    After fix: dependencies include needNativeEllipsisMeasure instead of cssEllipsis
    """
    content = read_file(TYPOGRAPHY_BASE)

    # Find the useEffect dependency array that should include needNativeEllipsisMeasure
    # The array should have: enableEllipsis, needNativeEllipsisMeasure, children, etc.
    pattern = r"\[\s*enableEllipsis\s*,\s*needNativeEllipsisMeasure\s*,\s*children\s*,"
    match = re.search(pattern, content)
    assert match is not None, \
        "useEffect dependencies should include needNativeEllipsisMeasure instead of cssEllipsis"


def test_tooltipProps_moved_before_needNativeEllipsisMeasure():
    """
    Verify that tooltipProps is defined before needNativeEllipsisMeasure.

    This is necessary because needNativeEllipsisMeasure depends on tooltipProps.title.
    Before fix: tooltipProps was defined later in the component
    After fix: tooltipProps is moved up before needNativeEllipsisMeasure
    """
    content = read_file(TYPOGRAPHY_BASE)

    # Find positions of tooltipProps and needNativeEllipsisMeasure definitions
    tooltipProps_match = re.search(r"const\s+tooltipProps\s*=\s*useTooltipProps", content)
    needMeasure_match = re.search(r"const\s+needNativeEllipsisMeasure\s*=", content)

    assert tooltipProps_match is not None, "tooltipProps should be defined"
    assert needMeasure_match is not None, "needNativeEllipsisMeasure should be defined"

    # tooltipProps should come before needNativeEllipsisMeasure
    assert tooltipProps_match.start() < needMeasure_match.start(), \
        "tooltipProps must be defined before needNativeEllipsisMeasure"


def test_isMergedEllipsis_uses_needNativeEllipsisMeasure():
    """
    Verify that isMergedEllipsis calculation uses needNativeEllipsisMeasure.

    Before fix: cssEllipsis ? isNativeEllipsis : isJsEllipsis
    After fix: cssEllipsis ? needNativeEllipsisMeasure && isNativeEllipsis : isJsEllipsis
    """
    content = read_file(TYPOGRAPHY_BASE)

    # The isMergedEllipsis should now check needNativeEllipsisMeasure && isNativeEllipsis
    pattern = r"needNativeEllipsisMeasure\s*&&\s*isNativeEllipsis"
    match = re.search(pattern, content)
    assert match is not None, \
        "isMergedEllipsis should use 'needNativeEllipsisMeasure && isNativeEllipsis'"


def test_intersection_observer_uses_needNativeEllipsisMeasure():
    """
    Verify that IntersectionObserver logic uses needNativeEllipsisMeasure.

    Before fix: early return checked !cssEllipsis
    After fix: early return checks !needNativeEllipsisMeasure
    """
    content = read_file(TYPOGRAPHY_BASE)

    # The IntersectionObserver useEffect should check needNativeEllipsisMeasure
    # Looking for: !needNativeEllipsisMeasure in the condition
    pattern = r"!\s*needNativeEllipsisMeasure\s*\|\|"
    match = re.search(pattern, content)
    assert match is not None, \
        "IntersectionObserver should check !needNativeEllipsisMeasure instead of !cssEllipsis"


# =============================================================================
# PASS-TO-PASS TESTS: These should pass on both base and fixed commits
# =============================================================================


def test_repo_biome_lint():
    """Run Biome linter on Typography component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/typography/Base/index.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr}{result.stdout}"


def test_repo_biome_lint_typography_dir():
    """Run Biome linter on entire Typography directory (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/typography/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr}{result.stdout}"


def test_repo_biome_check():
    """Run Biome check (lint + format) on Typography Base component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "check", "components/typography/Base/index.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Biome check failed:\n{result.stderr}{result.stdout}"


def test_repo_eslint():
    """Run ESLint on Typography Base component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/typography/Base/index.tsx"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stderr}{result.stdout}"


def test_repo_typescript_parse():
    """Verify TypeScript parser can parse Typography Base component (pass_to_pass)."""
    result = subprocess.run(
        ["node", "-e", """
const ts = require('typescript');
const fs = require('fs');
const content = fs.readFileSync('components/typography/Base/index.tsx', 'utf8');
const sourceFile = ts.createSourceFile(
    'index.tsx',
    content,
    ts.ScriptTarget.Latest,
    true,
    ts.ScriptKind.TSX
);
const diagnostics = [];
function visit(node) {
    if (node.kind === ts.SyntaxKind.Unknown) {
        diagnostics.push('Unknown syntax at position ' + node.pos);
    }
    ts.forEachChild(node, visit);
}
visit(sourceFile);
if (diagnostics.length > 0) {
    console.error('Parse errors:', diagnostics.join(', '));
    process.exit(1);
}
console.log('TypeScript parse OK');
"""],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"TypeScript parse failed:\n{result.stderr}"


def test_typography_base_required_imports():
    """Verify that required imports exist in Typography Base (pass_to_pass)."""
    content = read_file(TYPOGRAPHY_BASE)

    # Check for essential imports that should always be present
    assert "import React" in content or "from 'react'" in content, \
        "React import should be present"
    assert "useTooltipProps" in content, \
        "useTooltipProps hook should be imported/used"
    assert "isEleEllipsis" in content, \
        "isEleEllipsis utility should be imported/used"


def test_typography_base_exports():
    """Verify that Typography Base component exports correctly (pass_to_pass)."""
    content = read_file(TYPOGRAPHY_BASE)

    # Check that the Base component is exported
    assert "export default" in content or "export { Base" in content or "export default Base" in content, \
        "Base component should be exported"

    # Check that it's a forwardRef component
    assert "React.forwardRef" in content or "forwardRef" in content, \
        "Base should use forwardRef for ref forwarding"
