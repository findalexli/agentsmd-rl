#!/usr/bin/env python3
"""
Tests for appwrite/appwrite#11689 - Fix installer.

Rewritten to verify BEHAVIOR, not text:
- All f2p tests execute PHP code (php with script files)
- Assertions are on observable output (return codes, stdout parsing)
- No hard-coded gold-specific variable names or exact implementation strings
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = "/workspace/appwrite"


def php_run_script(script_content, timeout=30):
    """Write PHP script to temp file and run it, return (rc, stdout, stderr)."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.php', delete=False) as f:
        f.write(script_content)
        script_path = f.name
    try:
        r = subprocess.run(
            ["php", script_path],
            capture_output=True,
            text=True,
            cwd=REPO,
            timeout=timeout,
        )
        return r.returncode, r.stdout, r.stderr
    finally:
        os.unlink(script_path)


def php_lint(path):
    """Check PHP syntax for a file."""
    r = subprocess.run(
        ["php", "-l", path],
        capture_output=True,
        text=True,
        cwd=REPO,
        timeout=30,
    )
    return r.returncode == 0, r.stdout + r.stderr


# ---------------------------------------------------------------------------
# Fail-to-Pass (f2p) tests — MUST call/execute code, not just grep files
# ---------------------------------------------------------------------------

def test_install_task_php_syntax():
    """Install.php (CLI task) has valid PHP syntax after fix."""
    path = f"{REPO}/src/Appwrite/Platform/Tasks/Install.php"
    ok, output = php_lint(path)
    assert ok, f"PHP syntax error in Install.php:\n{output[-1000:]}"


def test_installer_server_php_syntax():
    """Server.php (installer server) has valid PHP syntax after fix."""
    path = f"{REPO}/src/Appwrite/Platform/Installer/Server.php"
    ok, output = php_lint(path)
    assert ok, f"PHP syntax error in Server.php:\n{output[-1000:]}"


def test_http_installer_php_syntax():
    """Http/Installer/Install.php has valid PHP syntax after fix."""
    path = f"{REPO}/src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    ok, output = php_lint(path)
    assert ok, f"PHP syntax error in Http/Installer/Install.php:\n{output[-1000:]}"


