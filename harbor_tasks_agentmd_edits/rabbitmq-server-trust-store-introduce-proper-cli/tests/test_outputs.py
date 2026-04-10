"""
Task: rabbitmq-server-trust-store-introduce-proper-cli
Repo: rabbitmq/rabbitmq-server @ 95cfcbac9099290f72f99665a8b9ba7f63a8c266
PR:   #15746

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess

REPO = "/workspace/rabbitmq-server"
TRUST_STORE_SRC = REPO + "/deps/rabbitmq_trust_store/src"
README = REPO + "/deps/rabbitmq_trust_store/README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static)
# ---------------------------------------------------------------------------

def test_syntax_check():
    """All .erl files in trust_store/src must have valid module declarations."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib
src = pathlib.Path("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src")
erl_files = list(src.glob("*.erl"))
assert len(erl_files) >= 1, "No .erl files found in trust store src"
for f in erl_files:
    content = f.read_text()
    assert "-module(" in content, f"{f.name} missing -module declaration"
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Syntax check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_trust_store_module_exports():
    """rabbit_trust_store.erl exports required console interface functions (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys
src = open("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src/rabbit_trust_store.erl").read()
exports = re.findall(r"-export\\(\\[([^\\]]+)\\]\\)", src, re.DOTALL)
export_text = " ".join(exports)
required = ["mode/0", "refresh/0", "list/0"]
for func in required:
    if func not in export_text:
        print(f"FAIL: missing export {func}", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Export check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_trust_store_behaviour_declaration():
    """rabbit_trust_store.erl has required behaviour declaration (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import sys
src = open("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src/rabbit_trust_store.erl").read()
if "-behaviour(gen_server)." not in src:
    print("FAIL: missing -behaviour(gen_server) declaration", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Behaviour check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_trust_store_src_structure():
    """Trust store src directory contains expected core modules (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib, sys
src = pathlib.Path("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src")
required_modules = [
    "rabbit_trust_store.erl",
    "rabbit_trust_store_app.erl",
    "rabbit_trust_store_sup.erl",
]
for mod in required_modules:
    if not (src / mod).exists():
        print(f"FAIL: required module {mod} not found", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Structure check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_exists_and_has_content():
    """README.md exists and has minimum content (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib, sys
readme = pathlib.Path("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/README.md")
if not readme.exists():
    print("FAIL: README.md not found", file=sys.stderr)
    sys.exit(1)
content = readme.read_text()
if len(content) < 100:
    print("FAIL: README.md is too short", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"README check failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_makefile_exists():
    """Makefile exists and defines required variables (pass_to_pass)."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib, sys
mf = pathlib.Path("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/Makefile")
if not mf.exists():
    print("FAIL: Makefile not found", file=sys.stderr)
    sys.exit(1)
content = mf.read_text()
required_vars = ["PROJECT = rabbitmq_trust_store", "DEPS ="]
for var in required_vars:
    if var not in content:
        print(f"FAIL: Makefile missing '{var}'", file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Makefile check failed: {r.stderr}"
    assert "PASS" in r.stdout


# ---------------------------------------------------------------------------
# Repo CI tests (pass_to_pass, repo_tests) — real CI commands
# ---------------------------------------------------------------------------

def test_trust_store_erlc_syntax():
    """Erlang syntax check for rabbit_trust_store.erl using erlc (pass_to_pass)."""
    r = subprocess.run(
        """apt-get update > /dev/null 2>&1
apt-get install -y --no-install-recommends erlang > /dev/null 2>&1
cd /workspace/rabbitmq-server/deps/rabbitmq_trust_store
erlc +syntax_check src/rabbit_trust_store.erl 2>&1
""",
        shell=True, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"erlc syntax check failed:\n{r.stderr}\n{r.stdout}"


def test_cli_command_modules_syntax():
    """Erlang syntax check for CLI command modules (pass_to_pass)."""
    r = subprocess.run(
        """apt-get update > /dev/null 2>&1
apt-get install -y --no-install-recommends erlang > /dev/null 2>&1
cd /workspace/rabbitmq-server/deps/rabbitmq_trust_store/src
for f in Elixir.*Command.erl; do
    if [ -f "$f" ]; then
        erlc +syntax_check "$f" 2>&1 || exit 1
    fi
done
echo "PASS"
""",
        shell=True, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"CLI command module syntax check failed:\n{r.stderr}"


def test_trust_store_core_modules_syntax():
    """Erlang syntax check for all core trust store modules (pass_to_pass)."""
    r = subprocess.run(
        """apt-get update > /dev/null 2>&1
apt-get install -y --no-install-recommends erlang > /dev/null 2>&1
cd /workspace/rabbitmq-server/deps/rabbitmq_trust_store/src
for f in rabbit_trust_store_*.erl; do
    erlc +syntax_check "$f" 2>&1 || exit 1
done
echo "PASS"
""",
        shell=True, capture_output=True, text=True, timeout=180,
    )
    assert r.returncode == 0, f"Core module syntax check failed:\n{r.stderr}"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

def test_list_command_module():
    """A CLI command module for listing trust store certificates must exist."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib, re, sys
src_dir = pathlib.Path("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src")
found = False
for f in src_dir.glob("*.erl"):
    content = f.read_text()
    if "CommandBehaviour" in content and "list_trust_store_certificates" in content:
        found = True
        exports = re.findall(r"-export\\(\\[([^\\]]+)\\]\\)", content, re.DOTALL)
        export_text = " ".join(exports)
        for cb in ["usage", "run", "description", "banner"]:
            if cb not in export_text:
                print("FAIL: missing export " + cb, file=sys.stderr)
                sys.exit(1)
        if "list_certificates" not in content:
            print("FAIL: must call list_certificates on rabbit_trust_store", file=sys.stderr)
            sys.exit(1)
        print("PASS")
        break
if not found:
    print("FAIL: No CLI command module for list_trust_store_certificates", file=sys.stderr)
    sys.exit(1)
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_refresh_command_module():
    """A CLI command module for refreshing the trust store must exist."""
    r = subprocess.run(
        ["python3", "-c", """
import pathlib, re, sys
src_dir = pathlib.Path("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src")
found = False
for f in src_dir.glob("*.erl"):
    content = f.read_text()
    if "CommandBehaviour" in content and "refresh_trust_store" in content:
        found = True
        exports = re.findall(r"-export\\(\\[([^\\]]+)\\]\\)", content, re.DOTALL)
        export_text = " ".join(exports)
        for cb in ["usage", "run", "description", "banner"]:
            if cb not in export_text:
                print("FAIL: missing export " + cb, file=sys.stderr)
                sys.exit(1)
        if "rabbit_trust_store" not in content or "refresh" not in content:
            print("FAIL: must call refresh on rabbit_trust_store", file=sys.stderr)
            sys.exit(1)
        print("PASS")
        break
if not found:
    print("FAIL: No CLI command module for refresh_trust_store", file=sys.stderr)
    sys.exit(1)
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_list_certificates_function():
    """rabbit_trust_store.erl must export a list_certificates function."""
    r = subprocess.run(
        ["python3", "-c", """
import re, sys
src = open("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src/rabbit_trust_store.erl").read()
exports = re.findall(r"-export\\(\\[([^\\]]+)\\]\\)", src, re.DOTALL)
export_text = " ".join(exports)
if "list_certificates" not in export_text:
    print("FAIL: list_certificates not in any -export directive", file=sys.stderr)
    sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_list_certificates_map_keys():
    """list_certificates must return maps with name, serial, subject, issuer, validity."""
    r = subprocess.run(
        ["python3", "-c", r"""
import re, sys
src = open("/workspace/rabbitmq-server/deps/rabbitmq_trust_store/src/rabbit_trust_store.erl").read()
func_match = re.search(
    r"list_certificates\\(\\).*?(?=\\n-spec|\\n[a-z_]+\\(|\\n%%\\s+\\S|\\Z)",
    src, re.DOTALL)
if not func_match:
    print("FAIL: list_certificates function body not found", file=sys.stderr)
    sys.exit(1)
body = func_match.group()
if "#{" not in body and "maps:" not in body:
    print("FAIL: list_certificates must return maps, not formatted strings", file=sys.stderr)
    sys.exit(1)
for key in ["name", "serial", "subject", "issuer", "validity"]:
    if key not in body:
        print("FAIL: missing map key " + key, file=sys.stderr)
        sys.exit(1)
print("PASS")
"""],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Failed: {r.stderr}"
    assert "PASS" in r.stdout


def test_readme_documents_list_command():
    """README must document the list_trust_store_certificates CLI command."""
    r = subprocess.run(
        ["grep", "-q", "list_trust_store_certificates",
         "/workspace/rabbitmq-server/deps/rabbitmq_trust_store/README.md"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "README must document list_trust_store_certificates command"


def test_readme_documents_refresh_command():
    """README must document the refresh_trust_store CLI command."""
    r = subprocess.run(
        ["grep", "-q", "refresh_trust_store",
         "/workspace/rabbitmq-server/deps/rabbitmq_trust_store/README.md"],
        capture_output=True, text=True, timeout=10,
    )
    assert r.returncode == 0, "README must document refresh_trust_store command"


def test_readme_no_eval_instructions():
    """README should not instruct users to use rabbitmqctl eval for trust store ops."""
    r = subprocess.run(
        ["grep", "-c", "rabbitmqctl eval",
         "/workspace/rabbitmq-server/deps/rabbitmq_trust_store/README.md"],
        capture_output=True, text=True, timeout=10,
    )
    # grep -c returns 0 when matches found, 1 when no matches — we want no matches
    assert r.returncode != 0 or r.stdout.strip() == "0", \
        "README should not use 'rabbitmqctl eval' for trust store operations"
