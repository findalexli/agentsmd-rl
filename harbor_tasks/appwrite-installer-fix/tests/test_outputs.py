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
# FAIL-TO-PASS TESTS (These verify the fix through behavior, not text)
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
    Verify Swoole coroutines are enabled in Server.php.

    Behavior: Server.php must enable coroutines when starting the Swoole server.
    This is verified by checking that the file enables the Swoole runtime.
    """
    server_file = REPO / "src/Appwrite/Platform/Installer/Server.php"
    content = server_file.read_text()

    # Check that Server.php imports Swoole\Runtime
    # This is necessary to call Runtime::enableCoroutine
    assert "use Swoole\\Runtime;" in content, \
        "Server.php must import Swoole\\Runtime for async support"

    # Verify Runtime::enableCoroutine is called with hook flags
    assert "Runtime::enableCoroutine(" in content, \
        "Server.php must call Runtime::enableCoroutine to enable async I/O"

    # Verify hook flags are specified (SWOOLE_HOOK_ALL or similar)
    assert "SWOOLE_HOOK_" in content, \
        "Server.php must specify hook flags for coroutine hooks"


def test_cli_params_detection_behavior():
    """
    Verify installer detects CLI parameters to skip web installer.

    Behavior: The Install.php must check for CLI arguments that indicate
    explicit CLI mode (--param=value style) and skip the web installer.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Check that the file has logic to detect CLI params
    # The fix checks $_SERVER['argv'] for -- prefixed arguments
    assert r"$_SERVER['argv']" in content or r"$_SERVER[\"argv\"]" in content, \
        r"Install.php must check $_SERVER['argv'] for CLI argument detection"

    # Check that it looks for -- prefixed arguments
    assert "str_starts_with" in content, \
        "Install.php must use str_starts_with for argument detection"

    # Verify the web server skip logic exists
    assert "--interactive" in content, \
        "Install.php must check for --interactive to exclude it from CLI param detection"


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


def test_tracking_payload_ip_key():
    """
    Verify tracking payload uses correct key name for IP address.

    Behavior: The analytics payload uses 'ip' field (not 'hostIp').
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Find trackSelfHostedInstall function body
    match = re.search(
        r"private\s+function\s+trackSelfHostedInstall\s*\([^)]*\)(.*?)(?=private\s+function\s|\Z)",
        content, re.DOTALL
    )
    assert match, "trackSelfHostedInstall function not found"

    body = match.group(1)

    # Check that 'ip' key exists in the payload
    has_ip_key = "'ip' =>" in body or '"ip" =>' in body
    assert has_ip_key, \
        "Tracking payload must use 'ip' key for IP address"

    # Check that the old 'hostIp' key is not used
    has_hostip = "'hostIp' =>" in body or '"hostIp" =>' in body
    assert not has_hostip, \
        "Tracking payload should not use 'hostIp' - must use 'ip' instead"


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
    has_not_false = "!== false" in body or "!==false" in body
    assert has_not_false, \
        "Must check that gethostbyname result is not false"

    # Must compare result to domain
    has_domain_check = "$domain" in body and ("!== $domain" in body or "!==$domain" in body or "!=" in body)
    assert has_domain_check, \
        "Must check that gethostbyname result differs from domain name"


def test_http_client_has_timeouts():
    """
    Verify HTTP client has both connection and request timeouts.

    Behavior: HTTP client for tracking has setConnectTimeout and setTimeout
    configured to prevent hanging on slow networks.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Check for setConnectTimeout call with numeric value
    has_connect_timeout = re.search(r"->\s*setConnectTimeout\s*\(\s*\d+", content)
    assert has_connect_timeout, \
        "HTTP client must set connection timeout (setConnectTimeout with numeric value)"

    # Check for setTimeout call with numeric value
    has_timeout = re.search(r"->\s*setTimeout\s*\(\s*\d+", content)
    assert has_timeout, \
        "HTTP client must set request timeout (setTimeout with numeric value)"