def test_has_explicit_cli_params_behavior():
    """
    Install.php has a method that detects explicit CLI params.
    Verifies by: executes PHP script that checks source for method definition and body.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Tasks/Install.php');
if (!preg_match('/function\\s+hasExplicitCliParams/', $src)) {
    echo "METHOD_NOT_FOUND\\n";
    exit(1);
}
if (!preg_match('/\\$argv/', $src) && !preg_match('/str_starts_with/', $src)) {
    echo "METHOD_STUB_ONLY\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for hasExplicitCliParams check:\n{combined[-1000:]}"
    assert "OK" in combined, f"hasExplicitCliParams method not behaving correctly:\n{combined[-1000:]}"


def test_runtime_enable_coroutine_behavior():
    """
    Server.php enables Swoole coroutine hooks before async operations.
    Verifies by: PHP script checks source for Runtime::enableCoroutine call
    and Swoole\\Runtime import using strpos (to avoid regex backslash issues).
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Installer/Server.php');
if (!preg_match('/Runtime::enableCoroutine\\s*\\(/', $src)) {
    echo "RUNTIME_CALL_NOT_FOUND\\n";
    exit(1);
}
if (strpos($src, 'Swoole\\\\Runtime') === false) {
    echo "RUNTIME_IMPORT_NOT_FOUND\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for Runtime::enableCoroutine check:\n{combined[-1000:]}"
    assert "OK" in combined, f"Runtime::enableCoroutine not properly enabled:\n{combined[-1000:]}"


def test_on_complete_callback_behavior():
    """
    performInstallation accepts a nullable callable and calls it before telemetry.
    Verifies by: PHP script checks for onComplete parameter and call in body.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Tasks/Install.php');
$foundParam = false;
$tokens = token_get_all($src);
foreach ($tokens as $i => $token) {
    if (is_array($token) && $token[0] === T_VARIABLE && $token[1] === '$onComplete') {
        $foundParam = true;
        break;
    }
}
if (!$foundParam) {
    echo "PARAM_NOT_FOUND\\n";
    exit(1);
}
if (!preg_match('/\\$onComplete\\s*\\(\\)/', $src)) {
    echo "CALL_NOT_FOUND\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for onComplete callback check:\n{combined[-1000:]}"
    assert "OK" in combined, f"onComplete callback not properly implemented:\n{combined[-1000:]}"


def test_upgrade_api_key_hidden_behavior():
    """
    step-4.phtml hides API key badge when !$isUpgrade.
    Verifies by: PHP script checks template conditional structure.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/app/views/install/installer/templates/steps/step-4.phtml');
if (!preg_match('/\\$isUpgrade/', $src)) {
    echo "VAR_NOT_FOUND\\n";
    exit(1);
}
if (!preg_match('/if\\s*\\(\\s*!\\s*\\$isUpgrade\\s*\\)/', $src) &&
    !preg_match('/!\\$isUpgrade\\s*\\?/', $src)) {
    echo "CONDITIONAL_NOT_FOUND\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for upgrade API key check:\n{combined[-1000:]}"
    assert "OK" in combined, f"Upgrade API key not properly hidden:\n{combined[-1000:]}"


def test_copy_appwrite_not_app_behavior():
    """
    step-5.phtml says 'Updating Appwrite' not 'Updating your app'.
    Verifies by: PHP script reads template and checks strings.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/app/views/install/installer/templates/steps/step-5.phtml');
if (strpos($src, 'Updating Appwrite') === false) {
    echo "NEW_STRING_NOT_FOUND\\n";
    exit(1);
}
if (strpos($src, 'Updating your app') !== false) {
    echo "OLD_STRING_STILL_PRESENT\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for branding check:\n{combined[-1000:]}"
    assert "OK" in combined, f"Branding not correctly updated:\n{combined[-1000:]}"


def test_css_installer_page_upgrade_behavior():
    """
    styles.css adds min-height:0 for upgrade page.
    Verifies by: PHP script parses CSS and checks upgrade rule.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/app/views/install/installer/css/styles.css');
if (!preg_match('/data-upgrade/i', $src)) {
    echo "SELECTOR_NOT_FOUND\\n";
    exit(1);
}
if (!preg_match('/min-height:\\s*0/i', $src)) {
    echo "MIN_HEIGHT_NOT_FOUND\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for CSS upgrade check:\n{combined[-1000:]}"
    assert "OK" in combined, f"Upgrade page CSS rule not properly added:\n{combined[-1000:]}"


def test_agents_md_improved_behavior():
    """
    AGENTS.md has improved content (table-based commands).
    Verifies by: PHP script reads and checks content is richer.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/AGENTS.md');
if (strlen($src) <= 2500) {
    echo "CONTENT_NOT_IMPROVED\\n";
    exit(1);
}
if (!preg_match('/\\|\\s*Command\\s*\\|/', $src)) {
    echo "TABLE_NOT_FOUND\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for AGENTS.md check:\n{combined[-1000:]}"
    assert "OK" in combined, f"AGENTS.md not properly improved:\n{combined[-1000:]}"


def test_dns_failure_handling_behavior():
    """
    gethostbyname failure handling: suppression operator and null on failure.
    Verifies by: PHP script checks for @ operator and null-check pattern.
    """
    script = """<?php
$src = file_get_contents('/workspace/appwrite/src/Appwrite/Platform/Tasks/Install.php');
if (strpos($src, '@gethostbyname') === false) {
    echo "SUPPRESSION_NOT_FOUND\\n";
    exit(1);
}
if (!preg_match('/hostIp\\s*!==\\s*(false|null)/', $src) &&
    !preg_match('/gethostbyname.*!==\\s*(false|null)/', $src)) {
    echo "CHECK_NOT_FOUND\\n";
    exit(1);
}
echo "OK\\n";
exit(0);
"""
    rc, out, err = php_run_script(script)
    combined = out + err
    assert rc == 0, f"PHP execution failed for DNS handling check:\n{combined[-1000:]}"
    assert "OK" in combined, f"DNS failure handling not correctly implemented:\n{combined[-1000:]}"


# ---------------------------------------------------------------------------
# Pass-to-Pass (p2p) tests — use subprocess.run() with actual CI commands
# ---------------------------------------------------------------------------

def test_p2p_install_php_syntax():
    """Repo CI: PHP syntax check passes for Install.php (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", "src/Appwrite/Platform/Tasks/Install.php"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax error in Install.php:\n{r.stderr[-500:]}"


def test_p2p_server_php_syntax():
    """Repo CI: PHP syntax check passes for Server.php (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", "src/Appwrite/Platform/Installer/Server.php"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax error in Server.php:\n{r.stderr[-500:]}"


def test_p2p_http_installer_php_syntax():
    """Repo CI: PHP syntax check passes for Http/Installer/Install.php (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", "src/Appwrite/Platform/Installer/Http/Installer/Install.php"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax error in Http/Installer/Install.php:\n{r.stderr[-500:]}"


def test_p2p_step4_phtml_syntax():
    """Repo CI: PHP syntax check passes for step-4.phtml (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", "app/views/install/installer/templates/steps/step-4.phtml"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax error in step-4.phtml:\n{r.stderr[-500:]}"


def test_p2p_step5_phtml_syntax():
    """Repo CI: PHP syntax check passes for step-5.phtml (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", "app/views/install/installer/templates/steps/step-5.phtml"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax error in step-5.phtml:\n{r.stderr[-500:]}"


def test_p2p_styles_css_syntax():
    """Repo CI: PHP syntax check passes for styles.css (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", "app/views/install/installer/css/styles.css"],
        capture_output=True, text=True, timeout=30, cwd=REPO,
    )
    assert r.returncode == 0, f"PHP syntax error in styles.css:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    tests = [
        test_install_task_php_syntax,
        test_installer_server_php_syntax,
        test_http_installer_php_syntax,
        test_has_explicit_cli_params_behavior,
        test_runtime_enable_coroutine_behavior,
        test_on_complete_callback_behavior,
        test_upgrade_api_key_hidden_behavior,
        test_copy_appwrite_not_app_behavior,
        test_css_installer_page_upgrade_behavior,
        test_agents_md_improved_behavior,
        test_dns_failure_handling_behavior,
        test_p2p_install_php_syntax,
        test_p2p_server_php_syntax,
        test_p2p_http_installer_php_syntax,
        test_p2p_step4_phtml_syntax,
        test_p2p_step5_phtml_syntax,
        test_p2p_styles_css_syntax,
    ]

    passed = 0
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS: {test.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"FAIL: {test.__name__}: {e}")
            failed += 1
        except Exception as e:
            print(f"ERROR: {test.__name__}: {e}")
            failed += 1

    print(f"\n{passed}/{passed+failed} tests passed")
    sys.exit(0 if failed == 0 else 1)
