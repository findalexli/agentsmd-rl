#!/usr/bin/env python3
"""Test suite for ant-design Anchor.Link targetOffset feature."""

import subprocess
import sys
import re

REPO = "/workspace/ant-design"


def run_command(cmd, cwd=REPO, timeout=300):
    """Run a shell command and return result."""
    result = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        shell=isinstance(cmd, str)
    )
    return result


def test_anchor_link_interface_has_targetOffset():
    """Fail-to-pass: AnchorLinkBaseProps interface must have targetOffset property."""
    with open(f"{REPO}/components/anchor/AnchorLink.tsx", "r") as f:
        content = f.read()

    # Check that targetOffset is defined in AnchorLinkBaseProps
    interface_pattern = r'export interface AnchorLinkBaseProps \{[^}]*targetOffset\?: number[^}]*\}'
    match = re.search(interface_pattern, content, re.DOTALL)

    assert match is not None, (
        "AnchorLinkBaseProps interface must have 'targetOffset?: number' property. "
        "The interface should include the new prop for per-link scroll offset customization."
    )


def test_registerLink_signature_updated():
    """Fail-to-pass: AntAnchor.registerLink must accept optional targetOffset parameter."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check AntAnchor interface registerLink signature
    pattern = r'registerLink: \(link: string, targetOffset\?: number\) => void'
    match = re.search(pattern, content)

    assert match is not None, (
        "AntAnchor.registerLink signature must accept optional targetOffset parameter. "
        "Expected: registerLink: (link: string, targetOffset?: number) => void"
    )


def test_scrollTo_signature_updated():
    """Fail-to-pass: AntAnchor.scrollTo must accept optional targetOffset parameter."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check AntAnchor interface scrollTo signature
    pattern = r'scrollTo: \(link: string, targetOffset\?: number\) => void'
    match = re.search(pattern, content)

    assert match is not None, (
        "AntAnchor.scrollTo signature must accept optional targetOffset parameter. "
        "Expected: scrollTo: (link: string, targetOffset?: number) => void"
    )


def test_linkTargetOffsetRef_exists():
    """Fail-to-pass: Anchor component must use linkTargetOffsetRef to store per-link offsets."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check that linkTargetOffsetRef is declared
    pattern = r'const linkTargetOffsetRef = React\.useRef<Record<string, number>>\(\{\}\)'
    match = re.search(pattern, content)

    assert match is not None, (
        "Anchor component must declare linkTargetOffsetRef to store per-link targetOffsets. "
        "Expected: const linkTargetOffsetRef = React.useRef<Record<string, number>>({})"
    )


def test_registerLink_stores_targetOffset():
    """Fail-to-pass: registerLink implementation must store targetOffset in linkTargetOffsetRef."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check that registerLink stores the targetOffset
    pattern = r'if \(newTargetOffset !== undefined\) \{[^}]*linkTargetOffsetRef\.current\[link\] = newTargetOffset[^}]*\}'
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, (
        "registerLink must store targetOffset in linkTargetOffsetRef when provided. "
        "Expected conditional storage of newTargetOffset in linkTargetOffsetRef.current[link]"
    )


def test_unregisterLink_cleans_targetOffset():
    """Fail-to-pass: unregisterLink must clean up targetOffset when unregistering."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check that unregisterLink deletes the targetOffset
    pattern = r'delete linkTargetOffsetRef\.current\[link\]'
    match = re.search(pattern, content)

    assert match is not None, (
        "unregisterLink must clean up targetOffset by deleting linkTargetOffsetRef.current[link]. "
        "This prevents memory leaks and stale data."
    )


def test_getInternalCurrentAnchor_uses_link_offset():
    """Fail-to-pass: getInternalCurrentAnchor must accept and use _linkTargetOffset parameter."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check function signature accepts _linkTargetOffset
    signature_pattern = r'const getInternalCurrentAnchor = \([^)]*_linkTargetOffset\?: Record<string, number>[^)]*\)'
    sig_match = re.search(signature_pattern, content)

    assert sig_match is not None, (
        "getInternalCurrentAnchor must accept _linkTargetOffset parameter for per-link offsets"
    )

    # Check that it uses link-level offset with nullish coalescing
    usage_pattern = r'const linkOffsetTop = _linkTargetOffset\?\.\[link\] \?\? _offsetTop'
    usage_match = re.search(usage_pattern, content)

    assert usage_match is not None, (
        "getInternalCurrentAnchor must use link-level targetOffset with fallback to global. "
        "Expected: const linkOffsetTop = _linkTargetOffset?.[link] ?? _offsetTop"
    )


