"""Behavioral tests for appwrite/appwrite#11689 ('Fix installer').

Strategy:
- The PHTML templates are renderable with PHP CLI; we run php to render them
  with $isUpgrade in {true,false} and assert on the output.
- The CSS file gets a new selector for the upgrade flow; we render the CSS
  through PHP's tokenizer (token_get_all-equivalent: just read it) and verify
  via a parsed-rule check, not a pure grep.
- The AGENTS.md rewrite is structurally validated for Track 1 (markdown_authoring
  side); the semantic comparison happens in Track 2 (Gemini judge).
- No tests touch the Swoole-coupled installer code (those changes need a
  running Swoole HTTP server; see the abandon-criteria in the scaffold prompt).
"""
import subprocess
from pathlib import Path

REPO = Path("/workspace/appwrite")
STEP_4 = REPO / "app/views/install/installer/templates/steps/step-4.phtml"
STEP_5 = REPO / "app/views/install/installer/templates/steps/step-5.phtml"
INSTALLER_CSS = REPO / "app/views/install/installer/css/styles.css"
AGENTS_MD = REPO / "AGENTS.md"


def _render(php_template: Path, vars_setup: str) -> str:
    """Render a PHP template by `require`ing it under a small wrapper."""
    assert php_template.exists(), f"Missing template: {php_template}"
    code = (
        f"<?php\n"
        f"{vars_setup}\n"
        f"require '{php_template}';\n"
    )
    r = subprocess.run(
        ["php", "-d", "display_errors=stderr", "-r", code.removeprefix("<?php\n")],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"PHP render failed (rc={r.returncode}):\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )
    return r.stdout


# ---------------------------------------------------------------------------
# fail_to_pass: behavioral tests on the gold patch
# ---------------------------------------------------------------------------

def test_step5_upgrade_says_appwrite_not_your_app():
    """step-5 in upgrade mode must show 'Updating Appwrite…', not 'your app'."""
    out = _render(STEP_5, "$isUpgrade = true;")
    assert "Updating Appwrite…" in out, (
        f"Expected 'Updating Appwrite…' in upgrade-mode render; got:\n{out[:600]}"
    )
    assert "Updating your app…" not in out, (
        f"Old phrase 'Updating your app…' still present:\n{out[:600]}"
    )


def test_step5_install_says_appwrite_not_your_app():
    """step-5 in fresh-install mode must show 'Installing Appwrite…'."""
    out = _render(STEP_5, "$isUpgrade = false;")
    assert "Installing Appwrite…" in out, (
        f"Expected 'Installing Appwrite…' in fresh-install render; got:\n{out[:600]}"
    )
    assert "Installing your app…" not in out, (
        f"Old phrase 'Installing your app…' still present:\n{out[:600]}"
    )


def test_step4_upgrade_hides_secret_api_key_row():
    """step-4 in upgrade mode must NOT render the 'Secret API key' review row."""
    out = _render(STEP_4, "$isUpgrade = true;")
    assert "Secret API key" not in out, (
        "In upgrade mode, the 'Secret API key' review row must be hidden; "
        f"but it appeared in the output:\n{out[:1200]}"
    )


def test_step4_install_shows_secret_api_key_row():
    """step-4 in fresh-install mode must still show the 'Secret API key' row."""
    out = _render(STEP_4, "$isUpgrade = false;")
    assert "Secret API key" in out, (
        "In fresh-install mode, the 'Secret API key' review row must be present; "
        f"missing from output:\n{out[:1200]}"
    )


def test_installer_css_has_upgrade_step_height_rule():
    """The installer CSS must scope step min-height for upgrade pages.

    Verified by parsing the CSS with PHP's tokenizer (treats the file as
    text, but specifically looks for a rule whose selector matches the
    upgrade-page form and whose body sets min-height to 0).
    """
    code = r"""
$css = file_get_contents('""" + str(INSTALLER_CSS) + r"""');
// Strip /* ... */ comments
$css = preg_replace('/\/\*.*?\*\//s', '', $css);
// Find rule blocks: selector { body }
preg_match_all('/([^{}]+)\{([^{}]*)\}/s', $css, $m, PREG_SET_ORDER);
$found = false;
foreach ($m as $rule) {
    $sel = trim($rule[1]);
    $body = $rule[2];
    if (
        preg_match('/installer-page\s*\[\s*data-upgrade\s*=\s*[\x27"]true[\x27"]\s*\]/', $sel)
        && preg_match('/installer-step/', $sel)
        && preg_match('/min-height\s*:\s*0/', $body)
    ) {
        $found = true;
        break;
    }
}
echo $found ? 'OK' : 'MISSING';
"""
    r = subprocess.run(
        ["php", "-r", code],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"PHP CSS-parse failed: {r.stderr}"
    assert r.stdout.strip() == "OK", (
        "Installer CSS is missing a rule that scopes min-height:0 to "
        ".installer-page[data-upgrade='true'] .installer-step"
    )


# ---------------------------------------------------------------------------
# Track-1 structural sanity for the AGENTS.md rewrite (markdown_authoring)
# ---------------------------------------------------------------------------

def test_agents_md_rewritten_with_new_signal_lines():
    """AGENTS.md must reflect the rewrite: new section headings + signal phrases."""
    assert AGENTS_MD.exists(), "AGENTS.md missing"
    content = AGENTS_MD.read_text()

    signal_phrases = [
        # New, more specific opening tagline
        "Self-hosted Backend-as-a-Service platform",
        # New top-level heading "## Commands" (was "## Development Commands")
        "\n## Commands\n",
        # New Stack section listing PHPUnit/Pint/PHPStan
        "PHPUnit 12, Pint (PSR-12), PHPStan level 3",
        # Action-pattern guidance now lives in the file
        "## Action pattern (HTTP endpoints)",
    ]
    missing = [p for p in signal_phrases if p not in content]
    assert not missing, f"Expected new AGENTS.md content missing: {missing}"

    # Old phrasing that should NOT remain after the rewrite.
    legacy_phrases = [
        "## Project Overview",
        "## Development Commands",
        "## Code Style Guidelines",
    ]
    leftover = [p for p in legacy_phrases if p in content]
    assert not leftover, f"Old AGENTS.md sections still present: {leftover}"


# ---------------------------------------------------------------------------
# pass_to_pass: PHP syntax-checks
# ---------------------------------------------------------------------------

def test_install_php_files_are_syntactically_valid():
    """Both modified PHP files must remain syntactically valid PHP."""
    targets = [
        REPO / "src/Appwrite/Platform/Tasks/Install.php",
        REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php",
        REPO / "src/Appwrite/Platform/Installer/Server.php",
    ]
    for t in targets:
        assert t.exists(), f"Missing source file: {t}"
        r = subprocess.run(
            ["php", "-l", str(t)],
            capture_output=True, text=True, timeout=30,
        )
        assert r.returncode == 0, (
            f"php -l failed for {t}:\n{r.stdout}\n{r.stderr}"
        )


def test_phtml_templates_are_syntactically_valid():
    """The two PHTML templates must remain valid PHP."""
    for t in (STEP_4, STEP_5):
        # `php -l` only handles whole-file PHP; use a tolerant render check.
        out = _render(t, "$isUpgrade = false;")
        # A successful render that emits SOMETHING is enough; failures throw.
        assert out.strip(), f"Template {t} rendered empty output"
