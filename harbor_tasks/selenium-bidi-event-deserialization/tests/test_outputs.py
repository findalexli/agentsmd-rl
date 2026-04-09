"""
Test suite for Selenium BiDi event deserialization refactor.

This PR refactors how BiDi events are processed:
1. Broker.cs: Changes from byte array slicing (paramsStartIndex/paramsEndIndex) to Utf8JsonReader snapshot
2. EventDispatcher.cs: Changes EnqueueEvent signature from (method, jsonUtf8Bytes, bidi) to (method, eventArgs)
"""

import subprocess
import re
import sys
from pathlib import Path

REPO = "/workspace/selenium"
BROKER_CS = Path(f"{REPO}/dotnet/src/webdriver/BiDi/Broker.cs")
EVENT_DISPATCHER_CS = Path(f"{REPO}/dotnet/src/webdriver/BiDi/EventDispatcher.cs")


def test_broker_no_byte_indices():
    """
    FAIL TO PASS: Broker.cs should NOT use paramsStartIndex/paramsEndIndex byte slicing.
    The old code tracked byte indices and sliced the array.
    The new code uses Utf8JsonReader snapshot (paramsReader).
    """
    content = BROKER_CS.read_text()

    # These should NOT exist in the fixed code (old implementation used these)
    assert "paramsStartIndex" not in content, \
        "Found paramsStartIndex - should use Utf8JsonReader snapshot instead"
    assert "paramsEndIndex" not in content, \
        "Found paramsEndIndex - should use Utf8JsonReader snapshot instead"


def test_broker_uses_params_reader():
    """
    FAIL TO PASS: Broker.cs should use paramsReader (Utf8JsonReader snapshot).
    This captures the reader state at the params property for later deserialization.
    """
    content = BROKER_CS.read_text()

    # Should have paramsReader variable declaration
    assert "Utf8JsonReader paramsReader = default;" in content, \
        "Missing paramsReader declaration"

    # Should assign paramsReader when reading params property
    assert "paramsReader = reader; // snapshot" in content, \
        "Missing paramsReader snapshot assignment"


def test_broker_deserializes_in_broker():
    """
    FAIL TO PASS: Broker.cs should deserialize event args before calling EnqueueEvent.
    The new pattern calls JsonSerializer.Deserialize before passing to EventDispatcher.
    """
    content = BROKER_CS.read_text()

    # Should try to get json type info from event dispatcher
    assert "_eventDispatcher.TryGetJsonTypeInfo" in content, \
        "Missing TryGetJsonTypeInfo call - should check if event type is registered"

    # Should deserialize event args in Broker
    assert "JsonSerializer.Deserialize(ref paramsReader, jsonTypeInfo)" in content, \
        "Missing JsonSerializer.Deserialize call with paramsReader"

    # Should assign BiDi to event args
    assert "eventArgs.BiDi = _bidi;" in content, \
        "Missing eventArgs.BiDi assignment"


def test_broker_passes_event_args_to_dispatcher():
    """
    FAIL TO PASS: Broker.cs should pass deserialized EventArgs to EnqueueEvent.
    Old: _eventDispatcher.EnqueueEvent(method, paramsJsonData, _bidi);
    New: _eventDispatcher.EnqueueEvent(method, eventArgs);
    """
    content = BROKER_CS.read_text()

    # Should NOT pass byte data to EnqueueEvent anymore
    assert "EnqueueEvent(method, paramsJsonData" not in content, \
        "Old pattern found: should not pass byte data to EnqueueEvent"

    # Should pass eventArgs to EnqueueEvent
    assert "_eventDispatcher.EnqueueEvent(method, eventArgs);" in content, \
        "Missing EnqueueEvent call with eventArgs"


