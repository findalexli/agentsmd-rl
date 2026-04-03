"""
Task: rabbitmq-server-trust-store-introduce-proper-cli
Repo: rabbitmq/rabbitmq-server @ 95cfcbac9099290f72f99665a8b9ba7f63a8c266
PR:   #15746

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import re
from pathlib import Path

REPO = "/workspace/rabbitmq-server"
TRUST_STORE_SRC = Path(REPO) / "deps" / "rabbitmq_trust_store" / "src"
TRUST_STORE_README = Path(REPO) / "deps" / "rabbitmq_trust_store" / "README.md"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — syntax / compilation checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_syntax_check():
    """All .erl files in trust_store/src must have valid module declarations."""
    erl_files = list(TRUST_STORE_SRC.glob("*.erl"))
    assert len(erl_files) >= 1, "No .erl files found in trust store src"
    for f in erl_files:
        content = f.read_text()
        assert "-module(" in content, f"{f.name} missing -module declaration"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_list_command_module():
    """A CLI command module for listing trust store certificates must exist."""
    found = False
    for f in TRUST_STORE_SRC.glob("*.erl"):
        content = f.read_text()
        # Must be a CommandBehaviour implementing list for trust store certs
        if "CommandBehaviour" in content and "list_trust_store_certificates" in content:
            found = True
            # Verify it exports the key callbacks
            assert "usage" in content, f"{f.name}: must export usage"
            assert "run" in content, f"{f.name}: must export run"
            assert "description" in content, f"{f.name}: must export description"
            # Verify it calls list_certificates on the trust store
            assert "list_certificates" in content, \
                f"{f.name}: must call list_certificates on rabbit_trust_store"
            break
    assert found, (
        "No CLI command module found that implements CommandBehaviour "
        "for list_trust_store_certificates"
    )


# [pr_diff] fail_to_pass
def test_refresh_command_module():
    """A CLI command module for refreshing the trust store must exist."""
    found = False
    for f in TRUST_STORE_SRC.glob("*.erl"):
        content = f.read_text()
        if "CommandBehaviour" in content and "refresh_trust_store" in content:
            found = True
            assert "usage" in content, f"{f.name}: must export usage"
            assert "run" in content, f"{f.name}: must export run"
            assert "description" in content, f"{f.name}: must export description"
            # Verify it calls refresh on the trust store
            assert "rabbit_trust_store" in content and "refresh" in content, \
                f"{f.name}: must call refresh on rabbit_trust_store"
            break
    assert found, (
        "No CLI command module found that implements CommandBehaviour "
        "for refresh_trust_store"
    )


# [pr_diff] fail_to_pass
def test_list_certificates_function():
    """rabbit_trust_store.erl must export a list_certificates function returning structured data."""
    src = (TRUST_STORE_SRC / "rabbit_trust_store.erl").read_text()
    # Must be in the export list
    assert "list_certificates" in src, \
        "rabbit_trust_store.erl must define list_certificates"
    # Must appear in an -export directive
    export_sections = re.findall(r"-export\(\[([^\]]+)\]\)", src, re.DOTALL)
    export_text = " ".join(export_sections)
    assert "list_certificates" in export_text, \
        "list_certificates must be exported (in an -export directive)"
    # Must return maps with structured fields (not just formatted strings)
    # Look for map construction syntax with at least name/serial/subject keys
    func_match = re.search(
        r"list_certificates\(\).*?(?=\n-spec|\n[a-z_]+\(|\n%%\s+\S|\Z)",
        src,
        re.DOTALL,
    )
    assert func_match, "list_certificates function body not found"
    func_body = func_match.group()
    assert "#{" in func_body or "maps:" in func_body, \
        "list_certificates must return maps (structured data), not formatted strings"


# [pr_diff] fail_to_pass
def test_list_certificates_map_keys():
    """list_certificates must return maps containing name, serial, subject, issuer, validity."""
    src = (TRUST_STORE_SRC / "rabbit_trust_store.erl").read_text()
    func_match = re.search(
        r"list_certificates\(\).*?(?=\n-spec|\n[a-z_]+\(|\n%%\s+\S|\Z)",
        src,
        re.DOTALL,
    )
    assert func_match, "list_certificates function body not found"
    func_body = func_match.group()
    required_keys = ["name", "serial", "subject", "issuer", "validity"]
    for key in required_keys:
        assert key in func_body, \
            f"list_certificates map must include '{key}' key"


# ---------------------------------------------------------------------------
# Config edit (config_edit) — README documentation tests
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_list_function_preserved():
    """The original list/0 function in rabbit_trust_store.erl must still exist."""
    src = (TRUST_STORE_SRC / "rabbit_trust_store.erl").read_text()
    export_sections = re.findall(r"-export\(\[([^\]]+)\]\)", src, re.DOTALL)
    export_text = " ".join(export_sections)
    assert re.search(r"\blist\b", export_text), \
        "The original list/0 function must still be exported"


# [pr_diff] fail_to_pass


# ---------------------------------------------------------------------------
# Agent config (agent_config) — rules from CLAUDE.md
# ---------------------------------------------------------------------------

# [agent_config] pass_to_pass — CLAUDE.md:133-134 @ 95cfcbac
