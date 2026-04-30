"""Behavioral tests for appwrite/appwrite#11689 ("Fix installer").

The PR adds a `hasExplicitCliParams()` private method on
`Appwrite\\Platform\\Tasks\\Install` that distinguishes whether the user
supplied installer-specific CLI flags (in which case the web installer
should be skipped). It also extends `performInstallation()` with a new
trailing `?callable $onComplete = null` parameter so SSE completion can
be signalled before slow tracking work.

The repo uses Swoole / a full HTTP stack at runtime, but the parts of
the diff that matter for the bug are reachable through ReflectionClass
on a vendored autoloader -- no Swoole runtime required.
"""
import json
import os
import subprocess
from pathlib import Path

REPO = "/workspace/appwrite"
PHP = "php"


def _php(script: str) -> subprocess.CompletedProcess:
    """Run a PHP one-liner that bootstraps the appwrite autoloader."""
    bootstrap = (
        f"require '{REPO}/vendor/autoload.php';"
        f"require '{REPO}/app/init/constants.php';"
    )
    return subprocess.run(
        [PHP, "-r", bootstrap + script],
        capture_output=True,
        text=True,
        timeout=60,
        cwd=REPO,
    )


def _reflect_has_method(method_name: str) -> bool:
    r = _php(
        f'$rc = new ReflectionClass("Appwrite\\\\Platform\\\\Tasks\\\\Install");'
        f'echo $rc->hasMethod({method_name!r}) ? "YES" : "NO";'
    )
    assert r.returncode == 0, f"php failed: {r.stderr}"
    return r.stdout.strip() == "YES"


def _invoke_has_explicit_cli_params(argv: list[str]) -> bool:
    """Use reflection to call the private hasExplicitCliParams method."""
    argv_php = "[" + ",".join(repr(a) for a in argv) + "]"
    script = (
        '$rc = new ReflectionClass("Appwrite\\\\Platform\\\\Tasks\\\\Install");'
        '$m  = $rc->getMethod("hasExplicitCliParams");'
        '$m->setAccessible(true);'
        '$inst = $rc->newInstanceWithoutConstructor();'
        f'$_SERVER["argv"] = {argv_php};'
        'echo $m->invoke($inst) ? "TRUE" : "FALSE";'
    )
    r = _php(script)
    assert r.returncode == 0, f"php failed: {r.stderr or r.stdout}"
    out = r.stdout.strip()
    assert out in ("TRUE", "FALSE"), f"unexpected stdout: {out!r}"
    return out == "TRUE"


# ---------------------------------------------------------------- f2p


def test_has_explicit_cli_params_method_exists():
    """The fix must introduce a hasExplicitCliParams method on Install."""
    assert _reflect_has_method("hasExplicitCliParams"), (
        "Tasks\\Install must expose a hasExplicitCliParams() method to detect "
        "when explicit installer flags were supplied"
    )


def test_no_explicit_params_returns_false():
    """argv with only the script name has no explicit CLI overrides."""
    assert _invoke_has_explicit_cli_params(["install"]) is False


def test_explicit_double_dash_param_returns_true():
    """A --http-port=80 flag is an explicit installer CLI override."""
    assert (
        _invoke_has_explicit_cli_params(["install", "--http-port=80"]) is True
    )


def test_explicit_database_param_returns_true():
    """A --database=mariadb flag is an explicit installer CLI override."""
    assert (
        _invoke_has_explicit_cli_params(["install", "--database=mariadb"]) is True
    )


def test_interactive_flag_alone_does_not_count():
    """--interactive must NOT count as an explicit override on its own;
    it's the very flag the gating condition already checks."""
    assert (
        _invoke_has_explicit_cli_params(["install", "--interactive=Y"]) is False
    )


def test_interactive_with_other_param_still_returns_true():
    """If --interactive=Y is combined with another --flag, the other
    flag is still an explicit override."""
    argv = ["install", "--interactive=Y", "--http-port=80"]
    assert _invoke_has_explicit_cli_params(argv) is True


def test_perform_installation_has_on_complete_callable_parameter():
    """performInstallation gains a trailing ?callable $onComplete = null
    parameter so SSE completion can be signalled before tracking."""
    script = (
        '$rc = new ReflectionClass("Appwrite\\\\Platform\\\\Tasks\\\\Install");'
        '$m  = $rc->getMethod("performInstallation");'
        '$out = [];'
        'foreach ($m->getParameters() as $p) {'
        '  $t = $p->getType();'
        '  $tn = $t ? ($t instanceof ReflectionNamedType ? $t->getName() : (string)$t) : "";'
        '  $out[] = ['
        '    "name" => $p->getName(),'
        '    "type" => $tn,'
        '    "allowsNull" => $t ? $t->allowsNull() : false,'
        '    "hasDefault" => $p->isDefaultValueAvailable(),'
        '  ];'
        '}'
        'echo json_encode($out);'
    )
    r = _php(script)
    assert r.returncode == 0, f"php failed: {r.stderr or r.stdout}"
    params = json.loads(r.stdout)
    by_name = {p["name"]: p for p in params}
    assert "onComplete" in by_name, (
        "performInstallation must accept an $onComplete parameter; "
        f"got params: {[p['name'] for p in params]}"
    )
    p = by_name["onComplete"]
    assert p["type"] == "callable", (
        f"$onComplete should be typed `callable`, got {p['type']!r}"
    )
    assert p["allowsNull"] is True, "$onComplete must be nullable (?callable)"
    assert p["hasDefault"] is True, "$onComplete must have a default of null"


# ---------------------------------------------------------------- p2p


def test_php_syntax_tasks_install():
    """Tasks/Install.php must parse cleanly (pass_to_pass)."""
    target = Path(REPO) / "src/Appwrite/Platform/Tasks/Install.php"
    r = subprocess.run(
        [PHP, "-l", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"php -l failed for {target}:\n{r.stdout}\n{r.stderr}"
    )


def test_php_syntax_http_installer_install():
    """Http/Installer/Install.php must parse cleanly (pass_to_pass)."""
    target = Path(REPO) / "src/Appwrite/Platform/Installer/Http/Installer/Install.php"
    r = subprocess.run(
        [PHP, "-l", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"php -l failed for {target}:\n{r.stdout}\n{r.stderr}"
    )


def test_php_syntax_installer_server():
    """Installer/Server.php must parse cleanly (pass_to_pass)."""
    target = Path(REPO) / "src/Appwrite/Platform/Installer/Server.php"
    r = subprocess.run(
        [PHP, "-l", str(target)],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"php -l failed for {target}:\n{r.stdout}\n{r.stderr}"
    )


def test_install_class_loads():
    """The Install class itself must be reachable via the autoloader (p2p)."""
    r = _php(
        '$rc = new ReflectionClass("Appwrite\\\\Platform\\\\Tasks\\\\Install");'
        'echo $rc->getName();'
    )
    assert r.returncode == 0, f"reflection failed: {r.stderr or r.stdout}"
    assert r.stdout.strip() == "Appwrite\\Platform\\Tasks\\Install"
