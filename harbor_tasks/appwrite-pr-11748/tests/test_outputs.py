"""
Test suite for Appwrite SMTP adapter refactor.

This verifies that PHPMailer has been replaced with utopia-php/messaging SMTP adapter
across the codebase: registers, Mails worker, and Doctor task.
"""

import subprocess
import sys
from pathlib import Path

# Repository path
REPO = Path("/workspace/appwrite")


def test_composer_dependency_updated():
    """Verify composer.json requires utopia-php/messaging ^0.22"""
    composer_json = REPO / "composer.json"
    content = composer_json.read_text()

    # Should require 0.22.* not 0.20.*
    assert '"utopia-php/messaging": "0.22.*"' in content, \
        "composer.json should require utopia-php/messaging 0.22.*"
    assert '"utopia-php/messaging": "0.20.*"' not in content, \
        "composer.json should not still reference 0.20.*"


def test_smtp_register_returns_adapter():
    """Verify registers.php returns SMTP adapter, not PHPMailer"""
    registers_file = REPO / "app/init/registers.php"
    content = registers_file.read_text()

    # Should have SMTP import
    assert "use Utopia\\Messaging\\Adapter\\Email\\SMTP;" in content, \
        r"registers.php should import Utopia\Messaging\Adapter\Email\SMTP"

    # Should NOT have PHPMailer import
    assert "use PHPMailer\\PHPMailer\\PHPMailer;" not in content, \
        "registers.php should not import PHPMailer"

    # Should return new SMTP(...) with named arguments
    assert "return new SMTP(" in content, \
        "registers.php should return new SMTP instance"

    # Should have key SMTP parameters
    assert "host:" in content, "SMTP should use named parameter 'host'"
    assert "port:" in content, "SMTP should use named parameter 'port'"
    assert "keepAlive:" in content, "SMTP should use named parameter 'keepAlive'"
    assert "timelimit:" in content, "SMTP should use named parameter 'timelimit'"


def test_smtp_register_no_phpmailer_methods():
    """Verify registers.php doesn't contain PHPMailer-specific setup code"""
    registers_file = REPO / "app/init/registers.php"
    content = registers_file.read_text()

    # These are PHPMailer-specific methods that should be gone
    phpmailer_patterns = [
        "$mail->isSMTP",
        "$mail->XMailer",
        "$mail->SMTPAuth",
        "$mail->Username",
        "$mail->Password",
        "$mail->SMTPSecure",
        "$mail->SMTPAutoTLS",
        "$mail->SMTPKeepAlive",
        "$mail->CharSet",
        "$mail->Timeout",
        "$mail->setFrom",
        "$mail->addReplyTo",
        "$mail->isHTML",
        "new PHPMailer",
    ]

    for pattern in phpmailer_patterns:
        assert pattern not in content, \
            f"registers.php should not contain PHPMailer pattern: {pattern}"


def test_mails_worker_refactored():
    """Verify Mails worker uses EmailAdapter and EmailMessage"""
    mails_file = REPO / "src/Appwrite/Platform/Workers/Mails.php"
    content = mails_file.read_text()

    # Should have new imports
    assert "use Utopia\\Messaging\\Adapter\\Email as EmailAdapter;" in content, \
        "Mails.php should import EmailAdapter"
    assert "use Utopia\\Messaging\\Adapter\\Email\\SMTP;" in content, \
        "Mails.php should import SMTP adapter"
    assert "use Utopia\\Messaging\\Messages\\Email as EmailMessage;" in content, \
        "Mails.php should import EmailMessage"
    assert "use Utopia\\Messaging\\Messages\\Email\\Attachment;" in content, \
        "Mails.php should import Attachment"

    # Should NOT have PHPMailer import
    assert "use PHPMailer\\PHPMailer\\PHPMailer;" not in content, \
        "Mails.php should not import PHPMailer"

    # Should use EmailAdapter type hint
    assert "@var EmailAdapter $adapter" in content or "EmailAdapter $adapter" in content, \
        "Mails.php should use EmailAdapter type hint"

    # Should construct EmailMessage
    assert "new EmailMessage(" in content, \
        "Mails.php should construct EmailMessage"

    # Should call adapter->send() with message
    assert "$adapter->send($emailMessage)" in content or "$adapter->send(" in content, \
        "Mails.php should call adapter->send() with message"


def test_mails_worker_no_phpmailer_cleanup():
    """Verify Mails worker doesn't use PHPMailer state management methods"""
    mails_file = REPO / "src/Appwrite/Platform/Workers/Mails.php"
    content = mails_file.read_text()

    # These PHPMailer-specific cleanup methods should be gone
    cleanup_methods = [
        "$mail->clearAddresses",
        "$mail->clearAllRecipients",
        "$mail->clearReplyTos",
        "$mail->clearAttachments",
        "$mail->clearBCCs",
        "$mail->clearCCs",
        "$mail->addAddress",
        "$mail->Subject",
        "$mail->Body",
        "$mail->AltBody",
        "$mail->AddStringAttachment",
    ]

    for method in cleanup_methods:
        assert method not in content, \
            f"Mails.php should not contain PHPMailer method: {method}"


