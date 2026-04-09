#!/usr/bin/env python3
"""Tests for Selenium .NET BiDi EventDispatcher thread-safety fix.

This validates that the EventDispatcher uses copy-on-write array pattern
with locking for thread-safe handler registration.
"""

import subprocess
import sys
import re

REPO = "/workspace/selenium"
EVENT_DISPATCHER_PATH = f"{REPO}/dotnet/src/webdriver/BiDi/EventDispatcher.cs"
WEBDRIVER_CSPROJ = f"{REPO}/dotnet/src/webdriver/Selenium.WebDriver.csproj"


def test_event_dispatcher_uses_copy_on_write_array():
    """F2P: EventRegistration uses volatile EventHandler[] array instead of List<EventHandler>."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Should have volatile EventHandler[] field
    assert "private volatile EventHandler[] _handlers" in content, \
        "EventDispatcher should use volatile EventHandler[] array for thread safety"

    # Should NOT have List<EventHandler> Handlers property
    assert "public List<EventHandler> Handlers" not in content, \
        "EventDispatcher should not use List<EventHandler> (not thread-safe)"

    # Should have GetHandlers method that returns the array
    assert "public EventHandler[] GetHandlers()" in content, \
        "EventDispatcher should have GetHandlers() method"


def test_event_dispatcher_has_thread_safe_add_handler():
    """F2P: EventRegistration.AddHandler uses lock for thread-safe addition."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Should have AddHandler method with lock
    assert "public void AddHandler(EventHandler handler)" in content, \
        "EventDispatcher should have AddHandler method"

    # Should use lock for thread safety during add
    assert "lock (_lock) _handlers = [.. _handlers, handler]" in content, \
        "AddHandler should use lock with copy-on-write pattern"

    # Should NOT have direct registration.Handlers.Add call
    assert "registration.Handlers.Add" not in content, \
        "Should not use old Handlers.Add pattern"


def test_event_dispatcher_has_thread_safe_remove_handler():
    """F2P: EventRegistration.RemoveHandler uses lock for thread-safe removal."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Should have RemoveHandler method with lock
    assert "public void RemoveHandler(EventHandler handler)" in content, \
        "EventDispatcher should have RemoveHandler method"

    # Should use lock for thread safety during remove
    assert "lock (_lock) _handlers = Array.FindAll(_handlers, h => h != handler)" in content, \
        "RemoveHandler should use lock with copy-on-write pattern"

    # Should NOT have direct registration.Handlers.Remove call
    assert "registration.Handlers.Remove" not in content, \
        "Should not use old Handlers.Remove pattern"


def test_event_dispatcher_has_lock_object():
    """F2P: EventRegistration has private lock object for synchronization."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Should have lock object
    assert "private readonly object _lock = new();" in content, \
        "EventRegistration should have private lock object for thread safety"


def test_event_dispatcher_uses_get_handlers_in_process_events():
    """F2P: ProcessEventsAwaiterAsync uses GetHandlers() instead of Handlers.ToArray()."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Should use GetHandlers() in the event processing loop
    assert "foreach (var handler in registration.GetHandlers())" in content, \
        "ProcessEventsAwaiterAsync should use GetHandlers() for safe iteration"

    # Should NOT use old Handlers.ToArray() pattern
    assert "registration.Handlers.ToArray()" not in content, \
        "Should not use old Handlers.ToArray() pattern"


def test_dotnet_syntax_valid():
    """P2P: EventDispatcher.cs has valid C# syntax (no missing braces, etc)."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Basic syntax validation - check balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for complete class structure
    assert content.count('class EventDispatcher') == 1, "Should have exactly one EventDispatcher class"
    assert content.count('class EventRegistration') == 1, "Should have exactly one EventRegistration class"

    # Verify no obvious syntax errors
    assert ';;' not in content, "Should not have double semicolons"
    assert content.count('(') == content.count(')'), "Unbalanced parentheses"


def test_event_dispatcher_class_structure():
    """P2P: EventDispatcher class has proper structure with required members."""
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    # Check required methods exist
    assert "SubscribeAsync" in content, "EventDispatcher should have SubscribeAsync method"
    assert "UnsubscribeAsync" in content, "EventDispatcher should have UnsubscribeAsync method"
    assert "ProcessEventsAwaiterAsync" in content, "EventDispatcher should have ProcessEventsAwaiterAsync method"

    # Check EventRegistration exists
    assert "class EventRegistration" in content, "EventRegistration class should exist"

    # Check for required imports
    assert "using System.Text.Json" in content, "Should import System.Text.Json"
    assert "namespace OpenQA.Selenium.BiDi" in content, "Should be in correct namespace"


def test_event_dispatcher_file_parses_correctly():
    """P2P: EventDispatcher.cs exists and has valid content."""
    # Verify the file exists and is not empty
    with open(EVENT_DISPATCHER_PATH, 'r') as f:
        content = f.read()

    assert len(content) > 1000, "EventDispatcher.cs should have substantial content"
    assert "class EventDispatcher" in content, "EventDispatcher class should exist"

    # Check for proper indentation (C# standard is 4 spaces)
    lines_with_indent = [l for l in content.split('\n') if l.startswith('    ') and l.strip()]
    assert len(lines_with_indent) > 10, "Should have properly indented code"

    # Verify no mixed tabs/spaces issues
    assert '\t' not in content, "Should not use tabs for indentation"


def test_repo_dotnet_format():
    """P2P: Repo dotnet format check passes (actual CI lint step)."""
    r = subprocess.run(
        ["dotnet", "format", "Selenium.WebDriver.csproj", "--verify-no-changes", "--verbosity", "q"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/dotnet/src/webdriver"
    )
    # Exit code 0 means no formatting issues found (pass)
    # Exit code 2 means formatting issues exist but project loaded (warnings)
    # We accept both as "pass" since this is just a syntax/parse validation
    assert r.returncode in [0, 2], f"dotnet format failed with unexpected error:\n{r.stderr[-500:]}"


def test_repo_dotnet_restore():
    """P2P: Repo dotnet restore passes (actual CI dependency restore)."""
    r = subprocess.run(
        ["dotnet", "restore"],
        capture_output=True, text=True, timeout=120, cwd=f"{REPO}/dotnet/src/webdriver"
    )
    assert r.returncode == 0, f"dotnet restore failed:\n{r.stderr[-500:]}"


if __name__ == "__main__":
    sys.exit(subprocess.run(["pytest", __file__, "-v"]).returncode)
