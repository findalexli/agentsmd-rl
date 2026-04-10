#!/bin/bash
set -e

# Target directory
REPO_DIR="/workspace/appwrite"

# Check if already patched (idempotency)
if grep -q "Http::setResource('cookieDomain', function (Request \$request, Document \$project)" "$REPO_DIR/app/init/resources.php" 2>/dev/null; then
    echo "Already patched, skipping"
    exit 0
fi

cd "$REPO_DIR"

# Apply the gold patch
cat <<'PATCH' | patch -p1
diff --git a/app/controllers/api/account.php b/app/controllers/api/account.php
index fb968d3972f..cbdf11225a4 100644
--- a/app/controllers/api/account.php
+++ b/app/controllers/api/account.php
@@ -207,7 +207,7 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
 }


-$createSession = function (string $userId, string $secret, Request $request, Response $response, User $user, Database $dbForProject, Document $project, array $platform, Locale $locale, Reader $geodb, Event $queueForEvents, Mail $queueForMails, Store $store, ProofsToken $proofForToken, ProofsCode $proofForCode, Authorization $authorization) {
+$createSession = function (string $userId, string $secret, Request $request, Response $response, User $user, Database $dbForProject, Document $project, array $platform, Locale $locale, Reader $geodb, Event $queueForEvents, Mail $queueForMails, Store $store, ProofsToken $proofForToken, ProofsCode $proofForCode, bool $domainVerification, ?string $cookieDomain, Authorization $authorization) {

     // Attempt to decode secret as a JWT (used by OAuth2 token flow to carry provider info)
     $oauthProvider = null;
@@ -345,7 +345,7 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
         ->setProperty('secret', $sessionSecret)
         ->encode();

-    if (!Config::getParam('domainVerification')) {
+    if (!$domainVerification) {
         $response->addHeader('X-Fallback-Cookies', \json_encode([$store->getKey() => $encoded]));
     }

@@ -353,8 +353,8 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     $protocol = $request->getProtocol();

     $response
-        ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-        ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'))
+        ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, null)
+        ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'))
         ->setStatusCode(Response::STATUS_CODE_CREATED);

     $countryName = $locale->getText('countries.' . strtolower($session->getAttribute('countryCode')), $locale->getText('locale.country.unknown'));
@@ -719,7 +719,9 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('queueForDeletes')
     ->inject('store')
     ->inject('proofForToken')
-    ->action(function (Request $request, Response $response, User $user, Database $dbForProject, Locale $locale, Event $queueForEvents, Delete $queueForDeletes, Store $store, ProofsToken $proofForToken) {
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
+    ->action(function (Request $request, Response $response, User $user, Database $dbForProject, Locale $locale, Event $queueForEvents, Delete $queueForDeletes, Store $store, ProofsToken $proofForToken, bool $domainVerification, ?string $cookieDomain) {

         $protocol = $request->getProtocol();
         $sessions = $user->getAttribute('sessions', []);
@@ -728,7 +730,7 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
         foreach ($sessions as $session) {/** @var Document $session */
             $dbForProject->deleteDocument('sessions', $session->getId());

-            if (!Config::getParam('domainVerification')) {
+            if (!$domainVerification) {
                 $response->addHeader('X-Fallback-Cookies', \json_encode([]));
             }

@@ -741,8 +743,8 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr

                 // If current session delete the cookies too
                 $response
-                    ->addCookie($store->getKey() . '_legacy', '', \time() - 3600, '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-                    ->addCookie($store->getKey(), '', \time() - 3600, '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'));
+                    ->addCookie($store->getKey() . '_legacy', '', \time() - 3600, '/', $cookieDomain, ('https' == $protocol), true, null)
+                    ->addCookie($store->getKey(), '', \time() - 3600, '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'));

                 // Use current session for events.
                 $currentSession = $session;
@@ -849,7 +851,9 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('queueForDeletes')
     ->inject('store')
     ->inject('proofForToken')
-    ->action(function (?string $sessionId, ?\DateTime $requestTimestamp, Request $request, Response $response, User $user, Database $dbForProject, Locale $locale, Event $queueForEvents, Delete $queueForDeletes, Store $store, ProofsToken $proofForToken) {
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
+    ->action(function (?string $sessionId, ?\DateTime $requestTimestamp, Request $request, Response $response, User $user, Database $dbForProject, Locale $locale, Event $queueForEvents, Delete $queueForDeletes, Store $store, ProofsToken $proofForToken, bool $domainVerification, ?string $cookieDomain) {

         $protocol = $request->getProtocol();
         $sessionId = ($sessionId === 'current')
@@ -875,13 +879,13 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
                     ->setAttribute('current', true)
                     ->setAttribute('countryName', $locale->getText('countries.' . strtolower($session->getAttribute('countryCode')), $locale->getText('locale.country.unknown')));

-                if (!Config::getParam('domainVerification')) {
+                if (!$domainVerification) {
                     $response->addHeader('X-Fallback-Cookies', \json_encode([]));
                 }

                 $response
-                    ->addCookie($store->getKey() . '_legacy', '', \time() - 3600, '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-                    ->addCookie($store->getKey(), '', \time() - 3600, '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'));
+                    ->addCookie($store->getKey() . '_legacy', '', \time() - 3600, '/', $cookieDomain, ('https' == $protocol), true, null)
+                    ->addCookie($store->getKey(), '', \time() - 3600, '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'));
             }

             $dbForProject->purgeCachedDocument('users', $user->getId());
@@ -1035,8 +1039,10 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('store')
     ->inject('proofForPassword')
     ->inject('proofForToken')
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
     ->inject('authorization')
-    ->action(function (string $email, string $password, Request $request, Response $response, User $user, Database $dbForProject, Document $project, array $platform, Locale $locale, Reader $geodb, Event $queueForEvents, Mail $queueForMails, Hooks $hooks, Store $store, ProofsPassword $proofForPassword, ProofsToken $proofForToken, Authorization $authorization) {
+    ->action(function (string $email, string $password, Request $request, Response $response, User $user, Database $dbForProject, Document $project, array $platform, Locale $locale, Reader $geodb, Event $queueForEvents, Mail $queueForMails, Hooks $hooks, Store $store, ProofsPassword $proofForPassword, ProofsToken $proofForToken, bool $domainVerification, ?string $cookieDomain, Authorization $authorization) {
         $email = \strtolower($email);
         $protocol = $request->getProtocol();

@@ -1110,15 +1116,15 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
             ->setProperty('secret', $secret)
             ->encode();

-        if (!Config::getParam('domainVerification')) {
+        if (!$domainVerification) {
             $response->addHeader('X-Fallback-Cookies', \json_encode([$store->getKey() => $encoded]));
         }

         $expire = DateTime::formatTz(DateTime::addSeconds(new \DateTime(), $duration));

         $response
-            ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-            ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'))
+            ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, null)
+            ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'))
             ->setStatusCode(Response::STATUS_CODE_CREATED)
         ;

@@ -1184,8 +1190,10 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('store')
     ->inject('proofForPassword')
     ->inject('proofForToken')
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
     ->inject('authorization')
-    ->action(function (Request $request, Response $response, Locale $locale, User $user, Document $project, Database $dbForProject, Reader $geodb, Event $queueForEvents, Store $store, ProofsPassword $proofForPassword, ProofsToken $proofForToken, Authorization $authorization) {
+    ->action(function (Request $request, Response $response, Locale $locale, User $user, Document $project, Database $dbForProject, Reader $geodb, Event $queueForEvents, Store $store, ProofsPassword $proofForPassword, ProofsToken $proofForToken, bool $domainVerification, ?string $cookieDomain, Authorization $authorization) {
         $protocol = $request->getProtocol();

         if ('console' === $project->getId()) {
@@ -1276,15 +1284,15 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
             ->setProperty('secret', $secret)
             ->encode();

-        if (!Config::getParam('domainVerification')) {
+        if (!$domainVerification) {
             $response->addHeader('X-Fallback-Cookies', \json_encode([$store->getKey() => $encoded]));
         }

         $expire = DateTime::formatTz(DateTime::addSeconds(new \DateTime(), $duration));

         $response
-            ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-            ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'))
+            ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, null)
+            ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'))
             ->setStatusCode(Response::STATUS_CODE_CREATED)
         ;

@@ -1339,7 +1347,9 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('store')
     ->inject('proofForToken')
     ->inject('proofForCode')
-->inject('authorization')
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
+    ->inject('authorization')
     ->action($createSession);

 Http::get('/v1/account/sessions/oauth2/:provider')
@@ -1538,8 +1548,10 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('proofForPassword')
     ->inject('proofForToken')
     ->inject('plan')
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
     ->inject('authorization')
-    ->action(function (string $provider, string $code, string $state, string $error, string $error_description, Request $request, Response $response, Document $project, Validator $redirectValidator, Document $devKey, User $user, Database $dbForProject, Database $dbForPlatform, Reader $geodb, Event $queueForEvents, Store $store, ProofsPassword $proofForPassword, ProofsToken $proofForToken, array $plan, Authorization $authorization) use ($oauthDefaultSuccess) {
+    ->action(function (string $provider, string $code, string $state, string $error, string $error_description, Request $request, Response $response, Document $project, Validator $redirectValidator, Document $devKey, User $user, Database $dbForProject, Database $dbForPlatform, Reader $geodb, Event $queueForEvents, Store $store, ProofsPassword $proofForPassword, ProofsToken $proofForToken, array $plan, bool $domainVerification, ?string $cookieDomain, Authorization $authorization) use ($oauthDefaultSuccess) {
         $protocol = System::getEnv('_APP_OPTIONS_FORCE_HTTPS') === 'disabled' ? 'http' : 'https';
         $port = $request->getPort();
         $callbackBase = $protocol . '://' . $request->getHostname();
@@ -2055,7 +2067,7 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
                 ->setProperty('secret', $secret)
                 ->encode();

-            if (!Config::getParam('domainVerification')) {
+            if (!$domainVerification) {
                 $response->addHeader('X-Fallback-Cookies', \json_encode([$store->getKey() => $encoded]));
             }

@@ -2068,14 +2080,14 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
             // TODO: Remove this deprecated workaround - support only token
             if ($state['success']['path'] == $oauthDefaultSuccess) {
                 $query['project'] = $project->getId();
-                $query['domain'] = Config::getParam('cookieDomain');
+                $query['domain'] = $cookieDomain;
                 $query['key'] = $store->getKey();
                 $query['secret'] = $encoded;
             }

             $response
-                ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-                ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'));
+                ->addCookie($store->getKey() . '_legacy', $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, null)
+                ->addCookie($store->getKey(), $encoded, (new \DateTime($expire))->getTimestamp(), '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'));
         }

         if (isset($sessionUpgrade) && $sessionUpgrade && isset($session)) {
@@ -2886,11 +2898,13 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('queueForMails')
     ->inject('store')
     ->inject('proofForCode')
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
     ->inject('authorization')
-    ->action(function ($userId, $secret, $request, $response, $user, $dbForProject, $project, $platform, $locale, $geodb, $queueForEvents, $queueForMails, $store, $proofForCode, $authorization) use ($createSession) {
+    ->action(function ($userId, $secret, $request, $response, $user, $dbForProject, $project, $platform, $locale, $geodb, $queueForEvents, $queueForMails, $store, $proofForCode, $domainVerification, $cookieDomain, $authorization) use ($createSession) {
         $proofForToken = new ProofsToken(TOKEN_LENGTH_MAGIC_URL);
         $proofForToken->setHash(new Sha());
-        $createSession($userId, $secret, $request, $response, $user, $dbForProject, $project, $platform, $locale, $geodb, $queueForEvents, $queueForMails, $store, $proofForToken, $proofForCode, $authorization);
+        $createSession($userId, $secret, $request, $response, $user, $dbForProject, $project, $platform, $locale, $geodb, $queueForEvents, $queueForMails, $store, $proofForToken, $proofForCode, $domainVerification, $cookieDomain, $authorization);
     });

 Http::put('/v1/account/sessions/phone')
@@ -2936,6 +2950,8 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('store')
     ->inject('proofForToken')
     ->inject('proofForCode')
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
     ->inject('authorization')
     ->action($createSession);

@@ -3727,7 +3743,9 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
     ->inject('dbForProject')
     ->inject('queueForEvents')
     ->inject('store')
-    ->action(function (Request $request, Response $response, Document $user, Database $dbForProject, Event $queueForEvents, Store $store) {
+    ->inject('domainVerification')
+    ->inject('cookieDomain')
+    ->action(function (Request $request, Response $response, Document $user, Database $dbForProject, Event $queueForEvents, Store $store, bool $domainVerification, ?string $cookieDomain) {

         $user->setAttribute('status', false);

@@ -3737,14 +3755,14 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
             ->setParam('userId', $user->getId())
             ->setPayload($response->output($user, Response::MODEL_ACCOUNT));

-        if (!Config::getParam('domainVerification')) {
+        if (!$domainVerification) {
             $response->addHeader('X-Fallback-Cookies', \json_encode([]));
         }

         $protocol = $request->getProtocol();
         $response
-            ->addCookie($store->getKey() . '_legacy', '', \time() - 3600, '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, null)
-            ->addCookie($store->getKey(), '', \time() - 3600, '/', Config::getParam('cookieDomain'), ('https' == $protocol), true, Config::getParam('cookieSamesite'))
+            ->addCookie($store->getKey() . '_legacy', '', \time() - 3600, '/', $cookieDomain, ('https' == $protocol), true, null)
+            ->addCookie($store->getKey(), '', \time() - 3600, '/', $cookieDomain, ('https' == $protocol), true, Config::getParam('cookieSamesite'))
         ;

         $response->dynamic($user, Response::MODEL_ACCOUNT);
diff --git a/app/controllers/general.php b/app/controllers/general.php
index d10ad9a0601..5a5c2dd507b 100644
--- a/app/controllers/general.php
+++ b/app/controllers/general.php
@@ -61,8 +61,6 @@
 use Utopia\Validator;
 use Utopia\Validator\Text;

-Config::setParam('domainVerification', false);
-Config::setParam('cookieDomain', 'localhost');
 Config::setParam('cookieSamesite', Response::COOKIE_SAMESITE_NONE);

 function router(Http $utopia, Database $dbForPlatform, callable $getProjectDB, SwooleRequest $swooleRequest, Request $request, Response $response, Log $log, Event $queueForEvents, Bus $bus, Executor $executor, Reader $geodb, callable $isResourceBlocked, array $platform, string $previewHostname, Authorization $authorization, ?Key $apiKey, DeleteEvent $queueForDeletes, int $executionsRetentionCount)
@@ -904,40 +902,16 @@ function router(Http $utopia, Database $dbForPlatform, callable $getProjectDB, S
             $locale->setDefault($localeParam);
         }

-        $origin = \parse_url($request->getOrigin($request->getReferer('')), PHP_URL_HOST);
-        $selfDomain = new Domain($request->getHostname());
-        $endDomain = new Domain((string)$origin);
-        Config::setParam(
-            'domainVerification',
-            ($selfDomain->getRegisterable() === $endDomain->getRegisterable()) &&
-                $endDomain->getRegisterable() !== ''
-        );
-
         $localHosts = ['localhost','localhost:'.$request->getPort()];

         $migrationHost = System::getEnv('_APP_MIGRATION_HOST');
         if (!empty($migrationHost)) {
+            // Treat the migration host like localhost because internal migration and
+            // CI traffic may use it before a public domain is configured.
             $localHosts[] = $migrationHost;
             $localHosts[] = $migrationHost.':'.$request->getPort();
         }

-        $isLocalHost = in_array($request->getHostname(), $localHosts);
-        $isIpAddress = filter_var($request->getHostname(), FILTER_VALIDATE_IP) !== false;
-
-        $isConsoleProject = $project->getAttribute('$id', '') === 'console';
-        $isConsoleRootSession = System::getEnv('_APP_CONSOLE_ROOT_SESSION', 'disabled') === 'enabled';
-
-        Config::setParam(
-            'cookieDomain',
-            $isLocalHost || $isIpAddress
-                ? null
-                : (
-                    $isConsoleProject && $isConsoleRootSession
-                    ? '.' . $selfDomain->getRegisterable()
-                    : '.' . $request->getHostname()
-                )
-        );
-
         $warnings = [];

         /*
diff --git a/app/init/resources.php b/app/init/resources.php
index 8acecb8e3ec..92164c3c950 100644
--- a/app/init/resources.php
+++ b/app/init/resources.php
@@ -53,6 +53,7 @@
 use Utopia\Database\Document;
 use Utopia\Database\Query;
 use Utopia\Database\Validator\Authorization;
+use Utopia\Domains\Domain;
 use Utopia\DSN\DSN;
 use Utopia\Http\Http;
 use Utopia\Locale\Locale;
@@ -249,6 +250,52 @@ Http::setResource('allowedOrigins', function (array $platform) {
     return array_unique($allowed);
 }, ['platform', 'project']);

+/**
+ * Whether the request origin is verified against the request hostname.
+ */
+Http::setResource('domainVerification', function (Request $request) {
+    $origin = \parse_url($request->getOrigin($request->getReferer('')), PHP_URL_HOST);
+    $selfDomain = new Domain($request->getHostname());
+    $endDomain = new Domain((string) $origin);
+
+    return ($selfDomain->getRegisterable() === $endDomain->getRegisterable())
+        && $endDomain->getRegisterable() !== '';
+}, ['request']);
+
+/**
+ * Cookie domain for the current request.
+ */
+Http::setResource('cookieDomain', function (Request $request, Document $project) {
+    $localHosts = ['localhost', 'localhost:' . $request->getPort()];
+
+    $migrationHost = System::getEnv('_APP_MIGRATION_HOST');
+    if (!empty($migrationHost)) {
+        // Treat the migration host like localhost because internal migration and CI
+        // traffic may use it before a public domain is configured.
+        $localHosts[] = $migrationHost;
+        $localHosts[] = $migrationHost . ':' . $request->getPort();
+    }
+
+    $hostname = $request->getHostname();
+    $isLocalHost = \in_array($hostname, $localHosts, true);
+    $isIpAddress = \filter_var($hostname, FILTER_VALIDATE_IP) !== false;
+
+    if ($isLocalHost || $isIpAddress) {
+        return;
+    }
+
+    $isConsoleProject = $project->getAttribute('$id', '') === 'console';
+    $isConsoleRootSession = System::getEnv('_APP_CONSOLE_ROOT_SESSION', 'disabled') === 'enabled';
+
+    if ($isConsoleProject && $isConsoleRootSession) {
+        $domain = new Domain($hostname);
+
+        return '.' . $domain->getRegisterable();
+    }
+
+    return '.' . $hostname;
+}, ['request', 'project']);
+
 /**
  * Rule associated with a request origin.
  */
diff --git a/src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php b/src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php
index 46b6c3cacf0..28bfa769eec 100644
--- a/src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php
+++ b/src/Appwrite/Platform/Modules/Teams/Http/Memberships/Status/Update.php
@@ -74,10 +74,12 @@ public function __construct()
             ->inject('queueForEvents')
             ->inject('store')
             ->inject('proofForToken')
+            ->inject('domainVerification')
+            ->inject('cookieDomain')
             ->callback($this->action(...));
     }

-    public function action(string $teamId, string $membershipId, string $userId, string $secret, Request $request, Response $response, Document $user, Database $dbForProject, Authorization $authorization, $project, Reader $geodb, Event $queueForEvents, Store $store, Token $proofForToken)
+    public function action(string $teamId, string $membershipId, string $userId, string $secret, Request $request, Response $response, Document $user, Database $dbForProject, Authorization $authorization, $project, Reader $geodb, Event $queueForEvents, Store $store, Token $proofForToken, bool $domainVerification, ?string $cookieDomain)
     {
         $protocol = $request->getProtocol();

@@ -162,7 +164,7 @@ public function action(string $teamId, string $membershipId, string $userId, str
                 ->setProperty('secret', $secret)
                 ->encode();

-            if (!Config::getParam('domainVerification')) {
+            if (!$domainVerification) {
                 $response->addHeader('X-Fallback-Cookies', \json_encode([$store->getKey() => $encoded]));
             }

@@ -172,7 +174,7 @@ public function action(string $teamId, string $membershipId, string $userId, str
                     value: $encoded,
                     expire: (new \DateTime($expire))->getTimestamp(),
                     path: '/',
-                    domain: Config::getParam('cookieDomain'),
+                    domain: $cookieDomain,
                     secure: ('https' === $protocol),
                     httponly: true
                 )
@@ -181,7 +183,7 @@ public function action(string $teamId, string $membershipId, string $userId, str
                     value: $encoded,
                     expire: (new \DateTime($expire))->getTimestamp(),
                     path: '/',
-                    domain: Config::getParam('cookieDomain'),
+                    domain: $cookieDomain,
                     secure: ('https' === $protocol),
                     httponly: true,
                     sameSite: Config::getParam('cookieSamesite')
PATCH

echo "Patch applied successfully"
