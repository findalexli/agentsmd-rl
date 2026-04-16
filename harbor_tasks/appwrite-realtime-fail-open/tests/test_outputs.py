#!/usr/bin/env python3
"""
Test suite for appwrite realtime fail-open fix.

This tests actual behavior — calling the code and asserting on return values,
not on source code text patterns.
"""

import subprocess
import sys
import os
import tempfile

REPO = "/workspace/appwrite"
TARGET_FILE = f"{REPO}/src/Appwrite/Event/Realtime.php"


def test_file_syntax_valid():
    """PHP syntax check passes (pass_to_pass)."""
    result = subprocess.run(
        ["php", "-l", TARGET_FILE],
        capture_output=True,
        text=True,
        timeout=30
    )
    assert result.returncode == 0, f"PHP syntax error:\n{result.stderr}"


def test_trigger_returns_true_despite_adapter_exception():
    """trigger() returns true even when realtime adapter throws (fail_to_pass).

    This behavioral test actually instantiates Realtime, injects a mock adapter
    that throws, and verifies trigger() returns true without propagating.
    """
    php_test = f'''<?php
require_once '{REPO}/vendor/autoload.php';

use Appwrite\\Event\\Realtime;
use Appwrite\\Messaging\\Adapter\\Realtime as RealtimeAdapter;
use Utopia\\Database\\Document;
use Utopia\\Database\\Role;
use Utopia\\Database\\ID;

class FailingRealtimeAdapter extends RealtimeAdapter {{
    public function send(mixed ...$args): void {{
        throw new \\Exception('Simulated Redis failure');
    }}
}}

$realtime = new Realtime();

// Inject our failing adapter via reflection
$reflection = new ReflectionClass($realtime);
$prop = $reflection->getProperty('realtime');
$prop->setAccessible(true);
$prop->setValue($realtime, new FailingRealtimeAdapter());

// Set up required context - use teams event with required param
$mockProject = new Document(['$id' => 'test-project', 'teamId' => 'team1']);
$realtime
    ->setProject($mockProject)
    ->setEvent('teams.[teamId].create')
    ->setParam('teamId', 'team1')
    ->setParam('userId', 'test-user');

$result = $realtime->trigger();

// Exit 0 if result is true (pass), exit 1 otherwise (fail)
exit($result === true ? 0 : 1);
'''
    test_file = "/tmp/test_trigger_behavior.php"
    with open(test_file, 'w') as f:
        f.write(php_test)

    try:
        result = subprocess.run(
            ["php", test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"trigger() must return true even when adapter throws.\n"
            f"Exit: {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"
        )
    finally:
        os.unlink(test_file)


def test_error_logged_via_console_on_failure():
    """Console::error is called with 'Realtime send failed' when adapter throws (fail_to_pass).

    This test verifies the error logging behavior by mocking Console::error
    and checking it was called with the expected message.
    """
    php_test = f'''<?php
require_once '{REPO}/vendor/autoload.php';

use Appwrite\\Event\\Realtime;
use Appwrite\\Messaging\\Adapter\\Realtime as RealtimeAdapter;
use Utopia\\Database\\Document;
use Utopia\\Database\\Role;
use Utopia\\Database\\ID;

// Track calls to Console::error
$consoleCalls = [];

class MockConsole {{
    public static function error($message) {{
        global $consoleCalls;
        $consoleCalls[] = $message;
    }}
}}

// Create a mock adapter that throws
class FailingRealtimeAdapter extends RealtimeAdapter {{
    public function send(mixed ...$args): void {{
        throw new \\Exception('Simulated connection failure');
    }}
}}

// Override Console class before loading Realtime
class_alias('MockConsole', 'Utopia\\Console');

$realtime = new Realtime();

// Inject failing adapter
$reflection = new ReflectionClass($realtime);
$prop = $reflection->getProperty('realtime');
$prop->setAccessible(true);
$prop->setValue($realtime, new FailingRealtimeAdapter());

// Set up context
$mockProject = new Document(['$id' => 'test-project', 'teamId' => 'team1']);
$realtime
    ->setProject($mockProject)
    ->setEvent('teams.[teamId].create')
    ->setParam('teamId', 'team1')
    ->setParam('userId', 'test-user');

$realtime->trigger();

// Verify Console::error was called with 'Realtime send failed'
$found = false;
foreach ($consoleCalls as $msg) {{
    if (strpos($msg, 'Realtime send failed') !== false) {{
        $found = true;
        break;
    }}
}}

exit($found ? 0 : 1);
'''
    test_file = "/tmp/test_console_error.php"
    with open(test_file, 'w') as f:
        f.write(php_test)

    try:
        result = subprocess.run(
            ["php", test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"Console::error must be called with 'Realtime send failed' on adapter exception.\n"
            f"Exit: {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"
        )
    finally:
        os.unlink(test_file)


def test_loop_continues_after_send_failure():
    """Loop continues to next project when send() fails (fail_to_pass).

    This test verifies requirement 4: when iterating over multiple project IDs,
    a failure on one project must not stop processing of subsequent projects.
    We track which project IDs were attempted by having a partially-failing adapter.
    """
    php_test = f'''<?php
require_once '{REPO}/vendor/autoload.php';

use Appwrite\\Event\\Realtime;
use Appwrite\\Messaging\\Adapter\\Realtime as RealtimeAdapter;
use Utopia\\Database\\Document;

// Track which project IDs received send() calls
$projectAttempts = [];
$failureCount = 0;

class TrackingRealtimeAdapter extends RealtimeAdapter {{
    public function send(mixed ...$args): void {{
        global $projectAttempts, $failureCount;

        // Record that send was called
        $projectAttempts[] = 'send-called';

        $failureCount++;
        if ($failureCount <= 1) {{
            throw new \\Exception('Simulated transient failure');
        }}
        // Succeed on second and subsequent calls
    }}
}}

$realtime = new Realtime();

// Inject tracking adapter
$reflection = new ReflectionClass($realtime);
$prop = $reflection->getProperty('realtime');
$prop->setAccessible(true);
$prop->setValue($realtime, new TrackingRealtimeAdapter());

$mockProject = new Document(['$id' => 'test-project', 'teamId' => 'team1']);
$realtime
    ->setProject($mockProject)
    ->setEvent('teams.[teamId].create')
    ->setParam('teamId', 'team1')
    ->setParam('userId', 'test-user');

// Set subscribers (multiple project IDs) so the loop processes each
$realtime->setSubscribers(['project1', 'project2']);

$result = $realtime->trigger();

// The loop should have continued after the first failure
// so we expect send() was called at least 2 times (once per target)
$success = ($result === true) && (count($projectAttempts) >= 2);
exit($success ? 0 : 1);
'''
    test_file = "/tmp/test_loop_continue.php"
    with open(test_file, 'w') as f:
        f.write(php_test)

    try:
        result = subprocess.run(
            ["php", test_file],
            capture_output=True,
            text=True,
            timeout=30
        )
        assert result.returncode == 0, (
            f"Loop must continue after send() failure - multiple targets should be processed.\n"
            f"Exit: {result.returncode}\nStderr: {result.stderr}\nStdout: {result.stdout}"
        )
    finally:
        os.unlink(test_file)


def test_composer_autoload_works():
    """Composer autoload is functional (pass_to_pass)."""
    if not os.path.exists(f"{REPO}/vendor/autoload.php"):
        print("SKIP: vendor/autoload.php not found")
        return

    php_test = """<?php
require_once '/workspace/appwrite/vendor/autoload.php';
echo 'OK';
"""
    test_file = "/tmp/test_autoload.php"
    with open(test_file, 'w') as f:
        f.write(php_test)

    result = subprocess.run(
        ["php", test_file],
        capture_output=True,
        text=True,
        timeout=30
    )
    os.unlink(test_file)
    assert result.returncode == 0, f"Autoload failed: {result.stderr}"
    assert "OK" in result.stdout, f"Autoload did not work: {result.stdout}"


def test_composer_validate():
    """Composer configuration is valid (pass_to_pass)."""
    result = subprocess.run(
        ["composer", "validate"],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )
    assert result.returncode == 0, f"Composer validate failed:\n{result.stderr}"


def test_composer_audit():
    """Composer security audit runs successfully (pass_to_pass).

    Note: composer audit may find vulnerabilities (returns 1) but still runs.
    We check that the command executes without errors.
    """
    result = subprocess.run(
        ["composer", "audit"],
        capture_output=True,
        text=True,
        timeout=120,
        cwd=REPO,
    )
    # Audit returns 0 or 1 depending on whether vulnerabilities are found
    # We just check it executes successfully (doesn't crash)
    assert result.returncode in [0, 1], f"Composer audit failed to run:\n{result.stderr}"
    output = result.stdout + result.stderr
    assert "Found" in output or "No known security vulnerabilities" in output or "Advisory ID" in output, \
        f"Unexpected audit output: {output[:200]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))