"""Tests for Sui protocol gate coin reservation PR #26088."""

import subprocess
import sys
import re

REPO = "/workspace/sui"


def test_patch_applied():
    """Verify the protocol gate fix is applied (fail-to-pass)."""
    # Check that the coin reservation validation exists in authority.rs
    authority_file = f"{REPO}/crates/sui-core/src/authority.rs"
    with open(authority_file, 'r') as f:
        content = f.read()

    # Look for the protocol gate validation
    assert "enable_coin_reservation_obj_refs" in content, \
        "Missing protocol config check for coin reservation"
    assert "is_coin_reservation_digest" in content, \
        "Missing coin reservation digest check"
    assert "coin reservations in gas payment are not supported" in content, \
        "Missing error message for unsupported coin reservations"


def test_select_gas_signature_updated():
    """Verify select_gas function accepts protocol_config parameter (fail-to-pass)."""
    simulate_mod = f"{REPO}/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs"
    with open(simulate_mod, 'r') as f:
        content = f.read()

    # Check that select_gas now takes protocol_config parameter
    # The function signature should be: fn select_gas(..., protocol_config: &ProtocolConfig)
    pattern = r"fn select_gas\([^)]*protocol_config:\s*&ProtocolConfig"
    assert re.search(pattern, content), \
        "select_gas function should accept protocol_config parameter"

    # Check that protocol_config.enable_coin_reservation_obj_refs() is called in select_gas
    assert "protocol_config.enable_coin_reservation_obj_refs()" in content, \
        "select_gas should check enable_coin_reservation_obj_refs protocol flag"


def test_protocol_gate_logic():
    """Verify the protocol gate logic is correctly implemented (fail-to-pass)."""
    simulate_mod = f"{REPO}/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs"
    with open(simulate_mod, 'r') as f:
        content = f.read()

    # The fix adds: if protocol_config.enable_coin_reservation_obj_refs() && gas_coin_used ...
    # This should be checked BEFORE the coin reservation logic
    lines = content.split('\n')

    # Find the line with enable_coin_reservation_obj_refs in the select_gas function
    found_gate = False
    for i, line in enumerate(lines):
        if 'protocol_config.enable_coin_reservation_obj_refs()' in line:
            # Check it's part of a condition with gas_coin_used
            # Look at surrounding lines for context
            context = '\n'.join(lines[max(0, i-2):min(len(lines), i+5)])
            if 'gas_coin_used' in context:
                found_gate = True
                break

    assert found_gate, \
        "Protocol gate should check enable_coin_reservation_obj_refs before using coin reservation"


def test_call_site_updated():
    """Verify the call site in simulate_transaction passes protocol_config (fail-to-pass)."""
    simulate_mod = f"{REPO}/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs"
    with open(simulate_mod, 'r') as f:
        content = f.read()

    # The call to select_gas should pass &protocol_config instead of just max_gas_payment_objects
    # Look for: select_gas(service, &mut transaction, &protocol_config)?
    pattern = r"select_gas\([^)]*&protocol_config\)"
    assert re.search(pattern, content), \
        "simulate_transaction should pass &protocol_config to select_gas"


def test_files_readable():
    """Verify modified files are readable and non-empty (pass-to-pass)."""
    # Check authority.rs
    authority_file = f"{REPO}/crates/sui-core/src/authority.rs"
    with open(authority_file, 'r') as f:
        content = f.read()
    assert len(content) > 0, "authority.rs should be non-empty"

    # Check simulate/mod.rs
    simulate_mod = f"{REPO}/crates/sui-rpc-api/src/grpc/v2/transaction_execution_service/simulate/mod.rs"
    with open(simulate_mod, 'r') as f:
        content = f.read()
    assert len(content) > 0, "simulate/mod.rs should be non-empty"
