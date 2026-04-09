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
    stdout, rc, stderr = _openssl(
        "x509", "-in", CERT, "-noout", "-checkend", "0"
    )
    assert rc == 0, f"Certificate is expired or invalid: {stdout}\n{stderr}"


# [pr_diff] fail_to_pass
def test_cert_long_validity():
    """Certificate must be valid for at least 5 years from now (not just 1 year)."""
    stdout, _, _ = _openssl("x509", "-in", CERT, "-noout", "-enddate")
    # stdout is like "notAfter=Mar 14 22:22:20 2126 GMT"
    assert "notAfter=" in stdout, f"Could not parse end date: {stdout}"
    date_str = stdout.split("notAfter=", 1)[1].strip()
    # Parse the date: "Mar 14 22:22:20 2126 GMT"
    not_after = datetime.strptime(date_str, "%b %d %H:%M:%S %Y %Z").replace(
        tzinfo=timezone.utc
    )
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
    assert issuer == subject, (
        f"Certificate is not self-signed.\nIssuer:  {issuer}\nSubject: {subject}"
    )