def test_event_dispatcher_new_method_signature():
    """
    FAIL TO PASS: EventDispatcher.EnqueueEvent should accept EventArgs, not bytes.
    Old: EnqueueEvent(string method, ReadOnlyMemory<byte> jsonUtf8Bytes, IBiDi bidi)
    New: EnqueueEvent(string method, EventArgs eventArgs)
    """
    content = EVENT_DISPATCHER_CS.read_text()

    # Should NOT have old signature
    assert "EnqueueEvent(string method, ReadOnlyMemory<byte> jsonUtf8Bytes" not in content, \
        "Old EnqueueEvent signature found - should accept EventArgs instead"

    # Should have new signature
    assert "EnqueueEvent(string method, EventArgs eventArgs)" in content, \
        "Missing new EnqueueEvent signature with EventArgs"


def test_event_dispatcher_renamed_field():
    """
    FAIL TO PASS: EventDispatcher should rename _events to _eventRegistrations.
    This improves clarity about what the dictionary contains.
    """
    content = EVENT_DISPATCHER_CS.read_text()

    # Should have new name
    assert "_eventRegistrations" in content, \
        "Missing _eventRegistrations field - should rename from _events"

    # Should NOT have old field name (check for exact field declaration)
    # The old code had: private readonly ConcurrentDictionary<string, EventRegistration> _events = new();
    old_field_pattern = r"EventRegistration\[\]\s+_events\s*=\s*new\(\)"
    if re.search(old_field_pattern, content):
        assert False, "Found old _events field declaration"

    # Check for ConcurrentDictionary declaration of _events
    old_dict_pattern = r"ConcurrentDictionary<[^>]+>\s+_events\s*=\s*new"
    match = re.search(old_dict_pattern, content)
    if match and "_eventRegistrations" not in content:
        assert False, "Found old _events ConcurrentDictionary declaration"


def test_event_dispatcher_try_get_json_type_info():
    """
    FAIL TO PASS: EventDispatcher should have TryGetJsonTypeInfo method.
    This new method allows Broker to check if an event type is registered.
    """
    content = EVENT_DISPATCHER_CS.read_text()

    # Should have TryGetJsonTypeInfo method
    assert "public bool TryGetJsonTypeInfo" in content, \
        "Missing TryGetJsonTypeInfo method - needed for Broker to check event registration"


def test_event_dispatcher_pending_event_struct():
    """
    FAIL TO PASS: PendingEvent record struct should only contain Method and EventArgs.
    Old: PendingEvent(string Method, ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, JsonTypeInfo TypeInfo)
    New: PendingEvent(string Method, EventArgs EventArgs)
    """
    content = EVENT_DISPATCHER_CS.read_text()

    # Should have new simplified PendingEvent
    assert "private readonly record struct PendingEvent(string Method, EventArgs EventArgs);" in content, \
        "PendingEvent struct should only have Method and EventArgs"

    # Should NOT have old PendingEvent definition with multiple fields
    old_pending = "private readonly record struct PendingEvent(string Method, ReadOnlyMemory<byte> JsonUtf8Bytes, IBiDi BiDi, JsonTypeInfo TypeInfo)"
    assert old_pending not in content, \
        "Old PendingEvent struct found - should be simplified to just Method and EventArgs"

    # Should NOT have old byte array field in PendingEvent context
    assert "JsonUtf8Bytes" not in content, \
        "PendingEvent should not contain JsonUtf8Bytes (deserialization moved to Broker)"

    # The EventRegistration class still has TypeInfo - that's expected
    # We only need to verify PendingEvent is simplified


def test_event_dispatcher_no_deserialize_in_process():
    """
    FAIL TO PASS: ProcessEventsAwaiterAsync should NOT call JsonSerializer.Deserialize.
    The deserialization now happens in Broker before events are enqueued.
    """
    content = EVENT_DISPATCHER_CS.read_text()

    # Get the ProcessEventsAwaiterAsync method body
    process_events_pattern = r"private async Task ProcessEventsAwaiterAsync\(\)[^{]*\{([^}]*(?:\{[^}]*\}[^}]*)*)\}"
    match = re.search(process_events_pattern, content, re.DOTALL)

    if match:
        method_body = match.group(1)
        # The old code deserialized here - new code should not
        assert "JsonSerializer.Deserialize" not in method_body, \
            "ProcessEventsAwaiterAsync should not deserialize - should happen in Broker"


