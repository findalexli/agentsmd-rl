# Reject EST simple re-enroll requests authenticated with a revoked client certificate

## Context

Infisical's PKI module exposes [EST (RFC 7030)](https://datatracker.ietf.org/doc/html/rfc7030) endpoints under `/v3` so PKI-managed devices can renew their X.509 certificates programmatically. The `simplereenroll` endpoint (the EST v3 service's `simpleReenrollByProfile` operation) accepts a CSR plus the client's existing certificate via mTLS — only the existing certificate's holder may rotate it.

There is a security gap in the current re-enrollment flow: a client that authenticates with a certificate whose **stored database status is `revoked`** is permitted to obtain a freshly signed certificate. Because EST re-enroll trusts the inbound certificate solely to identify the requester, a previously revoked subscriber can use the old (yet still cryptographically valid) certificate to undo the revocation and regain access.

## Bug to fix

`simpleReenrollByProfile` in the EST v3 service (`backend/src/services/certificate-est-v3/`) does not consult the `certificate` table to verify that the inbound client certificate is still active. It must reject re-enrollment whenever the certificate's stored status is revoked.

## Required behaviour

When `simpleReenrollByProfile` is invoked with a client certificate whose corresponding row in the `certificate` table has `status = "revoked"` (the `CertStatus.REVOKED` value from `@app/services/certificate/certificate-types`), the service must:

1. **Throw `UnauthorizedError`** (the class exported from `@app/lib/errors`) — not `BadRequestError`, `ForbiddenRequestError`, or any other error class.
2. **Not invoke the certificate-signing service** (`certificateV3Service.signCertificateFromProfile`) for that request — the signing operation must be short-circuited before it runs.

The check must run **before** the existing CSR-subject and approval-required validations, so a revoked-cert request fails fast with the authorisation error rather than a CSR or approval error.

When the lookup returns no row (no matching certificate found) or returns a row whose status is anything other than `revoked` (e.g. `active`, `expired`), the existing flow must continue unchanged — including the existing approval-required path and the existing subject-mismatch path.

## Wiring constraint

The EST v3 service is constructed via the manual DI pattern documented in `backend/CLAUDE.md` ("Service Factory + Manual DI"). The factory currently destructures dependencies such as `certificateV3Service`, `certificateAuthorityDAL`, `certificateAuthorityCertDAL`, `projectDAL`, etc. To consult certificate status, the factory must accept an additional dependency named `certificateDAL` (the certificate table's DAL — `TCertificateDALFactory` from `@app/services/certificate/certificate-dal`) exposing at least `findOne` and `transaction`.

That new dependency must also be wired in `backend/src/server/routes/index.ts` where the EST v3 service is instantiated, so the factory call passes the project's `certificateDAL` instance through.

## Replica-lag guarantee

Per the "Read replica pattern" rule in `backend/CLAUDE.md`, ordinary DAL reads use `db.replicaNode()` and may lag behind the primary. A certificate that was revoked moments ago might still appear `active` on a replica, defeating the check. Run the lookup inside `certificateDAL.transaction(...)` so the read is forced onto the primary connection. Pass the transaction handle (`tx`) into `findOne` so it threads through the same connection.

## Lookup criteria

Look up the certificate by both its serial number (extracted from the parsed inbound client certificate via `cert.serialNumber`) and the CA id of the EST profile (`profile.caId`). Querying on serial number alone is insufficient — different CAs can issue certificates that share a serial.

## Out of scope

- Do not change the behaviour of `simpleEnrollByProfile` (the *initial* enroll path) or `getCaCertsByProfile`.
- Do not add new routes, migrations, queues, or DALs.
- Do not change the existing approval-required or CSR-subject-mismatch behaviour for non-revoked certificates.