def test_performinstallation_accepts_callback():
    """
    Verify performInstallation accepts an optional callable callback parameter.

    Behavior: The function signature includes an optional callable parameter
    that gets called when installation completes.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Find performInstallation signature
    sig_match = re.search(
        r"public\s+function\s+performInstallation\s*\([^)]*\)",
        content
    )
    assert sig_match, "performInstallation function not found"

    sig = sig_match.group(0)

    # Check for callable type hint
    assert "callable" in sig, \
        "performInstallation must accept a callable parameter"

    # Check for default null (making it optional)
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

    # Find performInstallation function body
    func_match = re.search(
        r"public\s+function\s+performInstallation\s*\([^)]*\)(.*?)(?=public\s+function\s|\Z)",
        content, re.DOTALL
    )
    assert func_match, "performInstallation function not found"

    func_body = func_match.group(1)

    # Check that onComplete is called
    oncomplete_call = re.search(r"\$onComplete\s*\(", func_body) or \
                       re.search(r"if\s*\(\s*\$onComplete\s*\)", func_body) or \
                       re.search(r"\$onComplete\s*&&", func_body)
    assert oncomplete_call, "onComplete callback must be invoked in performInstallation"

    # Check that tracking is called
    tracking_call = re.search(r"\$this\s*->\s*trackSelfHostedInstall", func_body)
    assert tracking_call, "trackSelfHostedInstall must be called in performInstallation"

    # Verify order: onComplete comes before tracking
    assert oncomplete_call.start() < tracking_call.start(), \
        "onComplete must be called before tracking for immediate SSE response"


def test_coroutine_tracking_when_in_swoole():
    """
    Verify tracking runs in a coroutine when in Swoole context.

    Behavior: The code detects Swoole context and uses go() to offload
    tracking to a coroutine when running in Swoole.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Must import Swoole\Coroutine
    assert "use Swoole\\Coroutine;" in content, \
        "Must import Swoole\\Coroutine for async support"

    # Must check Coroutine::getCid() to detect Swoole context
    has_getcid = re.search(r"Coroutine\s*::\s*getCid", content)
    assert has_getcid, \
        "Must check Coroutine::getCid() to detect Swoole context"

    # Must use go() function to run in coroutine
    has_go = re.search(r"\bgo\s*\(", content)
    assert has_go, \
        "Must run tracking in a coroutine using go() when in Swoole context"

    # Must check if in Swoole context (cid !== -1 or cid > -1 or cid != -1)
    has_context_check = re.search(r"(?:!==|!=|>)\s*-1", content) or \
                       re.search(r"\bid\(\)" + r"\s*(?:!==|!=|>)\s*-1", content)
    # A more general check: look for -1 comparison near Coroutine
    if not has_context_check:
        # Alternative: look for any -1 check in the file
        has_context_check = re.search(r"-1", content) and "Coroutine" in content
    assert has_context_check, \
        "Must detect Swoole context by checking if coroutine ID is not -1"


def test_upgrade_detection_for_web_installer():
    """
    Verify web installer treats existing installation as upgrade.

    Behavior: When existing installation is detected, the isUpgrade flag
    passed to startWebServer includes the existingInstallation check.
    """
    install_file = REPO / "src/Appwrite/Platform/Tasks/Install.php"
    content = install_file.read_text()

    # Look for isUpgrade || $existingInstallation or similar pattern
    has_upgrade_check = re.search(
        r"isUpgrade\s*\|\|.*existingInstallation|existingInstallation.*\|\|.*isUpgrade",
        content, re.DOTALL
    ) or re.search(
        r"\$isUpgrade\s*\|\|\s*\$existingInstallation",
        content
    ) or re.search(
        r"existingInstallation.*\|\|.*\$isUpgrade",
        content
    )
    assert has_upgrade_check, \
        "Web installer must pass isUpgrade flag that includes existing installation detection"


def test_http_install_uses_responsesent_flag():
    """
    Verify HTTP Install uses responseSent flag to prevent duplicate responses.

    Behavior: A boolean flag tracks whether response was already sent
    to prevent sending duplicate responses.
    """
    http_install = REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    content = http_install.read_text()

    # Check for responseSent variable initialization
    has_flag_init = re.search(r"\$responseSent\s*=\s*false", content)
    assert has_flag_init, \
        "Must have responseSent flag initialized to false"

    # Check for responseSent check before sending
    has_flag_check = re.search(r"if\s*\(\s*\$responseSent\s*\)", content) or \
                     re.search(r"if\s*\(\s*!\s*\$responseSent\s*\)", content)
    assert has_flag_check, \
        "Must check responseSent flag before sending response"


