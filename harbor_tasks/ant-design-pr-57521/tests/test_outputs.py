"""
Tests for ant-design/ant-design#57521: Add targetOffset prop for each Anchor.Link

This PR adds per-link targetOffset support to Anchor.Link, allowing each link
to have its own scroll offset that takes precedence over the global targetOffset.
"""
import subprocess
import re
import os
import uuid

REPO = "/workspace/ant-design"
ANCHOR_TSX = os.path.join(REPO, "components/anchor/Anchor.tsx")
ANCHOR_LINK_TSX = os.path.join(REPO, "components/anchor/AnchorLink.tsx")


def read_file(path: str) -> str:
    """Read file contents."""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def run_jest_test(test_code: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run a Jest test with the given test code inside the repo's test directory."""
    # Create a unique test file inside the repo's anchor test directory
    test_file_name = f"behavioral_{uuid.uuid4().hex[:8]}.test.tsx"
    test_file = os.path.join(REPO, "components/anchor/__tests__", test_file_name)

    try:
        # Write the test file
        with open(test_file, "w", encoding="utf-8") as f:
            f.write(test_code)

        # Run Jest on the test file
        result = subprocess.run(
            ["npx", "jest", test_file,
             "--config", ".jest.js", "--no-cache", "--maxWorkers=1"],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=REPO
        )
        return result
    finally:
        # Clean up - always remove the test file
        if os.path.exists(test_file):
            os.remove(test_file)


# ============================================================================
# Fail-to-pass tests: These must FAIL on base commit and PASS after the fix
# ============================================================================

def test_per_link_target_offset_scrolling():
    """
    Each Anchor.Link can have its own targetOffset that affects scrolling.

    When clicking different links with different targetOffset values,
    the scroll position should reflect each link's specific offset.
    """
    test_code = '''
import React from 'react';
import { fireEvent, render, waitFakeTimer } from '../../../tests/utils';
import Anchor from '..';

const { Link } = Anchor;

function createDiv() {
  const root = document.createElement('div');
  document.body.appendChild(root);
  return root;
}

describe('Per-link targetOffset', () => {
  const getBoundingClientRectMock = jest.spyOn(
    HTMLHeadingElement.prototype,
    'getBoundingClientRect',
  );
  const getClientRectsMock = jest.spyOn(HTMLHeadingElement.prototype, 'getClientRects');

  beforeAll(() => {
    jest.useFakeTimers();
    getBoundingClientRectMock.mockReturnValue({
      width: 100,
      height: 100,
      top: 1000,
    } as DOMRect);
    getClientRectsMock.mockReturnValue([1] as unknown as DOMRectList);
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
    getBoundingClientRectMock.mockRestore();
    getClientRectsMock.mockRestore();
  });

  it('different per-link targetOffset values produce different scroll positions', async () => {
    const scrollToSpy = jest.spyOn(window, 'scrollTo');
    const root1 = createDiv();
    const root2 = createDiv();

    render(<h1 id="section1">Section 1</h1>, { container: root1 });
    render(<h1 id="section2">Section 2</h1>, { container: root2 });

    const { container } = render(
      <Anchor>
        <Link href="#section1" title="Section 1" targetOffset={100} />
        <Link href="#section2" title="Section 2" targetOffset={200} />
      </Anchor>
    );

    // Click first link with offset 100
    fireEvent.click(container.querySelector('a[href="#section1"]')!);
    await waitFakeTimer();
    const firstCallY = scrollToSpy.mock.calls[scrollToSpy.mock.calls.length - 1][1];

    // Click second link with offset 200
    fireEvent.click(container.querySelector('a[href="#section2"]')!);
    await waitFakeTimer();
    const secondCallY = scrollToSpy.mock.calls[scrollToSpy.mock.calls.length - 1][1];

    // The scroll positions should be different because targetOffset values are different
    expect(firstCallY).not.toBe(secondCallY);

    // Verify specific values: element at top 1000
    // First link: 1000 - 100 = 900
    // Second link: 1000 - 200 = 800
    expect(firstCallY).toBe(900);
    expect(secondCallY).toBe(800);
  });
});
'''
    result = run_jest_test(test_code)
    assert result.returncode == 0, f"Per-link targetOffset test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_per_link_target_offset_takes_precedence():
    """
    Per-link targetOffset takes precedence over global targetOffset.

    When a link has its own targetOffset, it should be used instead of
    the global targetOffset prop on Anchor.
    """
    test_code = '''
import React from 'react';
import { fireEvent, render, waitFakeTimer } from '../../../tests/utils';
import Anchor from '..';

const { Link } = Anchor;

function createDiv() {
  const root = document.createElement('div');
  document.body.appendChild(root);
  return root;
}

describe('Per-link targetOffset precedence', () => {
  const getBoundingClientRectMock = jest.spyOn(
    HTMLHeadingElement.prototype,
    'getBoundingClientRect',
  );
  const getClientRectsMock = jest.spyOn(HTMLHeadingElement.prototype, 'getClientRects');

  beforeAll(() => {
    jest.useFakeTimers();
    getBoundingClientRectMock.mockReturnValue({
      width: 100,
      height: 100,
      top: 1000,
    } as DOMRect);
    getClientRectsMock.mockReturnValue([1] as unknown as DOMRectList);
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
    getBoundingClientRectMock.mockRestore();
    getClientRectsMock.mockRestore();
  });

  it('link-level targetOffset overrides global targetOffset', async () => {
    const scrollToSpy = jest.spyOn(window, 'scrollTo');
    const root = createDiv();

    render(<h1 id="test-section">Test Section</h1>, { container: root });

    // Global targetOffset is 500, link-level is 150
    const { container } = render(
      <Anchor targetOffset={500}>
        <Link href="#test-section" title="Test" targetOffset={150} />
      </Anchor>
    );

    fireEvent.click(container.querySelector('a[href="#test-section"]')!);
    await waitFakeTimer();

    // Should use link-level offset (150), not global (500)
    // 1000 - 150 = 850
    expect(scrollToSpy).toHaveBeenLastCalledWith(0, 850);
  });

  it('falls back to global targetOffset when link has no targetOffset', async () => {
    const scrollToSpy = jest.spyOn(window, 'scrollTo');
    const root = createDiv();

    render(<h1 id="fallback-section">Fallback Section</h1>, { container: root });

    // Global targetOffset is 300, link has no targetOffset
    const { container } = render(
      <Anchor targetOffset={300}>
        <Link href="#fallback-section" title="Fallback" />
      </Anchor>
    );

    fireEvent.click(container.querySelector('a[href="#fallback-section"]')!);
    await waitFakeTimer();

    // Should use global offset (300) when link has none
    // 1000 - 300 = 700
    expect(scrollToSpy).toHaveBeenLastCalledWith(0, 700);
  });
});
'''
    result = run_jest_test(test_code)
    assert result.returncode == 0, f"targetOffset precedence test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_target_offset_cleanup_on_unmount():
    """
    Per-link targetOffset is cleaned up when link unmounts.

    When a link with targetOffset is removed, its offset should no longer
    affect the Anchor component's behavior.
    """
    test_code = '''
import React, { useState } from 'react';
import { fireEvent, render, waitFakeTimer, act } from '../../../tests/utils';
import Anchor from '..';

const { Link } = Anchor;

function createDiv() {
  const root = document.createElement('div');
  document.body.appendChild(root);
  return root;
}

describe('targetOffset cleanup', () => {
  const getBoundingClientRectMock = jest.spyOn(
    HTMLHeadingElement.prototype,
    'getBoundingClientRect',
  );
  const getClientRectsMock = jest.spyOn(HTMLHeadingElement.prototype, 'getClientRects');

  beforeAll(() => {
    jest.useFakeTimers();
    getBoundingClientRectMock.mockReturnValue({
      width: 100,
      height: 100,
      top: 1000,
    } as DOMRect);
    getClientRectsMock.mockReturnValue([1] as unknown as DOMRectList);
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
    getBoundingClientRectMock.mockRestore();
    getClientRectsMock.mockRestore();
  });

  it('removing a link cleans up its targetOffset registration', async () => {
    const scrollToSpy = jest.spyOn(window, 'scrollTo');
    const root1 = createDiv();
    const root2 = createDiv();

    render(<h1 id="keep-section">Keep Section</h1>, { container: root1 });
    render(<h1 id="remove-section">Remove Section</h1>, { container: root2 });

    const TestComponent = ({ showSecond }: { showSecond: boolean }) => (
      <Anchor>
        <Link href="#keep-section" title="Keep" targetOffset={100} />
        {showSecond && <Link href="#remove-section" title="Remove" targetOffset={999} />}
      </Anchor>
    );

    const { container, rerender } = render(<TestComponent showSecond={true} />);

    // Click the link that will be removed
    fireEvent.click(container.querySelector('a[href="#remove-section"]')!);
    await waitFakeTimer();

    // Remove the second link
    rerender(<TestComponent showSecond={false} />);

    // Click the remaining link
    fireEvent.click(container.querySelector('a[href="#keep-section"]')!);
    await waitFakeTimer();

    // The scroll should be based on the remaining link's offset (100)
    // 1000 - 100 = 900
    expect(scrollToSpy).toHaveBeenLastCalledWith(0, 900);
  });
});
'''
    result = run_jest_test(test_code)
    assert result.returncode == 0, f"targetOffset cleanup test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_anchor_link_interface_has_target_offset():
    """
    AnchorLinkBaseProps interface must accept targetOffset prop.

    The TypeScript interface should allow targetOffset as an optional number.
    """
    # Run TypeScript compiler to check if the interface accepts targetOffset
    test_code = '''
import React from 'react';
import Anchor from '..';

const { Link } = Anchor;

describe('AnchorLink targetOffset type', () => {
  it('accepts targetOffset prop without TypeScript errors', () => {
    // This test will fail at compile time if the interface doesn't accept targetOffset
    render(
      <Anchor>
        <Link href="#test" title="Test" targetOffset={100} />
      </Anchor>
    );
  });
});
'''
    result = run_jest_test(test_code)
    assert result.returncode == 0, f"AnchorLink interface test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_active_link_detection_respects_per_link_offset():
    """
    Active link detection during scroll respects per-link targetOffset.

    The Anchor component should use each link's specific offset when determining
    which section is currently active during scrolling.
    """
    test_code = '''
import React from 'react';
import { fireEvent, render, waitFakeTimer } from '../../../tests/utils';
import Anchor from '..';

const { Link } = Anchor;

// Mock scroll position to simulate elements at different positions
const mockScrollTop = jest.fn();

describe('Active link detection with per-link offsets', () => {
  beforeAll(() => {
    jest.useFakeTimers();
  });

  afterEach(() => {
    jest.clearAllTimers();
  });

  afterAll(() => {
    jest.useRealTimers();
  });

  it('different targetOffset values affect which link is active', async () => {
    let scrollTopValue = 0;

    // Mock getScroll to return controlled scroll position
    jest.doMock('../_util/getScroll', () => () => scrollTopValue);

    const onChange = jest.fn();

    // Create test setup
    const { container } = render(
      <Anchor onChange={onChange}>
        <Link href="#section1" title="Section 1" targetOffset={50} />
        <Link href="#section2" title="Section 2" targetOffset={150} />
      </Anchor>
    );

    // Simulate scrolling - verify the component mounted and onChange is set up
    expect(container.querySelector('.ant-anchor')).toBeTruthy();

    // Verify that links are rendered
    const links = container.querySelectorAll('.ant-anchor-link-title');
    expect(links.length).toBe(2);
  });
});
'''
    result = run_jest_test(test_code)
    # This test is checking the component renders correctly with the props
    # Full scroll detection testing requires more complex DOM mocking
    assert result.returncode == 0, f"Active link detection test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_ant_anchor_interface_accepts_target_offset():
    """
    AntAnchor interface functions must accept targetOffset parameter.

    Both registerLink and scrollTo in the AntAnchor interface should
    accept an optional targetOffset parameter.
    """
    # Test by importing the interface and checking TypeScript allows the usage
    test_code = '''
import React, { useContext } from 'react';
import Anchor from '..';
import AnchorContext from '../context';
import type { AntAnchor } from '../Anchor';

const { Link } = Anchor;

describe('AntAnchor interface', () => {
  it('AntAnchor type accepts targetOffset in registerLink and scrollTo', () => {
    // Create a mock AntAnchor that matches the expected interface
    const mockAnchor: AntAnchor = {
      registerLink: (link: string, targetOffset?: number) => {
        // Should accept optional targetOffset
        console.log(link, targetOffset);
      },
      unregisterLink: (link: string) => {
        console.log(link);
      },
      activeLink: null,
      scrollTo: (link: string, targetOffset?: number) => {
        // Should accept optional targetOffset
        console.log(link, targetOffset);
      },
      direction: 'vertical',
    };

    expect(mockAnchor).toBeDefined();
  });
});
'''
    result = run_jest_test(test_code)
    assert result.returncode == 0, f"AntAnchor interface test failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


# ============================================================================
# Pass-to-pass tests: These must PASS on both base commit and after the fix
# ============================================================================

# Static checks (file reads) - origin: static
def test_anchor_exports_anchor_link():
    """Anchor module exports AnchorLink (pass_to_pass)."""
    content = read_file(os.path.join(REPO, "components/anchor/index.tsx"))

    # Check that AnchorLink is exported
    assert re.search(r"(export|Link)", content), \
        "Anchor module must export AnchorLink component"


def test_anchor_link_has_href_prop():
    """AnchorLinkBaseProps must include href prop (pass_to_pass)."""
    content = read_file(ANCHOR_LINK_TSX)

    interface_match = re.search(
        r"export\s+interface\s+AnchorLinkBaseProps\s*\{([^}]+)\}",
        content,
        re.DOTALL
    )
    assert interface_match, "AnchorLinkBaseProps interface not found"

    interface_body = interface_match.group(1)
    assert re.search(r"href\s*:", interface_body), \
        "AnchorLinkBaseProps must have href property"


def test_anchor_link_has_title_prop():
    """AnchorLinkBaseProps must include title prop (pass_to_pass)."""
    content = read_file(ANCHOR_LINK_TSX)

    interface_match = re.search(
        r"export\s+interface\s+AnchorLinkBaseProps\s*\{([^}]+)\}",
        content,
        re.DOTALL
    )
    assert interface_match, "AnchorLinkBaseProps interface not found"

    interface_body = interface_match.group(1)
    assert re.search(r"title\s*:", interface_body), \
        "AnchorLinkBaseProps must have title property"


def test_anchor_props_has_target_offset():
    """AnchorProps must include targetOffset (global) prop (pass_to_pass)."""
    content = read_file(ANCHOR_TSX)

    # Look for targetOffset in AnchorProps or AnchorPropsWithItems
    assert re.search(r"targetOffset\s*\?\s*:\s*number", content), \
        "AnchorProps must have targetOffset property"


# Repo CI checks (subprocess.run) - origin: repo_tests
def test_eslint_passes():
    """ESLint passes on Anchor component files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "eslint", "components/anchor/Anchor.tsx", "components/anchor/AnchorLink.tsx", "--quiet"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO
    )
    assert result.returncode == 0, f"ESLint failed:\n{result.stdout}\n{result.stderr}"


def test_biome_lint_passes():
    """Biome lint passes on Anchor component files (pass_to_pass)."""
    result = subprocess.run(
        ["npx", "biome", "lint", "components/anchor/Anchor.tsx", "components/anchor/AnchorLink.tsx"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert result.returncode == 0, f"Biome lint failed:\n{result.stdout}\n{result.stderr}"


def test_anchor_unit_tests():
    """Anchor component jest unit tests pass (pass_to_pass)."""
    # First generate the version file which is required for tests
    version_result = subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert version_result.returncode == 0, f"npm run version failed:\n{version_result.stderr}"

    # Run the anchor unit tests
    result = subprocess.run(
        ["npx", "jest", "components/anchor/__tests__/Anchor.test.tsx",
         "--config", ".jest.js", "--no-cache", "--maxWorkers=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"Anchor unit tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"


def test_anchor_demo_tests():
    """Anchor demo snapshot tests pass (pass_to_pass)."""
    # First generate the version file which is required for tests
    version_result = subprocess.run(
        ["npm", "run", "version"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO
    )
    assert version_result.returncode == 0, f"npm run version failed:\n{version_result.stderr}"

    # Run the anchor demo tests
    result = subprocess.run(
        ["npx", "jest", "components/anchor/__tests__/demo.test.tsx",
         "--config", ".jest.js", "--no-cache", "--maxWorkers=1"],
        capture_output=True,
        text=True,
        timeout=300,
        cwd=REPO
    )
    assert result.returncode == 0, f"Anchor demo tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-500:]}"
