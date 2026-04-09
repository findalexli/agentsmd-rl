"""
Task: playwright-ansi2html-default-colors
Repo: microsoft/playwright @ 09a1261b764fc5c106fa8ca1e3c0bee4e8ddb3d1
PR:   40108

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
import json
import os
import tempfile

REPO = "/workspace/playwright"
ANSI2HTML = f"{REPO}/packages/web/src/ansi2html.ts"


def _ansi2html(text: str, fg: str, bg: str) -> str:
    """Run ansi2html via tsx and return the HTML output."""
    script = (
        f'import {{ ansi2html }} from "{ANSI2HTML}";\n'
        f'console.log(ansi2html({json.dumps(text)}, '
        f'{{ fg: {json.dumps(fg)}, bg: {json.dumps(bg)} }}));\n'
    )
    fd, tmp = tempfile.mkstemp(suffix=".mts")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        r = subprocess.run(
            ["npx", "tsx", tmp],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"tsx execution failed:\n{r.stderr}"
        return r.stdout.strip()
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------


def test_plain_text_no_default_bg():
    """Plain text with defaultColors should NOT have background-color applied."""
    html = _ansi2html("hello world", fg="rgb(200, 50, 50)", bg="rgb(240, 240, 240)")
    assert "background-color" not in html, (
        f"Expected no background-color for plain text, got: {html}"
    )


def test_ansi_fg_no_default_bg():
    """ANSI foreground color should NOT trigger background-color from defaultColors.bg."""
    text = "\x1b[31mred text\x1b[0m"
    html = _ansi2html(text, fg="rgb(200, 50, 50)", bg="rgb(240, 240, 240)")
    assert "background-color" not in html, (
        f"Expected no background-color for ANSI-colored text, got: {html}"
    )


def test_ansi_bold_no_default_bg():
    """ANSI bold text with defaultColors should NOT have background-color."""
    text = "\x1b[1mbold text\x1b[0m"
    html = _ansi2html(text, fg="rgb(200, 50, 50)", bg="rgb(240, 240, 240)")
    assert "background-color" not in html, (
        f"Expected no background-color for bold ANSI text, got: {html}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static / regression)
# ---------------------------------------------------------------------------


def test_default_fg_applied():
    """Default foreground color should be applied to plain text."""
    html = _ansi2html("hello", fg="rgb(200, 50, 50)", bg="rgb(240, 240, 240)")
    assert "rgb(200, 50, 50)" in html, (
        f"Expected default fg color in output, got: {html}"
    )


def test_reverse_mode_has_bg():
    """Reverse mode should apply background-color from the fg color."""
    text = "\x1b[7mreversed\x1b[0m"
    html = _ansi2html(text, fg="rgb(200, 50, 50)", bg="rgb(240, 240, 240)")
    assert "background-color" in html, (
        f"Expected background-color in reverse mode, got: {html}"
    )


def test_ansi_fg_overrides_default():
    """ANSI foreground color code should override the default fg color."""
    text = "\x1b[32mgreen\x1b[0m"
    html = _ansi2html(text, fg="rgb(200, 50, 50)", bg="rgb(240, 240, 240)")
    assert "color" in html, f"Expected color styling in output, got: {html}"


def test_typescript_imports():
    """The ansi2html.ts module imports and executes without errors."""
    script = f'import {{ ansi2html }} from "{ANSI2HTML}"; console.log("ok");'
    fd, tmp = tempfile.mkstemp(suffix=".mts")
    try:
        with os.fdopen(fd, "w") as f:
            f.write(script)
        r = subprocess.run(
            ["npx", "tsx", tmp],
            capture_output=True, text=True, timeout=30, cwd=REPO,
        )
        assert r.returncode == 0, f"Import failed:\n{r.stderr}"
        assert "ok" in r.stdout
    finally:
        os.unlink(tmp)
