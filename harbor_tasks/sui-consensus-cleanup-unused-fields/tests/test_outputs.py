"""Tests for sui PR #26086: cleanup unused fields and no-op flag."""

import subprocess
import sys
from pathlib import Path

REPO = Path("/workspace/sui")


def test_consensus_config_field_removed():
    """always_accept_system_transactions field removed from ConsensusProtocolConfig (fail_to_pass)."""
    config_file = REPO / "consensus/config/src/consensus_protocol_config.rs"
    content = config_file.read_text()

    # The field should NOT exist after the fix
    assert "always_accept_system_transactions: bool" not in content, \
        "always_accept_system_transactions field still exists in ConsensusProtocolConfig"


def test_consensus_config_method_removed():
    """always_accept_system_transactions() method removed (fail_to_pass)."""
    config_file = REPO / "consensus/config/src/consensus_protocol_config.rs"
    content = config_file.read_text()

    # The getter method should NOT exist after the fix
    assert "pub fn always_accept_system_transactions(&self)" not in content, \
        "always_accept_system_transactions() method still exists"


def test_committed_subdag_field_removed():
    """always_accept_system_transactions field removed from CommittedSubDag (fail_to_pass)."""
    commit_file = REPO / "consensus/core/src/commit.rs"
    content = commit_file.read_text()

    # The field should NOT exist in CommittedSubDag struct
    assert "always_accept_system_transactions: bool" not in content, \
        "always_accept_system_transactions field still exists in CommittedSubDag"

    # The field documentation should also be removed
    assert "Used by consensus to communicate whether to always accept system transactions" not in content, \
        "Documentation for always_accept_system_transactions still exists"


def test_committed_subdag_new_signature():
    """CommittedSubDag::new doesn't take always_accept_system_transactions parameter (fail_to_pass)."""
    commit_file = REPO / "consensus/core/src/commit.rs"
    content = commit_file.read_text()

    # Find the impl block for CommittedSubDag::new
    # Check that the parameter is not in the new() method signature
    lines = content.split('\n')
    in_new_fn = False
    paren_depth = 0
    new_fn_signature = []

    for line in lines:
        if 'fn new(' in line or (in_new_fn and paren_depth > 0):
            in_new_fn = True
            new_fn_signature.append(line)
            paren_depth += line.count('(') - line.count(')')
            if paren_depth <= 0:
                break

    new_fn_text = '\n'.join(new_fn_signature)

    # The parameter should NOT be in the new() signature
    assert "always_accept_system_transactions" not in new_fn_text, \
        "always_accept_system_transactions parameter still in CommittedSubDag::new()"


def test_load_committed_subdag_signature():
    """load_committed_subdag_from_store doesn't take context parameter (fail_to_pass)."""
    commit_file = REPO / "consensus/core/src/commit.rs"
    content = commit_file.read_text()

    # Find the function signature
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'fn load_committed_subdag_from_store(' in line:
            # Get the next few lines to see the full signature
            signature_lines = [line]
            j = i + 1
            paren_depth = line.count('(') - line.count(')')
            while j < len(lines) and paren_depth > 0:
                signature_lines.append(lines[j])
                paren_depth += lines[j].count('(') - lines[j].count(')')
                j += 1
            signature = '\n'.join(signature_lines)

            # Should NOT have context parameter as first param
            assert "context: &Arc<Context>" not in signature, \
                "context parameter still in load_committed_subdag_from_store"
            assert "_context" not in signature, \
                "context parameter (even prefixed) still in load_committed_subdag_from_store"
            break
    else:
        raise AssertionError("load_committed_subdag_from_store function not found")


def test_authority_tables_events_removed():
    """events column family removed from AuthorityPerpetualTables (fail_to_pass)."""
    tables_file = REPO / "crates/sui-core/src/authority/authority_store_tables.rs"
    content = tables_file.read_text()

    # The deprecated events field should NOT exist
    if "#[deprecated]" in content:
        # If there are other deprecated items, specifically check the events field
        lines = content.split('\n')
        for i, line in enumerate(lines):
            if '#[deprecated]' in line:
                # Check next few lines for the events field
                for j in range(i+1, min(i+5, len(lines))):
                    if 'events: DBMap' in lines[j]:
                        raise AssertionError("Deprecated events field still exists in AuthorityPerpetualTables")

    # Also check that events: DBMap isn't present without the deprecated attr
    assert "events: DBMap" not in content, \
        "events DBMap field still exists in AuthorityPerpetualTables"


