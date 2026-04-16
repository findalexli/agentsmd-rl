"""
Tests for ant-design solid variant default color feature.

This tests that Button and Tag components provide default colors
when variant="solid" is set without an explicit color prop.
"""

import subprocess
import os
import json

REPO = "/workspace/ant-design"


def run_jest_test(test_pattern: str, timeout: int = 300) -> subprocess.CompletedProcess:
    """Run a specific Jest test pattern."""
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns", test_pattern, "--testNamePattern", ""],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CI": "true"}
    )
    return result


def test_button_solid_variant_has_primary_color():
    """
    Button with variant='solid' should have 'ant-btn-color-primary' class.

    fail_to_pass: On base commit, Button with variant="solid" but no color
    prop does not get the primary color class. After the fix, it should.
    """
    # Create a test file to check Button solid variant behavior
    test_code = '''
const React = require('react');
const { render } = require('@testing-library/react');
const Button = require('..').default;

describe('Button solid variant default color', () => {
  it('should have ant-btn-color-primary class when variant is solid', () => {
    const { container } = render(<Button variant="solid">Test</Button>);
    const btn = container.querySelector('button');
    expect(btn).toHaveClass('ant-btn-variant-solid');
    expect(btn).toHaveClass('ant-btn-color-primary');
  });
});
'''
    test_file = os.path.join(REPO, "components/button/__tests__/solid-variant.test.tsx")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["npm", "test", "--", "--testPathPatterns", "button/__tests__/solid-variant"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "true"}
        )

        assert result.returncode == 0, f"Button solid variant test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_button_configprovider_solid_variant_has_primary_color():
    """
    Button inside ConfigProvider with button.variant='solid' should have primary color.

    fail_to_pass: On base commit, ConfigProvider's button variant="solid"
    does not apply primary color. After the fix, it should.
    """
    test_code = '''
const React = require('react');
const { render } = require('@testing-library/react');
const Button = require('..').default;
const ConfigProvider = require('../../config-provider').default;

describe('ConfigProvider Button solid variant', () => {
  it('should have ant-btn-color-primary when ConfigProvider sets variant solid', () => {
    const { container } = render(
      <ConfigProvider button={{ variant: 'solid' }}>
        <Button>Test</Button>
      </ConfigProvider>
    );
    const btn = container.querySelector('button');
    expect(btn).toHaveClass('ant-btn-variant-solid');
    expect(btn).toHaveClass('ant-btn-color-primary');
  });
});
'''
    test_file = os.path.join(REPO, "components/button/__tests__/solid-config.test.tsx")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["npm", "test", "--", "--testPathPatterns", "button/__tests__/solid-config"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "true"}
        )

        assert result.returncode == 0, f"ConfigProvider Button solid variant test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_tag_solid_variant_has_default_color():
    """
    Tag with variant='solid' should have 'ant-tag-default' class.

    fail_to_pass: On base commit, Tag with variant="solid" but no color
    prop does not get the default color class. After the fix, it should.
    """
    test_code = '''
const React = require('react');
const { render } = require('@testing-library/react');
const Tag = require('..').default;

describe('Tag solid variant default color', () => {
  it('should have ant-tag-default class when variant is solid', () => {
    const { container } = render(<Tag variant="solid">Test</Tag>);
    const tag = container.querySelector('.ant-tag');
    expect(tag).toHaveClass('ant-tag-solid');
    expect(tag).toHaveClass('ant-tag-default');
  });
});
'''
    test_file = os.path.join(REPO, "components/tag/__tests__/solid-variant.test.tsx")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["npm", "test", "--", "--testPathPatterns", "tag/__tests__/solid-variant"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "true"}
        )

        assert result.returncode == 0, f"Tag solid variant test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_tag_configprovider_solid_variant_has_default_color():
    """
    Tag inside ConfigProvider with tag.variant='solid' should have default color.

    fail_to_pass: On base commit, ConfigProvider's tag variant="solid"
    does not apply default color. After the fix, it should.
    """
    test_code = '''
const React = require('react');
const { render } = require('@testing-library/react');
const Tag = require('..').default;
const ConfigProvider = require('../../config-provider').default;

describe('ConfigProvider Tag solid variant', () => {
  it('should have ant-tag-default when ConfigProvider sets variant solid', () => {
    const { container } = render(
      <ConfigProvider tag={{ variant: 'solid' }}>
        <Tag>Test</Tag>
      </ConfigProvider>
    );
    const tag = container.querySelector('.ant-tag');
    expect(tag).toHaveClass('ant-tag-solid');
    expect(tag).toHaveClass('ant-tag-default');
  });
});
'''
    test_file = os.path.join(REPO, "components/tag/__tests__/solid-config.test.tsx")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["npm", "test", "--", "--testPathPatterns", "tag/__tests__/solid-config"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "true"}
        )

        assert result.returncode == 0, f"ConfigProvider Tag solid variant test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_tag_non_solid_variant_no_default_color():
    """
    Tag with variant='outlined' should NOT have 'ant-tag-default' class.

    pass_to_pass: This behavior should be consistent before and after the fix.
    Non-solid variants should not get the default color class.
    """
    test_code = '''
const React = require('react');
const { render } = require('@testing-library/react');
const Tag = require('..').default;

describe('Tag non-solid variant', () => {
  it('should not have ant-tag-default class when variant is outlined', () => {
    const { container } = render(<Tag variant="outlined">Test</Tag>);
    const tag = container.querySelector('.ant-tag');
    expect(tag).toHaveClass('ant-tag-outlined');
    expect(tag).not.toHaveClass('ant-tag-default');
  });
});
'''
    test_file = os.path.join(REPO, "components/tag/__tests__/outlined-variant.test.tsx")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["npm", "test", "--", "--testPathPatterns", "tag/__tests__/outlined-variant"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "true"}
        )

        assert result.returncode == 0, f"Tag outlined variant test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_button_explicit_color_overrides_default():
    """
    Button with variant='solid' and explicit color should use the explicit color.

    pass_to_pass: Explicit color prop should always take precedence.
    """
    test_code = '''
const React = require('react');
const { render } = require('@testing-library/react');
const Button = require('..').default;

describe('Button explicit color', () => {
  it('should use explicit color even with solid variant', () => {
    const { container } = render(<Button variant="solid" color="blue">Test</Button>);
    const btn = container.querySelector('button');
    expect(btn).toHaveClass('ant-btn-variant-solid');
    expect(btn).toHaveClass('ant-btn-color-blue');
    expect(btn).not.toHaveClass('ant-btn-color-primary');
  });
});
'''
    test_file = os.path.join(REPO, "components/button/__tests__/explicit-color.test.tsx")

    try:
        with open(test_file, 'w') as f:
            f.write(test_code)

        result = subprocess.run(
            ["npm", "test", "--", "--testPathPatterns", "button/__tests__/explicit-color"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=300,
            env={**os.environ, "CI": "true"}
        )

        assert result.returncode == 0, f"Button explicit color test failed:\n{result.stdout}\n{result.stderr}"
    finally:
        if os.path.exists(test_file):
            os.remove(test_file)


def test_repo_biome_lint():
    """
    Repo's biome linter passes (pass_to_pass).

    This runs the same biome lint check that CI uses to verify code formatting
    and lint rules are satisfied.
    """
    result = subprocess.run(
        ["npm", "run", "lint:biome"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stderr[-1000:]}"


def test_repo_button_tests():
    """
    Repo's existing Button component tests pass (pass_to_pass).

    Runs the existing Button unit tests to ensure the component works correctly.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns", "button/__tests__/index", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "true"}
    )
    assert result.returncode == 0, f"Button tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


def test_repo_tag_tests():
    """
    Repo's existing Tag component tests pass (pass_to_pass).

    Runs the existing Tag unit tests to ensure the component works correctly.
    """
    result = subprocess.run(
        ["npm", "test", "--", "--testPathPatterns", "tag/__tests__/index", "--passWithNoTests"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300,
        env={**os.environ, "CI": "true"}
    )
    assert result.returncode == 0, f"Tag tests failed:\n{result.stdout[-1500:]}\n{result.stderr[-500:]}"


if __name__ == "__main__":
    import sys
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
