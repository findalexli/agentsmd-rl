#!/usr/bin/env python3
"""Tests for Selenium .NET BiDi Input Actions serialization refactor.

This validates that the agent correctly:
1. Removes the custom InputSourceActionsConverter
2. Implements polymorphic serialization using JsonPolymorphic/JsonDerivedType
3. Renames action types (KeyActions -> KeySourceActions, etc.)
4. Changes int properties to long for consistency
5. Updates test file to use new API
"""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/selenium")
INPUT_DIR = REPO / "dotnet/src/webdriver/BiDi/Input"
CONVERTERS_DIR = REPO / "dotnet/src/webdriver/BiDi/Json/Converters/Enumerable"
TEST_DIR = REPO / "dotnet/test/webdriver/BiDi/Input"


def test_source_actions_syntax():
    """SourceActions.cs has valid C# syntax (p2p).

    Note: Full build requires Bazel which is not available in this environment.
    We verify syntax by checking for balanced braces and valid structure.
    """
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # Basic syntax validation: balanced braces
    open_braces = content.count('{')
    close_braces = content.count('}')
    assert open_braces == close_braces, f"Unbalanced braces: {open_braces} open, {close_braces} close"

    # Check for valid record declarations
    assert "public abstract record SourceActions;" in content or \
           "public abstract record SourceActions" in content, \
        "SourceActions record declaration should be valid"

    # Ensure no obvious syntax errors like double semicolons or unmatched parens
    assert ";;" not in content, "Double semicolons found (syntax error)"


def test_custom_converter_removed():
    """Custom InputSourceActionsConverter is removed (f2p)."""
    converter_file = CONVERTERS_DIR / "InputSourceActionsConverter.cs"
    assert not converter_file.exists(), \
        f"InputSourceActionsConverter.cs should be deleted but still exists"


def test_sequential_actions_removed():
    """SequentialSourceActions.cs is removed (f2p)."""
    seq_file = INPUT_DIR / "SequentialSourceActions.cs"
    assert not seq_file.exists(), \
        f"SequentialSourceActions.cs should be deleted but still exists"


