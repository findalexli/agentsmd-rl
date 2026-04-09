#!/usr/bin/env python3
"""
Test outputs for Selenium CDP Domain Lifecycle fix.

This verifies that V143Domains, V144Domains, and V145Domains use lazy initialization
for their Network, JavaScript, Target, and Log properties to ensure the same
instance is returned on multiple accesses.
"""

import subprocess
import sys
import re
from pathlib import Path

REPO = Path("/workspace/selenium")


def test_v143domains_has_lazy_fields():
    """V143Domains class has Lazy<T> fields for network, javaScript, target, log."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v143/V143Domains.cs"
    content = source_file.read_text()

    assert "private readonly Lazy<V143Network> network" in content, "Missing lazy network field in V143Domains"
    assert "private readonly Lazy<V143JavaScript> javaScript" in content, "Missing lazy javaScript field in V143Domains"
    assert "private readonly Lazy<V143Target> target" in content, "Missing lazy target field in V143Domains"
    assert "private readonly Lazy<V143Log> log" in content, "Missing lazy log field in V143Domains"


def test_v144domains_has_lazy_fields():
    """V144Domains class has Lazy<T> fields for network, javaScript, target, log."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v144/V144Domains.cs"
    content = source_file.read_text()

    assert "private readonly Lazy<V144Network> network" in content, "Missing lazy network field in V144Domains"
    assert "private readonly Lazy<V144JavaScript> javaScript" in content, "Missing lazy javaScript field in V144Domains"
    assert "private readonly Lazy<V144Target> target" in content, "Missing lazy target field in V144Domains"
    assert "private readonly Lazy<V144Log> log" in content, "Missing lazy log field in V144Domains"


def test_v145domains_has_lazy_fields():
    """V145Domains class has Lazy<T> fields for network, javaScript, target, log."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v145/V145Domains.cs"
    content = source_file.read_text()

    assert "private readonly Lazy<V145Network> network" in content, "Missing lazy network field in V145Domains"
    assert "private readonly Lazy<V145JavaScript> javaScript" in content, "Missing lazy javaScript field in V145Domains"
    assert "private readonly Lazy<V145Target> target" in content, "Missing lazy target field in V145Domains"
    assert "private readonly Lazy<V145Log> log" in content, "Missing lazy log field in V145Domains"


def test_v143domains_lazy_initialized_in_constructor():
    """V143Domains constructor initializes Lazy fields with correct factory lambdas."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v143/V143Domains.cs"
    content = source_file.read_text()

    # Check that constructor initializes all Lazy fields
    assert "this.network = new Lazy<V143Network>(() => new V143Network(domains.Network, domains.Fetch))" in content
    assert "this.javaScript = new Lazy<V143JavaScript>(() => new V143JavaScript(domains.Runtime, domains.Page))" in content
    assert "this.target = new Lazy<V143Target>(() => new V143Target(domains.Target))" in content
    assert "this.log = new Lazy<V143Log>(() => new V143Log(domains.Log))" in content


def test_v144domains_lazy_initialized_in_constructor():
    """V144Domains constructor initializes Lazy fields with correct factory lambdas."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v144/V144Domains.cs"
    content = source_file.read_text()

    # Check that constructor initializes all Lazy fields
    assert "this.network = new Lazy<V144Network>(() => new V144Network(domains.Network, domains.Fetch))" in content
    assert "this.javaScript = new Lazy<V144JavaScript>(() => new V144JavaScript(domains.Runtime, domains.Page))" in content
    assert "this.target = new Lazy<V144Target>(() => new V144Target(domains.Target))" in content
    assert "this.log = new Lazy<V144Log>(() => new V144Log(domains.Log))" in content


def test_v145domains_lazy_initialized_in_constructor():
    """V145Domains constructor initializes Lazy fields with correct factory lambdas."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v145/V145Domains.cs"
    content = source_file.read_text()

    # Check that constructor initializes all Lazy fields
    assert "this.network = new Lazy<V145Network>(() => new V145Network(domains.Network, domains.Fetch))" in content
    assert "this.javaScript = new Lazy<V145JavaScript>(() => new V145JavaScript(domains.Runtime, domains.Page))" in content
    assert "this.target = new Lazy<V145Target>(() => new V145Target(domains.Target))" in content
    assert "this.log = new Lazy<V145Log>(() => new V145Log(domains.Log))" in content