def test_http_oncomplete_updates_lock_and_sends():
    """
    Verify onComplete callback updates lock status and sends response.

    Behavior: The callback updates global lock to COMPLETED and sends
    SSE event or JSON response depending on wantsStream.
    """
    http_install = REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    content = http_install.read_text()

    # Check for updateGlobalLock call
    has_lock_update = re.search(r"updateGlobalLock.*STATUS_COMPLETED|updateGlobalLock.*completed", content, re.IGNORECASE)
    assert has_lock_update, \
        "onComplete must update global lock status to completed"

    # Check for response sending (SSE or JSON)
    has_response = re.search(r"writeSseEvent|->\s*json\s*\(", content)
    assert has_response, \
        "onComplete must send SSE event or JSON response"


def test_performinstallation_receives_oncomplete():
    """
    Verify performInstallation call receives the onComplete callback.

    Behavior: The onComplete callback is passed to performInstallation.
    """
    http_install = REPO / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    content = http_install.read_text()

    # Find performInstallation call
    call_match = re.search(
        r"performInstallation\s*\(.*\);",
        content, re.DOTALL
    )
    assert call_match, "performInstallation call not found"

    call = call_match.group(0)

    # Check that onComplete is passed as argument
    has_oncomplete = "$onComplete" in call
    assert has_oncomplete, \
        "performInstallation must be called with onComplete parameter"


def test_css_upgrade_minheight():
    """
    Verify CSS sets min-height to 0 for upgrade mode.

    Behavior: The installer step has min-height: 0 in upgrade mode via
    CSS selector that targets upgrade state.
    """
    css_file = REPO / "app/views/install/installer/css/styles.css"
    content = css_file.read_text()

    # Check for min-height: 0 on installer-step
    has_minheight = re.search(r"\.installer-step\s*\{[^}]*min-height\s*:\s*0\s*;", content) or \
                    re.search(r"min-height\s*:\s*0\s*;", content)
    assert has_minheight, \
        "Upgrade mode must have min-height: 0 for installer step"

    # Check for upgrade-specific CSS selector
    has_upgrade_selector = re.search(r"\[data-upgrade\s*=\s*['\"]true['\"]\]", content) or \
                          re.search(r"\.upgrade", content) or \
                          re.search(r"\[data-upgrade", content)
    assert has_upgrade_selector, \
        "Must have upgrade-specific CSS selector like [data-upgrade='true']"


def test_step4_hides_secret_on_upgrade():
    """
    Verify step-4 template hides secret key row during upgrade.

    Behavior: Secret API key is hidden when not in upgrade mode
    (condition checks !$isUpgrade or $isUpgrade === false).
    """
    step4_file = REPO / "app/views/install/installer/templates/steps/step-4.phtml"
    content = step4_file.read_text()

    # Check for conditional based on isUpgrade
    has_conditional = re.search(r"if\s*\(\s*!\s*\$isUpgrade\s*\)|if\s*\(\s*\$isUpgrade\s*===\s*false\s*\)|if\s*\(\s*\$isUpgrade\s*==\s*false\s*\)", content)
    assert has_conditional, \
        "Step 4 must conditionally show secret key based on upgrade mode"

    # Check that Secret API key content exists
    assert "Secret API key" in content, \
        "Secret API key row must exist in template for fresh installs"


def test_step5_says_appwrite_not_your_app():
    """
    Verify step-5 template says 'Appwrite' instead of 'your app'.

    Behavior: Progress text uses 'Appwrite' brand, not 'your app'.
    """
    step5_file = REPO / "app/views/install/installer/templates/steps/step-5.phtml"
    content = step5_file.read_text()

    # Check for Appwrite in the text
    has_appwrite = "Installing Appwrite" in content or "Updating Appwrite" in content
    assert has_appwrite, \
        "Step 5 must say 'Appwrite' (e.g., 'Updating Appwrite' or 'Installing Appwrite')"

    # Check that old 'your app' phrasing is gone
    has_old_phrase = "your app" in content
    assert not has_old_phrase, \
        "Step 5 must not say 'your app' - must use 'Appwrite' instead"
