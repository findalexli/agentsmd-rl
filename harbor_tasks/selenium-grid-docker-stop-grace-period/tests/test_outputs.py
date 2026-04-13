"""
Tests for Selenium Grid Docker stop-grace-period fix.

This PR addresses two issues in DockerSession.stop():
1. No try-finally protection: if videoContainer.stop() or saveLogs() threw,
   container.stop() and super.stop() were skipped, leaking the browser container.
2. Hardcoded timeouts (60s browser, 10s video) with no way to configure them.

The fix:
1. Adds try-finally to guarantee container.stop() and super.stop() always execute
2. Adds --docker-stop-grace-period flag and stop-grace-period config option
3. Uses Duration fields instead of hardcoded values
"""

import subprocess
import re
import os

REPO = "/workspace/selenium"
DOCKER_SESSION_PATH = f"{REPO}/java/src/org/openqa/selenium/grid/node/docker/DockerSession.java"
DOCKER_OPTIONS_PATH = f"{REPO}/java/src/org/openqa/selenium/grid/node/docker/DockerOptions.java"
DOCKER_FLAGS_PATH = f"{REPO}/java/src/org/openqa/selenium/grid/node/docker/DockerFlags.java"
DOCKER_FACTORY_PATH = f"{REPO}/java/src/org/openqa/selenium/grid/node/docker/DockerSessionFactory.java"


def test_docker_session_has_try_finally():
    """DockerSession.stop() uses try-finally for guaranteed cleanup (fail-to-pass)."""
    with open(DOCKER_SESSION_PATH, 'r') as f:
        content = f.read()

    # Check for try block before video container stop
    assert "try {" in content, "Missing try block in stop() method"

    # Check for finally block containing container.stop() and super.stop()
    assert "finally {" in content, "Missing finally block in stop() method"

    # Verify the finally block has the right cleanup calls
    # The pattern: container.stop() and super.stop() must be inside finally
    finally_match = re.search(r'finally\s*\{([^}]+)\}', content, re.DOTALL)
    assert finally_match, "Could not parse finally block"
    finally_block = finally_match.group(1)

    assert "container.stop(" in finally_block, "container.stop() must be in finally block"
    assert "super.stop()" in finally_block, "super.stop() must be in finally block"


def test_docker_session_has_duration_fields():
    """DockerSession stores containerStopTimeout and videoContainerStopTimeout fields (f2p)."""
    with open(DOCKER_SESSION_PATH, 'r') as f:
        content = f.read()

    # Check for Duration fields
    assert "private final Duration containerStopTimeout" in content, \
        "Missing containerStopTimeout Duration field"
    assert "private final Duration videoContainerStopTimeout" in content, \
        "Missing videoContainerStopTimeout Duration field"


def test_docker_session_constructor_accepts_durations():
    """DockerSession constructor accepts Duration timeout parameters (f2p)."""
    with open(DOCKER_SESSION_PATH, 'r') as f:
        content = f.read()

    # Look for constructor with Duration parameters
    # The constructor signature should include Duration parameters
    constructor_pattern = r'DockerSession\([^)]*Duration\s+containerStopTimeout[^)]*Duration\s+videoContainerStopTimeout[^)]*\)'
    assert re.search(constructor_pattern, content, re.DOTALL), \
        "Constructor must accept Duration containerStopTimeout and videoContainerStopTimeout parameters"


def test_docker_session_no_hardcoded_timeouts():
    """DockerSession.stop() no longer uses hardcoded Duration values (f2p)."""
    with open(DOCKER_SESSION_PATH, 'r') as f:
        content = f.read()

    # The old code had: videoContainer.stop(Duration.ofSeconds(10))
    # and container.stop(Duration.ofMinutes(1))
    assert "Duration.ofSeconds(10)" not in content, \
        "Hardcoded 10s timeout must be replaced with configurable value"
    assert "Duration.ofMinutes(1)" not in content, \
        "Hardcoded 1m timeout must be replaced with configurable value"


