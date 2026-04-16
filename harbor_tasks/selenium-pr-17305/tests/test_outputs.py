"""
Tests for Selenium .NET DevTools lazy initialization fix.

The bug: Each access to Network, JavaScript, Target, Log properties creates a new
instance, causing lifecycle issues with event subscriptions and unnecessary allocations.

The fix: Use Lazy<T> fields to cache instances on first access, returning the same
instance on subsequent accesses.
"""
import re
import subprocess
from pathlib import Path

REPO = Path("/workspace/selenium")
DOTNET_DIR = REPO / "dotnet"
DEVTOOLS_DIR = DOTNET_DIR / "src" / "webdriver" / "DevTools"

# Domain versions to test - pattern is consistent across all versions
DOMAIN_VERSIONS = ["v143", "v144", "v145"]
DOMAIN_PROPERTIES = ["Network", "JavaScript", "Target", "Log"]


def read_file(filepath: Path) -> str:
    """Read file content."""
    return filepath.read_text()


# =============================================================================
# FAIL-TO-PASS TESTS - These must fail on base commit, pass after fix
# =============================================================================


def test_v143_has_lazy_network_field():
    """V143Domains declares Lazy<V143Network> field (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    # Must have: private readonly Lazy<V143Network> network;
    pattern = r"private\s+readonly\s+Lazy<V143Network>\s+network\s*;"
    assert re.search(pattern, content), (
        "V143Domains.cs must declare 'private readonly Lazy<V143Network> network;' field"
    )


def test_v143_has_lazy_javascript_field():
    """V143Domains declares Lazy<V143JavaScript> field (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    pattern = r"private\s+readonly\s+Lazy<V143JavaScript>\s+javaScript\s*;"
    assert re.search(pattern, content), (
        "V143Domains.cs must declare 'private readonly Lazy<V143JavaScript> javaScript;' field"
    )


def test_v143_has_lazy_target_field():
    """V143Domains declares Lazy<V143Target> field (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    pattern = r"private\s+readonly\s+Lazy<V143Target>\s+target\s*;"
    assert re.search(pattern, content), (
        "V143Domains.cs must declare 'private readonly Lazy<V143Target> target;' field"
    )


def test_v143_has_lazy_log_field():
    """V143Domains declares Lazy<V143Log> field (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    pattern = r"private\s+readonly\s+Lazy<V143Log>\s+log\s*;"
    assert re.search(pattern, content), (
        "V143Domains.cs must declare 'private readonly Lazy<V143Log> log;' field"
    )


def test_v143_network_property_uses_lazy_value():
    """V143Domains.Network property returns lazy value (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    # Property should use: this.network.Value or network.Value, not "new V143Network(...)"
    # Check for the pattern: Network => ... .Value
    pattern = r"Network\s*=>\s*(?:this\.)?network\.Value"
    assert re.search(pattern, content), (
        "V143Domains.Network property must return 'this.network.Value' instead of creating new instance"
    )


def test_v143_javascript_property_uses_lazy_value():
    """V143Domains.JavaScript property returns lazy value (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    pattern = r"JavaScript\s*=>\s*(?:this\.)?javaScript\.Value"
    assert re.search(pattern, content), (
        "V143Domains.JavaScript property must return 'this.javaScript.Value' instead of creating new instance"
    )


def test_v143_target_property_uses_lazy_value():
    """V143Domains.Target property returns lazy value (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    pattern = r"Target\s*=>\s*(?:this\.)?target\.Value"
    assert re.search(pattern, content), (
        "V143Domains.Target property must return 'this.target.Value' instead of creating new instance"
    )


def test_v143_log_property_uses_lazy_value():
    """V143Domains.Log property returns lazy value (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")
    pattern = r"Log\s*=>\s*(?:this\.)?log\.Value"
    assert re.search(pattern, content), (
        "V143Domains.Log property must return 'this.log.Value' instead of creating new instance"
    )


def test_v144_implements_lazy_pattern():
    """V144Domains implements lazy initialization for all domain properties (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v144" / "V144Domains.cs")

    # Check all four lazy fields exist
    fields = [
        (r"private\s+readonly\s+Lazy<V144Network>\s+network\s*;", "network"),
        (r"private\s+readonly\s+Lazy<V144JavaScript>\s+javaScript\s*;", "javaScript"),
        (r"private\s+readonly\s+Lazy<V144Target>\s+target\s*;", "target"),
        (r"private\s+readonly\s+Lazy<V144Log>\s+log\s*;", "log"),
    ]

    for pattern, name in fields:
        assert re.search(pattern, content), f"V144Domains.cs must declare Lazy<...> {name} field"

    # Check all properties use .Value
    props = [
        (r"Network\s*=>\s*(?:this\.)?network\.Value", "Network"),
        (r"JavaScript\s*=>\s*(?:this\.)?javaScript\.Value", "JavaScript"),
        (r"Target\s*=>\s*(?:this\.)?target\.Value", "Target"),
        (r"Log\s*=>\s*(?:this\.)?log\.Value", "Log"),
    ]

    for pattern, name in props:
        assert re.search(pattern, content), f"V144Domains.{name} property must return lazy value"


def test_v145_implements_lazy_pattern():
    """V145Domains implements lazy initialization for all domain properties (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v145" / "V145Domains.cs")

    # Check all four lazy fields exist
    fields = [
        (r"private\s+readonly\s+Lazy<V145Network>\s+network\s*;", "network"),
        (r"private\s+readonly\s+Lazy<V145JavaScript>\s+javaScript\s*;", "javaScript"),
        (r"private\s+readonly\s+Lazy<V145Target>\s+target\s*;", "target"),
        (r"private\s+readonly\s+Lazy<V145Log>\s+log\s*;", "log"),
    ]

    for pattern, name in fields:
        assert re.search(pattern, content), f"V145Domains.cs must declare Lazy<...> {name} field"

    # Check all properties use .Value
    props = [
        (r"Network\s*=>\s*(?:this\.)?network\.Value", "Network"),
        (r"JavaScript\s*=>\s*(?:this\.)?javaScript\.Value", "JavaScript"),
        (r"Target\s*=>\s*(?:this\.)?target\.Value", "Target"),
        (r"Log\s*=>\s*(?:this\.)?log\.Value", "Log"),
    ]

    for pattern, name in props:
        assert re.search(pattern, content), f"V145Domains.{name} property must return lazy value"


def test_v143_constructor_initializes_lazy_fields():
    """V143Domains constructor initializes all lazy fields with factory lambdas (fail_to_pass)."""
    content = read_file(DEVTOOLS_DIR / "v143" / "V143Domains.cs")

    # Check constructor initializes lazy fields
    patterns = [
        r"this\.network\s*=\s*new\s+Lazy<V143Network>\s*\(\s*\(\s*\)\s*=>\s*new\s+V143Network",
        r"this\.javaScript\s*=\s*new\s+Lazy<V143JavaScript>\s*\(\s*\(\s*\)\s*=>\s*new\s+V143JavaScript",
        r"this\.target\s*=\s*new\s+Lazy<V143Target>\s*\(\s*\(\s*\)\s*=>\s*new\s+V143Target",
        r"this\.log\s*=\s*new\s+Lazy<V143Log>\s*\(\s*\(\s*\)\s*=>\s*new\s+V143Log",
    ]

    for pattern in patterns:
        assert re.search(pattern, content), (
            f"V143Domains constructor must initialize lazy fields with factory lambdas"
        )


def test_no_new_instance_in_property_getter():
    """Domain properties must NOT create new instances directly (fail_to_pass)."""
    for version in DOMAIN_VERSIONS:
        filepath = DEVTOOLS_DIR / version / f"{version.upper()}Domains.cs"
        content = read_file(filepath)

        # These patterns indicate the BUG - creating new instance on each access
        # Property syntax: PropertyName => new TypeName(...)
        bug_patterns = [
            rf"Network\s*=>\s*new\s+{version.upper()}Network\s*\(",
            rf"JavaScript\s*=>\s*new\s+{version.upper()}JavaScript\s*\(",
            rf"Target\s*=>\s*new\s+{version.upper()}Target\s*\(",
            rf"Log\s*=>\s*new\s+{version.upper()}Log\s*\(",
        ]

        for pattern in bug_patterns:
            assert not re.search(pattern, content), (
                f"{version.upper()}Domains.cs still creates new instances in property getters - "
                f"must use lazy initialization instead"
            )


# =============================================================================
# PASS-TO-PASS TESTS - These should pass both before and after the fix
# =============================================================================


def test_domain_files_exist():
    """All version-specific domain files exist (pass_to_pass)."""
    for version in DOMAIN_VERSIONS:
        filepath = DEVTOOLS_DIR / version / f"{version.upper()}Domains.cs"
        assert filepath.exists(), f"Missing domain file: {filepath}"


def test_domain_classes_have_required_properties():
    """Domain classes expose Network, JavaScript, Target, Log properties (pass_to_pass)."""
    for version in DOMAIN_VERSIONS:
        filepath = DEVTOOLS_DIR / version / f"{version.upper()}Domains.cs"
        content = read_file(filepath)

        for prop in DOMAIN_PROPERTIES:
            # Check property declaration exists
            pattern = rf"public\s+override\s+\S+\s+{prop}\s*=>"
            assert re.search(pattern, content), (
                f"{version.upper()}Domains.cs must have 'public override ... {prop}' property"
            )


def test_domain_classes_extend_devtools_domains():
    """All version domain classes extend DevToolsDomains base class (pass_to_pass)."""
    for version in DOMAIN_VERSIONS:
        filepath = DEVTOOLS_DIR / version / f"{version.upper()}Domains.cs"
        content = read_file(filepath)

        class_name = f"{version.upper()}Domains"
        pattern = rf"public\s+class\s+{class_name}\s*:\s*DevToolsDomains"
        assert re.search(pattern, content), (
            f"{class_name} must extend DevToolsDomains base class"
        )


def test_domain_classes_have_constructor_with_session():
    """Domain classes have constructor accepting DevToolsSession (pass_to_pass)."""
    for version in DOMAIN_VERSIONS:
        filepath = DEVTOOLS_DIR / version / f"{version.upper()}Domains.cs"
        content = read_file(filepath)

        class_name = f"{version.upper()}Domains"
        pattern = rf"public\s+{class_name}\s*\(\s*DevToolsSession\s+session\s*\)"
        assert re.search(pattern, content), (
            f"{class_name} must have constructor accepting DevToolsSession"
        )


def test_csharp_syntax_valid():
    """C# files have valid syntax - no obvious syntax errors (pass_to_pass)."""
    for version in DOMAIN_VERSIONS:
        filepath = DEVTOOLS_DIR / version / f"{version.upper()}Domains.cs"
        content = read_file(filepath)

        # Basic syntax checks - balanced braces
        open_braces = content.count("{")
        close_braces = content.count("}")
        assert open_braces == close_braces, (
            f"{filepath.name} has unbalanced braces: {open_braces} open, {close_braces} close"
        )

        # Check for namespace declaration
        assert re.search(r"namespace\s+OpenQA\.Selenium\.DevTools\.", content), (
            f"{filepath.name} must be in OpenQA.Selenium.DevTools namespace"
        )


# =============================================================================
# PASS-TO-PASS TESTS - Repo CI commands that should pass before and after fix
# =============================================================================

# Target only the modified VxxxDomains.cs files, not the whole DevTools directory
MODIFIED_FILES = [
    "src/webdriver/DevTools/v143/V143Domains.cs",
    "src/webdriver/DevTools/v144/V144Domains.cs",
    "src/webdriver/DevTools/v145/V145Domains.cs",
]


def test_repo_dotnet_format_whitespace():
    """Modified Domains files pass dotnet whitespace formatting check (pass_to_pass)."""
    cmd = [
        "dotnet", "format", "whitespace",
        "src/webdriver/Selenium.WebDriver.csproj",
        "--verify-no-changes",
        "--no-restore",
    ]
    for f in MODIFIED_FILES:
        cmd.extend(["--include", f])
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=DOTNET_DIR,
    )
    assert r.returncode == 0, f"dotnet format whitespace failed:\n{r.stderr[-1000:]}"


def test_repo_dotnet_format_style():
    """Modified Domains files pass dotnet style formatting check (pass_to_pass)."""
    cmd = [
        "dotnet", "format", "style",
        "src/webdriver/Selenium.WebDriver.csproj",
        "--verify-no-changes",
        "--no-restore",
    ]
    for f in MODIFIED_FILES:
        cmd.extend(["--include", f])
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=DOTNET_DIR,
    )
    assert r.returncode == 0, f"dotnet format style failed:\n{r.stderr[-1000:]}"


def test_repo_dotnet_format_analyzers():
    """Modified Domains files pass dotnet analyzer checks (pass_to_pass)."""
    cmd = [
        "dotnet", "format", "analyzers",
        "src/webdriver/Selenium.WebDriver.csproj",
        "--verify-no-changes",
        "--no-restore",
    ]
    for f in MODIFIED_FILES:
        cmd.extend(["--include", f])
    r = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=DOTNET_DIR,
    )
    assert r.returncode == 0, f"dotnet format analyzers failed:\n{r.stderr[-1000:]}"
