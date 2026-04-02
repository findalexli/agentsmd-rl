#!/usr/bin/env bash
set -euo pipefail

cd /repo

# Idempotency check: if already fixed, exit early
if grep -q 'Incomplete credentials' crates/uv-auth/src/middleware.rs 2>/dev/null &&
   grep -q 'Incomplete credentials' crates/uv/tests/it/edit.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/uv-auth/src/middleware.rs b/crates/uv-auth/src/middleware.rs
index d73fbff9656ad..b9ab7a4d3496e 100644
--- a/crates/uv-auth/src/middleware.rs
+++ b/crates/uv-auth/src/middleware.rs
@@ -551,8 +551,10 @@ impl AuthMiddleware {
             return next.run(request, extensions).await;
         };
         let url = DisplaySafeUrl::from_url(request.url().clone());
-        if matches!(auth_policy, AuthPolicy::Always) && credentials.password().is_none() {
-            return Err(Error::Middleware(format_err!("Missing password for {url}")));
+        if matches!(auth_policy, AuthPolicy::Always) && !credentials.is_authenticated() {
+            return Err(Error::Middleware(format_err!(
+                "Incomplete credentials for {url}"
+            )));
         }
         let result = next.run(request, extensions).await;

@@ -582,9 +584,9 @@ impl AuthMiddleware {
     ) -> reqwest_middleware::Result<Response> {
         let credentials = Arc::new(credentials);

-        // If there's a password, send the request and cache
+        // If the request already contains complete authentication, send it and cache it.
         if credentials.is_authenticated() {
-            trace!("Request for {url} already contains username and password");
+            trace!("Request for {url} already contains complete authentication");
             return self
                 .complete_request(Some(credentials), request, extensions, next, auth_policy)
                 .await;
diff --git a/crates/uv/tests/it/edit.rs b/crates/uv/tests/it/edit.rs
index 40ab11f0a2b14..0b8133564f979 100644
--- a/crates/uv/tests/it/edit.rs
+++ b/crates/uv/tests/it/edit.rs
@@ -13843,7 +13843,7 @@ fn add_auth_policy_always_with_username_no_password() -> Result<()> {

     ----- stderr -----
     error: Failed to fetch: `https://pypi.org/simple/anyio/`
-      Caused by: Missing password for https://pypi.org/simple/anyio/
+      Caused by: Incomplete credentials for https://pypi.org/simple/anyio/
     "
     );
     Ok(())

PATCH

echo "Patch applied successfully."