def test_docker_options_has_get_stop_grace_period():
    """DockerOptions has getStopGracePeriod() method with validation (f2p)."""
    with open(DOCKER_OPTIONS_PATH, 'r') as f:
        content = f.read()

    # Check for the method
    assert "private Duration getStopGracePeriod()" in content, \
        "Missing getStopGracePeriod() method"

    # Check for DEFAULT_STOP_GRACE_PERIOD constant
    assert "DEFAULT_STOP_GRACE_PERIOD = 60" in content, \
        "Missing DEFAULT_STOP_GRACE_PERIOD constant"

    # Check for validation that throws on negative values
    assert 'stop-grace-period must be a non-negative integer' in content, \
        "Missing validation for negative stop-grace-period values"


def test_docker_options_passes_grace_period_to_factory():
    """DockerOptions passes stopGracePeriod to DockerSessionFactory (f2p)."""
    with open(DOCKER_OPTIONS_PATH, 'r') as f:
        content = f.read()

    # Check that stopGracePeriod is fetched and passed to factory
    assert "Duration stopGracePeriod = getStopGracePeriod()" in content, \
        "Must call getStopGracePeriod() and store result"
    assert "stopGracePeriod)" in content, \
        "Must pass stopGracePeriod to DockerSessionFactory constructor"


def test_docker_flags_has_stop_grace_period_parameter():
    """DockerFlags has --docker-stop-grace-period parameter (f2p)."""
    with open(DOCKER_FLAGS_PATH, 'r') as f:
        content = f.read()

    # Check for the parameter annotation
    assert '"--docker-stop-grace-period"' in content, \
        "Missing --docker-stop-grace-period parameter"

    # Check for the ConfigValue annotation with correct section/name
    assert 'name = "stop-grace-period"' in content, \
        "Missing stop-grace-period config value"

    # Check for the description
    assert "Grace period" in content and "seconds" in content, \
        "Parameter must document grace period in seconds"


def test_docker_session_factory_accepts_stop_grace_period():
    """DockerSessionFactory constructor accepts and stores stopGracePeriod (f2p)."""
    with open(DOCKER_FACTORY_PATH, 'r') as f:
        content = f.read()

    # Check for the Duration field
    assert "private final Duration stopGracePeriod" in content, \
        "Missing stopGracePeriod Duration field in DockerSessionFactory"

    # Check constructor parameter
    constructor_pattern = r'public\s+DockerSessionFactory\([^)]*Duration\s+stopGracePeriod[^)]*\)'
    assert re.search(constructor_pattern, content, re.DOTALL), \
        "DockerSessionFactory constructor must accept Duration stopGracePeriod parameter"

    # Check Require.nonNull validation
    assert 'Require.nonNull("Container stop grace period", stopGracePeriod)' in content, \
        "stopGracePeriod must be validated with Require.nonNull"


def test_docker_session_factory_passes_timeout_to_session():
    """DockerSessionFactory passes stopGracePeriod to DockerSession constructor (f2p)."""
    with open(DOCKER_FACTORY_PATH, 'r') as f:
        content = f.read()

    # The factory should pass stopGracePeriod twice (for both browser and video containers)
    # Look for the new DockerSession(...) call with stopGracePeriod passed
    assert "stopGracePeriod," in content, \
        "DockerSessionFactory must pass stopGracePeriod to DockerSession constructor"


def test_debug_uses_static_logger():
    """Debug.configureLogger() uses static SELENIUM_LOGGER for thread safety (f2p)."""
    debug_path = f"{REPO}/java/src/org/openqa/selenium/internal/Debug.java"
    with open(debug_path, 'r') as f:
        content = f.read()

    # Check for static logger field
    assert "private static final Logger SELENIUM_LOGGER" in content, \
        "Missing SELENIUM_LOGGER static field"

    # Check it's used in configureLogger instead of local variable
    assert "SELENIUM_LOGGER.setLevel(Level.FINE)" in content, \
        "Must use SELENIUM_LOGGER.setLevel() instead of local variable"
    assert "SELENIUM_LOGGER.addHandler(handler)" in content, \
        "Must use SELENIUM_LOGGER.addHandler() instead of local variable"