def test_v143domains_properties_return_lazy_value():
    """V143Domains properties return cached Lazy value instead of new instances."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v143/V143Domains.cs"
    content = source_file.read_text()

    # Properties should return this.field.Value, not create new instances
    assert "public override DevTools.Network Network => this.network.Value" in content
    assert "public override JavaScript JavaScript => this.javaScript.Value" in content
    assert "public override DevTools.Target Target => this.target.Value" in content
    assert "public override DevTools.Log Log => this.log.Value" in content

    # Should NOT have the old pattern of creating new instances
    assert "Network => new V143Network" not in content
    assert "JavaScript => new V143JavaScript" not in content
    assert "Target => new V143Target" not in content
    assert "Log => new V143Log" not in content


def test_v144domains_properties_return_lazy_value():
    """V144Domains properties return cached Lazy value instead of new instances."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v144/V144Domains.cs"
    content = source_file.read_text()

    # Properties should return this.field.Value, not create new instances
    assert "public override DevTools.Network Network => this.network.Value" in content
    assert "public override JavaScript JavaScript => this.javaScript.Value" in content
    assert "public override DevTools.Target Target => this.target.Value" in content
    assert "public override DevTools.Log Log => this.log.Value" in content

    # Should NOT have the old pattern of creating new instances
    assert "Network => new V144Network" not in content
    assert "JavaScript => new V144JavaScript" not in content
    assert "Target => new V144Target" not in content
    assert "Log => new V144Log" not in content


def test_v145domains_properties_return_lazy_value():
    """V145Domains properties return cached Lazy value instead of new instances."""
    source_file = REPO / "dotnet/src/webdriver/DevTools/v145/V145Domains.cs"
    content = source_file.read_text()

    # Properties should return this.field.Value, not create new instances
    assert "public override DevTools.Network Network => this.network.Value" in content
    assert "public override JavaScript JavaScript => this.javaScript.Value" in content
    assert "public override DevTools.Target Target => this.target.Value" in content
    assert "public override DevTools.Log Log => this.log.Value" in content

    # Should NOT have the old pattern of creating new instances
    assert "Network => new V145Network" not in content
    assert "JavaScript => new V145JavaScript" not in content
    assert "Target => new V145Target" not in content
    assert "Log => new V145Log" not in content


def test_devtools_domains_tests_file_exists():
    """DevToolsDomainsTests.cs test file exists with proper content."""
    test_file = REPO / "dotnet/test/webdriver/DevTools/DevToolsDomainsTests.cs"
    assert test_file.exists(), "DevToolsDomainsTests.cs should be created"

    content = test_file.read_text()

    # Check for the SameAs assertions that verify instance caching
    assert "Is.SameAs(domains.Log)" in content
    assert "Is.SameAs(domains.Network)" in content
    assert "Is.SameAs(domains.Target)" in content
    assert "Is.SameAs(domains.JavaScript)" in content


def test_dotnet_syntax_valid():
    """C# source files have valid syntax with proper type consistency."""
    # Check that all three V*Domains.cs files have proper Lazy field types
    for version in ["v143", "v144", "v145"]:
        version_num = version.replace("v", "")
        source_file = REPO / f"dotnet/src/webdriver/DevTools/{version}/V{version_num}Domains.cs"
        content = source_file.read_text()

        # Basic syntax checks
        assert "class" in content, f"Missing class keyword in V{version_num}Domains.cs"
        assert "{" in content, f"Missing opening braces in V{version_num}Domains.cs"
        assert "}" in content, f"Missing closing braces in V{version_num}Domains.cs"

        # Check that all Lazy fields are properly typed (no cross-version mixing)
        assert f"Lazy<V{version_num}Network>" in content, f"Missing or incorrect Lazy<V{version_num}Network> in {version}"
        assert f"Lazy<V{version_num}JavaScript>" in content, f"Missing or incorrect Lazy<V{version_num}JavaScript> in {version}"
        assert f"Lazy<V{version_num}Target>" in content, f"Missing or incorrect Lazy<V{version_num}Target> in {version}"
        assert f"Lazy<V{version_num}Log>" in content, f"Missing or incorrect Lazy<V{version_num}Log> in {version}"


