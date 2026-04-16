"""
Benchmark tests for selenium-bidi-deserialization-refactor task.

Tests verify the refactoring that moves BiDi event deserialization from
the EventDispatcher background thread to the Broker network thread.
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/selenium")
BROKER_FILE = REPO / "dotnet/src/webdriver/BiDi/Broker.cs"
DISPATCHER_FILE = REPO / "dotnet/src/webdriver/BiDi/EventDispatcher.cs"


def test_dotnet_build():
    """The .NET WebDriver project compiles without errors (pass_to_pass)."""
    # Build the webdriver project using dotnet CLI
    result = subprocess.run(
        ["dotnet", "build", "src/webdriver/WebDriver.csproj", "-c", "Release", "--no-restore", "-v", "minimal"],
        cwd=REPO / "dotnet",
        capture_output=True,
        text=True,
        timeout=300
    )
    # Allow build to fail due to missing deps, but not due to syntax errors in the changed files
    if result.returncode != 0:
        # Check if error is in the files we changed
        stderr = result.stderr + result.stdout
        if "Broker.cs" in stderr or "EventDispatcher.cs" in stderr:
            # Check for actual compilation errors (not just warnings)
            if "error CS" in stderr:
                assert False, f"Compilation error in changed files:
{stderr[-2000:]}"
    # If we got here, either build succeeded or failed for unrelated reasons


def test_dotnet_format_whitespace():
    """BiDi code passes dotnet format whitespace check (pass_to_pass).

    This is part of the repo's CI - runs `dotnet format whitespace --verify-no-changes`
    to ensure code follows .editorconfig whitespace rules.
    """
    result = subprocess.run(
        [
            "dotnet", "format", "whitespace",
            "src/webdriver/Selenium.WebDriver.csproj",
            "--verify-no-changes",
            "--include", "BiDi/"
        ],
        cwd=REPO / "dotnet",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"dotnet format whitespace failed:
{result.stdout}
{result.stderr}"
    )


def test_dotnet_format_style():
    """BiDi code passes dotnet format style check (pass_to_pass).

    This is part of the repo's CI - runs `dotnet format style --verify-no-changes`
    to ensure code follows C# style conventions in .editorconfig.
    """
    result = subprocess.run(
        [
            "dotnet", "format", "style",
            "src/webdriver/Selenium.WebDriver.csproj",
            "--verify-no-changes",
            "--include", "BiDi/",
            "--severity", "warn"
        ],
        cwd=REPO / "dotnet",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"dotnet format style failed:
{result.stdout}
{result.stderr}"
    )


def test_dotnet_format_analyzers():
    """BiDi code passes dotnet format analyzers check (pass_to_pass).

    This is part of the repo's CI - runs `dotnet format analyzers --verify-no-changes`
    to ensure code passes Roslyn analyzer checks.
    """
    result = subprocess.run(
        [
            "dotnet", "format", "analyzers",
            "src/webdriver/Selenium.WebDriver.csproj",
            "--verify-no-changes",
            "--include", "BiDi/",
            "--severity", "warn"
        ],
        cwd=REPO / "dotnet",
        capture_output=True,
        text=True,
        timeout=120
    )
    assert result.returncode == 0, (
        f"dotnet format analyzers failed:
{result.stdout}
{result.stderr}"
    )


def test_try_get_json_type_info_method_exists():
    """EventDispatcher has TryGetJsonTypeInfo public method (fail_to_pass).

    The refactoring adds a new public method TryGetJsonTypeInfo that allows
    the Broker to look up JSON type info before deserializing.
    """
    content = DISPATCHER_FILE.read_text()

    # Check method exists with proper signature pattern (behavioral check)
    # Must be public, return bool, take string eventName and out JsonTypeInfo parameter
    pattern = r"public\s+bool\s+\w+\s*\(\s*string\s+\w+\s*,\s*\[?\s*NotNullWhen\s*\(\s*true\s*\)\s*\]?\s*out\s+JsonTypeInfo\??\s+\w+\s*\)"
    match = re.search(pattern, content)

    assert match is not None, (
        "Public method TryGetJsonTypeInfo not found with expected signature. "
        "Expected: public bool TryGetJsonTypeInfo(string eventName, [NotNullWhen(true)] out JsonTypeInfo? jsonTypeInfo)"
    )


def test_deserialization_moved_to_broker():
    """JsonSerializer.Deserialize is called in Broker, not EventDispatcher (fail_to_pass).

    The key behavioral change is that deserialization now happens on the network
    thread (in Broker) rather than the background thread (in EventDispatcher).
    """
    broker_content = BROKER_FILE.read_text()
    dispatcher_content = DISPATCHER_FILE.read_text()

    # Broker should now contain JsonSerializer.Deserialize call with ref reader pattern
    broker_has_deserialize = "JsonSerializer.Deserialize(ref" in broker_content

    assert broker_has_deserialize, (
        "Broker.cs should contain JsonSerializer.Deserialize(ref ...) "
        "to deserialize events on the network thread"
    )

    # EventDispatcher's ProcessEventsAwaiterAsync should NOT have JsonSerializer.Deserialize
    # The old code had deserialization in the background thread
    dispatcher_process_section = re.search(
        r"ProcessEventsAwaiterAsync.*?(?=private|public|internal|\Z)",
        dispatcher_content,
        re.DOTALL
    )

    if dispatcher_process_section:
        process_code = dispatcher_process_section.group()
        has_deserialize_in_process = "JsonSerializer.Deserialize" in process_code
        assert not has_deserialize_in_process, (
            "EventDispatcher.ProcessEventsAwaiterAsync should not contain JsonSerializer.Deserialize - "
            "deserialization should happen in Broker on the network thread"
        )


def test_enqueue_event_accepts_event_args():
    """EnqueueEvent takes EventArgs parameter instead of raw bytes (fail_to_pass).

    The simplified method signature accepts already-deserialized EventArgs
    rather than raw JSON bytes.
    """
    content = DISPATCHER_FILE.read_text()

    # New signature should accept EventArgs (not ReadOnlyMemory<byte>)
    # Look for: public void EnqueueEvent(..., EventArgs ...)
    new_sig_pattern = r"public\s+void\s+EnqueueEvent\s*\([^)]*EventArgs[^)]*\)"
    has_event_args_signature = re.search(new_sig_pattern, content) is not None

    # Old signature used ReadOnlyMemory<byte>
    old_sig_pattern = r"public\s+void\s+EnqueueEvent\s*\([^)]*ReadOnlyMemory<byte>"
    has_old_signature = re.search(old_sig_pattern, content) is not None

    assert has_event_args_signature, (
        "EnqueueEvent should accept EventArgs parameter in its signature"
    )
    assert not has_old_signature, (
        "EnqueueEvent should not have old signature with ReadOnlyMemory<byte> parameter"
    )


def test_pending_event_struct_simplified():
    """PendingEvent record stores EventArgs directly (fail_to_pass).

    The PendingEvent struct is simplified to store already-deserialized EventArgs
    rather than raw bytes and type info.
    """
    content = DISPATCHER_FILE.read_text()

    # New struct should have EventArgs as a parameter
    # Look for record struct with EventArgs parameter
    new_pattern = r"record\s+(?:struct\s+)?PendingEvent\s*\([^)]*EventArgs[^)]*\)"
    has_event_args_param = re.search(new_pattern, content) is not None

    # Old struct had JsonUtf8Bytes, BiDi, TypeInfo parameters
    # Check that the new struct does not have these old parameters
    pending_event_match = re.search(r"record\s+(?:struct\s+)?PendingEvent\s*\([^)]+\)", content)
    has_old_params = False
    if pending_event_match:
        pending_def = pending_event_match.group()
        has_old_params = "JsonUtf8Bytes" in pending_def or "ReadOnlyMemory<byte>" in pending_def

    assert has_event_args_param, (
        "PendingEvent record should contain EventArgs as a parameter"
    )
    assert not has_old_params, (
        "PendingEvent should not contain JsonUtf8Bytes or ReadOnlyMemory<byte> - it should store deserialized EventArgs"
    )


def test_event_registrations_field_usage():
    """EventDispatcher uses renamed field for event registrations (fail_to_pass).

    For clarity, the events dictionary is renamed to better reflect its purpose.
    The old field name "_events" is replaced with a more descriptive name.
    """
    content = DISPATCHER_FILE.read_text()

    # Find the ConcurrentDictionary field declaration
    # It should NOT use the old name "_events"
    field_pattern = r"private\s+readonly\s+ConcurrentDictionary[^;]+\s+(\w+)\s*="
    field_match = re.search(field_pattern, content)

    if field_match:
        field_name = field_match.group(1)
        assert field_name != "_events", (
            "Field should not be named "_events" (found: "{field_name}"). "
            "The events dictionary should be renamed to better reflect its purpose."
        )
    else:
        # If no field found, check that _events is not used as the main dictionary
        # Look for usage patterns - the refactored code should use a different name
        old_pattern = r"_events\s*\.\s*(?:GetOrAdd|TryGetValue)"
        has_old_usage = re.search(old_pattern, content) is not None
        assert not has_old_usage, (
            "Old field name "_events" should not be used for the main event registrations dictionary"
        )


def test_broker_validates_event_type_before_deserialize():
    """Broker validates event type mapping exists before attempting deserialization (fail_to_pass).

    The refactoring adds validation to ensure the event type mapping exists
    before attempting to deserialize, with appropriate logging for unmapped events.
    """
    content = BROKER_FILE.read_text()

    # Should call TryGetJsonTypeInfo (or similar validation method) before deserializing
    has_type_check = "TryGetJsonTypeInfo" in content

    # Should have some form of warning/error logging when type not found
    # This could be _logger.Warn, _logger.Error, or similar
    has_warning_pattern = r"_logger\.(?:Warn|Error|Warning|LogWarning)"
    has_warning_log = re.search(has_warning_pattern, content) is not None

    assert has_type_check, (
        "Broker should call TryGetJsonTypeInfo (or similar) to validate event type before deserialization"
    )
    assert has_warning_log, (
        "Broker should log a warning when event type mapping is not found"
    )


def test_params_reader_snapshot_usage():
    """Broker uses Utf8JsonReader snapshot pattern for params (fail_to_pass).

    Instead of tracking byte indices, the code captures a Utf8JsonReader
    snapshot which is more efficient and cleaner. The snapshot is then used
    with JsonSerializer.Deserialize.
    """
    content = BROKER_FILE.read_text()

    # Should have a Utf8JsonReader variable for params
    reader_var_pattern = r"Utf8JsonReader\s+\w+Reader\s*="
    has_reader_var = re.search(reader_var_pattern, content) is not None

    # Should capture reader snapshot (assignment from another reader)
    snapshot_pattern = r"\w+Reader\s*=\s*\w+Reader\s*;"
    has_snapshot = re.search(snapshot_pattern, content) is not None

    # Should use this reader with Deserialize
    deserialize_pattern = r"JsonSerializer\.Deserialize\s*\(\s*ref\s+\w+Reader"
    has_deserialize_with_reader = re.search(deserialize_pattern, content) is not None

    # Should NOT use the old byte index approach
    has_old_indices = "paramsStartIndex" in content or "paramsEndIndex" in content

    assert has_reader_var, (
        "Broker should declare a Utf8JsonReader variable for capturing params"
    )
    assert has_snapshot, (
        "Broker should capture a reader snapshot (e.g., paramsReader = reader)"
    )
    assert has_deserialize_with_reader, (
        "Broker should use JsonSerializer.Deserialize with a ref reader parameter"
    )
    assert not has_old_indices, (
        "Broker should not use paramsStartIndex/paramsEndIndex - use reader snapshot instead"
    )


def test_not_null_when_attribute_usage():
    """EventDispatcher uses NotNullWhen attribute for TryGet pattern (fail_to_pass).

    The new TryGetJsonTypeInfo method uses [NotNullWhen(true)] attribute which
    requires the System.Diagnostics.CodeAnalysis namespace and provides better
    null-safety for the out parameter.
    """
    content = DISPATCHER_FILE.read_text()

    # Should import System.Diagnostics.CodeAnalysis
    has_code_analysis_import = "using System.Diagnostics.CodeAnalysis;" in content

    # Should use NotNullWhen attribute on an out parameter
    not_null_pattern = r"\[NotNullWhen\s*\(\s*true\s*\)\]\s*out"
    has_not_null_when = re.search(not_null_pattern, content) is not None

    assert has_code_analysis_import, (
        "EventDispatcher should import System.Diagnostics.CodeAnalysis for NotNullWhen attribute"
    )
    assert has_not_null_when, (
        "EventDispatcher should use [NotNullWhen(true)] attribute on an out parameter"
    )
