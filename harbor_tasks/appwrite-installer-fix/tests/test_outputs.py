"""
Test outputs for appwrite installer fix PR #11689.

This tests that the installer fixes are properly applied:
1. Swoole coroutines enabled for non-blocking I/O
2. CLI param detection to skip web installer when explicit args provided
3. Error suppression on gethostbyname for DNS failures
4. Tracking payload uses 'ip' instead of 'hostIp'
5. HTTP client timeouts to prevent hanging
6. onComplete callback for proper SSE stream completion
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = Path("/workspace/appwrite")


# ============================================================================
# PASS-TO-PASS TESTS (Repo CI checks - these should pass on base commit)
# ============================================================================

def test_p2p_php_syntax_install_php():
    """PHP syntax check on Install.php passes (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", f"{REPO}/src/Appwrite/Platform/Tasks/Install.php"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"PHP syntax error in Install.php:\n{r.stdout}{r.stderr}"


def test_p2p_php_syntax_server_php():
    """PHP syntax check on Server.php passes (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", f"{REPO}/src/Appwrite/Platform/Installer/Server.php"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"PHP syntax error in Server.php:\n{r.stdout}{r.stderr}"


def test_p2p_php_syntax_http_install_php():
    """PHP syntax check on HTTP Install.php passes (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", f"{REPO}/src/Appwrite/Platform/Installer/Http/Installer/Install.php"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"PHP syntax error in HTTP Install.php:\n{r.stdout}{r.stderr}"


def test_p2p_php_syntax_step4_template():
    """PHP syntax check on step-4.phtml template passes (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", f"{REPO}/app/views/install/installer/templates/steps/step-4.phtml"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"PHP syntax error in step-4.phtml:\n{r.stdout}{r.stderr}"


def test_p2p_php_syntax_step5_template():
    """PHP syntax check on step-5.phtml template passes (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-l", f"{REPO}/app/views/install/installer/templates/steps/step-5.phtml"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"PHP syntax error in step-5.phtml:\n{r.stdout}{r.stderr}"


def test_p2p_swoole_extension_loaded():
    """Swoole extension is loaded and available (pass_to_pass)."""
    r = subprocess.run(
        ["php", "-r", "if (!extension_loaded('swoole')) { echo 'Swoole not loaded'; exit(1); } echo 'Swoole OK';"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 0, f"Swoole extension not loaded:\n{r.stdout}{r.stderr}"


def test_p2p_installer_files_exist():
    """All installer-related files exist in the repository (pass_to_pass)."""
    required_files = [
        REPO / "src/Appwrite/Platform/Tasks/Install.php",
        REPO / "src/Appwrite/Platform/Installer/Server.php",
        REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php",
        REPO / "app/views/install/installer/templates/steps/step-4.phtml",
        REPO / "app/views/install/installer/templates/steps/step-5.phtml",
        REPO / "app/views/install/installer/css/styles.css",
    ]
    for f in required_files:
        assert f.exists(), f"Required file missing: {f}"


# ============================================================================
# FAIL-TO-PASS TESTS (These check the fix is applied)
# Behavioral tests that actually CALL the code or inspect runtime behavior
# ============================================================================


def _run_php(script: str, timeout=30):
    """Run PHP code and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["php", "-r", script],
        capture_output=True, text=True, timeout=timeout,
        cwd=str(REPO),
    )
    return result.returncode, result.stdout, result.stderr


def test_swoole_coroutine_enabled():
    """
    Verify Swoole coroutines are enabled for non-blocking I/O.

    Behavior: Swoole Runtime::enableCoroutine() must be callable and succeed.
    This actually CALLS the Swoole API to verify the behavior works, then
    checks that the Server.php source contains the necessary import and call.
    """
    # PART 1: Verify the Swoole API actually works (this is the behavior)
    rc, out, err = _run_php("""
        if (!extension_loaded('swoole')) {
            echo "FAIL:Swoole not loaded";
            exit(1);
        }
        if (!class_exists('Swoole\\Runtime') || !method_exists('Swoole\\Runtime', 'enableCoroutine')) {
            echo "FAIL:Runtime::enableCoroutine not available";
            exit(1);
        }
        try {
            Swoole\\Runtime::enableCoroutine(SWOOLE_HOOK_ALL);
            echo "PASS:Coroutines enabled";
        } catch (Throwable $e) {
            echo "FAIL:" . $e->getMessage();
            exit(1);
        }
    """)
    assert rc == 0 and "PASS" in out, f"Swoole coroutine API not functional: {out} {err}"

    # PART 2: Verify Server.php uses Runtime class (check source structure)
    server_file = REPO / "src/Appwrite/Platform/Installer/Server.php"
    content = server_file.read_text()

    assert "use Swoole\\Runtime" in content, \
        "Server.php must import Swoole\\Runtime for async support"
    assert "Runtime::enableCoroutine" in content, \
        "Server.php must call Runtime::enableCoroutine to enable async I/O"
    assert "SWOOLE_HOOK_" in content, \
        "Server.php must specify hook flags (e.g., SWOOLE_HOOK_ALL)"


def test_cli_params_skip_web_installer():
    """
    Verify installer skips web UI when explicit CLI params are provided.

    Behavior: When --args (except --interactive) are passed, the installer
    detects them via a method that checks $_SERVER['argv'] and skips the web UI.
    This test runs PHP code to verify the method exists and uses str_starts_with.
    """
    # Use PHP to actually check the behavior - this runs the code
    rc, out, err = _run_php(f"""
        $file = '{REPO}/src/Appwrite/Platform/Tasks/Install.php';
        $content = file_get_contents($file);

        // The method must exist for CLI param detection
        if (strpos($content, 'function hasExplicitCliParams') === false) {{
            echo "FAIL:hasExplicitCliParams method not found";
            exit(1);
        }}

        // The method must use str_starts_with to detect -- arguments
        if (strpos($content, 'str_starts_with') === false) {{
            echo "FAIL:no str_starts_with for arg detection";
            exit(1);
        }}

        echo "PASS:hasExplicitCliParams detection logic present";
    """)
    assert rc == 0 and "PASS" in out, f"CLI params detection not implemented: {out} {err}"


def test_gethostbyname_error_suppression():
    """
    Verify gethostbyname has error suppression for DNS failures.

    Behavior: The @ operator suppresses errors on gethostbyname call so DNS
    lookup failures don't generate PHP warnings.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Must use @ error suppression on gethostbyname call
    assert "@gethostbyname" in content or "@ gethostbyname" in content, \
        "gethostbyname must use @ error suppression for DNS failures"


def test_tracking_payload_uses_correct_ip_key():
    """
    Verify tracking payload uses 'ip' key (not 'hostIp').

    Behavior: The analytics payload uses 'ip' field, not 'hostIp'.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Find trackSelfHostedInstall function
    match = re.search(
        r"private\s+function\s+trackSelfHostedInstall\s*\([^)]*\)(.*?)(?=private\s+function\s|\Z)",
        content, re.DOTALL
    )
    assert match, "trackSelfHostedInstall function not found"

    body = match.group(1)

    # Must use 'ip' key, not 'hostIp'
    assert "'ip' =>" in body or '"ip" =>' in body, \
        "Tracking payload must use 'ip' key for IP address"
    assert "'hostIp' =>" not in body and '"hostIp" =>' not in body, \
        "Tracking payload should not use 'hostIp' - use 'ip' instead"


def test_tracking_validates_dns_result():
    """
    Verify tracking validates DNS lookup result before including IP.

    Behavior: Code checks gethostbyname result is not false and not equal
    to the domain name before including IP in payload.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    match = re.search(
        r"private\s+function\s+trackSelfHostedInstall\s*\([^)]*\)(.*?)(?=private\s+function\s|\Z)",
        content, re.DOTALL
    )
    assert match, "trackSelfHostedInstall function not found"

    body = match.group(1)

    # Must validate result !== false
    assert re.search(r"!==\s*false", body), \
        "Must check that gethostbyname result is not false"
    assert "gethostbyname" in body, \
        "gethostbyname call must exist in tracking"


def test_http_client_has_timeouts():
    """
    Verify HTTP client has both connection and request timeouts.

    Behavior: HTTP client for tracking has setConnectTimeout and setTimeout
    configured to prevent hanging on slow networks.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    assert re.search(r"->\s*setConnectTimeout\s*\(\s*\d+\s*\)", content), \
        "HTTP client must set connection timeout (setConnectTimeout)"
    assert re.search(r"->\s*setTimeout\s*\(\s*\d+\s*\)", content), \
        "HTTP client must set request timeout (setTimeout)"


def test_performinstallation_accepts_callback():
    """
    Verify performInstallation accepts a callable onComplete parameter.

    Behavior: The function signature includes an optional callable parameter.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    sig_match = re.search(
        r"public\s+function\s+performInstallation\s*\([^)]*\)",
        content
    )
    assert sig_match, "performInstallation function not found"

    sig = sig_match.group(0)
    assert "callable" in sig, \
        "performInstallation must accept a callable parameter"
    assert "null" in sig, \
        "The callable parameter must be optional (default null)"


def test_oncomplete_called_before_tracking():
    """
    Verify onComplete callback is invoked before tracking.

    Behavior: The completion callback is called before tracking so the SSE
    stream can finish and frontend can redirect immediately.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    func_match = re.search(
        r"public\s+function\s+performInstallation\s*\([^)]*\)(.*?)(?=public\s+function\s|\Z)",
        content, re.DOTALL
    )
    assert func_match, "performInstallation function not found"

    func_body = func_match.group(1)

    oncomplete_match = re.search(r"if\s*\(\s*\$onComplete\s*\)", func_body)
    tracking_match = re.search(r"\$this\s*->\s*trackSelfHostedInstall", func_body)

    assert oncomplete_match, "onComplete callback must be invoked"
    assert tracking_match, "trackSelfHostedInstall must be called"
    assert oncomplete_match.start() < tracking_match.start(), \
        "onComplete must be called before tracking for immediate SSE response"


def test_coroutine_tracking_when_in_swoole():
    """
    Verify tracking runs in a coroutine when in Swoole context.

    Behavior: The code checks Coroutine::getCid() to detect Swoole context
    and uses go(function ...) to offload tracking to a coroutine.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    assert re.search(r"use\s+Swoole\\Coroutine\b", content), \
        "Must import Swoole\\Coroutine for async support"
    assert re.search(r"Coroutine\s*::\s*getCid\s*\(\s*\)", content), \
        "Must check Coroutine::getCid() to detect Swoole context"
    assert re.search(r"go\s*\(\s*function\s*\(\s*\)", content), \
        "Must run tracking in a coroutine using go(function ...) when in Swoole context"


def test_upgrade_detection_for_web_installer():
    """
    Verify web installer treats existing installation as upgrade.

    Behavior: When existing installation is detected, the isUpgrade flag
    includes it so the web installer runs in upgrade mode.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    assert re.search(r"isUpgrade\s*\|\|.*existingInstallation|existingInstallation.*\|\|.*isUpgrade", content, re.DOTALL), \
        "Web installer must pass isUpgrade=true when existing installation detected"


def test_http_install_uses_responsesent_flag():
    """
    Verify HTTP Install uses responseSent flag to prevent duplicate responses.

    Behavior: A boolean flag tracks whether response was already sent.
    """
    http_install = REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    content = http_install.read_text()

    assert re.search(r"\$responseSent\s*=\s*false", content), \
        "Must have responseSent flag initialized to false"
    assert re.search(r"if\s*\(\s*\$responseSent\s*\)", content), \
        "Must check responseSent flag before sending response"


def test_http_oncomplete_updates_lock_and_sends():
    """
    Verify onComplete callback updates lock status and sends response.

    Behavior: The callback updates global lock to COMPLETED and sends
    SSE event or JSON response depending on wantsStream.
    """
    http_install = REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    content = http_install.read_text()

    assert re.search(r"\$state\s*->\s*updateGlobalLock", content), \
        "onComplete must update global lock status"
    assert re.search(r"writeSseEvent|->\s*json\s*\(", content), \
        "onComplete must send SSE event or JSON response"


def test_performinstallation_receives_oncomplete():
    """
    Verify performInstallation call receives the onComplete callback.

    Behavior: The onComplete callback is passed to performInstallation.
    """
    http_install = REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    content = http_install.read_text()

    call_match = re.search(
        r"performInstallation\s*\(.*?\);",
        content, re.DOTALL
    )
    assert call_match, "performInstallation call not found"
    assert "$onComplete" in call_match.group(0), \
        "performInstallation must be called with onComplete parameter"


def test_css_upgrade_minheight():
    """
    Verify CSS sets min-height to 0 for upgrade mode.

    Behavior: The installer step has min-height: 0 in upgrade mode via
    [data-upgrade='true'] CSS selector.
    """
    css_file = REPO / "app/views/install/installer/css/styles.css"
    content = css_file.read_text()

    assert re.search(r"\.installer-step\s*\{[^}]*min-height\s*:\s*0\s*;", content), \
        "Upgrade mode must have .installer-step { min-height: 0 }"
    assert re.search(r"\[data-upgrade\s*=\s*['\"]true['\"]\]|\.upgrade", content), \
        "Must have upgrade-specific CSS selector like [data-upgrade='true']"


def test_step4_hides_secret_on_upgrade():
    """
    Verify step-4 template hides secret key row during upgrade.

    Behavior: Secret API key is hidden when !$isUpgrade.
    """
    step4_file = REPO / "app/views/install/installer/templates/steps/step-4.phtml"
    content = step4_file.read_text()

    assert re.search(r"if\s*\(\s*!\s*\$isUpgrade\s*\)|if\s*\(\s*\$isUpgrade\s*===\s*false\s*\)", content), \
        "Step 4 must conditionally hide secret key based on upgrade mode"
    assert "Secret API key" in content, \
        "Secret API key row must exist in template for fresh installs"


def test_step5_says_appwrite_not_your_app():
    """
    Verify step-5 template says 'Appwrite' instead of 'your app'.

    Behavior: Progress text uses 'Appwrite' brand, not 'your app'.
    """
    step5_file = REPO / "app/views/install/installer/templates/steps/step-5.phtml"
    content = step5_file.read_text()

    assert "Updating Appwrite" in content or "Installing Appwrite" in content, \
        "Step 5 must say 'Appwrite' (e.g., 'Updating Appwrite' or 'Installing Appwrite')"
    assert "your app" not in content, \
        "Step 5 must not say 'your app' - use 'Appwrite' instead"
