# Fix OAuth2 Token Flow Provider Name

## Problem

When using the OAuth2 **token flow** (where a secret is returned via callback URL and then exchanged for a session), the session provider is set to a generic OAuth2 value instead of the specific provider name (e.g., 'google', 'github', 'mock').

In contrast, the OAuth2 **session flow** (where the session is created directly via cookie) correctly preserves the provider name.

## Expected Behavior

When a user authenticates via Google OAuth2 using the token flow, the session should show the correct provider name (e.g., 'google'), not a generic OAuth2 value. Both OAuth2 flows should preserve and use the specific provider name when creating sessions.

## Technical Context

The `Ahc\Jwt\JWT` class is available in the Appwrite codebase for JWT signing and verification. The environment variable `_APP_OPENSSL_KEY_V1` holds the signing key. The file to modify is `app/controllers/api/account.php`.

The OAuth callback handler encodes a secret into the token. When the token is redeemed to create a session, the provider name must be extracted from the token and used as the session provider, not a generic constant.

## Verification Criteria

Your implementation is correct when all of the following pass:

1. **PHP syntax validation** passes (`php -l` on the modified file)

2. **Composer configuration** is valid (`composer validate --no-check-publish`)

3. **Composer audit** passes with no security issues (`composer audit --no-dev`)

4. **PHP syntax** checks pass for all controller files and src/ files

5. **JWT encoding in OAuth callback**: The OAuth callback handler must wrap the secret in a JWT that contains both the secret value and the provider name.

6. **JWT decoding in createSession**: The `createSession` function must decode the secret as a JWT to extract the provider name and secret value.

7. **Provider variable mapping**: The `TOKEN_TYPE_OAUTH2` case in the session provider mapping must use the provider extracted from the JWT (not a generic constant).

8. **OAuth provider validation**: The code must validate that when `TOKEN_TYPE_OAUTH2` is used, the provider extracted from the JWT is not null.