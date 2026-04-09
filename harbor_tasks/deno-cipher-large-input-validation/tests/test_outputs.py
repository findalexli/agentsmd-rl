"""
Task: deno-cipher-large-input-validation
Repo: deno @ 8295a2cf2aabe2ecd9ccce8a802d0d5d61095a2e
PR:   33201

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.

Note: Deno polyfills are compiled into the Deno binary (Rust build).
Triggering the bug requires allocating a 2GB+ buffer, which is impractical
in a Docker CI environment. Source analysis is used for f2p tests since
building Deno from source requires ~30 min Rust compilation.
"""

import re
from pathlib import Path

REPO = "/workspace/deno"
CIPHER_FILE = f"{REPO}/ext/node/polyfills/internal/crypto/cipher.ts"

# Threshold patterns representing 2^31 - 1 (INT_MAX for 32-bit signed int)
_THRESHOLD_PATTERNS = [
    r"2\s*\*\*\s*31\s*-\s*1",                       # 2 ** 31 - 1
    r"2147483647",                                     # decimal literal
    r"0x[0]?7[Ff]{7}",                                # hex 0x7FFFFFFF
    r"Math\.pow\s*\(\s*2\s*,\s*31\s*\)\s*-\s*1",     # Math.pow(2, 31) - 1
]
_THRESHOLD_RE = "|".join(f"(?:{p})" for p in _THRESHOLD_PATTERNS)


def _read_cipher_source():
    return Path(CIPHER_FILE).read_text()


def _extract_update_body(source: str, class_name: str) -> str:
    """Extract the body of <ClassName>.prototype.update from cipher.ts."""
    pattern = rf"{class_name}\.prototype\.update\s*=\s*function\s*\("
    match = re.search(pattern, source)
    assert match, f"Could not find {class_name}.prototype.update in cipher.ts"

    brace_pos = source.index("{", match.end())
    depth = 1
    i = brace_pos + 1
    while i < len(source) and depth > 0:
        if source[i] == "{":
            depth += 1
        elif source[i] == "}":
            depth -= 1
        i += 1

    return source[brace_pos:i]


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cipheriv_update_rejects_large_input():
    """Cipheriv.prototype.update must check buffer size >= 2^31-1 and throw."""
    source = _read_cipher_source()
    body = _extract_update_body(source, "Cipheriv")

    check_re = rf"\.(?:length|byteLength)\s*>=\s*(?:{_THRESHOLD_RE})"
    assert re.search(check_re, body), (
        "Cipheriv.prototype.update must reject inputs with length >= 2^31-1 "
        "(INT_MAX). No size boundary check found."
    )


# [pr_diff] fail_to_pass
def test_decipheriv_update_rejects_large_input():
    """Decipheriv.prototype.update must check buffer size >= 2^31-1 and throw."""
    source = _read_cipher_source()
    body = _extract_update_body(source, "Decipheriv")

    check_re = rf"\.(?:length|byteLength)\s*>=\s*(?:{_THRESHOLD_RE})"
    assert re.search(check_re, body), (
        "Decipheriv.prototype.update must reject inputs with length >= 2^31-1 "
        "(INT_MAX). No size boundary check found."
    )


# [pr_diff] fail_to_pass
def test_error_message_matches_nodejs():
    """Both cipher/decipher must throw 'Trying to add data in unsupported state'."""
    source = _read_cipher_source()
    expected_msg = "Trying to add data in unsupported state"

    cipher_body = _extract_update_body(source, "Cipheriv")
    assert expected_msg in cipher_body, (
        f"Cipheriv.prototype.update must throw with Node.js-compatible message: "
        f"'{expected_msg}'"
    )

    decipher_body = _extract_update_body(source, "Decipheriv")
    assert expected_msg in decipher_body, (
        f"Decipheriv.prototype.update must throw with Node.js-compatible message: "
        f"'{expected_msg}'"
    )


# [pr_diff] fail_to_pass
def test_size_check_before_encrypt_call():
    """Size check must appear before the encrypt/decrypt op call in both functions."""
    source = _read_cipher_source()

    # Cipheriv: threshold check must precede op_node_cipheriv_encrypt
    cipher_body = _extract_update_body(source, "Cipheriv")
    threshold_match = re.search(_THRESHOLD_RE, cipher_body)
    encrypt_match = re.search(r"op_node_cipheriv_encrypt", cipher_body)
    assert threshold_match and encrypt_match, (
        "Cipheriv.prototype.update must have both size check and encrypt op call"
    )
    assert threshold_match.start() < encrypt_match.start(), (
        "Size check must appear before op_node_cipheriv_encrypt call"
    )

    # Decipheriv: threshold check must precede op_node_decipheriv_decrypt
    decipher_body = _extract_update_body(source, "Decipheriv")
    threshold_match = re.search(_THRESHOLD_RE, decipher_body)
    decrypt_match = re.search(r"op_node_decipheriv_decrypt", decipher_body)
    assert threshold_match and decrypt_match, (
        "Decipheriv.prototype.update must have both size check and decrypt op call"
    )
    assert threshold_match.start() < decrypt_match.start(), (
        "Size check must appear before op_node_decipheriv_decrypt call"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — structural integrity
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cipher_file_structure():
    """cipher.ts must define both Cipheriv and Decipheriv with update methods."""
    source = _read_cipher_source()

    assert re.search(
        r"Cipheriv\.prototype\.update\s*=\s*function", source
    ), "Cipheriv.prototype.update must be defined"

    assert re.search(
        r"Decipheriv\.prototype\.update\s*=\s*function", source
    ), "Decipheriv.prototype.update must be defined"

    # Both update methods must still check _finalized state
    cipher_body = _extract_update_body(source, "Cipheriv")
    assert "this._finalized" in cipher_body, (
        "Cipheriv.prototype.update must retain the _finalized state check"
    )

    decipher_body = _extract_update_body(source, "Decipheriv")
    assert "this._finalized" in decipher_body, (
        "Decipheriv.prototype.update must retain the _finalized state check"
    )