def test_event_dispatcher_uses_event_registrations():
    """
    FAIL TO PASS: EventDispatcher should use _eventRegistrations consistently.
    All references to the dictionary should use the new name.
    """
    content = EVENT_DISPATCHER_CS.read_text()

    # Count usages - all should be _eventRegistrations
    events_count = content.count("_events.")
    event_registrations_count = content.count("_eventRegistrations.")

    # Should have multiple usages of _eventRegistrations
    assert event_registrations_count >= 3, \
        f"Expected at least 3 _eventRegistrations references, found {event_registrations_count}"

    # Should not use old _events. references
    assert events_count == 0, \
        f"Found {events_count} references to _events - should use _eventRegistrations"


def test_broker_has_warning_log_for_unknown_events():
    """
    FAIL TO PASS: Broker should log warning for unknown event types.
    The logic was moved from EventDispatcher to Broker.
    """
    content = BROKER_CS.read_text()

    # Should have warning log about unknown events
    assert "no event type mapping was found" in content, \
        "Missing warning for unknown event types"

    assert "Event will be ignored" in content, \
        "Missing 'Event will be ignored' message"


def test_code_syntax_valid():
    """
    PASS TO PASS: The BiDi C# files should have valid syntax.
    We verify this by checking no obvious syntax errors exist.
    """
    broker_content = BROKER_CS.read_text()
    dispatcher_content = EVENT_DISPATCHER_CS.read_text()

    # Check for balanced braces in each file (basic syntax check)
    def check_braces_balanced(content, filename):
        # Simple check - count opening and closing braces
        # Exclude braces in strings and comments
        lines = content.split('\n')
        brace_count = 0
        in_string = False
        string_char = None
        in_line_comment = False
        in_block_comment = False

        for line in lines:
            i = 0
            while i < len(line):
                ch = line[i]

                # Handle line comments
                if not in_block_comment and not in_string and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
                    break  # Rest of line is comment

                # Handle block comments
                if not in_string:
                    if not in_block_comment and ch == '/' and i + 1 < len(line) and line[i + 1] == '*':
                        in_block_comment = True
                        i += 2
                        continue
                    if in_block_comment and ch == '*' and i + 1 < len(line) and line[i + 1] == '/':
                        in_block_comment = False
                        i += 2
                        continue
                    if in_block_comment:
                        i += 1
                        continue

                # Handle strings
                if not in_line_comment and not in_block_comment:
                    if not in_string and ch in ('"', "'"):
                        in_string = True
                        string_char = ch
                        i += 1
                        continue
                    if in_string:
                        if ch == '\\':
                            i += 2  # Skip escaped char
                            continue
                        if ch == string_char:
                            in_string = False
                            string_char = None
                            i += 1
                            continue

                # Count braces
                if not in_string and not in_line_comment and not in_block_comment:
                    if ch == '{':
                        brace_count += 1
                    elif ch == '}':
                        brace_count -= 1

                i += 1

        assert brace_count == 0, f"{filename}: Unbalanced braces (count: {brace_count})"

    check_braces_balanced(broker_content, "Broker.cs")
    check_braces_balanced(dispatcher_content, "EventDispatcher.cs")

    # Check for key syntax elements that should exist in valid C# files
    assert "namespace OpenQA.Selenium.BiDi;" in broker_content, "Broker.cs missing namespace"
    assert "namespace OpenQA.Selenium.BiDi;" in dispatcher_content, "EventDispatcher.cs missing namespace"
    assert "class Broker" in broker_content or "sealed class Broker" in broker_content, "Broker.cs missing class"
    assert "class EventDispatcher" in dispatcher_content or "sealed class EventDispatcher" in dispatcher_content, "EventDispatcher.cs missing class"


def test_broker_no_isParams_flag():
    """
    FAIL TO PASS: Broker should not use isParams boolean flag.
    The old code used this to track when to capture paramsEndIndex.
    """
    content = BROKER_CS.read_text()

    # Should not have isParams variable
    assert "bool isParams = false;" not in content, \
        "Found isParams flag - no longer needed with new implementation"

    assert "if (isParams)" not in content, \
        "Found isParams check - no longer needed with new implementation"
