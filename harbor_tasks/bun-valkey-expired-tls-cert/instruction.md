# Fix Expired TLS Certificate for Valkey Tests

## Problem

The TLS certificate used by the Valkey Docker test environment has expired. When running tests that require a TLS connection to Valkey, the connection fails because the certificate at `test/js/valkey/docker-unified/server.crt` is no longer valid (its `notAfter` date is in the past). The corresponding private key is at `test/js/valkey/docker-unified/server.key`.

## Expected Behavior

Generate a new self-signed TLS certificate and private key pair to replace the expired files. The new certificate must meet the following requirements:

- **File locations**: `test/js/valkey/docker-unified/server.crt` and `test/js/valkey/docker-unified/server.key`
- **Key algorithm**: RSA 2048-bit
- **Signature algorithm**: sha256WithRSAEncryption
- **Common Name (CN)**: `localhost`
- **Subject Alternative Name (SAN)**: must include `DNS:localhost`
- **Self-signed**: The issuer must match the subject (both CN=localhost)
- **Validity period**: At least 5 years from now (not just 1 year)
- **Certificate version**: X.509 v3 (required for TLS extensions)
- **Format**: Valid PEM format for both certificate and key

The existing `test/js/valkey/docker-unified/redis.conf` and `test/js/valkey/docker-unified/Dockerfile` reference these certificate files and should continue to work once the new certificate/key are in place. The certificate must be valid for SSL server use.
