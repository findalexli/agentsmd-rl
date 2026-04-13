"""
Task: gradio-localfont-css-weight-numeric
Repo: gradio-app/gradio @ 0595d1b15ba6b7c47f68ddf7f79152b3d1d3c467
PR:   12966

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import ast
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/gradio"

# Ensure repo is importable
sys.path.insert(0, REPO)


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """Modified files must parse without errors."""
    import py_compile

    py_compile.compile(f"{REPO}/gradio/themes/utils/fonts.py", doraise=True)
    py_compile.compile(f"{REPO}/scripts/generate_theme.py", doraise=True)


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_numeric_font_weight():
    """LocalFont.stylesheet() produces numeric font-weight values (400, 700)."""
    from gradio.themes.utils.fonts import LocalFont

    # Test with multiple font names to prevent hardcoding
    for font_name in ["IBM Plex Mono", "Roboto", "Open Sans"]:
        font = LocalFont(font_name)
        css = font.stylesheet()["css"]

        weights = re.findall(r"font-weight:\s*(\S+);", css)
        assert weights, f"No font-weight values found in CSS for {font_name}"
        for w in weights:
            val = int(w)  # ValueError if not numeric
            assert 1 <= val <= 1000, f"font-weight {val} out of CSS range 1-1000"
        int_weights = [int(w) for w in weights]
        assert 400 in int_weights, f"Expected 400 in weights for {font_name}, got {int_weights}"
        assert 700 in int_weights, f"Expected 700 in weights for {font_name}, got {int_weights}"

    # Test with custom weight list
    font = LocalFont("TestFont", weights=(100, 300, 400, 700, 900))
    css = font.stylesheet()["css"]
    int_weights = [int(w) for w in re.findall(r"font-weight:\s*(\S+);", css)]
    for expected in [100, 300, 400, 700, 900]:
        assert expected in int_weights, f"Expected {expected} in weights, got {int_weights}"


# [pr_diff] fail_to_pass
def test_weight_path_separation():
    """CSS font-weight is numeric while file paths still use text names (Regular, Bold)."""
    from gradio.themes.utils.fonts import LocalFont

    # Test with multiple font names
    for font_name in ["IBM Plex Mono", "Noto Sans", "Fira Code"]:
        font = LocalFont(font_name)
        css = font.stylesheet()["css"]
        sanitized = font_name.replace(" ", "")

        blocks = css.split("@font-face")
        found_regular = False
        found_bold = False
        for block in blocks:
            if not block.strip():
                continue
            weight_m = re.search(r"font-weight:\s*(\S+);", block)
            url_m = re.search(r"url\([\'\"]?([^)\'\"]*)[\'\"]?\)", block)
            if not weight_m or not url_m:
                continue
            weight = weight_m.group(1)
            url = url_m.group(1)
            # Verify font name appears in URL correctly
            assert sanitized in url, f"Expected '{sanitized}' in URL: {url}"
            if weight == "400" and "Regular" in url:
                found_regular = True
            if weight == "700" and "Bold" in url:
                found_bold = True

        assert found_regular, f"font-weight 400 should pair with 'Regular' in URL path ({font_name})"
        assert found_bold, f"font-weight 700 should pair with 'Bold' in URL path ({font_name})"


# [pr_diff] fail_to_pass
def test_website_flag_rewrites_paths():
    """generate_theme.py --website rewrites url('static/...) to url('/...)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".css", delete=False) as f:
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, f"{REPO}/scripts/generate_theme.py", "--website", "--outfile", tmp],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        assert result.returncode == 0, f"generate_theme.py --website failed: {result.stderr}"
        css = Path(tmp).read_text()
        assert "url('static/" not in css, "--website flag did not rewrite static/ paths"
    finally:
        os.unlink(tmp)


# ---------------------------------------------------------------------------
# Pass-to-pass (pr_diff / repo_tests / static) — regression + anti-stub
# ---------------------------------------------------------------------------