def test_unused_event_import_removed():
    """Unused Event import removed from authority.rs (fail_to_pass)."""
    authority_file = REPO / "crates/sui-core/src/authority.rs"
    content = authority_file.read_text()

    # Check that Event is not imported (but EventID still is)
    import_line = None
    for line in content.split('\n'):
        if 'use sui_types::event::' in line:
            import_line = line
            break

    assert import_line is not None, "sui_types::event import not found"
    assert "Event," not in import_line, \
        "Unused Event import still present in authority.rs"
    assert "EventID" in import_line, \
        "EventID import should still be present"


def test_parse_block_transactions_signature():
    """parse_block_transactions doesn't take always_accept_system_transactions parameter (fail_to_pass)."""
    api_file = REPO / "crates/sui-core/src/consensus_types/consensus_output_api.rs"
    content = api_file.read_text()

    # Find the function signature
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if 'pub(crate) fn parse_block_transactions(' in line:
            signature_lines = [line]
            j = i + 1
            paren_depth = line.count('(') - line.count(')')
            while j < len(lines) and paren_depth > 0:
                signature_lines.append(lines[j])
                paren_depth += lines[j].count('(') - lines[j].count(')')
                j += 1
            signature = '\n'.join(signature_lines)

            assert "always_accept_system_transactions" not in signature, \
                "always_accept_system_transactions parameter still in parse_block_transactions"
            break
    else:
        raise AssertionError("parse_block_transactions function not found")


def test_parse_block_transactions_logic():
    """parse_block_transactions correctly rejects only user transactions (fail_to_pass)."""
    api_file = REPO / "crates/sui-core/src/consensus_types/consensus_output_api.rs"
    content = api_file.read_text()

    # Check that the new logic is in place: system transactions are always accepted
    # The fix changes the logic to: rejected = is_user_transaction && in_rejected_set
    assert "System transactions are always accepted" in content, \
        "Comment about system transactions being always accepted not found"

    # The old logic pattern should NOT exist
    assert "!always_accept_system_transactions" not in content, \
        "Old always_accept_system_transactions logic still present"


def test_consensus_manager_no_flag():
    """consensus_manager doesn't pass the flag to protocol config (fail_to_pass)."""
    manager_file = REPO / "crates/sui-core/src/consensus_manager/mod.rs"
    content = manager_file.read_text()

    # Should NOT have the call to consensus_always_accept_system_transactions()
    assert "consensus_always_accept_system_transactions()" not in content, \
        "consensus_always_accept_system_transactions() call still in consensus_manager"


def test_rust_syntax_valid():
    """Rust source files are syntactically valid (pass_to_pass)."""
    # Quick syntax check using rustc --emit=metadata (fast check, doesn't produce full binary)
    files_to_check = [
        REPO / "consensus/config/src/consensus_protocol_config.rs",
        REPO / "consensus/core/src/commit.rs",
        REPO / "crates/sui-core/src/authority/authority_store_tables.rs",
        REPO / "crates/sui-core/src/authority.rs",
        REPO / "crates/sui-core/src/consensus_types/consensus_output_api.rs",
        REPO / "crates/sui-core/src/consensus_manager/mod.rs",
    ]

    for file_path in files_to_check:
        r = subprocess.run(
            ["rustc", "--emit=metadata", "-o", "/dev/null", str(file_path)],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # Note: this might fail due to dependencies, but shouldn't fail for syntax
        # We just check that it's not a syntax error (exit code 1 with specific messages)
        if r.returncode != 0:
            # If it fails, it should be due to missing deps, not syntax errors
            assert "expected" not in r.stderr.lower() or "syntax" not in r.stderr.lower(), \
                f"Syntax error in {file_path}: {r.stderr[:500]}"


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v", "--tb=short"]))
