"""Behavioral tests for SeleniumHQ/selenium PR #17147 (Keys.java PUA dedup)."""
import os
import shutil
import subprocess
from pathlib import Path

REPO = "/workspace/selenium"
KEYS_FILE = f"{REPO}/java/src/org/openqa/selenium/Keys.java"
SRC_ROOT = f"{REPO}/java/src"
STUBS = "/opt/keys_stubs"
BUILD = "/tmp/keys_build"
HARNESS = "/tests/TestKeysHarness.java"


def _ensure_compiled():
    """Compile Keys.java + Nullable stub + the harness once. Idempotent."""
    if Path(f"{BUILD}/TestKeysHarness.class").exists():
        return BUILD
    if Path(BUILD).exists():
        shutil.rmtree(BUILD)
    os.makedirs(BUILD, exist_ok=True)
    sources = [
        f"{STUBS}/org/jspecify/annotations/Nullable.java",
        KEYS_FILE,
        HARNESS,
    ]
    for s in sources:
        if not Path(s).exists():
            raise FileNotFoundError(f"Missing required source: {s}")
    r = subprocess.run(
        ["javac", "-d", BUILD, "-cp", BUILD, *sources],
        capture_output=True, text=True, timeout=120,
    )
    if r.returncode != 0:
        raise RuntimeError(
            f"javac failed (code {r.returncode}):\nSTDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
        )
    return BUILD


def _run_check(name: str):
    cp = _ensure_compiled()
    r = subprocess.run(
        ["java", "-cp", cp, "TestKeysHarness", name],
        capture_output=True, text=True, timeout=30,
    )
    return r


# --- f2p tests (must FAIL on base, PASS after fix) ----------------------------

def test_option_charat_equals_alt():
    """OPTION must share its Unicode char with ALT (alias semantics)."""
    r = _run_check("option_charat_equals_alt")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"
    assert "OK" in r.stdout


def test_option_unicode_e00a():
    """OPTION.charAt(0) must equal 0xE00A (the ALT code point)."""
    r = _run_check("option_unicode_e00a")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_option_codepoint_equals_alt():
    """OPTION.getCodePoint() must match ALT.getCodePoint()."""
    r = _run_check("option_codepoint_equals_alt")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_option_tostring_equals_alt():
    """OPTION.toString() must equal ALT.toString()."""
    r = _run_check("option_tostring_equals_alt")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_fn_is_deprecated():
    """Keys.FN must be annotated with @Deprecated (visible via reflection)."""
    r = _run_check("fn_is_deprecated")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


# --- p2p tests (regression — must pass before AND after) ----------------------

def test_keys_file_compiles():
    """Keys.java must compile cleanly with -Werror-equivalent settings."""
    _ensure_compiled()


def test_right_alt_unicode():
    """RIGHT_ALT must remain mapped to 0xE052."""
    r = _run_check("right_alt_unicode")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_right_control_unicode():
    """RIGHT_CONTROL must remain mapped to 0xE051."""
    r = _run_check("right_control_unicode")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_alt_unicode():
    """ALT must remain mapped to 0xE00A."""
    r = _run_check("alt_unicode")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_fn_charat_equals_right_control():
    """FN must expose the same Unicode char as RIGHT_CONTROL (0xE051)."""
    r = _run_check("fn_charat_equals_right_control")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_option_field_exists():
    """Keys.OPTION must remain a public enum constant (API compat)."""
    r = _run_check("option_field_exists")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_fn_field_exists():
    """Keys.FN must remain a public enum constant (API compat)."""
    r = _run_check("fn_field_exists")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"


def test_right_alt_returned_for_e052():
    """getKeyFromUnicode(0xE052) must resolve to RIGHT_ALT."""
    r = _run_check("right_alt_returned_for_e052")
    assert r.returncode == 0, f"FAIL stdout={r.stdout!r} stderr={r.stderr!r}"
