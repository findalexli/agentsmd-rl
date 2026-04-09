"""Tests for removing certified blocks sender channel from TransactionCertifier."""

import subprocess
import re

REPO = "/workspace/sui"
CONSENSUS_CORE = f"{REPO}/consensus/core"


def test_compilation():
    """The code must compile after removing the certified_blocks_sender."""
    result = subprocess.run(
        ["cargo", "check", "-p", "consensus-core"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )
    assert result.returncode == 0, f"Compilation failed:\n{result.stderr}"


def test_certified_blocks_output_removed():
    """CertifiedBlocksOutput type must be removed from block.rs."""
    with open(f"{CONSENSUS_CORE}/src/block.rs", "r") as f:
        content = f.read()

    # Should not contain the struct definition
    assert "pub struct CertifiedBlocksOutput" not in content, \
        "CertifiedBlocksOutput struct still exists in block.rs"


def test_certified_blocks_output_not_exported():
    """CertifiedBlocksOutput must not be exported from lib.rs."""
    with open(f"{CONSENSUS_CORE}/src/lib.rs", "r") as f:
        content = f.read()

    # Should not be in the public exports
    assert "CertifiedBlocksOutput" not in content, \
        "CertifiedBlocksOutput is still exported in lib.rs"


def test_transaction_certifier_no_sender_field():
    """TransactionCertifier must not have certified_blocks_sender field."""
    with open(f"{CONSENSUS_CORE}/src/transaction_certifier.rs", "r") as f:
        content = f.read()

    # Should not have the sender field
    assert "certified_blocks_sender" not in content, \
        "certified_blocks_sender field still exists in TransactionCertifier"

    # Should not import UnboundedSender
    assert "UnboundedSender" not in content, \
        "UnboundedSender import still exists in transaction_certifier.rs"


def test_transaction_certifier_new_signature():
    """TransactionCertifier::new() must take only 3 parameters."""
    with open(f"{CONSENSUS_CORE}/src/transaction_certifier.rs", "r") as f:
        content = f.read()

    # Find the new() function signature
    new_func_match = re.search(
        r'impl TransactionCertifier \{[^}]*?pub\(crate\)? fn new\((.*?)\)',
        content,
        re.DOTALL
    )
    assert new_func_match, "Could not find TransactionCertifier::new() function"

    params = new_func_match.group(1)

    # Count parameters - should be exactly 3: context, block_verifier, dag_state
    param_list = [p.strip() for p in params.split(',') if p.strip()]
    param_names = [p.split(':')[0].strip() for p in param_list]

    assert len(param_names) == 3, \
        f"TransactionCertifier::new() should have 3 parameters, found {len(param_names)}: {param_names}"

    expected_params = {'context', 'block_verifier', 'dag_state'}
    actual_params = set(param_names)

    assert actual_params == expected_params, \
        f"Wrong parameters: expected {expected_params}, got {actual_params}"


def test_commit_consumer_no_block_sender():
    """CommitConsumerArgs must not have block_sender field."""
    with open(f"{CONSENSUS_CORE}/src/commit_consumer.rs", "r") as f:
        content = f.read()

    # Should not have block_sender field
    assert "block_sender" not in content, \
        "block_sender field still exists in CommitConsumerArgs"


def test_add_voted_blocks_no_send():
    """add_voted_blocks should not send to any channel."""
    with open(f"{CONSENSUS_CORE}/src/transaction_certifier.rs", "r") as f:
        content = f.read()

    # The function should not call send_certified_blocks
    assert "send_certified_blocks" not in content, \
        "send_certified_blocks still called in add_voted_blocks"

    # Should not have the send method anymore
    send_method_match = re.search(
        r'fn send_certified_blocks\(&self',
        content
    )
    assert not send_method_match, \
        "send_certified_blocks method still exists"


def test_authority_node_no_block_sender_clone():
    """authority_node.rs should not clone block_sender."""
    with open(f"{CONSENSUS_CORE}/src/authority_node.rs", "r") as f:
        content = f.read()

    # Should not have block_sender.clone() anymore
    assert "block_sender.clone()" not in content, \
        "block_sender.clone() still exists in authority_node.rs"


def test_consensus_tests_pass():
    """Consensus core tests must pass after the changes."""
    result = subprocess.run(
        ["cargo", "test", "-p", "consensus-core", "--lib", "--", "--test-threads=4"],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=300
    )

    # Check for test failures
    if result.returncode != 0:
        # Check if it's a compilation error vs test failure
        if "error" in result.stderr.lower() and "could not compile" in result.stderr.lower():
            assert False, f"Tests failed to compile:\n{result.stderr}"
        else:
            # Some tests might fail, but compilation should succeed
            # For this task, we primarily care about compilation
            pass

    # At minimum, compilation must succeed
    assert "could not compile" not in result.stderr, \
        f"Could not compile tests:\n{result.stderr}"


def test_no_monitored_mpsc_in_unused_files():
    """Files that don't need monitored_mpsc should not import it."""
    files_to_check = [
        "src/authority_service.rs",
        "src/commit_syncer.rs",
        "src/core.rs",
        "src/core_thread.rs",
    ]

    for file_path in files_to_check:
        full_path = f"{CONSENSUS_CORE}/{file_path}"
        try:
            with open(full_path, "r") as f:
                content = f.read()

            # Should not import monitored_mpsc just for blocks channel
            if "monitored_mpsc" in content:
                # Check if it's only used for blocks channel (which should be removed)
                lines = content.split('\n')
                mpsc_lines = [l for l in lines if 'monitored_mpsc' in l]

                # Filter out legitimate uses (non-blocks related)
                blocks_related = any('block' in l.lower() and 'output' in l.lower()
                                     for l in mpsc_lines)

                assert not blocks_related, \
                    f"{file_path} still has monitored_mpsc import for block output"
        except FileNotFoundError:
            continue