# [pr_diff] pass_to_pass
def test_default_preserves_static_paths():
    """generate_theme.py without --website preserves url('static/...) paths."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".css", delete=False) as f:
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, f"{REPO}/scripts/generate_theme.py", "--outfile", tmp],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        assert result.returncode == 0, f"generate_theme.py failed: {result.stderr}"
        css = Path(tmp).read_text()
        assert "url('static/" in css, "Without --website, static/ paths should be preserved"
    finally:
        os.unlink(tmp)


# [repo_tests] pass_to_pass
def test_repo_ruff_format():
    """Repo's Python files are formatted according to ruff (pass_to_pass)."""
    import shutil
    ruff = shutil.which("ruff")
    if ruff is None:
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
        )
        if ruff_result.returncode != 0:
            import pytest
            pytest.skip("ruff not available in this environment")
        ruff_cmd = [sys.executable, "-m", "ruff"]
    else:
        ruff_cmd = [ruff]

    result = subprocess.run(
        ruff_cmd + ["format", "--check", f"{REPO}/gradio/themes/utils/fonts.py", f"{REPO}/scripts/generate_theme.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"ruff format --check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_google_font_stylesheet():
    """GoogleFont still generates valid stylesheets with googleapis URL."""
    from gradio.themes.utils.fonts import GoogleFont

    for name in ["Source Sans Pro", "Roboto", "Inter"]:
        font = GoogleFont(name)
        result = font.stylesheet()
        assert result["url"] is not None, f"GoogleFont({name}) should have a URL"
        assert "fonts.googleapis.com" in result["url"], f"Unexpected URL for {name}: {result['url']}"
        assert name.replace(" ", "+") in result["url"] or name in result["url"], \
            f"Font name not in URL for {name}: {result['url']}"


# [repo_tests] pass_to_pass
def test_font_base_class():
    """Font base class returns expected defaults."""
    from gradio.themes.utils.fonts import Font

    font = Font("sans-serif")
    assert str(font) == "sans-serif", f"Expected 'sans-serif', got '{str(font)}'"
    result = font.stylesheet()
    assert result == {"url": None, "css": None}, f"Unexpected result: {result}"


# [static] pass_to_pass
def test_not_stub():
    """LocalFont.stylesheet method has real logic, not just pass/return."""
    src = Path(f"{REPO}/gradio/themes/utils/fonts.py").read_text()
    tree = ast.parse(src)
    found = False
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == "stylesheet":
            body = [s for s in node.body if not isinstance(s, (ast.Pass, ast.Expr))]
            if len(body) >= 3:
                found = True
                break
    assert found, "No non-trivial stylesheet() method found"


# [agent_config] pass_to_pass
def test_ruff_format_python():
    """Modified Python files are formatted according to ruff (AGENTS.md line 43)."""
    import shutil
    ruff = shutil.which("ruff")
    if ruff is None:
        # ruff not installed — try running via the repo's Python environment
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
        )
        if ruff_result.returncode != 0:
            import pytest
            pytest.skip("ruff not available in this environment")
        ruff_cmd = [sys.executable, "-m", "ruff"]
    else:
        ruff_cmd = [ruff]

    files = [
        f"{REPO}/gradio/themes/utils/fonts.py",
        f"{REPO}/scripts/generate_theme.py",
    ]
    result = subprocess.run(
        ruff_cmd + ["format", "--check"] + files,
        capture_output=True, text=True,
    )
    assert result.returncode == 0, (
        f"ruff format --check failed on modified Python files:\n{result.stdout}\n{result.stderr}"
    )


# [repo_tests] pass_to_pass
def test_gradio_themes_ruff_check():
    """Repo's ruff linter passes on gradio/themes/ directory (pass_to_pass)."""
    import shutil
    ruff = shutil.which("ruff")
    if ruff is None:
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
        )
        if ruff_result.returncode != 0:
            import pytest
            pytest.skip("ruff not available in this environment")
        ruff_cmd = [sys.executable, "-m", "ruff"]
    else:
        ruff_cmd = [ruff]

    result = subprocess.run(
        ruff_cmd + ["check", f"{REPO}/gradio/themes/utils/fonts.py", f"{REPO}/scripts/generate_theme.py"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass

# [repo_tests] pass_to_pass
def test_gradio_theme_tests():
    """Repo's theme-related tests pass (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_theme_sharing.py", "-v", "-k", "not test_theme_builder_launches", "-x"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Theme tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_gradio_fonts_module_imports():
    """Fonts module can be imported without errors (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c", "from gradio.themes.utils.fonts import LocalFont, GoogleFont, Font; print('OK')"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"Fonts module import failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_google_font_stylesheet_url_generation():
    """GoogleFont.stylesheet() generates valid googleapis URLs (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from gradio.themes.utils.fonts import GoogleFont; " +
         "f = GoogleFont('Roboto'); " +
         "r = f.stylesheet(); " +
         "assert r['url'] and 'fonts.googleapis.com' in r['url']; " +
         "assert 'display=swap' in r['url']; " +
         "print('OK')"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"GoogleFont stylesheet test failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_generate_theme_script_runs():
    """generate_theme.py script runs successfully without --website flag (pass_to_pass)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".css", delete=False) as f:
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, f"{REPO}/scripts/generate_theme.py", "--outfile", tmp],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        assert result.returncode == 0, f"generate_theme.py failed: {result.stderr}"
        with open(tmp) as f:
            content = f.read()
        assert len(content) > 0, "Generated CSS file should not be empty"
        assert "url('static/" in content, "Default CSS should contain static/ paths"
    finally:
        os.unlink(tmp)


# [repo_tests] pass_to_pass
def test_gradio_theme_unit_tests():
    """Repo's theme unit tests (BuiltInThemes, SemverMatch, GetThemeAssets) pass (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest",
         "test/test_theme_sharing.py::TestBuiltInThemes",
         "test/test_theme_sharing.py::TestSemverMatch",
         "test/test_theme_sharing.py::TestGetThemeAssets",
         "-v", "--tb=short"],
        capture_output=True, text=True, timeout=120, cwd=REPO,
    )
    assert result.returncode == 0, f"Theme unit tests failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


# [repo_tests] pass_to_pass
def test_gradio_imports_clean():
    """Main gradio module imports without errors (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c", "import gradio; print(gradio.__version__)"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert result.returncode == 0, f"Gradio import failed:\n{result.stderr}"
    assert result.stdout.strip(), "Gradio version should be available"


# [repo_tests] pass_to_pass
def test_localfont_css_structure():
    """LocalFont generates expected CSS structure with @font-face rules (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from gradio.themes.utils.fonts import LocalFont; " +
         "f = LocalFont('IBM Plex Mono'); " +
         "r = f.stylesheet(); " +
         "assert '@font-face' in r['css']; " +
         "assert 'font-family' in r['css']; " +
         "assert 'url(' in r['css']; " +
         "assert 'woff2' in r['css']; " +
         "print('OK')"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"LocalFont CSS structure test failed:\n{result.stderr}"


# [repo_tests] pass_to_pass
def test_gradio_fonts_full_api():
    """Fonts module exports all expected classes and functions (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c",
         "from gradio.themes.utils.fonts import Font, GoogleFont, LocalFont, FontEncoder, as_font; " +
         "from gradio.themes.utils.fonts import json, textwrap; " +  # verify module internals available
         "print('OK')"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"Fonts full API test failed:\n{result.stderr}"


# [repo_tests] pass_to_pass - CI tests from test-python.yml and test-hygiene.yml
def test_ci_ruff_check_gradio_themes():
    """CI: ruff check on gradio/themes/ directory passes (pass_to_pass)."""
    ruff = shutil.which("ruff")
    if ruff is None:
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
        )
        if ruff_result.returncode != 0:
            import pytest
            pytest.skip("ruff not available in this environment")
        ruff_cmd = [sys.executable, "-m", "ruff"]
    else:
        ruff_cmd = [ruff]

    result = subprocess.run(
        ruff_cmd + ["check", f"{REPO}/gradio/themes/"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"ruff check on gradio/themes/ failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass - CI tests
def test_ci_ruff_format_gradio_themes():
    """CI: ruff format check on gradio/themes/ passes (pass_to_pass)."""
    ruff = shutil.which("ruff")
    if ruff is None:
        ruff_result = subprocess.run(
            [sys.executable, "-m", "ruff", "--version"],
            capture_output=True,
        )
        if ruff_result.returncode != 0:
            import pytest
            pytest.skip("ruff not available in this environment")
        ruff_cmd = [sys.executable, "-m", "ruff"]
    else:
        ruff_cmd = [ruff]

    result = subprocess.run(
        ruff_cmd + ["format", "--check", f"{REPO}/gradio/themes/"],
        capture_output=True, text=True, cwd=REPO,
    )
    assert result.returncode == 0, f"ruff format check on gradio/themes/ failed:\n{result.stdout}\n{result.stderr}"


# [repo_tests] pass_to_pass - CI tests
def test_ci_pytest_themes_utils():
    """CI: pytest on theme utils related tests passes (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "test/test_theme_sharing.py::TestBuiltInThemes", "-v", "--tb=short"],
        capture_output=True, text=True, cwd=REPO, timeout=120,
    )
    assert result.returncode == 0, f"Theme utils pytest failed:\n{result.stdout[-1000:]}\n{result.stderr[-500:]}"


# [repo_tests] pass_to_pass - CI tests
def test_ci_gradio_module_imports_clean():
    """CI: gradio module imports without errors and version is accessible (pass_to_pass)."""
    result = subprocess.run(
        [sys.executable, "-c", "import gradio; print(gradio.__version__)"],
        capture_output=True, text=True, cwd=REPO, timeout=30,
    )
    assert result.returncode == 0, f"Gradio import failed:\n{result.stderr}"
    assert result.stdout.strip(), "Gradio version should be available"


# [repo_tests] pass_to_pass - CI tests
def test_ci_generate_theme_script_runs():
    """CI: generate_theme.py runs and produces valid CSS output (pass_to_pass)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".css", delete=False) as f:
        tmp = f.name
    try:
        result = subprocess.run(
            [sys.executable, f"{REPO}/scripts/generate_theme.py", "--outfile", tmp],
            capture_output=True, text=True, cwd=REPO, timeout=30,
        )
        assert result.returncode == 0, f"generate_theme.py failed:\n{result.stderr}"
        content = Path(tmp).read_text()
        assert len(content) > 0, "Generated CSS file should not be empty"
        assert ":root {" in content, "Generated CSS should contain :root selector"
    finally:
        os.unlink(tmp)
