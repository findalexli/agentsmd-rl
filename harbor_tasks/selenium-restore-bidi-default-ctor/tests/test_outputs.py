"""Behavioral tests for selenium PR #17014: restore BiDi(Connection) constructor."""

import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/selenium")
STUBS = Path("/workspace/stubs")
PROBE_SRC = Path("/workspace/probe/BiDiProbe.java")
BIDI_SRC = REPO / "java/src/org/openqa/selenium/bidi/BiDi.java"
BUILD = Path("/tmp/build")


def _compile() -> subprocess.CompletedProcess:
    """Compile BiDi.java + stubs + probe into BUILD. Returns the javac result."""
    if BUILD.exists():
        shutil.rmtree(BUILD)
    BUILD.mkdir(parents=True)

    sources = [
        STUBS / "org/openqa/selenium/internal/Require.java",
        STUBS / "org/openqa/selenium/bidi/Connection.java",
        STUBS / "org/openqa/selenium/bidi/Command.java",
        STUBS / "org/openqa/selenium/bidi/Event.java",
        STUBS / "org/openqa/selenium/bidi/BiDiSessionStatus.java",
        BIDI_SRC,
        PROBE_SRC,
    ]
    return subprocess.run(
        ["javac", "-d", str(BUILD), *[str(s) for s in sources]],
        capture_output=True,
        text=True,
        timeout=120,
    )


def _run_probe(mode: str) -> subprocess.CompletedProcess:
    """Run BiDiProbe with a particular mode against the compiled classes."""
    return subprocess.run(
        ["java", "-cp", str(BUILD), "BiDiProbe", mode],
        capture_output=True,
        text=True,
        timeout=60,
    )


def test_javac_compiles():
    """The repo's BiDi.java must compile against the stub classpath (pass_to_pass)."""
    r = _compile()
    assert r.returncode == 0, f"javac failed:\nstdout={r.stdout}\nstderr={r.stderr}"


def test_two_arg_constructor_still_works():
    """The original BiDi(Connection, Duration) constructor must remain (pass_to_pass)."""
    r = _compile()
    assert r.returncode == 0, f"compile failed: {r.stderr}"
    p = _run_probe("two-arg-ctor")
    assert p.returncode == 0, f"two-arg ctor probe failed:\n{p.stdout}\n{p.stderr}"
    assert "TWO_ARG_CTOR:OK:seconds=7" in p.stdout, p.stdout


def test_single_arg_constructor_exists():
    """BiDi(Connection) constructor must exist (fail_to_pass)."""
    r = _compile()
    assert r.returncode == 0, f"compile failed: {r.stderr}"
    p = _run_probe("ctor-exists")
    assert p.returncode == 0, (
        f"BiDi(Connection) constructor missing or unreachable:\n{p.stdout}\n{p.stderr}"
    )
    assert "CTOR_EXISTS:OK" in p.stdout, p.stdout


def test_single_arg_constructor_deprecated_for_removal():
    """BiDi(Connection) must be annotated @Deprecated(forRemoval = true) (fail_to_pass)."""
    r = _compile()
    assert r.returncode == 0, f"compile failed: {r.stderr}"
    p = _run_probe("ctor-deprecated")
    assert p.returncode == 0, (
        f"@Deprecated(forRemoval=true) check failed:\n{p.stdout}\n{p.stderr}"
    )
    assert "CTOR_DEPRECATED:OK:forRemoval=true" in p.stdout, (
        f"constructor must be marked forRemoval=true; got: {p.stdout}"
    )


def test_single_arg_default_timeout_30_seconds():
    """new BiDi(connection) must default to a 30-second timeout (fail_to_pass)."""
    r = _compile()
    assert r.returncode == 0, f"compile failed: {r.stderr}"
    p = _run_probe("default-timeout")
    assert p.returncode == 0, f"default-timeout probe failed:\n{p.stdout}\n{p.stderr}"
    assert "DEFAULT_TIMEOUT:OK:seconds=30" in p.stdout, (
        f"expected default 30s; got: {p.stdout}"
    )
