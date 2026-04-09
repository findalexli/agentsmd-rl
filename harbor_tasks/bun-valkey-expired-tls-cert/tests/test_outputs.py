"""
Task: bun-valkey-expired-tls-cert
Repo: oven-sh/bun @ c99fd9d1e17ec73ce4c0edd1c49f34be8e8edc25
PR:   28974

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

import subprocess
from datetime import datetime, timezone
from pathlib import Path

REPO = "/workspace/bun"
CERT = f"{REPO}/test/js/valkey/docker-unified/server.crt"
KEY = f"{REPO}/test/js/valkey/docker-unified/server.key"


def _openssl(*args):
    """Run openssl command and return stdout."""
    r = subprocess.run(
        ["openssl", *args],
        capture_output=True, text=True, timeout=30,
    )
    return r.stdout.strip(), r.returncode, r.stderr.strip()


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_cert_not_expired():
    """Certificate must not be expired (notAfter must be in the future)."""
    stdout, rc, stderr = _openssl("x509", "-in", CERT, "-noout", "-checkend", "0")
    assert rc == 0, f"Certificate is expired or invalid: {stdout}\n{stderr}"


# [pr_diff] fail_to_pass
def test_cert_long_validity():
    """Certificate must be valid for at least 5 years from now (not just 1 year)."""
    stdout, _, _ = _openssl("x509", "-in", CERT, "-noout", "-enddate")
    # stdout is like "notAfter=Mar 14 22:22:20 2126 GMT"
    assert "notAfter=" in stdout, f"Could not parse end date: {stdout}"
    date_str = stdout.split("notAfter=", 1)[1].strip()
    # Parse the date: "Mar 14 22:22:20 2126 GMT"
    not_after = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(tzinfo=timezone.utc)
    now = datetime.now(timezone.utc)
    remaining_years = (not_after - now).days / 365.25
    assert remaining_years >= 5, (
        f"Certificate validity too short: {remaining_years:.1f} years remaining "
        f"(expires {date_str})"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests / static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_cert_cn_localhost():
    """Certificate CN must be 'localhost'."""
    stdout, _, _ = _openssl("x509", "-in", CERT, "-noout", "-subject")
    assert "CN = localhost" in stdout or "CN=localhost" in stdout, (
        f"Certificate CN is not localhost: {stdout}"
    )


# [static] pass_to_pass
def test_cert_san_localhost():
    """Certificate must include SAN DNS:localhost."""
    stdout, _, _ = _openssl("x509", "-in", CERT, "-noout", "-ext", "subjectAltName")
    assert "DNS:localhost" in stdout, (
        f"Certificate SAN does not include DNS:localhost: {stdout}"
    )


# [static] pass_to_pass
def test_key_matches_cert():
    """Private key modulus must match certificate modulus."""
    cert_mod, _, _ = _openssl("x509", "-in", CERT, "-noout", "-modulus")
    key_mod, _, _ = _openssl("rsa", "-in", KEY, "-noout", "-modulus")
    assert cert_mod == key_mod, (
        f"Certificate and key moduli do not match.\n"
        f"Cert: {cert_mod[:60]}...\nKey:  {key_mod[:60]}..."
    )


# [static] pass_to_pass
def test_cert_self_signed():
    """Certificate issuer must match subject (self-signed)."""
    issuer, _, _ = _openssl("x509", "-in", CERT, "-noout", "-issuer")
    subject, _, _ = _openssl("x509", "-in", CERT, "-noout", "-subject")
    # Strip the "issuer=" and "subject=" prefixes for comparison
    issuer_val = issuer.replace("issuer=", "").strip() if issuer.startswith("issuer=") else issuer
    subject_val = subject.replace("subject=", "").strip() if subject.startswith("subject=") else subject
    assert issuer_val == subject_val, (
        f"Certificate is not self-signed.\nIssuer:  {issuer}\nSubject: {subject}"
    )


# ---------------------------------------------------------------------------
# Pass-to-pass (repo_tests) — Repository structure and file validity checks
# ---------------------------------------------------------------------------

# [repo_tests] pass_to_pass
def test_cert_file_exists():
    """TLS certificate file must exist in the expected location."""
    assert Path(CERT).exists(), f"Certificate file not found: {CERT}"


# [repo_tests] pass_to_pass
def test_key_file_exists():
    """TLS private key file must exist in the expected location."""
    assert Path(KEY).exists(), f"Private key file not found: {KEY}"


# [repo_tests] pass_to_pass
def test_cert_valid_pem_format():
    """Certificate must be a valid PEM format file."""
    r = subprocess.run(
        ["openssl", "x509", "-in", CERT, "-noout"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Certificate is not valid PEM format: {r.stderr}"


# [repo_tests] pass_to_pass
def test_key_valid_pem_format():
    """Private key must be a valid PEM format file."""
    r = subprocess.run(
        ["openssl", "rsa", "-in", KEY, "-noout"],
        capture_output=True, text=True, timeout=30,
    )
    assert r.returncode == 0, f"Private key is not valid PEM format: {r.stderr}"


# [repo_tests] pass_to_pass
def test_cert_has_rsa_2048():
    """Certificate must use RSA 2048-bit key."""
    stdout, _, _ = _openssl("x509", "-in", CERT, "-noout", "-text")
    assert "RSA Public-Key: (2048 bit)" in stdout or "Public-Key: (2048 bit)" in stdout, (
        f"Certificate does not use RSA 2048-bit key"
    )


# [repo_tests] pass_to_pass
def test_cert_sig_sha256():
    """Certificate must use sha256WithRSAEncryption signature algorithm."""
    stdout, _, _ = _openssl("x509", "-in", CERT, "-noout", "-text")
    assert "sha256WithRSAEncryption" in stdout, (
        f"Certificate does not use sha256WithRSAEncryption signature"
    )


# [repo_tests] pass_to_pass
def test_repo_files_unchanged():
    """Test that other repo files (besides the cert/key) are not modified."""
    # Check that the Dockerfile in the same directory exists and is readable
    dockerfile = Path(f"{REPO}/test/js/valkey/docker-unified/Dockerfile")
    assert dockerfile.exists(), "Dockerfile should exist"
    # Check that redis.conf exists
    redis_conf = Path(f"{REPO}/test/js/valkey/docker-unified/redis.conf")
    assert redis_conf.exists(), "redis.conf should exist"


# [repo_tests] pass_to_pass
def test_cert_not_empty():
    """Certificate file must not be empty."""
    cert_path = Path(CERT)
    assert cert_path.stat().st_size > 500, "Certificate file is too small or empty"


# [repo_tests] pass_to_pass
def test_key_not_empty():
    """Private key file must not be empty."""
    key_path = Path(KEY)
    assert key_path.stat().st_size > 500, "Private key file is too small or empty"


# [repo_tests] pass_to_pass
def test_redis_conf_valid():
    """Redis configuration file must exist and reference TLS files."""
    redis_conf = Path(f"{REPO}/test/js/valkey/docker-unified/redis.conf")
    assert redis_conf.exists(), "redis.conf should exist"
    content = redis_conf.read_text()
    # Basic validation: should contain required TLS settings
    assert "tls-cert-file" in content, "redis.conf should reference tls-cert-file"
    assert "tls-key-file" in content, "redis.conf should reference tls-key-file"


# [repo_tests] pass_to_pass
def test_valkey_dockerfile_valid():
    """Valkey Dockerfile must exist and reference certificate files."""
    dockerfile = Path(f"{REPO}/test/js/valkey/docker-unified/Dockerfile")
    assert dockerfile.exists(), "Dockerfile should exist"
    content = dockerfile.read_text()
    # Should reference the certificate files
    assert "server.crt" in content, "Dockerfile should reference server.crt"
    assert "server.key" in content, "Dockerfile should reference server.key"
