"""
Tests for ant-design Cascader ellipsis style fix.

PR #57540 fixes the text-overflow ellipsis not working on Cascader menu items.
The fix moves textEllipsis from the parent &-item to the child &-content element,
and adds minWidth: 0 to enable proper flex item text truncation.

These tests verify BEHAVIOR, not implementation details. They actually execute
the getColumnsStyle function with a mock token and inspect the returned CSS
structure, rather than grepping source code.
"""

import subprocess
import os
import json
from pathlib import Path

REPO = Path("/workspace/antd")
COLUMNS_TS = REPO / "components" / "cascader" / "style" / "columns.ts"


def ensure_version_file():
    """Ensure the version.ts file exists (required for bundling)."""
    version_ts = REPO / "components" / "version" / "version.ts"
    if not version_ts.exists():
        version_ts.parent.mkdir(parents=True, exist_ok=True)
        with open(REPO / "package.json") as f:
            version = json.load(f)["version"]
        version_ts.write_text(f"export default '{version}';")


def ensure_bundled():
    """Ensure columns.ts is bundled to columns.js for testing."""
    ensure_version_file()

    # Bundle to a temp location in the container's writable filesystem
    bundle_script = """
const esbuild = require('esbuild');
const path = require('path');
const fs = require('fs');

const destDir = '/tmp/columns_bundle';
if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
}

esbuild.build({
  bundle: true,
  entryPoints: ['./components/cascader/style/columns.ts'],
  outfile: '/tmp/columns_bundle/columns.js',
  platform: 'node',
  format: 'cjs',
  loader: { '.ts': 'ts', '.tsx': 'tsx' },
  jsx: 'automatic',
  jsxImportSource: 'react',
}).then(result => {
  if (result.errors.length > 0) {
    console.error('Build errors:', JSON.stringify(result.errors));
    process.exit(1);
  }
  console.log('Bundle complete');
}).catch(e => {
  console.error('Build failed:', e.message);
  process.exit(1);
});
"""
    result = subprocess.run(
        ["node", "-e", bundle_script],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise RuntimeError(f"Bundling failed: {result.stderr}")


# ============== Fail-to-Pass Tests ==============

def test_css_ellipsis_behavior():
    """
    Behavioral test: textEllipsis must be applied to the text container element.

    Per the instruction: "The text-overflow properties must be applied to the
    element that contains the actual text content — not to its parent flex container"

    The instruction also explicitly states: "The text container element must have minWidth: 0"

    This test verifies the CSS output contains proper text truncation by searching
    for textEllipsis properties (overflow: hidden, white-space: nowrap,
    text-overflow: ellipsis) AND minWidth: 0 anywhere in the style tree,
    without requiring specific selector names.
    """
    # Ensure the TypeScript is bundled to JavaScript
    ensure_bundled()

    # Create a test script that runs the behavioral test
    test_script = """
const path = require('path');
const cssinjs = require('/workspace/antd/node_modules/@ant-design/cssinjs');
const columnsPath = '/tmp/columns_bundle/columns.js';
const { default: getColumnsStyle } = require(columnsPath);

const genCalc = cssinjs.genCalc;

const mockToken = {
  prefixCls: 'ant-cascader',
  componentCls: '.ant-cascader',
  borderRadiusSM: 2,
  colorHighlight: '#ff4d4f',
  colorIcon: 'rgba(0, 0, 0, 0.45)',
  colorSplit: '#f0f0f0',
  colorTextDisabled: 'rgba(0, 0, 0, 0.25)',
  controlItemBgHover: '#f5f5f5',
  controlItemWidth: 120,
  dropdownHeight: 200,
  fontSizeIcon: '10px',
  lineHeight: 1.5715,
  lineType: 'solid',
  lineWidth: 1,
  menuPadding: '4px 0',
  motionDurationMid: '0.3s',
  optionPadding: '5px 12px',
  optionSelectedBg: '#f5f5f5',
  optionSelectedColor: 'rgba(0, 0, 0, 0.88)',
  optionSelectedFontWeight: 600,
  paddingXS: '8px',
  paddingXXS: '4px',
  calc: genCalc({}),
  fontSizeLG: 14,
  checkboxSize: 20,
  colorPrimary: '#1890ff',
  colorBgContainer: '#ffffff',
};

const result = getColumnsStyle(mockToken);

// Find the cascader style block
let cascaderStyle = null;

if (Array.isArray(result) && result.length >= 2) {
  for (const item of result) {
    if (item && typeof item === 'object' && item['.ant-cascader']) {
      cascaderStyle = item['.ant-cascader'];
      break;
    }
  }
}

if (!cascaderStyle) {
  console.log('FAIL: Could not find .ant-cascader style block');
  process.exit(1);
}

// Search for any block that has textEllipsis properties (overflow, whiteSpace, textOverflow)
// This is behavior-focused: we're looking for the ellipsis styling, not a specific selector
function findTextEllipsisBlock(obj, depth) {
  if (depth > 6) return null;  // safeguard
  if (typeof obj !== 'object' || obj === null) return null;

  // Check if this block has textEllipsis properties
  if (obj.overflow === 'hidden' && obj.whiteSpace === 'nowrap' && obj.textOverflow === 'ellipsis') {
    return obj;
  }

  // Recurse into nested objects
  if (Array.isArray(obj)) {
    for (const item of obj) {
      const found = findTextEllipsisBlock(item, depth + 1);
      if (found) return found;
    }
  } else {
    for (const [key, val] of Object.entries(obj)) {
      if (key !== 'overflow' && key !== 'whiteSpace' && key !== 'textOverflow' && key !== 'minWidth') {
        const found = findTextEllipsisBlock(val, depth + 1);
        if (found) return found;
      }
    }
  }
  return null;
}

// Search for minWidth: 0 anywhere in the style tree
function findMinWidthZero(obj, depth) {
  if (depth > 6) return null;
  if (typeof obj !== 'object' || obj === null) return null;

  if (obj.minWidth === 0) return obj;

  if (Array.isArray(obj)) {
    for (const item of obj) {
      const found = findMinWidthZero(item, depth + 1);
      if (found) return found;
    }
  } else {
    for (const [key, val] of Object.entries(obj)) {
      if (key !== 'minWidth') {
        const found = findMinWidthZero(val, depth + 1);
        if (found) return found;
      }
    }
  }
  return null;
}

const textEllipsisBlock = findTextEllipsisBlock(result, 0);
const minWidthZeroBlock = findMinWidthZero(result, 0);

console.log('=== Test: textEllipsis properties present ===');
if (!textEllipsisBlock) {
  console.log('FAIL: No textEllipsis properties found (overflow: hidden, whiteSpace: nowrap, textOverflow: ellipsis)');
  process.exit(1);
}
console.log('PASS: textEllipsis properties found');

console.log('=== Test: minWidth: 0 present ===');
if (!minWidthZeroBlock) {
  console.log('FAIL: No minWidth: 0 found in style tree');
  process.exit(1);
}
console.log('PASS: minWidth: 0 found');

console.log('ALL TESTS_PASSED');
process.exit(0);
"""

    # Run the behavioral test script via Node.js
    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    # The test script exits with 0 if all checks pass, 1 if any fail
    if result.returncode != 0:
        output = result.stdout + result.stderr
        assert False, f"Cascader ellipsis behavior test failed:\n{output}"


# ============== Pass-to-Pass Tests ==============

def test_typescript_syntax_valid():
    """TypeScript file has valid syntax (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "-p", "tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    if result.returncode != 0:
        output = result.stdout + result.stderr
        if "columns.ts" in output:
            assert False, f"TypeScript syntax error in columns.ts:\n{output}"


def test_columns_ts_imports_are_valid():
    """
    Verify that columns.ts can be bundled without import errors (pass_to_pass).

    This tests that any imports used in the file actually exist and are resolvable.
    We don't check for specific import paths (those are implementation details),
    just that the file can be successfully bundled.
    """
    ensure_bundled()
    # If we got here without exception, the bundling succeeded
    # which means all imports are valid and resolvable


def test_columns_ts_exports_callable():
    """
    Verify that columns.ts exports a callable function that produces valid CSS output (pass_to_pass).

    This tests that the exported function exists and returns a proper data structure
    when called with a token. We don't check for specific variable names.
    """
    ensure_bundled()

    test_script = """
const columnsPath = '/tmp/columns_bundle/columns.js';
const mod = require(columnsPath);

// The module should have some export that is a function
const exportKeys = Object.keys(mod);
if (exportKeys.length === 0) {
  console.log('FAIL: No exports found');
  process.exit(1);
}

// At least one export should be a function
const fn = mod.default || mod[exportKeys[0]];
if (typeof fn !== 'function') {
  console.log('FAIL: No function export found');
  process.exit(1);
}

// The function should return an array (CSS-in-JS style)
const cssinjs = require('/workspace/antd/node_modules/@ant-design/cssinjs');
const genCalc = cssinjs.genCalc;
const mockToken = {
  prefixCls: 'ant-cascader',
  componentCls: '.ant-cascader',
  borderRadiusSM: 2,
  colorHighlight: '#ff4d4f',
  colorIcon: 'rgba(0, 0, 0, 0.45)',
  colorSplit: '#f0f0f0',
  colorTextDisabled: 'rgba(0, 0, 0, 0.25)',
  controlItemBgHover: '#f5f5f5',
  controlItemWidth: 120,
  dropdownHeight: 200,
  fontSizeIcon: '10px',
  lineHeight: 1.5715,
  lineType: 'solid',
  lineWidth: 1,
  menuPadding: '4px 0',
  motionDurationMid: '0.3s',
  optionPadding: '5px 12px',
  optionSelectedBg: '#f5f5f5',
  optionSelectedColor: 'rgba(0, 0, 0, 0.88)',
  optionSelectedFontWeight: 600,
  paddingXS: '8px',
  paddingXXS: '4px',
  calc: genCalc({}),
  fontSizeLG: 14,
  checkboxSize: 20,
  colorPrimary: '#1890ff',
  colorBgContainer: '#ffffff',
};

const result = fn(mockToken);
if (!Array.isArray(result)) {
  console.log('FAIL: Function did not return an array');
  process.exit(1);
}

console.log('PASS: Function exports callable and returns array');
process.exit(0);
"""

    result = subprocess.run(
        ["node", "-e", test_script],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=REPO
    )

    if result.returncode != 0:
        assert False, f"columns.ts export test failed:\n{result.stdout}\n{result.stderr}"


def test_eslint_passes():
    """ESLint passes on the changed file (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", str(COLUMNS_TS), "--no-error-on-unmatched-pattern"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"ESLint errors:\n{result.stdout}\n{result.stderr}"


def test_cascader_style_index_imports_columns():
    """Cascader style index properly imports columns (pass_to_pass)."""
    index_path = REPO / "components" / "cascader" / "style" / "index.ts"
    if index_path.exists():
        content = index_path.read_text()
        assert "columns" in content.lower() or "getColumnsStyle" in content, (
            "Cascader style index should import columns style"
        )


def test_build_cascader_component():
    """Cascader component can be built (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "-p", "tsconfig.json"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO,
        env={**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    )
    if result.returncode != 0:
        if "cascader" in result.stderr.lower() or "cascader" in result.stdout.lower():
            assert False, f"TypeScript errors in Cascader:\n{result.stderr}"


def test_biome_lint_cascader():
    """Biome lint passes on Cascader component (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/cascader/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"Biome lint errors:\n{result.stdout}\n{result.stderr}"


def test_biome_format_columns_ts():
    """Biome format check passes on columns.ts (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "format", "components/cascader/style/columns.ts"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Biome format errors:\n{result.stdout}\n{result.stderr}"


def test_eslint_cascader_style():
    """ESLint passes on Cascader style directory (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/cascader/style/"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"ESLint errors:\n{result.stdout}\n{result.stderr}"
