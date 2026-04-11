"""
Test suite for ant-design-solid-variant-default-colors task.

This task verifies that Button and Tag components provide default colors
when the 'solid' variant is used without an explicit color prop.
"""

import subprocess
import sys
import os

# Repository path
REPO = "/workspace/ant-design"
COMPONENTS_DIR = os.path.join(REPO, "components")


def setup_module():
    """Ensure repository exists and dependencies are installed."""
    if not os.path.exists(REPO):
        raise RuntimeError(f"Repository not found at {REPO}")
    if not os.path.exists(os.path.join(REPO, "node_modules")):
        raise RuntimeError("Dependencies not installed. Run npm install in the Dockerfile.")


# =============================================================================
# Fail-to-Pass Tests: Button Component
# =============================================================================

def test_button_solid_has_default_primary_color():
    """
    Button with variant='solid' and no color prop should render with 'ant-btn-color-primary' class.

    This tests the fix for: feat(Button,Tag): support default colors for solid variants
    Issue: When variant="solid" was used without a color prop, the button had no color class.
    Fix: Button should default to 'primary' color when variant='solid' and color is not set.
    """
    test_code = '''
import React from 'react';
import { render } from '@testing-library/react';
import Button from '../button/Button';

describe('Button Solid Default Color', () => {
  it('should have primary color class when variant is solid and color is not set', () => {
    const { container } = render(<Button variant="solid">Test</Button>);
    const button = container.firstChild;

    // Should have the solid variant class
    expect(button).toHaveClass('ant-btn-variant-solid');

    // Should have the primary color class (default for solid)
    expect(button).toHaveClass('ant-btn-color-primary');
  });
});
'''
    test_file = os.path.join(COMPONENTS_DIR, "button", "__tests__", "verify-solid-default.test.tsx")

    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["npx", "jest", "verify-solid-default.test.tsx", "--testPathPattern=button", "--no-coverage"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        stdout = result.stdout + result.stderr

        if result.returncode != 0:
            # Check if it's a test failure vs setup error
            if "FAIL" in stdout or "expect" in stdout.lower() or "toHaveClass" in stdout:
                raise AssertionError(f"Button solid default color test failed:\n{stdout}")
            raise RuntimeError(f"Test execution error:\n{stdout}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_button_config_provider_solid_default_color():
    """
    Button inside ConfigProvider with button={{variant: 'solid'}} should have primary color.

    Tests the ConfigProvider context fallback for solid variant.
    """
    test_code = '''
import React from 'react';
import { render } from '@testing-library/react';
import ConfigProvider from '../config-provider';
import Button from '../button/Button';

describe('Button ConfigProvider Solid Default Color', () => {
  it('should have primary color when ConfigProvider sets variant to solid', () => {
    const { container } = render(
      <ConfigProvider button={{ variant: 'solid' }}>
        <Button>Test</Button>
      </ConfigProvider>
    );
    const button = container.firstChild;

    expect(button).toHaveClass('ant-btn-variant-solid');
    expect(button).toHaveClass('ant-btn-color-primary');
  });
});
'''
    test_file = os.path.join(COMPONENTS_DIR, "button", "__tests__", "verify-config-solid.test.tsx")

    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["npx", "jest", "verify-config-solid.test.tsx", "--testPathPattern=button", "--no-coverage"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        stdout = result.stdout + result.stderr

        if result.returncode != 0:
            if "FAIL" in stdout or "expect" in stdout.lower():
                raise AssertionError(f"Button ConfigProvider solid test failed:\n{stdout}")
            raise RuntimeError(f"Test execution error:\n{stdout}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# =============================================================================
# Fail-to-Pass Tests: Tag Component
# =============================================================================

def test_tag_solid_has_default_color():
    """
    Tag with variant='solid' and no color prop should render with 'ant-tag-default' class.

    Tests the fix for Tag component default color for solid variant.
    Fix: Tag should default to 'default' color when variant='solid' and color is not set.
    """
    test_code = '''
import React from 'react';
import { render } from '@testing-library/react';
import Tag from '../tag';

describe('Tag Solid Default Color', () => {
  it('should have default color class when variant is solid and color is not set', () => {
    const { container } = render(<Tag variant="solid">Test</Tag>);
    const tag = container.querySelector('.ant-tag');

    expect(tag).not.toBeNull();
    expect(tag).toHaveClass('ant-tag-solid');
    expect(tag).toHaveClass('ant-tag-default');
  });
});
'''
    test_file = os.path.join(COMPONENTS_DIR, "tag", "__tests__", "verify-solid-default.test.tsx")

    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["npx", "jest", "verify-solid-default.test.tsx", "--testPathPattern=tag", "--no-coverage"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        stdout = result.stdout + result.stderr

        if result.returncode != 0:
            if "FAIL" in stdout or "expect" in stdout.lower():
                raise AssertionError(f"Tag solid default color test failed:\n{stdout}")
            raise RuntimeError(f"Test execution error:\n{stdout}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_tag_config_provider_solid_default_color():
    """
    Tag inside ConfigProvider with tag={{variant: 'solid'}} should have default color.

    Tests the ConfigProvider context fallback for Tag solid variant.
    """
    test_code = '''
import React from 'react';
import { render } from '@testing-library/react';
import ConfigProvider from '../config-provider';
import Tag from '../tag';

describe('Tag ConfigProvider Solid Default Color', () => {
  it('should have default color when ConfigProvider sets variant to solid', () => {
    const { container } = render(
      <ConfigProvider tag={{ variant: 'solid' }}>
        <Tag>Test</Tag>
      </ConfigProvider>
    );
    const tag = container.querySelector('.ant-tag');

    expect(tag).not.toBeNull();
    expect(tag).toHaveClass('ant-tag-solid');
    expect(tag).toHaveClass('ant-tag-default');
  });
});
'''
    test_file = os.path.join(COMPONENTS_DIR, "tag", "__tests__", "verify-config-solid.test.tsx")

    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["npx", "jest", "verify-config-solid.test.tsx", "--testPathPattern=tag", "--no-coverage"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        stdout = result.stdout + result.stderr

        if result.returncode != 0:
            if "FAIL" in stdout or "expect" in stdout.lower():
                raise AssertionError(f"Tag ConfigProvider solid test failed:\n{stdout}")
            raise RuntimeError(f"Test execution error:\n{stdout}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# =============================================================================
# Pass-to-Pass Tests: Verify non-solid variants are not affected
# =============================================================================

def test_tag_non_solid_no_default_color():
    """
    Tag with variant='outlined' should NOT have 'ant-tag-default' class.

    Pass-to-pass test: non-solid variants should continue to work as before.
    """
    test_code = '''
import React from 'react';
import { render } from '@testing-library/react';
import Tag from '../tag';

describe('Tag Non-Solid No Default Color', () => {
  it('should NOT have default color class when variant is outlined', () => {
    const { container } = render(<Tag variant="outlined">Test</Tag>);
    const tag = container.querySelector('.ant-tag');

    expect(tag).not.toBeNull();
    expect(tag).toHaveClass('ant-tag-outlined');
    expect(tag).not.toHaveClass('ant-tag-default');
  });
});
'''
    test_file = os.path.join(COMPONENTS_DIR, "tag", "__tests__", "verify-non-solid.test.tsx")

    with open(test_file, "w") as f:
        f.write(test_code)

    try:
        result = subprocess.run(
            ["npx", "jest", "verify-non-solid.test.tsx", "--testPathPattern=tag", "--no-coverage"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60
        )
        stdout = result.stdout + result.stderr

        if result.returncode != 0:
            if "FAIL" in stdout:
                raise AssertionError(f"Tag non-solid test failed:\n{stdout}")
            raise RuntimeError(f"Test execution error:\n{stdout}")
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


# =============================================================================
# Pass-to-Pass Tests: Repository CI checks (added as p2p enrichment)
# =============================================================================

def test_repo_biome_lint():
    """
    Repository biome linting passes (pass_to_pass).

    CI command: npm run lint:biome
    Origin: repo_tests
    Verifies code follows biome linting rules.
    """
    result = subprocess.run(
        ["npm", "run", "lint:biome"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_biome_check():
    """
    Repository biome check passes (pass_to_pass).

    CI command: npx biome check components/button/Button.tsx components/tag/hooks/useColor.ts
    Origin: repo_tests
    Verifies modified files pass formatting and linting.
    """
    result = subprocess.run(
        ["npx", "biome", "check", "components/button/Button.tsx", "components/tag/hooks/useColor.ts"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Biome check failed:\n{result.stderr[-500:]}"


def test_repo_version():
    """
    Repository version script passes (pass_to_pass).

    CI command: npm run version
    Origin: repo_tests
    Quick sanity check that version generation works.
    """
    result = subprocess.run(
        ["npm", "run", "version"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=60
    )
    assert result.returncode == 0, f"Version script failed:\n{result.stderr[-500:]}"


def test_repo_button_preset_colors():
    """
    Repository Button preset colors test exists and runs (pass_to_pass).

    CI command: npx jest --config .jest.js components/button/__tests__/index.test.tsx --testNamePattern="preset colors"
    Origin: repo_tests
    Runs existing Button tests for preset colors and variants.
    """
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js",
         "components/button/__tests__/index.test.tsx",
         "--testNamePattern", "preset colors",
         "--no-coverage", "--maxWorkers=1", "--testTimeout=60000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # The test might fail due to module resolution in shallow clone,
    # but if it runs and fails with "Cannot find module", that's an env issue, not code issue
    # We accept both success and known module resolution issues
    if result.returncode != 0:
        # If it's a known module resolution issue from shallow clone, skip
        if "Cannot find module" in result.stderr:
            import pytest
            pytest.skip("Jest module resolution issue in shallow clone environment")
        # Otherwise it's a real failure
        assert False, f"Button preset colors test failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


def test_repo_tag_variant_class():
    """
    Repository Tag variant className test exists and runs (pass_to_pass).

    CI command: npx jest --config .jest.js components/tag/__tests__/index.test.tsx --testNamePattern="should have variant"
    Origin: repo_tests
    Runs existing Tag tests for variant className.
    """
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js",
         "components/tag/__tests__/index.test.tsx",
         "--testNamePattern", "should have variant",
         "--no-coverage", "--maxWorkers=1", "--testTimeout=60000"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )
    # Accept success or known module resolution issues
    if result.returncode != 0:
        if "Cannot find module" in result.stderr:
            import pytest
            pytest.skip("Jest module resolution issue in shallow clone environment")
        assert False, f"Tag variant test failed:\n{result.stdout[-500:]}\n{result.stderr[-500:]}"


# =============================================================================
# Structural/Compilation Tests
# =============================================================================

def test_typescript_compiles():
    """
    TypeScript should compile without errors.

    Guard test: ensures the code is syntactically valid.
    """
    result = subprocess.run(
        ["npx", "tsc", "--noEmit", "--skipLibCheck", "-p", "tsconfig.json"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=120
    )

    if result.returncode != 0:
        raise AssertionError(f"TypeScript compilation failed:\n{result.stdout}\n{result.stderr}")
