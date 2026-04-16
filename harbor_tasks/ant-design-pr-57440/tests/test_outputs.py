"""
Tests for ant-design/ant-design#57440
Feature: Typography actions placement
"""

import subprocess
import os
import tempfile

REPO = "/workspace/antd"


def test_actions_config_typescript_compilation():
    """
    Fail-to-pass: ActionsConfig interface is properly exported and usable.
    """
    ts_test_code = """
import type { ActionsConfig } from './components/typography/Base/index';
const testConfig: ActionsConfig = { placement: 'start' };
const testConfig2: ActionsConfig = { placement: 'end' };
export type TestActionsConfig = ActionsConfig;
"""

    # Use a temp directory to avoid tsconfig.json conflicts
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file_path = os.path.join(tmpdir, "actions-config-test.ts")
        with open(test_file_path, 'w') as f:
            f.write(ts_test_code)

        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
             "--module", "ESNext", "--moduleResolution", "node",
             "--esModuleInterop", "--jsx", "react", "--ignoreConfig",
             test_file_path],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert result.returncode == 0, f"ActionsConfig interface not properly exported: {result.stdout}{result.stderr}"


def test_actions_prop_type_integration():
    """
    Fail-to-pass: BlockProps accepts actions prop with correct type.
    """
    ts_test_code = """
import type { BlockProps } from './components/typography/Base/index';
const testProps: BlockProps = { actions: { placement: 'start' } };
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file_path = os.path.join(tmpdir, "actions-prop-test.ts")
        with open(test_file_path, 'w') as f:
            f.write(ts_test_code)

        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
             "--module", "ESNext", "--moduleResolution", "node",
             "--esModuleInterop", "--jsx", "react", "--ignoreConfig",
             test_file_path],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert result.returncode == 0, f"BlockProps does not accept actions prop: {result.stdout}{result.stderr}"


def test_actions_placement_behavior():
    """
    Fail-to-pass: Actions placement prop changes component rendering.
    """
    jest_test_code = """
import * as React from 'react';
import { render } from '@testing-library/react';
import Typography from './components/typography';
const { Text } = Typography;

describe('Typography actions placement', () => {
    it('should apply actions-start class when placement is start', () => {
        const { container } = render(
            React.createElement(Text, { copyable: true, actions: { placement: 'start' } }, 'Test')
        );
        expect(container.querySelector('.ant-typography-actions-start')).toBeTruthy();
    });

    it('should not apply actions-start class when placement is end', () => {
        const { container } = render(
            React.createElement(Text, { copyable: true, actions: { placement: 'end' } }, 'Test')
        );
        expect(container.querySelector('.ant-typography-actions-start')).toBeFalsy();
    });
});
"""

    test_file_path = os.path.join(REPO, "actions-placement-behavior.test.tsx")
    with open(test_file_path, 'w') as f:
        f.write(jest_test_code)

    try:
        subprocess.run(["npm", "run", "version"], capture_output=True, timeout=60, cwd=REPO)
        result = subprocess.run(
            ["npx", "jest", "--config", ".jest.js", test_file_path, "--no-cache", "--passWithNoTests"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        assert result.returncode == 0, f"Actions placement behavior tests failed: {result.stdout[-2000:]}"
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


def test_measure_deps_integration():
    """
    Fail-to-pass: Ellipsis component accepts and uses measureDeps prop.
    """
    ts_test_code = """
import * as React from 'react';
import type { EllipsisProps } from './components/typography/Base/Ellipsis';
const props: EllipsisProps = {
    width: 100, rows: 1,
    onEllipsis: () => {}, expanded: false,
    measureDeps: ['start'], miscDeps: [],
    children: (cutChildren, canEllipsis) => React.createElement('span', {}, 'test')
};
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file_path = os.path.join(tmpdir, "measure-deps-test.ts")
        with open(test_file_path, 'w') as f:
            f.write(ts_test_code)

        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
             "--module", "ESNext", "--moduleResolution", "node",
             "--esModuleInterop", "--jsx", "react", "--ignoreConfig",
             test_file_path],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert result.returncode == 0, f"Ellipsis does not accept measureDeps prop: {result.stdout}{result.stderr}"


def test_actions_start_css_compilation():
    """
    Fail-to-pass: CSS styles compile correctly with actions-start styles.
    """
    ts_test_code = """
import genTypographyStyle from './components/typography/style';
export const styleHooks = genTypographyStyle;
"""

    with tempfile.TemporaryDirectory() as tmpdir:
        test_file_path = os.path.join(tmpdir, "css-compilation-test.ts")
        with open(test_file_path, 'w') as f:
            f.write(ts_test_code)

        result = subprocess.run(
            ["npx", "tsc", "--noEmit", "--skipLibCheck", "--target", "ES2020",
             "--module", "ESNext", "--moduleResolution", "node",
             "--esModuleInterop", "--jsx", "react", "--ignoreConfig",
             test_file_path],
            capture_output=True, text=True, timeout=120, cwd=REPO,
        )
        assert result.returncode == 0, f"CSS styles not valid: {result.stdout}{result.stderr}"


def test_repo_biome_lint():
    """Pass-to-pass: Biome lint passes for modified Typography files."""
    result = subprocess.run(
        ["npx", "biome", "lint",
         "components/typography/Base/index.tsx",
         "components/typography/Base/Ellipsis.tsx",
         "components/typography/style/index.ts"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Biome lint failed: {result.stderr}"


def test_repo_eslint_typography():
    """Pass-to-pass: ESLint passes for modified Typography files."""
    result = subprocess.run(
        ["npx", "eslint",
         "components/typography/Base/index.tsx",
         "components/typography/Base/Ellipsis.tsx",
         "components/typography/style/index.ts",
         "--ext", ".ts,.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"ESLint failed: {result.stderr}"


def test_repo_typography_unit_tests():
    """Pass-to-pass: Typography unit tests pass."""
    subprocess.run(["npm", "run", "version"], capture_output=True, timeout=60, cwd=REPO)
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js",
         "components/typography/__tests__/index.test.tsx",
         "--no-cache", "--passWithNoTests"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"Typography unit tests failed: {result.stderr[-500:]}"


def test_repo_ellipsis_tests():
    """Pass-to-pass: Typography ellipsis tests pass."""
    subprocess.run(["npm", "run", "version"], capture_output=True, timeout=60, cwd=REPO)
    result = subprocess.run(
        ["npx", "jest", "--config", ".jest.js",
         "components/typography/__tests__/ellipsis.test.tsx",
         "--no-cache", "--passWithNoTests"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert result.returncode == 0, f"Ellipsis tests failed: {result.stderr[-500:]}"