def test_cs_files_balanced_braces():
    """C# source files have balanced braces (pass_to_pass)."""
    for version in ["v143", "v144", "v145"]:
        version_num = version.replace("v", "")
        source_file = REPO / f"dotnet/src/webdriver/DevTools/{version}/V{version_num}Domains.cs"
        content = source_file.read_text()

        open_braces = content.count("{")
        close_braces = content.count("}")
        open_parens = content.count("(")
        close_parens = content.count(")")
        open_brackets = content.count("[")
        close_brackets = content.count("]")

        assert open_braces == close_braces, (
            f"Unbalanced braces in V{version_num}Domains.cs: "
            f"{open_braces} open, {close_braces} close"
        )
        assert open_parens == close_parens, (
            f"Unbalanced parentheses in V{version_num}Domains.cs: "
            f"{open_parens} open, {close_parens} close"
        )
        assert open_brackets == close_brackets, (
            f"Unbalanced brackets in V{version_num}Domains.cs: "
            f"{open_brackets} open, {close_brackets} close"
        )


def test_cs_files_valid_identifiers():
    """C# source files use valid C# identifiers (pass_to_pass)."""
    import re

    # Basic C# identifier pattern (simplified)
    identifier_pattern = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')

    for version in ["v143", "v144", "v145"]:
        version_num = version.replace("v", "")
        source_file = REPO / f"dotnet/src/webdriver/DevTools/{version}/V{version_num}Domains.cs"
        content = source_file.read_text()

        # Check class name follows conventions
        class_match = re.search(r'class\s+(V\d+Domains)', content)
        assert class_match is not None, f"Class declaration not found in V{version_num}Domains.cs"
        class_name = class_match.group(1)
        assert class_name == f"V{version_num}Domains", (
            f"Class name mismatch in {version}: expected V{version_num}Domains, got {class_name}"
        )

        # Check namespace follows conventions
        ns_match = re.search(r'namespace\s+OpenQA\.Selenium\.DevTools\.(V\d+)', content)
        assert ns_match is not None, f"Namespace declaration not found in V{version_num}Domains.cs"
        ns_version = ns_match.group(1)
        assert ns_version == f"V{version_num}", (
            f"Namespace version mismatch in {version}: expected V{version_num}, got {ns_version}"
        )


def test_cs_files_no_syntax_errors():
    """C# source files have no obvious syntax errors (pass_to_pass)."""
    for version in ["v143", "v144", "v145"]:
        version_num = version.replace("v", "")
        source_file = REPO / f"dotnet/src/webdriver/DevTools/{version}/V{version_num}Domains.cs"
        content = source_file.read_text()

        # Check for common syntax issues
        assert ";;" not in content, f"Double semicolon found in V{version_num}Domains.cs"

        # Check all string literals are properly closed (basic check)
        quote_count = content.count('"')
        # Note: This is a heuristic - doesn't handle escaped quotes
        # but works for our specific files

        # Check class has proper inheritance
        assert "class V{}Domains : DevToolsDomains".format(version_num) in content, (
            f"Class inheritance declaration missing or malformed in V{version_num}Domains.cs"
        )

        # Check constructor exists with proper signature
        expected_ctor = f"public V{version_num}Domains(DevToolsSession session)"
        assert expected_ctor in content, (
            f"Constructor with correct signature not found in V{version_num}Domains.cs"
        )


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