def test_getmailer_method_removed():
    """Verify getMailer() protected method is removed from Mails worker"""
    mails_file = REPO / "src/Appwrite/Platform/Workers/Mails.php"
    content = mails_file.read_text()

    # The getMailer method should not exist
    assert "protected function getMailer(" not in content, \
        "getMailer() method should be removed from Mails.php"
    assert "protected function getMailer" not in content, \
        "getMailer() method signature should not exist"


def test_doctor_task_refactored():
    """Verify Doctor task uses SMTP adapter and EmailMessage"""
    doctor_file = REPO / "src/Appwrite/Platform/Tasks/Doctor.php"
    content = doctor_file.read_text()

    # Should have new imports
    assert "use Utopia\\Messaging\\Adapter\\Email as EmailAdapter;" in content, \
        "Doctor.php should import EmailAdapter"
    assert "use Utopia\\Messaging\\Messages\\Email as EmailMessage;" in content, \
        "Doctor.php should import EmailMessage"

    # Should NOT have PHPMailer import
    assert "use PHPMailer\\PHPMailer\\PHPMailer;" not in content, \
        "Doctor.php should not import PHPMailer"

    # Should use EmailAdapter type hint
    assert "@var EmailAdapter $smtp" in content or "EmailAdapter $smtp" in content, \
        "Doctor.php should use EmailAdapter type hint"

    # Should construct EmailMessage
    assert "new EmailMessage(" in content, \
        "Doctor.php should construct EmailMessage"

    # Should call smtp->send() with message
    assert "$smtp->send($emailMessage)" in content, \
        "Doctor.php should call smtp->send() with message"


def test_doctor_no_phpmailer_methods():
    """Verify Doctor task doesn't use PHPMailer-specific methods"""
    doctor_file = REPO / "src/Appwrite/Platform/Tasks/Doctor.php"
    content = doctor_file.read_text()

    # These PHPMailer-specific methods should be gone
    phpmailer_methods = [
        "$mail->addAddress",
        "$mail->Subject",
        "$mail->Body",
        "$mail->AltBody",
        "$mail->send()",
    ]

    for method in phpmailer_methods:
        # Note: $smtp->send($emailMessage) is OK, just $mail->send() is not
        if method == "$mail->send()":
            assert "$mail->send()" not in content, \
                "Doctor.php should not call $mail->send()"
        else:
            assert method not in content, \
                f"Doctor.php should not contain PHPMailer method: {method}"


def test_usage_class_not_final():
    """Verify Usage class is no longer final (allows subclassing)"""
    usage_file = REPO / "src/Appwrite/Event/Message/Usage.php"
    content = usage_file.read_text()

    # Should NOT be final
    assert "final class Usage" not in content, \
        "Usage class should not be final"

    # Should use new static instead of new self
    assert "return new static(" in content, \
        "Usage::fromArray should use 'new static' instead of 'new self'"


def test_php_syntax_registers():
    """Verify registers.php has valid PHP syntax"""
    result = subprocess.run(
        ["php", "-l", str(REPO / "app/init/registers.php")],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"registers.php has syntax errors: {result.stderr}"


def test_php_syntax_mails():
    """Verify Mails.php has valid PHP syntax"""
    result = subprocess.run(
        ["php", "-l", str(REPO / "src/Appwrite/Platform/Workers/Mails.php")],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Mails.php has syntax errors: {result.stderr}"


def test_php_syntax_doctor():
    """Verify Doctor.php has valid PHP syntax"""
    result = subprocess.run(
        ["php", "-l", str(REPO / "src/Appwrite/Platform/Tasks/Doctor.php")],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Doctor.php has syntax errors: {result.stderr}"


def test_php_syntax_usage():
    """Verify Usage.php has valid PHP syntax"""
    result = subprocess.run(
        ["php", "-l", str(REPO / "src/Appwrite/Event/Message/Usage.php")],
        capture_output=True,
        text=True
    )
    assert result.returncode == 0, \
        f"Usage.php has syntax errors: {result.stderr}"


# ============================================================================
# PASS-TO-PASS TESTS: Repository CI/CD checks
# These verify that the repo's own tests/lints pass on both base and fixed
# ============================================================================


def test_composer_validate():
    """Repo's composer.json is valid (pass_to_pass)."""
    r = subprocess.run(
        ["composer", "validate", "--no-check-publish", "--no-check-lock"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert r.returncode == 0, f"composer validate failed:\n{r.stderr[-500:]}"


def test_php_syntax_all_modified():
    """All modified PHP files have valid syntax (pass_to_pass)."""
    modified_files = [
        "app/init/registers.php",
        "src/Appwrite/Platform/Workers/Mails.php",
        "src/Appwrite/Platform/Tasks/Doctor.php",
        "src/Appwrite/Event/Message/Usage.php",
    ]

    for file_path in modified_files:
        full_path = REPO / file_path
        r = subprocess.run(
            ["php", "-l", str(full_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        assert r.returncode == 0, f"{file_path} has syntax errors:\n{r.stderr}"
