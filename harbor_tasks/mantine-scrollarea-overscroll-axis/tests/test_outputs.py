"""
Benchmark tests for mantinedev/mantine#8591

Tests that ScrollArea correctly applies axis-aware overscroll-behavior
when using directional scrollbars (x or y).
"""
import subprocess
import os
import textwrap

REPO = "/workspace/mantine"

JEST_TEST_CONTENT = textwrap.dedent(r"""
import React from 'react';
import { render, cleanup } from '@testing-library/react';
import { ScrollArea, MantineProvider } from '@mantine/core';

afterEach(cleanup);

function renderWithProvider(ui: React.ReactElement) {
  return render(React.createElement(MantineProvider, null, ui));
}

describe('ScrollArea overscroll axis behavior', () => {
  it('produces value-auto for x-axis scrollbars with contain', () => {
    const { container } = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'contain',
        scrollbars: 'x',
      }, 'test')
    );
    const html = container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior[^;]*contain\s+auto/);
  });

  it('produces auto-value for y-axis scrollbars with contain', () => {
    const { container } = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'contain',
        scrollbars: 'y',
      }, 'test')
    );
    const html = container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior[^;]*auto\s+contain/);
  });

  it('handles different overscrollBehavior values with x scrollbars', () => {
    // Test with 'none'
    let result = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'none',
        scrollbars: 'x',
      }, 'test')
    );
    let html = result.container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior[^;]*none\s+auto/);
    result.unmount();

    // Test with 'auto'
    result = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'auto',
        scrollbars: 'x',
      }, 'test')
    );
    html = result.container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior[^;]*auto\s+auto/);
  });

  it('handles different overscrollBehavior values with y scrollbars', () => {
    // Test with 'none'
    let result = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'none',
        scrollbars: 'y',
      }, 'test')
    );
    let html = result.container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior[^;]*auto\s+none/);
    result.unmount();

    // Test with 'auto'
    result = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'auto',
        scrollbars: 'y',
      }, 'test')
    );
    html = result.container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior[^;]*auto\s+auto/);
  });

  it('keeps single value for xy scrollbars with overscrollBehavior', () => {
    const { container } = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'contain',
        scrollbars: 'xy',
      }, 'test')
    );
    const html = container.innerHTML;
    // Should have contain but NOT contain auto or auto contain
    expect(html).toMatch(/--scrollarea-over-scroll-behavior/);
    expect(html).not.toMatch(/--scrollarea-over-scroll-behavior[^;]*contain\s+auto/);
    expect(html).not.toMatch(/--scrollarea-over-scroll-behavior[^;]*auto\s+contain/);
  });

  it('keeps single value with default scrollbars', () => {
    const { container } = renderWithProvider(
      React.createElement(ScrollArea, {
        overscrollBehavior: 'contain',
      }, 'test')
    );
    const html = container.innerHTML;
    expect(html).toMatch(/--scrollarea-over-scroll-behavior/);
    expect(html).not.toMatch(/--scrollarea-over-scroll-behavior[^;]*contain\s+auto/);
  });

  it('does not set overscroll variable when overscrollBehavior is not provided', () => {
    const { container } = renderWithProvider(
      React.createElement(ScrollArea, {
        scrollbars: 'x',
      }, 'test')
    );
    const html = container.innerHTML;
    // overscrollBehavior is undefined so the CSS variable should not be set
    expect(html).not.toMatch(/--scrollarea-over-scroll-behavior[^;]*auto/);
  });
});
""")

JEST_TEST_PATH = os.path.join(
    REPO,
    "packages/@mantine/core/src/components/ScrollArea/ScrollArea.overscroll.test.tsx",
)


def _write_jest_test():
    with open(JEST_TEST_PATH, "w") as f:
        f.write(JEST_TEST_CONTENT)


def _cleanup_jest_test():
    if os.path.exists(JEST_TEST_PATH):
        os.unlink(JEST_TEST_PATH)


def _run_jest(test_pattern=None, timeout=120):
    cmd = ["npx", "jest", JEST_TEST_PATH, "--no-coverage"]
    if test_pattern:
        cmd.extend(["-t", test_pattern])
    return subprocess.run(
        cmd, capture_output=True, text=True, timeout=timeout, cwd=REPO
    )


# ---- Fail-to-pass tests (f2p) ----


def test_overscroll_x_axis():
    """f2p: ScrollArea with scrollbars='x' should produce 'value auto' for overscroll-behavior."""
    _write_jest_test()
    try:
        r = _run_jest("x-axis scrollbars with contain")
        assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    finally:
        _cleanup_jest_test()


def test_overscroll_y_axis():
    """f2p: ScrollArea with scrollbars='y' should produce 'auto value' for overscroll-behavior."""
    _write_jest_test()
    try:
        r = _run_jest("y-axis scrollbars with contain")
        assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    finally:
        _cleanup_jest_test()


def test_overscroll_various_x_values():
    """f2p: Different overscrollBehavior values (none, auto) work with x-axis scrollbars."""
    _write_jest_test()
    try:
        r = _run_jest("different overscrollBehavior values with x")
        assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    finally:
        _cleanup_jest_test()


def test_overscroll_various_y_values():
    """f2p: Different overscrollBehavior values (none, auto) work with y-axis scrollbars."""
    _write_jest_test()
    try:
        r = _run_jest("different overscrollBehavior values with y")
        assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    finally:
        _cleanup_jest_test()


# ---- Pass-to-pass tests (p2p) ----


def test_repo_scrollarea_tests():
    """p2p: Existing ScrollArea Jest tests still pass."""
    r = subprocess.run(
        ["npx", "jest", "ScrollArea.test", "--no-coverage"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"Existing tests failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"


def test_repo_eslint_scrollarea():
    """p2p: ESLint passes on ScrollArea.tsx (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_prettier_scrollarea():
    """p2p: Prettier formatting check passes on ScrollArea.tsx (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/core/src/components/ScrollArea/ScrollArea.tsx"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_typecheck():
    """p2p: TypeScript typecheck passes at repo root (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "tsc", "--noEmit"],
        capture_output=True, text=True, timeout=300, cwd=REPO,
    )
    assert r.returncode == 0, f"Typecheck failed:\n{r.stderr[-500:]}"


def test_repo_stylelint_scrollarea():
    """p2p: Stylelint passes on ScrollArea CSS (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "stylelint", "packages/@mantine/core/src/components/ScrollArea/*.css"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Stylelint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_eslint_scrollarea_dir():
    """p2p: ESLint passes on entire ScrollArea directory (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "eslint", "packages/@mantine/core/src/components/ScrollArea/"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert r.returncode == 0, f"ESLint failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_repo_prettier_scrollarea_dir():
    """p2p: Prettier formatting check passes on all ScrollArea files (pass_to_pass)."""
    r = subprocess.run(
        ["npx", "prettier", "--check", "packages/@mantine/core/src/components/ScrollArea/"],
        capture_output=True, text=True, timeout=60, cwd=REPO,
    )
    assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}\n{r.stderr[-500:]}"


def test_overscroll_xy_unchanged():
    """p2p: xy scrollbars and default scrollbars still produce single overscroll value."""
    _write_jest_test()
    try:
        r = _run_jest("single value")
        assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    finally:
        _cleanup_jest_test()


def test_no_overscroll_no_change():
    """p2p: Without overscrollBehavior prop, overscroll CSS variable is not set."""
    _write_jest_test()
    try:
        r = _run_jest("overscroll variable when overscrollBehavior is not provided")
        assert r.returncode == 0, f"Test failed:\n{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    finally:
        _cleanup_jest_test()
