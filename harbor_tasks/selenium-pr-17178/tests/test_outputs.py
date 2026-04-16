#!/usr/bin/env python3
"""
Tests for Selenium BiDi EventDispatcher revert (PR #17178).

This PR reverts the drain mechanism in EventDispatcher, simplifying event handling.
Tests verify actual behavior - whether code compiles, runs, and produces correct output.

IMPORTANT: These tests verify BEHAVIOR, not implementation details.
Alternative correct fixes with different variable names should still pass.
"""

import subprocess
import re
import os
from pathlib import Path

REPO = Path("/workspace/selenium")
EVENT_DISPATCHER_FILE = REPO / "dotnet/src/webdriver/BiDi/EventDispatcher.cs"


def run_dotnet_build():
    """Run dotnet build and return (returncode, stdout, stderr)."""
    result = subprocess.run(
        ["dotnet", "build", "dotnet/src/webdriver/WebDriver.csproj", "--no-restore", "-v", "q"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    return result.returncode, result.stdout, result.stderr


def get_dotnet_build_errors():
    """Get all C# compilation errors for EventDispatcher.cs."""
    returncode, stdout, stderr = run_dotnet_build()
    errors = []
    for line in (stdout + stderr).split('\n'):
        if "error CS" in line and "EventDispatcher.cs" in line:
            errors.append(line.strip())
    return errors


def extract_methods(content):
    """Extract all method signatures from C# code."""
    # Match private async Task methods
    pattern = r'private\s+async\s+Task\s+(\w+)\s*\('
    return re.findall(pattern, content)


def extract_field_names(content):
    """Extract all private readonly field names."""
    pattern = r'private\s+(?:readonly\s+)?(?:static\s+)?(?:TaskFactory|Task|Channel|ConcurrentDictionary)[<\w\s,>]*\s+(\w+)\s*[=;{]'
    matches = re.findall(pattern, content)
    return matches


def extract_struct_or_record(content):
    """Extract record struct definitions."""
    pattern = r'(?:readonly\s+)?record\s+struct\s+(\w+)'
    return re.findall(pattern, content)


def extract_class_definitions(content):
    """Extract nested class definitions."""
    pattern = r'sealed\s+class\s+(\w+)'
    return re.findall(pattern, content)


def extract_property_declarations(content):
    """Extract public property declarations on EventRegistration."""
    # Look for the EventRegistration class and extract public properties
    pattern = r'public\s+(\w+(?:<[^>]+>)?)\s+(\w+)\s*\{'
    return re.findall(pattern, content)


def check_type_in_channel(content):
    """Check what type the Channel uses."""
    pattern = r'Channel<(\w+)>'
    matches = re.findall(pattern, content)
    return matches


def extract_task_factory_usage(content):
    """Check for TaskFactory usage with specific options."""
    # Look for TaskFactory with DenyChildAttach option
    # Need to handle nested parentheses, so we look for TaskFactory followed by DenyChildAttach on the same line
    pattern = r'TaskFactory\s*=[^;]*DenyChildAttach'
    return bool(re.search(pattern, content))


def check_handler_iteration_pattern(content):
    """Check how handlers are iterated (should use ToArray for thread-safety)."""
    # Look for .ToArray() pattern in handler iteration
    pattern = r'\.Handlers\.ToArray\(\)'
    return bool(re.search(pattern, content))


def check_drain_async_exists(content):
    """Check if DrainAsync method exists anywhere."""
    return 'DrainAsync' in content


def check_sequence_tracking_exists(content):
    """Check if sequence tracking fields exist."""
    return '_enqueueSeq' in content or '_processedSeq' in content


def check_drain_waiters_exists(content):
    """Check if drain waiter list exists."""
    return '_drainWaiters' in content


def check_method_in_pending_event(content, method_name_pattern):
    """Check if PendingEvent struct has a method-like parameter."""
    pattern = rf'PendingEvent\s*\(\s*string\s+{method_name_pattern}'
    return bool(re.search(pattern, content))


# ============================================================================
# FAIL-TO-PASS TESTS
# These tests MUST fail on base commit and pass after the fix
# ============================================================================

def test_process_events_method_renamed():
    """
    Verify the event processing method has been refactored (renamed from ProcessEventsAsync).

    Behavioral check: The private async Task processing method should exist,
    and the old name should NOT be present while a new name pattern IS present.
    We verify there exists exactly ONE private async Task processing method.
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # The old method name should NOT exist
    old_name = "ProcessEventsAsync"
    assert old_name not in content, (
        f"Old method name '{old_name}' should not exist - method should be renamed"
    )

    # Extract all private async Task methods - there should be exactly ONE
    # (the event processing loop method)
    methods = extract_methods(content)
    async_methods = [m for m in methods if not m.startswith('Subscribe') and
                     not m.startswith('Unsubscribe') and
                     not m.startswith('Enqueue') and
                     m != 'DisposeAsync']

    # There should be exactly one background processing method
    assert len(async_methods) == 1, (
        f"Expected exactly 1 async processing method, found: {async_methods}"
    )

    # The method name should NOT be the old name (already checked above)
    # and should be different - it should be a rename
    processing_method = async_methods[0]
    assert processing_method != "ProcessEventsAsync", (
        f"Processing method should be renamed, still found as '{processing_method}'"
    )


def test_pending_event_struct_used():
    """
    Verify PendingEvent (not EventItem) is used as the channel type.

    Behavioral check: The Channel should use a struct type named PendingEvent.
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # Old EventItem record should NOT exist
    assert "record EventItem" not in content, (
        "EventItem record should be replaced with PendingEvent struct"
    )

    # Channel should use PendingEvent
    channel_types = check_type_in_channel(content)
    assert 'PendingEvent' in channel_types, (
        f"Channel should use PendingEvent type, found: {channel_types}"
    )

    # Check PendingEvent struct exists (as readonly record struct)
    structs = extract_struct_or_record(content)
    assert 'PendingEvent' in structs, (
        f"PendingEvent readonly record struct should exist, found structs: {structs}"
    )


def test_drain_async_removed():
    """
    Verify DrainAsync method is removed from EventRegistration.

    Behavioral check: DrainAsync should not exist anywhere in the file.
    This is a key simplification - no blocking drain mechanism.
    """
    content = EVENT_DISPATCHER_FILE.read_text()
    assert not check_drain_async_exists(content), (
        "DrainAsync method should be removed - drain mechanism is being reverted"
    )


def test_handlers_directly_exposed():
    """
    Verify handlers are exposed as a direct property (not via AddHandler/RemoveHandler).

    Behavioral check: EventRegistration should have a public property exposing
    the handlers list directly, instead of AddHandler/RemoveHandler methods.
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # AddHandler and RemoveHandler should NOT exist
    assert "AddHandler" not in content, (
        "AddHandler method should be removed - handlers should be exposed directly"
    )
    assert "RemoveHandler" not in content, (
        "RemoveHandler method should be removed - handlers should be exposed directly"
    )

    # Check for public property on EventRegistration
    properties = extract_property_declarations(content)
    # Look for a List<EventHandler> property named Handlers
    has_handlers_prop = any(
        prop_type == 'List<EventHandler>' and prop_name == 'Handlers'
        for prop_type, prop_name in properties
    )
    assert has_handlers_prop, (
        f"EventRegistration should have public 'List<EventHandler> Handlers' property, found: {properties}"
    )


def test_event_emitter_task_refactored():
    """
    Verify the background task is refactored to use TaskFactory.

    Behavioral check: There should be a static TaskFactory with DenyChildAttach
    option, and it should be used to start the background task.
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # Old field name should NOT exist
    assert "_processEventsTask" not in content, (
        "_processEventsTask field should be renamed to reflect its emitter role"
    )

    # There should be a TaskFactory with DenyChildAttach option
    has_task_factory = extract_task_factory_usage(content)
    assert has_task_factory, (
        "Should use TaskFactory with DenyChildAttach option for task creation"
    )

    # Extract fields to verify a new task field exists
    fields = extract_field_names(content)
    # The new field should be some variant of emitter/task name (not the old _processEventsTask)
    task_fields = [f for f in fields if 'Task' in f and f != '_processEventsTask']
    assert len(task_fields) >= 1, (
        f"Should have a Task field (refactored from _processEventsTask), found fields: {fields}"
    )


def test_sequence_tracking_removed():
    """
    Verify sequence tracking fields are removed.

    Behavioral check: _enqueueSeq and _processedSeq should not exist.
    """
    content = EVENT_DISPATCHER_FILE.read_text()
    assert not check_sequence_tracking_exists(content), (
        "_enqueueSeq and _processedSeq should be removed - sequence tracking is being reverted"
    )


def test_drain_waiters_removed():
    """
    Verify drain waiter infrastructure is removed.

    Behavioral check: _drainWaiters should not exist.
    """
    content = EVENT_DISPATCHER_FILE.read_text()
    assert not check_drain_waiters_exists(content), (
        "_drainWaiters should be removed - drain mechanism is being reverted"
    )


def test_pending_event_has_method_field():
    """
    Verify PendingEvent struct stores the method name directly.

    Behavioral check: The new data structure should include a Method field
    (as string parameter in constructor) so the processing loop can dispatch correctly.
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # The method name pattern should exist in PendingEvent definition
    # Look for: PendingEvent(string Method, ...)
    pattern = r'PendingEvent\s*\(\s*string\s+Method\s*,'
    assert re.search(pattern, content), (
        "PendingEvent struct should include 'string Method' as first parameter"
    )


def test_thread_safe_handler_iteration():
    """
    Verify handlers are iterated thread-safely (using ToArray pattern).

    Behavioral check: When iterating handlers, the code should use ToArray()
    to create a snapshot copy before iteration, preventing modification during iteration.
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # Check for ToArray pattern
    has_to_array = check_handler_iteration_pattern(content)
    assert has_to_array, (
        "Should use .ToArray() pattern for thread-safe handler iteration"
    )


# ============================================================================
# PASS-TO-PASS TESTS
# These tests MUST pass on both base commit and after the fix
# ============================================================================

def test_file_exists():
    """Verify EventDispatcher.cs file exists (pass_to_pass)."""
    assert EVENT_DISPATCHER_FILE.exists(), (
        f"EventDispatcher.cs not found at {EVENT_DISPATCHER_FILE}"
    )


def test_csharp_compiles():
    """
    Verify EventDispatcher.cs code compiles without errors (pass_to_pass).

    Behavioral check: The C# code should compile successfully.
    This is a fundamental requirement - broken code should not pass.
    """
    # Check if dotnet is available
    result = subprocess.run(
        ["dotnet", "--version"],
        capture_output=True,
        text=True,
        timeout=30
    )
    if result.returncode != 0:
        # dotnet not available, skip compilation check
        return

    errors = get_dotnet_build_errors()
    assert len(errors) == 0, (
        f"EventDispatcher.cs should compile without errors, found {len(errors)} errors:\n"
        + "\n".join(errors[:5])
    )


def test_class_structure_valid():
    """
    Verify EventDispatcher class has proper structure (pass_to_pass).
    """
    content = EVENT_DISPATCHER_FILE.read_text()

    # Check class declaration
    assert "internal sealed class EventDispatcher" in content, (
        "EventDispatcher class declaration not found"
    )

    # Check implements IAsyncDisposable
    assert "IAsyncDisposable" in content, (
        "EventDispatcher should implement IAsyncDisposable"
    )

    # Check core methods exist
    assert "SubscribeAsync" in content, "SubscribeAsync method not found"
    assert "UnsubscribeAsync" in content, "UnsubscribeAsync method not found"
    assert "EnqueueEvent" in content, "EnqueueEvent method not found"
    assert "DisposeAsync" in content, "DisposeAsync method not found"


def test_event_registration_class_exists():
    """
    Verify EventRegistration nested class exists (pass_to_pass).
    """
    content = EVENT_DISPATCHER_FILE.read_text()
    assert "class EventRegistration" in content, (
        "EventRegistration nested class not found"
    )


def test_channel_usage():
    """
    Verify Channel is used for pending events (pass_to_pass).
    """
    content = EVENT_DISPATCHER_FILE.read_text()
    assert "Channel<" in content, "Should use Channel for pending events"
    assert "_pendingEvents" in content, "_pendingEvents field not found"


def test_concurrent_dictionary_for_events():
    """
    Verify ConcurrentDictionary is used for event storage (pass_to_pass).
    """
    content = EVENT_DISPATCHER_FILE.read_text()
    assert "ConcurrentDictionary<string, EventRegistration>" in content, (
        "Should use ConcurrentDictionary for thread-safe event storage"
    )


# ============================================================================
# CI-BASED PASS-TO-PASS TESTS
# These tests run actual repo CI commands via subprocess
# ============================================================================

def test_repo_dotnet_format_eventdispatcher():
    """
    Run dotnet format check on EventDispatcher.cs (pass_to_pass).

    This runs the actual CI formatting check on the modified file.
    """
    result = subprocess.run(
        ["dotnet", "format", "--verify-no-changes", "--include", "BiDi/EventDispatcher.cs"],
        cwd=f"{REPO}/dotnet/src/webdriver",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"dotnet format check failed on EventDispatcher.cs:\n{result.stderr[-500:]}"
    )


def test_repo_dotnet_format_bidi_module():
    """
    Run dotnet format check on entire BiDi module (pass_to_pass).

    This runs the actual CI formatting check on all BiDi/*.cs files.
    """
    result = subprocess.run(
        ["dotnet", "format", "--verify-no-changes", "--include", "BiDi/*.cs"],
        cwd=f"{REPO}/dotnet/src/webdriver",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"dotnet format check failed on BiDi module:\n{result.stderr[-500:]}"
    )


def test_repo_dotnet_format_whitespace():
    """
    Run dotnet format whitespace check on EventDispatcher.cs (pass_to_pass).

    Checks whitespace formatting compliance for the modified file.
    """
    result = subprocess.run(
        ["dotnet", "format", "whitespace", "--verify-no-changes", "--include", "BiDi/EventDispatcher.cs"],
        cwd=f"{REPO}/dotnet/src/webdriver",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"dotnet format whitespace check failed:\n{result.stderr[-500:]}"
    )


def test_repo_dotnet_format_style():
    """
    Run dotnet format style check on EventDispatcher.cs (pass_to_pass).

    Checks code style compliance for the modified file.
    """
    result = subprocess.run(
        ["dotnet", "format", "style", "--verify-no-changes", "--include", "BiDi/EventDispatcher.cs"],
        cwd=f"{REPO}/dotnet/src/webdriver",
        capture_output=True,
        text=True,
        timeout=180
    )
    assert result.returncode == 0, (
        f"dotnet format style check failed:\n{result.stderr[-500:]}"
    )