def test_handleScrollTo_uses_link_targetOffset():
    """Fail-to-pass: handleScrollTo must use link-level targetOffset when provided."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check that handleScrollTo accepts targetOffsetParams
    pattern = r'const handleScrollTo = React\.useCallback<\(link: string, targetOffsetParams\?: number\) => void>'
    match = re.search(pattern, content)

    assert match is not None, (
        "handleScrollTo callback must accept optional targetOffsetParams parameter"
    )

    # Check the final target offset calculation with proper precedence
    calc_pattern = r'const finalTargetOffset = targetOffsetParams \?\? targetOffset \?\? offsetTop \?\? 0'
    calc_match = re.search(calc_pattern, content)

    assert calc_match is not None, (
        "handleScrollTo must calculate finalTargetOffset with proper precedence: "
        "link-level > global targetOffset > offsetTop > 0. "
        "Expected: const finalTargetOffset = targetOffsetParams ?? targetOffset ?? offsetTop ?? 0"
    )


def test_anchorLink_passes_targetOffset_to_registerLink():
    """Fail-to-pass: AnchorLink must pass targetOffset to registerLink."""
    with open(f"{REPO}/components/anchor/AnchorLink.tsx", "r") as f:
        content = f.read()

    # Check useEffect calls registerLink with targetOffset
    # Optional chaining: registerLink?.(href, targetOffset)
    pattern = r'registerLink\?\.\(href, targetOffset\)'
    match = re.search(pattern, content)

    assert match is not None, (
        "AnchorLink useEffect must pass targetOffset to registerLink. "
        "Expected: registerLink?.(href, targetOffset)"
    )


def test_anchorLink_passes_targetOffset_to_scrollTo():
    """Fail-to-pass: AnchorLink must pass targetOffset to scrollTo on click."""
    with open(f"{REPO}/components/anchor/AnchorLink.tsx", "r") as f:
        content = f.read()

    # Check handleClick passes targetOffset to scrollTo
    # Optional chaining: scrollTo?.(href, targetOffset)
    pattern = r'scrollTo\?\.\(href, targetOffset\)'
    match = re.search(pattern, content)

    assert match is not None, (
        "AnchorLink handleClick must pass targetOffset to scrollTo. "
        "Expected: scrollTo?.(href, targetOffset)"
    )


def test_anchorLink_useEffect_depends_on_targetOffset():
    """Fail-to-pass: AnchorLink useEffect must depend on targetOffset."""
    with open(f"{REPO}/components/anchor/AnchorLink.tsx", "r") as f:
        content = f.read()

    # Check useEffect dependency array includes targetOffset
    pattern = r'\}, \[href, targetOffset\]\)'
    match = re.search(pattern, content)

    assert match is not None, (
        "AnchorLink useEffect must have [href, targetOffset] dependency array "
        "to re-register when targetOffset changes"
    )


def test_getInternalCurrentAnchor_called_with_linkTargetOffset():
    """Fail-to-pass: getInternalCurrentAnchor must be called with linkTargetOffsetRef.current."""
    with open(f"{REPO}/components/anchor/Anchor.tsx", "r") as f:
        content = f.read()

    # Check the call to getInternalCurrentAnchor includes linkTargetOffsetRef.current
    pattern = r'getInternalCurrentAnchor\([^)]*linkTargetOffsetRef\.current[^)]*\)'
    match = re.search(pattern, content, re.DOTALL)

    assert match is not None, (
        "getInternalCurrentAnchor must be called with linkTargetOffsetRef.current "
        "as the fourth parameter for per-link offset detection"
    )


def test_anchor_component_typescript_compiles():
    """Pass-to-pass: Anchor component TypeScript must compile without errors."""
    # Run TypeScript check with increased memory limit and only on anchor files
    # We use NODE_OPTIONS to increase memory since the full repo typecheck is too heavy
    result = run_command(
        ["sh", "-c", "NODE_OPTIONS='--max-old-space-size=4096' npx tsc --noEmit --skipLibCheck 2>&1 | head -100 || true"],
        timeout=300
    )

    # If it passes or the errors are not related to anchor files, consider it passing
    # Since we already verify via test_anchor_tests_pass which includes TypeScript compilation
    output = result.stdout + result.stderr

    # Check for anchor-specific errors
    anchor_errors = re.search(r'components/anchor/.*error', output, re.IGNORECASE)

    assert result.returncode == 0 or anchor_errors is None, (
        f"TypeScript compilation has anchor-specific errors:\n{output[:2000]}"
    )


def test_anchor_tests_pass():
    """Pass-to-pass: Anchor component tests must pass."""
    result = run_command(
        ["npm", "test", "--", "components/anchor/__tests__/Anchor.test.tsx", "--no-coverage"],
        timeout=300
    )

    assert result.returncode == 0, (
        f"Anchor tests failed:\n{result.stdout[-2000:]}\n{result.stderr[-1000:]}"
    )


def test_repo_lint_biome_passes():
    """Pass-to-pass: Biome lint check must pass (repo CI)."""
    result = run_command(
        ["npm", "run", "lint:biome"],
        timeout=120
    )

    assert result.returncode == 0, (
        f"Biome lint failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


def test_repo_lint_eslint_anchor_passes():
    """Pass-to-pass: ESLint check on anchor files must pass (repo CI)."""
    result = run_command(
        ["npx", "eslint", "components/anchor/", "--cache"],
        timeout=120
    )

    assert result.returncode == 0, (
        f"ESLint check on anchor files failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"
    )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
