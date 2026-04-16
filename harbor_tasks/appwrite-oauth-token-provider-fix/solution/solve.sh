#!/bin/bash
set -e

cd /workspace/appwrite

# Check if already applied (idempotency)
if grep -q "Attempt to decode secret as a JWT" app/controllers/api/account.php; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/app/controllers/api/account.php b/app/controllers/api/account.php
index 6d33b45f0ba..3d7db8f4576 100644
--- a/app/controllers/api/account.php
+++ b/app/controllers/api/account.php
@@ -209,6 +209,22 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr

 $createSession = function (string $userId, string $secret, Request $request, Response $response, User $user, Database $dbForProject, Document $project, array $platform, Locale $locale, Reader $geodb, Event $queueForEvents, Mail $queueForMails, Store $store, ProofsToken $proofForToken, ProofsCode $proofForCode, Authorization $authorization) {

+    // Attempt to decode secret as a JWT (used by OAuth2 token flow to carry provider info)
+    $oauthProvider = null;
+    try {
+        $jwtDecoder = new JWT(System::getEnv('_APP_OPENSSL_KEY_V1'), 'HS256', 60, 0);
+        $payload = $jwtDecoder->decode($secret);
+
+        if (empty($payload['provider'])) {
+            throw new Exception(Exception::USER_INVALID_TOKEN);
+        }
+
+        $oauthProvider = $payload['provider'];
+        $secret = $payload['secret'];
+    } catch (\Ahc\Jwt\JWTException) {
+        // Not a JWT — use secret as-is (non-OAuth flows)
+    }
+
     /** @var Appwrite\Utopia\Database\Documents\User $userFromRequest */
     $userFromRequest = $authorization->skip(fn () => $dbForProject->getDocument('users', $userId));

@@ -220,6 +236,12 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
         ?: $userFromRequest->tokenVerify(null, $secret, $proofForCode);

     if (!$verifiedToken) {
+        // Could mean invalid/expired JWT, or expired secret
+        throw new Exception(Exception::USER_INVALID_TOKEN);
+    }
+
+    // OAuth2 tokens must have a provider from the JWT
+    if ($verifiedToken->getAttribute('type') === TOKEN_TYPE_OAUTH2 && $oauthProvider === null) {
         throw new Exception(Exception::USER_INVALID_TOKEN);
     }

@@ -245,7 +267,7 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
         TOKEN_TYPE_INVITE => SESSION_PROVIDER_EMAIL,
         TOKEN_TYPE_MAGIC_URL => SESSION_PROVIDER_MAGIC_URL,
         TOKEN_TYPE_PHONE => SESSION_PROVIDER_PHONE,
-        TOKEN_TYPE_OAUTH2 => SESSION_PROVIDER_OAUTH2,
+        TOKEN_TYPE_OAUTH2 => $oauthProvider,
         default => SESSION_PROVIDER_TOKEN,
     };
     $session = new Document(array_merge(
@@ -1899,7 +1921,12 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
                 ->setParam('tokenId', $token->getId())
             ;

-            $query['secret'] = $secret;
+            // Wrap secret in a JWT that also carries the provider name
+            $jwtEncoder = new JWT(System::getEnv('_APP_OPENSSL_KEY_V1'), 'HS256', 60, 0);
+            $query['secret'] = $jwtEncoder->encode([
+                'secret' => $secret,
+                'provider' => $provider,
+            ]);
             $query['userId'] = $user->getId();

             // If the `token` param is not set, we persist the session in a cookie
PATCH

echo "Patch applied successfully!"