def test_parse_multiplexed_stream_uses_read_fully():
    """DockerSession.parseMultiplexedStream() uses readFully() instead of skipBytes() (f2p)."""
    with open(DOCKER_SESSION_PATH, 'r') as f:
        content = f.read()

    # Check for readFully usage instead of skipBytes
    assert "in.readFully(new byte[1])" in content, \
        "Must use readFully() for stream type byte instead of skipBytes()"
    assert "in.readFully(new byte[3])" in content, \
        "Must use readFully() for padding bytes instead of skipBytes()"

    # Ensure skipBytes is no longer used in this method
    method_match = re.search(
        r'private void parseMultiplexedStream\(InputStream[^}]+\}[^}]*\}',
        content,
        re.DOTALL
    )
    if method_match:
        method_body = method_match.group(0)
        # skipBytes should not appear in the parseMultiplexedStream method
        assert "skipBytes" not in method_body, \
            "skipBytes should be replaced with readFully in parseMultiplexedStream"


def test_docker_session_unit_tests_exist():
    """DockerSessionTest.java exists with comprehensive tests (pass-to-pass)."""
    test_path = f"{REPO}/java/test/org/openqa/selenium/grid/node/docker/DockerSessionTest.java"

    # Check file exists
    assert os.path.exists(test_path), \
        "DockerSessionTest.java should exist after applying the fix"

    with open(test_path, 'r') as f:
        content = f.read()

    # Check for key test methods
    assert "void stopWithVideo_videoContainerStoppedBeforeLogs()" in content, \
        "Missing test: stopWithVideo_videoContainerStoppedBeforeLogs"
    assert "void stop_browserContainerAlwaysStoppedEvenIfVideoStopFails()" in content, \
        "Missing test: stop_browserContainerAlwaysStoppedEvenIfVideoStopFails"
    assert "void stop_browserContainerStoppedEvenIfLogFetchThrows()" in content, \
        "Missing test: stop_browserContainerStoppedEvenIfLogFetchThrows"
    assert "void stop_configuredStopGracePeriodIsPassedToBothContainers()" in content, \
        "Missing test: stop_configuredStopGracePeriodIsPassedToBothContainers"


def test_bazel_build_targets_include_new_deps():
    """BUILD.bazel files include new dependencies (fail-to-pass)."""
    # Check docker test BUILD file has new deps
    docker_build_path = f"{REPO}/java/test/org/openqa/selenium/grid/node/docker/BUILD.bazel"
    with open(docker_build_path, 'r') as f:
        content = f.read()

    assert '"//java/src/org/openqa/selenium:core"' in content, \
        "BUILD.bazel missing //java/src/org/openqa/selenium:core dependency"
    assert '"//java/src/org/openqa/selenium/remote"' in content, \
        "BUILD.bazel missing //java/src/org/openqa/selenium/remote dependency"


def test_repo_bazel_build_all_docker():
    """Repo's Bazel docker library and grid targets build successfully (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "build", "//java/src/org/openqa/selenium/grid/node/docker/...", "//java/src/org/openqa/selenium/docker/..."],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Bazel docker targets build failed:\n{r.stderr[-500:]}"


def test_repo_docker_unit_tests():
    """Repo's Docker unit tests pass (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/grid/node/docker:small-tests", "--test_output=errors"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"Docker unit tests failed:\n{r.stderr[-500:]}"


def test_repo_docker_options_test():
    """Repo's DockerOptionsTest passes (pass_to_pass)."""
    r = subprocess.run(
        ["bazel", "test", "//java/test/org/openqa/selenium/grid/node/docker:DockerOptionsTest", "--test_output=errors"],
        capture_output=True, text=True, timeout=600, cwd=REPO,
    )
    assert r.returncode == 0, f"DockerOptionsTest failed:\n{r.stderr[-500:]}"
