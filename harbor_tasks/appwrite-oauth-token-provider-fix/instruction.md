# Fix OAuth2 Token Flow Provider Name

## Problem

When using the OAuth2 **token flow** (where a secret is returned via callback URL and then exchanged for a session), the session provider is set to a generic OAuth2 value instead of the specific provider name (e.g., 'google', 'github', 'mock').

In contrast, the OAuth2 **session flow** (where the session is created directly via cookie) correctly preserves the provider name.

## Expected Behavior

When a user authenticates via Google OAuth2 using the token flow, the session should show the correct provider name (e.g., 'google'), not a generic OAuth2 value. Both OAuth2 flows should preserve and use the specific provider name when creating sessions.

## Verification Criteria

Your implementation is correct when all of the following pass:

1. **PHP syntax validation** passes (`php -l` on the modified file)

2. **Composer configuration** is valid (`composer validate --no-check-publish`)

3. **Composer audit** passes with no security issues (`composer audit --no-dev`)

4. **JWT encoding in OAuth callback**: The OAuth callback handler must encode the secret as a JWT that includes both a `secret` field and a `provider` field. The JWT library from the `Ahc` namespace should be imported and used.

5. **JWT decoding in createSession**: The `createSession` function must decode the secret as a JWT to extract the provider name. This requires using a `$jwtDecoder` variable, a `$payload` variable, and a call to the decoder's `->decode()` method. The decoded payload must be validated with `empty()` to ensure the `provider` field is present. The extracted provider is stored in a variable (such as `$oauthProvider`) for use in session creation.

6. **Provider variable mapping**: The `TOKEN_TYPE_OAUTH2` entry in the session provider mapping must use the provider extracted from the JWT (not a generic constant like `SESSION_PROVIDER_OAUTH2`).

7. **OAuth provider validation**: The code must validate that when `TOKEN_TYPE_OAUTH2` is used, the provider extracted from the JWT is not null. This involves a `$verifiedToken` variable.

8. **PHP syntax** checks pass for all controller files and src/ files

## Technical Context

The `Ahc\Jwt\JWT` class is available in the Appwrite codebase for JWT signing and verification. The environment variable `_APP_OPENSSL_KEY_V1` holds the signing key. The file to modify is `app/controllers/api/account.php`.
