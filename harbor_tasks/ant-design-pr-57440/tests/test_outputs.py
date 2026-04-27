"""
Tests for ant-design/ant-design#57440
Feature: Typography actions placement
"""

import subprocess
import os
import json

REPO = "/workspace/antd"

# Shared helper: TypeScript compiler API type-check that only reports
# diagnostics for the test file, avoiding OOM and errors in transitive deps.
_TS_CHECK_SCRIPT = r"""
const ts = require("typescript");
const fs = require("fs");
const path = require("path");
const testFile = path.resolve(process.argv[2]);
const options = {
    target: ts.ScriptTarget.ES2020,
    module: ts.ModuleKind.ESNext,
    moduleResolution: ts.ModuleResolutionKind.Bundler,
    esModuleInterop: true,
    jsx: ts.JsxEmit.React,
    skipLibCheck: true,
    noEmit: true,
    strict: false,
    baseUrl: ".",
    types: ["node", "react"],
};
const program = ts.createProgram([testFile], options);
const sf = program.getSourceFile(testFile);
const diags = [
    ...program.getSyntacticDiagnostics(sf),
    ...program.getSemanticDiagnostics(sf),
];
if (diags.length > 0) {
    diags.forEach(d => {
        const msg = ts.flattenDiagnosticMessageText(d.messageText, "\n");
        console.error(msg);
    });
    process.exit(1);
}
console.log("Type check passed");
"""


def _run_ts_type_check(ts_code, filename, timeout=180):
    """Run a targeted TypeScript type check using the compiler API."""
    test_file = os.path.join(REPO, filename)
    checker_file = os.path.join(REPO, "_eval_ts_checker.js")
    env = dict(os.environ)
    env["NODE_OPTIONS"] = "--max-old-space-size=4096"

    with open(test_file, 'w') as f:
        f.write(ts_code)
    with open(checker_file, 'w') as f:
        f.write(_TS_CHECK_SCRIPT)

    try:
        return subprocess.run(
            ["node", checker_file, filename],
            capture_output=True, text=True, timeout=timeout, cwd=REPO,
            env=env,
        )
    finally:
        for p in [test_file, checker_file]:
            if os.path.exists(p):
                os.remove(p)


def test_actions_config_typescript_compilation():
    """
    Fail-to-pass: ActionsConfig interface is properly exported and usable.
    """
    ts_code = """\
import type { ActionsConfig } from './components/typography/Base/index';
const testConfig: ActionsConfig = { placement: 'start' };
const testConfig2: ActionsConfig = { placement: 'end' };
export type TestActionsConfig = ActionsConfig;
"""
    result = _run_ts_type_check(ts_code, "_eval_actions_config_test.ts")
    assert result.returncode == 0, \
        f"ActionsConfig interface not properly exported: {result.stdout}{result.stderr}"


def test_actions_prop_type_integration():
    """
    Fail-to-pass: BlockProps accepts actions prop with correct type.
    """
    ts_code = """\
import type { BlockProps } from './components/typography/Base/index';
const testProps: BlockProps = { actions: { placement: 'start' } };
"""
    result = _run_ts_type_check(ts_code, "_eval_actions_prop_test.ts")
    assert result.returncode == 0, \
        f"BlockProps does not accept actions prop: {result.stdout}{result.stderr}"


