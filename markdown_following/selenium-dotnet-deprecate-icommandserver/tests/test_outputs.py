"""Behavioral tests for SeleniumHQ/selenium#17103.

The PR removes the unnecessary ICommandServer interface from DriverService's
inheritance and marks ICommandServer as [Obsolete] (per the project's
deprecation policy in dotnet/AGENTS.md).

Selenium's full WebDriver build is Bazel-driven (it generates CDP bindings
and a ResourceUtilities helper at build time), so we cannot do a plain
`dotnet build` against the agent's edits without bringing in the Bazel
toolchain. Instead, the Docker image bakes a small Roslyn-based "reflcheck"
console app that:

  * Compiles ICommandServer.cs in isolation (it only depends on IDisposable)
    and reflects on the resulting assembly to verify the [Obsolete] attribute.
  * Parses DriverService.cs syntactically with the C# compiler (Roslyn) to
    verify its inheritance list.

Both checks invoke the real C# compiler infrastructure via subprocess.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

REPO = Path("/workspace/selenium")
DOTNET_REPO = REPO / "dotnet"
DRIVER_SERVICE = DOTNET_REPO / "src/webdriver/DriverService.cs"
ICOMMAND_SERVER = DOTNET_REPO / "src/webdriver/Remote/ICommandServer.cs"
REFLCHECK = Path("/workspace/reflcheck")
REFLCHECK_DLL = REFLCHECK / "bin/Release/net8.0/Reflcheck.dll"


def _run_reflcheck(check: str, timeout: int = 120) -> subprocess.CompletedProcess:
    """Invoke the pre-built reflcheck app with a single check argument."""
    assert REFLCHECK_DLL.exists(), f"reflcheck binary missing at {REFLCHECK_DLL}"
    return subprocess.run(
        ["dotnet", str(REFLCHECK_DLL), check],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REFLCHECK),
    )


# -----------------------------------------------------------------------------
# pass_to_pass — should hold both at base and after the fix.
# -----------------------------------------------------------------------------

def test_source_files_present():
    """The two files the PR touches exist in the repo (sanity p2p)."""
    assert DRIVER_SERVICE.exists(), f"missing: {DRIVER_SERVICE}"
    assert ICOMMAND_SERVER.exists(), f"missing: {ICOMMAND_SERVER}"


def test_source_files_parse_cleanly():
    """Both files parse as valid C# (real Roslyn parse)."""
    r = _run_reflcheck("parse_ok")
    assert r.returncode == 0, (
        f"parse_ok failed (rc={r.returncode}):\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )


def test_dotnet_sdk_available():
    """The .NET 8 SDK is installed (required by the deprecation pattern in dotnet/AGENTS.md)."""
    r = subprocess.run(
        ["dotnet", "--list-sdks"], capture_output=True, text=True, timeout=30
    )
    assert r.returncode == 0, f"dotnet --list-sdks failed: {r.stderr}"
    assert any(line.startswith("8.") for line in r.stdout.splitlines()), (
        f"No .NET 8 SDK detected:\n{r.stdout}"
    )


def test_dotnet_sln_present():
    """The .NET solution file exists at the standard path."""
    assert (DOTNET_REPO / "Selenium.slnx").exists()


# -----------------------------------------------------------------------------
# fail_to_pass — must FAIL at the base commit and PASS after the gold fix.
# -----------------------------------------------------------------------------

def test_driver_service_no_longer_implements_icommandserver():
    """DriverService's base list must no longer name ICommandServer.

    At the base commit, DriverService is declared as
        public abstract class DriverService : ICommandServer
    The PR replaces this with
        public abstract class DriverService : IDisposable
    so the class continues to satisfy the IDisposable contract its callers
    rely on without going through the now-deprecated ICommandServer.
    """
    r = _run_reflcheck("driverservice_base")
    assert r.returncode == 0, (
        f"DriverService base-list check failed (rc={r.returncode}):\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )
    # Defense in depth: the OK message names IDisposable explicitly.
    assert "IDisposable" in r.stdout, r.stdout


def test_icommandserver_is_obsolete_via_compilation():
    """Compile ICommandServer.cs in isolation and reflect on the resulting type.

    This is a real compile-and-reflect test:
      1. Roslyn compiles the modified source file into an in-memory assembly.
      2. The ICommandServer Type is loaded.
      3. typeof(ObsoleteAttribute) is read off it via standard reflection.

    At the base commit, ICommandServer has no [Obsolete] attribute, so the
    reflection step returns null and this test fails. After the fix, the
    attribute is present and carries a non-empty deprecation message.
    """
    r = _run_reflcheck("icommandserver_obsolete", timeout=180)
    assert r.returncode == 0, (
        f"ICommandServer obsolete-via-compilation check failed (rc={r.returncode}):\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )
    assert "Obsolete" in r.stdout, r.stdout


def test_icommandserver_obsolete_message_mentions_removal():
    """The deprecation message must point users to the alternative / removal.

    dotnet/AGENTS.md states: 'before removing public functionality, mark it
    as deprecated with a message pointing to the alternative.' A bare
    [Obsolete] with an empty string would technically be present but would
    not satisfy the policy. We require the message to be non-empty AND to
    contain wording that signals future removal (so users know this is a
    real deprecation, not just a soft warning).
    """
    r = _run_reflcheck("icommandserver_obsolete", timeout=180)
    assert r.returncode == 0, r.stderr
    msg_line = next(
        (ln for ln in r.stdout.splitlines() if "message:" in ln),
        "",
    )
    assert msg_line, f"reflcheck did not emit a 'message:' line:\n{r.stdout}"
    msg = msg_line.split("message:", 1)[1].strip().lower()
    assert any(
        token in msg for token in ("remove", "removal", "future release", "no longer")
    ), f"Obsolete message does not signal removal: {msg!r}"


def test_icommandserver_obsolete_attribute_in_source():
    """Cross-check: the attribute is present in source syntax too.

    Compilation could in principle succeed with the attribute applied
    elsewhere; this Roslyn-syntax check pins the attribute to the interface
    declaration itself, where the deprecation policy expects it.
    """
    r = _run_reflcheck("icommandserver_obsolete_attr_syntax")
    assert r.returncode == 0, (
        f"obsolete-attr-syntax check failed (rc={r.returncode}):\n"
        f"STDOUT:\n{r.stdout}\nSTDERR:\n{r.stderr}"
    )
