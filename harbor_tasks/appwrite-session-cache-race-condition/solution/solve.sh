#!/bin/bash
set -e

cd /workspace/appwrite

# Check if already applied (idempotency)
if grep -q "createDocument('sessions')" app/controllers/api/account.php && \
   grep -A5 "createDocument('sessions')" app/controllers/api/account.php | grep -q "purgeCachedDocument('users')"; then
    echo "Fix already applied, skipping."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/app/controllers/api/account.php b/app/controllers/api/account.php
index cbdf11225a4..8eb49ea27bd 100644
--- a/app/controllers/api/account.php
+++ b/app/controllers/api/account.php
@@ -1103,14 +1103,14 @@ function sendSessionAlert(Locale $locale, Document $user, Document $project, arr
             ]));
         }

-        $dbForProject->purgeCachedDocument('users', $user->getId());
-
         $session = $dbForProject->createDocument('sessions', $session->setAttribute('$permissions', [
             Permission::read(Role::user($user->getId())),
             Permission::update(Role::user($user->getId())),
             Permission::delete(Role::user($user->getId())),
         ]));

+        $dbForProject->purgeCachedDocument('users', $user->getId());
+
         $encoded = $store
             ->setProperty('id', $user->getId())
             ->setProperty('secret', $secret)
PATCH

echo "Fix applied successfully."