def test_actions_placement_behavior():
    """
    Fail-to-pass: Actions placement prop changes component rendering.
    Verifies that when placement='start', the actions appear before text content.
    """
    jest_test_code = """
import * as React from 'react';
import { render } from '@testing-library/react';
import Typography from './components/typography';
const { Text } = Typography;

describe('Typography actions placement', () => {
    it('should render actions before text when placement is start', () => {
        const { container } = render(
            React.createElement(Text, { copyable: true, actions: { placement: 'start' } }, 'Test Content')
        );
        const typographyEl = container.querySelector('.ant-typography');
        expect(typographyEl).toBeTruthy();

        // Get all child elements
        const children = Array.from(typographyEl.children);

        // Find the actions element
        const actionsEl = children.find(el => el.classList.contains('ant-typography-actions'));
        expect(actionsEl).toBeTruthy();

        // When placement='start', actions should come before text content
        // The actions element should be the first significant child
        const actionsIndex = children.indexOf(actionsEl);
        expect(actionsIndex).toBe(0);
    });

    it('should render actions after text when placement is end (default)', () => {
        const { container } = render(
            React.createElement(Text, { copyable: true }, 'Test Content')
        );
        const typographyEl = container.querySelector('.ant-typography');
        expect(typographyEl).toBeTruthy();

        // Get all child elements
        const children = Array.from(typographyEl.children);

        // Find the actions element
        const actionsEl = children.find(el => el.classList.contains('ant-typography-actions'));
        expect(actionsEl).toBeTruthy();

        // When placement='end' (default), actions should be last
        const actionsIndex = children.indexOf(actionsEl);
        expect(actionsIndex).toBe(children.length - 1);
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
        assert result.returncode == 0, f"Actions placement behavior tests failed: stdout={result.stdout[-2000:]}, stderr={result.stderr[-500:]}"
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


def test_ellipsis_layout_deps_integration():
    """
    Fail-to-pass: Ellipsis component accepts dependencies that affect layout measurement.
    """
    ts_code = """\
import * as React from 'react';
import type { EllipsisProps } from './components/typography/Base/Ellipsis';
const props: EllipsisProps = {
    width: 100, rows: 1,
    onEllipsis: () => {}, expanded: false,
    measureDeps: ['start'], miscDeps: [],
    children: (cutChildren: React.ReactNode[], canEllipsis: boolean) => React.createElement('span', {}, 'test')
};
"""
    result = _run_ts_type_check(ts_code, "_eval_measure_deps_test.tsx")
    assert result.returncode == 0, \
        f"Ellipsis does not accept layout measurement dependencies: {result.stdout}{result.stderr}"


def test_actions_start_css_class_applied():
    """
    Fail-to-pass: When placement='start', the actions container receives a
    distinguishing CSS class so that start-specific styles can target it.
    """
    jest_test_code = """
import * as React from 'react';
import { render } from '@testing-library/react';
import Typography from './components/typography';
const { Text } = Typography;

describe('Typography actions start CSS class', () => {
    it('should apply a start-specific CSS class when placement is start', () => {
        const { container } = render(
            React.createElement(Text, { copyable: true, actions: { placement: 'start' } }, 'Test')
        );
        const actionsEl = container.querySelector('[class*="actions"]');
        expect(actionsEl).toBeTruthy();
        expect(actionsEl.className).toMatch(/start/);
    });

    it('should NOT apply a start CSS class for default (end) placement', () => {
        const { container } = render(
            React.createElement(Text, { copyable: true }, 'Test')
        );
        const actionsEl = container.querySelector('[class*="actions"]');
        expect(actionsEl).toBeTruthy();
        expect(actionsEl.className).not.toMatch(/start/);
    });
});
"""
    test_file_path = os.path.join(REPO, "actions-start-css-class.test.tsx")
    with open(test_file_path, 'w') as f:
        f.write(jest_test_code)

    try:
        subprocess.run(["npm", "run", "version"], capture_output=True, timeout=60, cwd=REPO)
        result = subprocess.run(
            ["npx", "jest", "--config", ".jest.js", test_file_path, "--no-cache", "--passWithNoTests"],
            capture_output=True, text=True, timeout=300, cwd=REPO,
        )
        assert result.returncode == 0, f"Actions start CSS class tests failed: stdout={result.stdout[-2000:]}, stderr={result.stderr[-500:]}"
    finally:
        if os.path.exists(test_file_path):
            os.remove(test_file_path)


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
