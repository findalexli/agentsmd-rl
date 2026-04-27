"""
Test file for ant-design Popconfirm icon semantic support PR #57528
Tests that classNames.icon and styles.icon are properly supported in Popconfirm component.
"""

import subprocess
import re
import os

REPO = "/workspace/ant-design"


def test_icon_classnames_behavior():
    """
    Fail-to-pass: Verify that classNames.icon is actually applied to the icon element.
    Runs the semantic tests which check that the custom-icon class is rendered.
    """
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # Generate version file first
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)

    # Run only the semantic.test.tsx which tests that icon classNames work
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/semantic.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm semantic tests failed (classNames.icon not working):\n{r.stderr[-1000:]}"


def test_icon_styles_behavior():
    """
    Fail-to-pass: Verify that styles.icon is actually applied to the icon element.
    Runs the semantic tests which check that the color style is rendered.
    """
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # Generate version file first
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)

    # Run only the semantic.test.tsx which tests that icon styles work
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/semantic.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm semantic tests failed (styles.icon not working):\n{r.stderr[-1000:]}"


def test_type_definition_behavior():
    """
    Fail-to-pass: Verify that TypeScript accepts icon in classNames and styles.
    Runs the type tests which validate the type definitions at compile time.
    """
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # Generate version file first
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)

    # Run the type test which validates icon is accepted in classNames/styles
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/type.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm type tests failed (icon type not defined):\n{r.stderr[-1000:]}"


def test_demo_renders_icon():
    """
    Fail-to-pass: Verify that the semantic demo renders with icon element.
    The demo-semantic snapshot test validates the icon appears in the semantics list.
    """
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # Generate version file first
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)

    # Run the demo-semantic test which validates the demo renders icon correctly
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/demo-semantic.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm demo-semantic test failed (icon not in demo):\n{r.stderr[-1000:]}"


def test_icon_uses_popconfirm_semantic_type():
    """
    Fail-to-pass: Verify that the icon classNames/styles use Popconfirm-specific types.
    This is validated by TypeScript compilation - if PurePanel uses wrong types,
    the TS check will fail.
    """
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}

    # TypeScript will catch if PopconfirmSemanticAllType is not properly used
    r = subprocess.run(
        ["npx", "tsc", "--noEmit", "components/popconfirm/PurePanel.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"TypeScript check failed for PurePanel.tsx (wrong semantic types):\n{r.stderr[-500:]}"


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


def test_repo_tsc():
    """Repo's TypeScript typecheck passes (pass_to_pass)."""
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"TypeScript check failed:\n{r.stderr[-500:]}"


def test_repo_popconfirm_unit():
    """Repo's Popconfirm unit tests pass (pass_to_pass)."""
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # First generate version file
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/index.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm unit tests failed:\n{r.stderr[-1000:]}"


def test_repo_popconfirm_a11y():
    """Repo's Popconfirm accessibility tests pass (pass_to_pass)."""
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # First generate version file
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/a11y.test.ts", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm a11y tests failed:\n{r.stderr[-1000:]}"


def test_repo_popconfirm_demo():
    """Repo's Popconfirm demo tests pass (pass_to_pass)."""
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # First generate version file
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/demo.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm demo tests failed:\n{r.stderr[-1000:]}"


def test_repo_popconfirm_type():
    """Repo's Popconfirm TypeScript type tests pass (pass_to_pass)."""
    env = {**os.environ, "NODE_OPTIONS": "--max-old-space-size=4096"}
    # First generate version file
    subprocess.run(["npm", "run", "version"], capture_output=True, cwd=REPO, env=env)
    r = subprocess.run(
        ["npx", "jest", "--config", ".jest.js", "components/popconfirm/__tests__/type.test.tsx", "--no-cache"],
        capture_output=True, text=True, timeout=300, cwd=REPO, env=env,
    )
    assert r.returncode == 0, f"Popconfirm type tests failed:\n{r.stderr[-1000:]}"