def test_sourceactions_has_polymorphic_attribute():
    """SourceActions uses JsonPolymorphic attribute (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # Check for JsonPolymorphic attribute on SourceActions
    assert "[JsonPolymorphic(TypeDiscriminatorPropertyName = \"type\")]" in content, \
        "SourceActions should have [JsonPolymorphic] attribute"

    # Check for JsonDerivedType attributes for all action types
    assert '[JsonDerivedType(typeof(KeySourceActions), "key")]' in content, \
        "Should have JsonDerivedType for KeySourceActions"
    assert '[JsonDerivedType(typeof(PointerSourceActions), "pointer")]' in content, \
        "Should have JsonDerivedType for PointerSourceActions"
    assert '[JsonDerivedType(typeof(WheelSourceActions), "wheel")]' in content, \
        "Should have JsonDerivedType for WheelSourceActions"
    assert '[JsonDerivedType(typeof(NoneSourceActions), "none")]' in content, \
        "Should have JsonDerivedType for NoneSourceActions"


def test_old_json_converter_removed():
    """Old [JsonConverter(typeof(InputSourceActionsConverter))] is removed (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    assert "[JsonConverter(typeof(InputSourceActionsConverter))]" not in content, \
        "Old JsonConverter attribute should be removed from SourceActions"
    assert "using OpenQA.Selenium.BiDi.Json.Converters.Enumerable;" not in content, \
        "Using statement for Enumerable converters should be removed"


def test_key_source_actions_renamed():
    """KeyActions renamed to KeySourceActions with immutable pattern (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # New type should exist
    assert "public sealed record KeySourceActions(string Id, IEnumerable<IKeySourceAction> Actions)" in content, \
        "KeySourceActions with new signature should exist"

    # Old type should not exist
    assert "public sealed record KeyActions(string Id)" not in content, \
        "Old KeyActions should be removed"


def test_pointer_source_actions_renamed():
    """PointerActions renamed to PointerSourceActions with immutable pattern (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # New type should exist
    assert "public sealed record PointerSourceActions(string Id, IEnumerable<IPointerSourceAction> Actions)" in content, \
        "PointerSourceActions with new signature should exist"

    # Old type should not exist
    assert "public sealed record PointerActions(string Id)" not in content, \
        "Old PointerActions should be removed"

    # Options renamed to Parameters
    assert "public PointerParameters? Parameters { get; init; }" in content, \
        "Options should be renamed to Parameters"


def test_wheel_source_actions_renamed():
    """WheelActions renamed to WheelSourceActions with immutable pattern (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    assert "public sealed record WheelSourceActions(string Id, IEnumerable<IWheelSourceAction> Actions)" in content, \
        "WheelSourceActions with new signature should exist"

    assert "public sealed record WheelActions(string Id)" not in content, \
        "Old WheelActions should be removed"


def test_none_source_actions_renamed():
    """NoneActions renamed to NoneSourceActions with immutable pattern (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    assert "public sealed record NoneSourceActions(string Id, IEnumerable<INoneSourceAction> Actions)" in content, \
        "NoneSourceActions with new signature should exist"

    assert "public sealed record NoneActions(string Id)" not in content, \
        "Old NoneActions should be removed"


def test_int_changed_to_long():
    """int properties changed to long for consistency (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # PointerDownAction should use long Button
    assert "public sealed record PointerDownAction(long Button)" in content, \
        "PointerDownAction.Button should be long"

    # PointerUpAction should use long Button
    assert "public sealed record PointerUpAction(long Button)" in content, \
        "PointerUpAction.Button should be long"

    # WheelScrollAction should use long coordinates
    assert "public sealed record WheelScrollAction(long X, long Y, long DeltaX, long DeltaY)" in content, \
        "WheelScrollAction should use long for coordinates"

    # IPointerCommonProperties should use long
    assert "public long? Width { get; init; }" in content, \
        "IPointerCommonProperties.Width should be long?"
    assert "public long? Height { get; init; }" in content, \
        "IPointerCommonProperties.Height should be long?"
    assert "public long? Twist { get; init; }" in content, \
        "IPointerCommonProperties.Twist should be long?"


def test_inputmodule_serialization_removed():
    """InputModule.cs removes enumerable serialization types (f2p)."""
    module_file = INPUT_DIR / "InputModule.cs"
    content = module_file.read_text()

    assert "[JsonSerializable(typeof(IEnumerable<IPointerSourceAction>))]" not in content, \
        "IEnumerable<IPointerSourceAction> serialization should be removed"
    assert "[JsonSerializable(typeof(IEnumerable<IKeySourceAction>))]" not in content, \
        "IEnumerable<IKeySourceAction> serialization should be removed"
    assert "[JsonSerializable(typeof(IEnumerable<INoneSourceAction>))]" not in content, \
        "IEnumerable<INoneSourceAction> serialization should be removed"
    assert "[JsonSerializable(typeof(IEnumerable<IWheelSourceAction>))]" not in content, \
        "IEnumerable<IWheelSourceAction> serialization should be removed"


def test_test_file_uses_new_api():
    """Test file uses new SourceActions API (f2p)."""
    test_file = TEST_DIR / "CombinedInputActionsTests.cs"
    content = test_file.read_text()

    # Should use new type names
    assert "PointerSourceActions" in content, "Test should use PointerSourceActions"
    assert "KeySourceActions" in content, "Test should use KeySourceActions"

    # Should use immutable pattern with array initializer syntax
    assert "new PointerSourceActions(\"id0\", [" in content or \
           "new PointerSourceActions(\"pointer\", [" in content, \
        "Test should use immutable pattern with array initializer for PointerSourceActions"

    assert "new KeySourceActions(\"id1\", [" in content or \
           "new KeySourceActions(\"key\", [" in content, \
        "Test should use immutable pattern with array initializer for KeySourceActions"

    # Should NOT use old mutable collection initializer pattern
    assert "new PointerActions(\"id0\") {" not in content, \
        "Test should not use old mutable PointerActions pattern"
    assert "new KeyActions(\"id1\") {" not in content, \
        "Test should not use old mutable KeyActions pattern"


def test_key_down_up_implements_interface_directly():
    """KeyDownAction and KeyUpAction implement IKeySourceAction directly (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # Should implement interface directly, not through abstract base
    assert "public sealed record KeyDownAction(char Value) : IKeySourceAction;" in content or \
           "public sealed record KeyDownAction(char Value) : IKeySourceAction" in content, \
        "KeyDownAction should implement IKeySourceAction directly"

    assert "public sealed record KeyUpAction(char Value) : IKeySourceAction;" in content or \
           "public sealed record KeyUpAction(char Value) : IKeySourceAction" in content, \
        "KeyUpAction should implement IKeySourceAction directly"

    # Abstract base should be removed
    assert "public abstract record KeySourceAction : IKeySourceAction;" not in content, \
        "KeySourceAction abstract class should be removed"


def test_pointer_actions_implements_interface_directly():
    """Pointer actions implement IPointerSourceAction directly (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    assert "public sealed record PointerDownAction(long Button) : IPointerSourceAction" in content, \
        "PointerDownAction should implement IPointerSourceAction directly"

    assert "public sealed record PointerUpAction(long Button) : IPointerSourceAction;" in content or \
        "public sealed record PointerUpAction(long Button) : IPointerSourceAction" in content, \
        "PointerUpAction should implement IPointerSourceAction directly"

    # Abstract base should be removed
    assert "public abstract record PointerSourceAction : IPointerSourceAction;" not in content, \
        "PointerSourceAction abstract class should be removed"


def test_sourceactions_generic_signature():
    """SourceActions<T> has correct new signature (f2p)."""
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    assert "public abstract record SourceActions<TSourceAction>(string Id, IEnumerable<TSourceAction> Actions)" in content, \
        "SourceActions<T> should have new signature with IEnumerable<TSourceAction> Actions parameter"

    # Should NOT have old mutable IList pattern
    assert "public IList<ISourceAction> Actions { get; init; }" not in content, \
        "Old mutable IList pattern should be removed"


def test_sourceactions_consistency():
    """SourceActions.cs has consistent structure (p2p).

    Verifies that key relationships between types are maintained.
    """
    source_file = INPUT_DIR / "SourceActions.cs"
    content = source_file.read_text()

    # Check that interface implementations are consistent
    key_down_matches = content.count("KeyDownAction")
    key_up_matches = content.count("KeyUpAction")

    # These types should exist
    assert key_down_matches >= 2, "KeyDownAction should be defined and used"
    assert key_up_matches >= 2, "KeyUpAction should be defined and used"

    # Verify all records have proper closing braces by checking file ends properly
    lines = content.strip().split('\n')
    assert lines[-1].strip() == "}", "File should end with closing brace"


def test_inputmodule_consistency():
    """InputModule.cs has consistent structure (p2p).

    Verifies the serialization context is properly defined.
    """
    module_file = INPUT_DIR / "InputModule.cs"
    content = module_file.read_text()

    # Check that the serializer context class exists
    assert "internal partial class InputJsonSerializerContext : JsonSerializerContext" in content, \
        "InputJsonSerializerContext should be defined"

    # Check that JsonSerializable attributes are balanced
    json_serializable_count = content.count("[JsonSerializable")
    assert json_serializable_count > 0, "Should have JsonSerializable attributes"

    # Check for basic structural integrity
    assert "class InputModule" in content, "InputModule class should exist"
    assert "public async Task<PerformActionsResult> PerformActionsAsync" in content, \
        "PerformActionsAsync method should exist"


def test_repo_dotnet_format_error_only():
    """Repo's .NET code has no syntax errors (pass_to_pass).

    Uses dotnet format --severity error to verify there are no
    syntax errors or critical issues in the codebase.
    """
    webdriver_proj = REPO / "dotnet/src/webdriver/Selenium.WebDriver.csproj"
    r = subprocess.run(
        ["dotnet", "format", str(webdriver_proj), "--severity", "error", "--verify-no-changes"],
        capture_output=True, text=True, timeout=600, cwd=REPO / "dotnet/src/webdriver",
    )
    assert r.returncode == 0, f"dotnet format found syntax errors:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_repo_dotnet_restore_webdriver():
    """WebDriver project can restore NuGet packages (pass_to_pass)."""
    webdriver_proj = REPO / "dotnet/src/webdriver/Selenium.WebDriver.csproj"
    r = subprocess.run(
        ["dotnet", "restore", str(webdriver_proj)],
        capture_output=True, text=True, timeout=600, cwd=REPO / "dotnet/src/webdriver",
    )
    assert r.returncode == 0, f"dotnet restore failed:\n{r.stderr[-500:]}"


def test_repo_dotnet_restore_tests():
    """Test project can restore NuGet packages (pass_to_pass)."""
    test_proj = REPO / "dotnet/test/webdriver/Selenium.WebDriver.Tests.csproj"
    r = subprocess.run(
        ["dotnet", "restore", str(test_proj)],
        capture_output=True, text=True, timeout=600, cwd=REPO / "dotnet/test/webdriver",
    )
    assert r.returncode == 0, f"dotnet restore failed:\n{r.stderr[-500:]}"


def test_repo_dotnet_restore_support():
    """Support project can restore NuGet packages (pass_to_pass)."""
    support_proj = REPO / "dotnet/src/support/Selenium.WebDriver.Support.csproj"
    r = subprocess.run(
        ["dotnet", "restore", str(support_proj)],
        capture_output=True, text=True, timeout=600, cwd=REPO / "dotnet/src/support",
    )
    assert r.returncode == 0, f"dotnet restore failed:\n{r.stderr[-500:]}"


def test_repo_dotnet_format_bidi_input():
    """BiDi Input files pass dotnet format --severity error (pass_to_pass).

    Verifies the BiDi Input module code has no formatting errors or
    syntax issues that would fail dotnet format validation.
    """
    webdriver_proj = REPO / "dotnet/src/webdriver/Selenium.WebDriver.csproj"
    r = subprocess.run(
        [
            "dotnet", "format", str(webdriver_proj),
            "--include", "src/webdriver/BiDi/Input/*.cs",
            "--severity", "error", "--verify-no-changes"
        ],
        capture_output=True, text=True, timeout=600, cwd=REPO / "dotnet",
    )
    assert r.returncode == 0, f"dotnet format found errors in BiDi Input files:\n{r.stdout[-1000:]}\n{r.stderr[-500:]}"


def test_bidi_input_files_exist():
    """BiDi Input module files exist and are readable (pass_to_pass)."""
    source_actions = INPUT_DIR / "SourceActions.cs"
    input_module = INPUT_DIR / "InputModule.cs"
    test_file = TEST_DIR / "CombinedInputActionsTests.cs"

    assert source_actions.exists(), "SourceActions.cs should exist"
    assert input_module.exists(), "InputModule.cs should exist"
    assert test_file.exists(), "CombinedInputActionsTests.cs should exist"

    # Verify files are readable
    for f in [source_actions, input_module, test_file]:
        content = f.read_text()
        assert len(content) > 0, f"{f.name} should not be empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
