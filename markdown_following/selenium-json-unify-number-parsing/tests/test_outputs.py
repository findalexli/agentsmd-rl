"""Behavioral verification for selenium-json-unify-number-parsing task.

Each test invokes the agent's modified Selenium json package via javac/java.
Compilation runs once at module level; individual tests dispatch to a shared
JsonTaskTest driver via reflection on a method name.
"""

import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path("/workspace/selenium")
JSON_SRC = REPO / "java/src/org/openqa/selenium/json"
LIBS = "/workspace/libs/selenium-api-4.41.0.jar:/workspace/libs/jspecify-1.0.0.jar"
JSON_OUT = Path("/tmp/json-classes")
TEST_OUT = Path("/tmp/test-classes")
DRIVER_SRC = Path("/tests/JsonTaskTest.java")


def _run(cmd, **kw):
    """Run a subprocess and return CompletedProcess. Always capture text output."""
    return subprocess.run(cmd, capture_output=True, text=True, timeout=300, **kw)


@pytest.fixture(scope="session")
def json_compiled():
    """Compile the (possibly modified) Selenium json package once per session."""
    if JSON_OUT.exists():
        shutil.rmtree(JSON_OUT)
    JSON_OUT.mkdir(parents=True)
    sources = sorted(str(p) for p in JSON_SRC.glob("*.java"))
    if not sources:
        pytest.fail(f"No .java files found in {JSON_SRC}")
    r = _run(["javac", "-d", str(JSON_OUT), "-cp", LIBS, *sources])
    if r.returncode != 0:
        pytest.fail(
            f"json package failed to compile (exit {r.returncode}):\n{r.stderr[-2000:]}"
        )
    return JSON_OUT


@pytest.fixture(scope="session")
def driver_compiled(json_compiled):
    """Compile JsonTaskTest.java against the agent-built json classes."""
    if TEST_OUT.exists():
        shutil.rmtree(TEST_OUT)
    TEST_OUT.mkdir(parents=True)
    cp = f"{LIBS}:{json_compiled}"
    r = _run(["javac", "-d", str(TEST_OUT), "-cp", cp, str(DRIVER_SRC)])
    if r.returncode != 0:
        pytest.fail(
            f"JsonTaskTest.java failed to compile (exit {r.returncode}):\n{r.stderr[-2000:]}"
        )
    return TEST_OUT


def _invoke(json_compiled, driver_compiled, method):
    cp = f"{LIBS}:{json_compiled}:{driver_compiled}"
    return _run(["java", "-cp", cp, "selenium.tasktest.JsonTaskTest", method])


# --- pass-to-pass ---


def test_json_package_compiles(json_compiled):
    """The agent's modified json package compiles against the published api jar."""
    assert json_compiled.exists()
    classes = list(json_compiled.rglob("*.class"))
    assert len(classes) >= 20, f"expected the full json package to compile, got {len(classes)} classes"


def test_can_read_boolean(json_compiled, driver_compiled):
    r = _invoke(json_compiled, driver_compiled, "canReadBoolean")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_can_read_integer_and_double(json_compiled, driver_compiled):
    r = _invoke(json_compiled, driver_compiled, "canReadIntegerAndDouble")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_can_read_iso_instant_string(json_compiled, driver_compiled):
    r = _invoke(json_compiled, driver_compiled, "canReadIsoInstantString")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_can_round_trip_map(json_compiled, driver_compiled):
    r = _invoke(json_compiled, driver_compiled, "canRoundTripMap")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


# --- fail-to-pass ---


def test_parse_very_negative_exponential_not_clamped_to_long(json_compiled, driver_compiled):
    """Coercing a number whose magnitude exceeds Long range (e.g., -1e20)
    must not silently clamp to Long.MIN_VALUE."""
    r = _invoke(
        json_compiled, driver_compiled, "parseVeryNegativeExponentialNotClampedToLong"
    )
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_parse_negative_string_as_instant(json_compiled, driver_compiled):
    """A JSON string holding a numeric (signed) timestamp must parse to an
    Instant the same way a bare JSON number would."""
    r = _invoke(json_compiled, driver_compiled, "parseNegativeStringAsInstant")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_jsoninput_has_next_end_method(json_compiled, driver_compiled):
    """JsonInput must expose a public void nextEnd() that asserts END-of-input."""
    r = _invoke(json_compiled, driver_compiled, "jsonInputHasNextEndMethod")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_next_end_rejects_remaining_tokens(json_compiled, driver_compiled):
    """nextEnd() must raise when there are unread tokens left in the stream."""
    r = _invoke(json_compiled, driver_compiled, "nextEndRejectsRemainingTokens")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_next_end_accepts_fully_consumed_input(json_compiled, driver_compiled):
    """nextEnd() must succeed when the stream has been fully consumed."""
    r = _invoke(json_compiled, driver_compiled, "nextEndAcceptsFullyConsumedInput")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"


def test_nextinstant_is_deprecated_for_removal(json_compiled, driver_compiled):
    """JsonInput.nextInstant must be annotated @Deprecated(forRemoval=true)."""
    r = _invoke(json_compiled, driver_compiled, "nextInstantIsDeprecatedForRemoval")
    assert r.returncode == 0, f"stdout={r.stdout!r}\nstderr={r.stderr!r}"
