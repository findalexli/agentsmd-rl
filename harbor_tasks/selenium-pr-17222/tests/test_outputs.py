"""
Test suite for Selenium Grid Docker stop grace period task.

This task adds:
1. Configurable --docker-stop-grace-period flag and TOML option
2. Try-finally exception safety in DockerSession.stop()
3. Fix for stream parsing (skipBytes -> readFully)
"""

import subprocess
import re
from pathlib import Path

REPO = Path("/workspace/selenium")

# === Fail-to-Pass Tests ===

def test_docker_options_has_stop_grace_period_constant():
    """DockerOptions defines DEFAULT_STOP_GRACE_PERIOD constant (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java").read_text()

    # Must have the constant defined
    assert "DEFAULT_STOP_GRACE_PERIOD" in source, "Missing DEFAULT_STOP_GRACE_PERIOD constant"

    # Check it's a static final int with value 60
    pattern = r'static\s+final\s+int\s+DEFAULT_STOP_GRACE_PERIOD\s*=\s*60\s*;'
    assert re.search(pattern, source), "DEFAULT_STOP_GRACE_PERIOD must be static final int = 60"


def test_docker_options_has_get_stop_grace_period_method():
    """DockerOptions has getStopGracePeriod() method (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java").read_text()

    # Must have the method
    assert "getStopGracePeriod" in source, "Missing getStopGracePeriod method"

    # Method should return Duration
    pattern = r'private\s+Duration\s+getStopGracePeriod\s*\(\s*\)'
    assert re.search(pattern, source), "getStopGracePeriod must return Duration"

    # Method should validate non-negative
    assert 'stop-grace-period must be a non-negative' in source, "Missing validation for non-negative value"


def test_docker_flags_has_stop_grace_period_parameter():
    """DockerFlags defines --docker-stop-grace-period CLI parameter (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java").read_text()

    # Must have the flag name
    assert "--docker-stop-grace-period" in source, "Missing --docker-stop-grace-period flag"

    # Must have ConfigValue annotation with correct section and name
    assert 'name = "stop-grace-period"' in source, "Missing ConfigValue name for stop-grace-period"

    # Must have description mentioning grace period
    assert "Grace period" in source or "grace period" in source, "Missing description for grace period flag"


def test_docker_session_has_timeout_fields():
    """DockerSession has containerStopTimeout and videoContainerStopTimeout fields (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Must have both timeout fields
    assert "containerStopTimeout" in source, "Missing containerStopTimeout field"
    assert "videoContainerStopTimeout" in source, "Missing videoContainerStopTimeout field"

    # Fields should be Duration type
    pattern_container = r'private\s+final\s+Duration\s+containerStopTimeout'
    pattern_video = r'private\s+final\s+Duration\s+videoContainerStopTimeout'
    assert re.search(pattern_container, source), "containerStopTimeout must be private final Duration"
    assert re.search(pattern_video, source), "videoContainerStopTimeout must be private final Duration"


def test_docker_session_constructor_accepts_timeouts():
    """DockerSession constructor accepts timeout Duration parameters (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Find the DockerSession constructor
    # Should have Duration containerStopTimeout and Duration videoContainerStopTimeout parameters
    assert "Duration containerStopTimeout" in source, "Constructor missing containerStopTimeout parameter"
    assert "Duration videoContainerStopTimeout" in source, "Constructor missing videoContainerStopTimeout parameter"

    # Should initialize the fields with Require.nonNull
    assert 'Require.nonNull("Container stop timeout", containerStopTimeout)' in source, \
        "Missing null check for containerStopTimeout"
    assert 'Require.nonNull("Video container stop timeout", videoContainerStopTimeout)' in source, \
        "Missing null check for videoContainerStopTimeout"


def test_docker_session_stop_uses_try_finally():
    """DockerSession.stop() uses try-finally for exception safety (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Look for the method signature followed by try block
    stop_with_try_pattern = r'public\s+void\s+stop\s*\(\s*\)\s*\{\s*try\s*\{'
    assert re.search(stop_with_try_pattern, source, re.DOTALL), "stop() method should have try block"

    # Find the stop() method position
    stop_pos = source.find("public void stop()")
    assert stop_pos != -1, "Could not find stop() method"

    # Look at the code after stop() up to saveLogs() method (next method)
    savelogs_pos = source.find("private void saveLogs()")
    if savelogs_pos == -1:
        savelogs_pos = len(source)

    stop_section = source[stop_pos:savelogs_pos]

    # Must have finally block
    assert "finally {" in stop_section or "finally{" in stop_section, "stop() method missing finally block"

    # finally block should contain container.stop
    finally_pos = stop_section.find("finally")
    container_stop_after_finally = stop_section[finally_pos:].find("container.stop")
    assert container_stop_after_finally != -1, "container.stop must be in finally block"


def test_docker_session_stop_uses_configurable_timeout():
    """DockerSession.stop() uses configured timeout instead of hardcoded value (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Find the stop() method position
    stop_pos = source.find("public void stop()")
    assert stop_pos != -1, "Could not find stop() method"

    # Look at the code after stop() up to saveLogs() method (next method)
    savelogs_pos = source.find("private void saveLogs()")
    if savelogs_pos == -1:
        savelogs_pos = len(source)

    stop_section = source[stop_pos:savelogs_pos]

    # Should NOT have hardcoded Duration.ofMinutes(1) or Duration.ofSeconds(60) in stop()
    assert "Duration.ofMinutes(1)" not in stop_section, "stop() should not use hardcoded Duration.ofMinutes(1)"
    assert "Duration.ofSeconds(60)" not in stop_section, "stop() should not use hardcoded Duration.ofSeconds(60)"
    assert "Duration.ofSeconds(10)" not in stop_section, "stop() should not use hardcoded Duration.ofSeconds(10)"

    # Should use the configurable timeout fields
    assert "containerStopTimeout" in stop_section, "stop() should use containerStopTimeout"
    assert "videoContainerStopTimeout" in stop_section, "stop() should use videoContainerStopTimeout"


def test_docker_session_factory_has_stop_grace_period():
    """DockerSessionFactory has stopGracePeriod field and passes it to DockerSession (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java").read_text()

    # Must have the field
    assert "stopGracePeriod" in source, "Missing stopGracePeriod field"

    # Field should be Duration type
    pattern = r'private\s+final\s+Duration\s+stopGracePeriod'
    assert re.search(pattern, source), "stopGracePeriod must be private final Duration"

    # Constructor should accept Duration stopGracePeriod parameter
    assert "Duration stopGracePeriod" in source, "Constructor missing stopGracePeriod parameter"

    # Should have null check
    assert 'Require.nonNull("Container stop grace period", stopGracePeriod)' in source, \
        "Missing null check for stopGracePeriod"


def test_docker_session_uses_read_fully_not_skip_bytes():
    """DockerSession.parseMultiplexedStream uses readFully instead of skipBytes (fail_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Find parseMultiplexedStream method
    parse_pattern = r'private\s+void\s+parseMultiplexedStream[^{]+\{([^}]+(?:\{[^}]*\}[^}]*)*)\}'
    match = re.search(parse_pattern, source, re.DOTALL)
    assert match, "Could not find parseMultiplexedStream method"

    parse_body = match.group(1)

    # Should NOT use skipBytes - this is the bug being fixed
    assert "skipBytes" not in parse_body, "parseMultiplexedStream should not use skipBytes (causes data loss)"

    # Should use readFully for reading the header bytes
    assert "readFully" in parse_body, "parseMultiplexedStream should use readFully to properly read bytes"


# === Pass-to-Pass Tests ===

def test_java_source_compiles_syntax_check():
    """Java source files have valid syntax (pass_to_pass)."""
    files = [
        "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java",
        "java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java",
        "java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java",
        "java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java",
    ]

    for f in files:
        path = REPO / f
        assert path.exists(), f"Source file missing: {f}"
        content = path.read_text()

        # Basic structural integrity checks
        assert content.count('{') == content.count('}'), f"Unbalanced braces in {f}"
        assert content.count('(') == content.count(')'), f"Unbalanced parentheses in {f}"

        # Must have a package declaration
        assert "package org.openqa.selenium" in content, f"Missing package declaration in {f}"

        # Must have a class, interface, or enum definition
        import_keywords = ("public class ", "public interface ", "public enum ",
                           "class ", "interface ", "enum ")
        assert any(kw in content for kw in import_keywords), f"No class/interface/enum definition in {f}"

        # Check no unclosed string literals on any non-comment line
        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if stripped.startswith('//') or stripped.startswith('*') or stripped.startswith('/*'):
                continue
            dq_count = stripped.count('"') - stripped.count('\\"')
            assert dq_count % 2 == 0, f"Unbalanced double quotes on line {i} in {f}"


def test_docker_session_preserves_existing_fields():
    """DockerSession preserves existing container and assetsPath fields (pass_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Must preserve existing fields
    assert "private final Container container" in source, "Missing container field"
    assert "private final @Nullable Container videoContainer" in source or \
           "private final Container videoContainer" in source, "Missing videoContainer field"
    assert "private final DockerAssetsPath assetsPath" in source, "Missing assetsPath field"


def test_docker_session_calls_super_stop():
    """DockerSession.stop() calls super.stop() (pass_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    # Must call super.stop()
    assert "super.stop()" in source, "stop() must call super.stop()"


def test_docker_options_imports_duration():
    """DockerOptions imports java.time.Duration (pass_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java").read_text()

    assert "import java.time.Duration" in source, "Missing Duration import"


def test_docker_session_imports_duration():
    """DockerSession imports java.time.Duration (pass_to_pass)."""
    source = (REPO / "java/src/org/openqa/selenium/grid/node/docker/DockerSession.java").read_text()

    assert "import java.time.Duration" in source, "Missing Duration import"


# === Real CI Tests (subprocess-based) ===

def test_repo_bazel_build_docker_module():
    """Bazel build of docker module succeeds (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/grid/node/docker:docker"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel build failed:\n{r.stderr[-2000:]}"


def test_repo_docker_options_unit_test():
    """Repo's DockerOptionsTest unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/grid/node/docker:DockerOptionsTest"],
        capture_output=True,
        text=True,
        timeout=600,
        cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel test failed:\n{r.stderr[-2000:]}"
