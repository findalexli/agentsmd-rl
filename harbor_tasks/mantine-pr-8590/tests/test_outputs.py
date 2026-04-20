"""
Tests for mantinedev/mantine#8590:
Popover flip middleware ordering bug fix.

The bug: when shift middleware runs before flip, it pushes the Popover
into the viewport, preventing flip from triggering when a SubMenu overlaps
the parent at screen edges. The fix moves flip before shift so the
element first flips to the opposite side, then shift adjusts within viewport.
"""

import os
import re

REPO = "/workspace/mantine"
TARGET_FILE = "packages/@mantine/core/src/components/Popover/use-popover.ts"


def get_middleware_order_via_source() -> list[str]:
    """
    Parse the source file and determine the relative order of flip/shift
    middleware pushes in getPopoverMiddlewares.

    The flip push looks like:
      middlewares.push(
        typeof middlewaresOptions.flip === 'boolean' ? flip() : flip(middlewaresOptions.flip)
      );

    The shift push looks like:
      middlewares.push(
        shift(
          typeof middlewaresOptions.shift === 'boolean'
            ? { limiter: limitShift(), padding: 5 }
            : { limiter: limitShift(), padding: 5, ...middlewaresOptions.shift }
        )
      );

    We find both push call positions and compare them.
    """
    file_path = os.path.join(REPO, TARGET_FILE)
    with open(file_path, "r") as f:
        content = f.read()

    # Find the getPopoverMiddlewares function body
    func_match = re.search(
        r"function getPopoverMiddlewares\([^)]*\)[^{]*\{",
        content,
        re.MULTILINE | re.DOTALL,
    )
    if not func_match:
        raise RuntimeError("Could not find getPopoverMiddlewares function")

    # Search only within the function body
    search_start = func_match.end() - 1
    func_content = content[search_start:]

    # Find flip middleware push - distinctive because it uses a ternary with 'flip()'
    # and the string "middlewaresOptions.flip === 'boolean' ? flip() : flip"
    flip_pattern = r"middlewares\.push\s*\(\s*typeof middlewaresOptions\.flip === 'boolean' \? flip\(\) : flip"
    flip_match = re.search(flip_pattern, func_content)

    # Find shift middleware push - distinctive because it starts with 'shift(' inside the push
    shift_pattern = r"middlewares\.push\s*\(\s*shift\s*\("
    shift_match = re.search(shift_pattern, func_content)

    if not flip_match:
        raise RuntimeError("Could not find flip middleware push in getPopoverMiddlewares")
    if not shift_match:
        raise RuntimeError("Could not find shift middleware push in getPopoverMiddlewares")

    flip_pos = flip_match.start() + search_start
    shift_pos = shift_match.start() + search_start

    if flip_pos < shift_pos:
        return ["flip", "shift"]
    else:
        return ["shift", "flip"]


class TestFlipBeforeShift:
    """
    Verify flip middleware is registered before shift in getPopoverMiddlewares.

    The fix ensures that when both flip and shift are enabled (the default),
    flip appears earlier in the middleware array. This allows flip to
    reposition the element to the opposite side before shift adjusts.
    """

    def test_flip_before_shift_when_both_enabled(self):
        """
        When flip and shift are both enabled (the default), flip must
        appear earlier in the middleware array than shift.
        """
        order = get_middleware_order_via_source()
        flip_idx = order.index("flip")
        shift_idx = order.index("shift")
        assert flip_idx < shift_idx, (
            f"flip (index {flip_idx}) must come before shift (index {shift_idx}) "
            f"in middleware array, got order: {order}"
        )

    def test_middleware_order_is_consistent(self):
        """
        The flip middleware push must appear before the shift push in the
        getPopoverMiddlewares function source. This is the structural
        change introduced by the fix.
        """
        order = get_middleware_order_via_source()
        assert order == ["flip", "shift"], (
            f"Expected flip before shift, got order: {order}"
        )


class TestRepoTests:
    """pass_to_pass: existing repo tests should still pass after the fix."""

    def test_repo_jest_popovertest(self):
        """Repo's Popover Jest tests pass."""
        import subprocess
        r = subprocess.run(
            ["yarn", "jest", "--testPathPatterns", "Popover", "--no-coverage"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=120,
        )
        assert r.returncode == 0, f"Jest Popover tests failed:\n{r.stderr[-1000:]}\n{r.stdout[-500:]}"

    def test_repo_eslint_popover(self):
        """Repo's ESLint passes for the Popover directory."""
        import subprocess
        r = subprocess.run(
            ["npx", "eslint", "packages/@mantine/core/src/components/Popover", "--cache"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, f"ESLint failed:\n{r.stderr[-500:]}"

    def test_repo_prettier_popover(self):
        """Repo's Prettier check passes for the Popover directory."""
        import subprocess
        r = subprocess.run(
            ["yarn", "prettier", "--check", "packages/@mantine/core/src/components/Popover/**/*"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, f"Prettier check failed:\n{r.stdout[-500:]}"

    def test_repo_stylelint_popover_css(self):
        """Repo's Stylelint passes for Popover CSS files."""
        import subprocess
        r = subprocess.run(
            ["yarn", "stylelint", "packages/@mantine/core/src/components/Popover/**/*.css", "--cache"],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=60,
        )
        assert r.returncode == 0, f"Stylelint failed:\n{r.stderr[-500:]}"
