#!/usr/bin/env bash
set -euo pipefail

cd /workspace/uv

# Idempotent: skip if already applied
if grep -q 'use uv_keyring::{Entry, Result};' crates/uv-keyring/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/Cargo.lock b/Cargo.lock
index 578d40498116c..27ee24a1c022e 100644
--- a/Cargo.lock
+++ b/Cargo.lock
@@ -6735,7 +6735,6 @@ version = "0.0.36"
 dependencies = [
  "async-trait",
  "byteorder",
- "doc-comment",
  "env_logger",
  "fastrand",
  "secret-service",
diff --git a/crates/uv-keyring/Cargo.toml b/crates/uv-keyring/Cargo.toml
index a1339c5c1b5d0..052a7058a4be2 100644
--- a/crates/uv-keyring/Cargo.toml
+++ b/crates/uv-keyring/Cargo.toml
@@ -40,7 +40,6 @@ windows = { workspace = true, features = ["Win32_Foundation", "Win32_Security_Cr
 zeroize = { workspace = true }

 [dev-dependencies]
-doc-comment = "0.3"
 env_logger = "0.11.5"
 fastrand = { workspace = true }

diff --git a/crates/uv-keyring/README.md b/crates/uv-keyring/README.md
index 613bff88af70f..5b598f2f09559 100644
--- a/crates/uv-keyring/README.md
+++ b/crates/uv-keyring/README.md
@@ -19,9 +19,10 @@ platform's persistent credential store.) The password or secret can then be read
 can then be removed using the `delete_credential` method.

 ```rust
-use keyring::{Entry, Result};
+use uv_keyring::{Entry, Result};

-fn main() -> Result<()> {
+#[tokio::main]
+async fn main() -> Result<()> {
     let entry = Entry::new("my-service", "my-name")?;
     entry.set_password("topS3cr3tP4$$w0rd").await?;
     let password = entry.get_password().await?;
diff --git a/crates/uv-keyring/src/lib.rs b/crates/uv-keyring/src/lib.rs
index 07f6a92fccc10..d95867a2d24ac 100644
--- a/crates/uv-keyring/src/lib.rs
+++ b/crates/uv-keyring/src/lib.rs
@@ -398,9 +398,6 @@ impl Entry {
     }
 }

-#[cfg(doctest)]
-doc_comment::doctest!("../README.md", readme);
-
 #[cfg(test)]
 /// There are no actual tests in this module.
 /// Instead, it contains generics that each keystore invokes in their tests,
diff --git a/crates/uv-keyring/src/mock.rs b/crates/uv-keyring/src/mock.rs
index 891cb029186ad..ab41542d50717 100644
--- a/crates/uv-keyring/src/mock.rs
+++ b/crates/uv-keyring/src/mock.rs
@@ -7,11 +7,10 @@ that is platform-independent, provides no persistence, and allows the client
 to specify the return values (including errors) for each call. The credentials
 in this store have no attributes at all.

-To use this credential store instead of the default, make this call during
-application startup _before_ creating any entries:
-```rust
-keyring::set_default_credential_builder(keyring::mock::default_credential_builder());
-```
+To use this credential store instead of the default, call
+[`set_default_credential_builder`](crate::set_default_credential_builder)
+with [`default_credential_builder`] during application startup
+_before_ creating any entries.

 You can then create entries as you usually do, and call their usual methods
 to set, get, and delete passwords.  There is no persistence other than
@@ -22,16 +21,7 @@ If you want a method call on an entry to fail in a specific way, you can
 downcast the entry to a [`MockCredential`] and then call [`set_error`](MockCredential::set_error)
 with the appropriate error.  The next entry method called on the credential
 will fail with the error you set.  The error will then be cleared, so the next
-call on the mock will operate as usual.  Here's a complete example:
-```rust
-# use keyring::{Entry, Error, mock, mock::MockCredential};
-# keyring::set_default_credential_builder(mock::default_credential_builder());
-let entry = Entry::new("service", "user").unwrap();
-let mock: &MockCredential = entry.get_credential().downcast_ref().unwrap();
-mock.set_error(Error::Invalid("mock error".to_string(), "takes precedence".to_string()));
-entry.set_password("test").expect_err("error will override");
-entry.set_password("test").expect("error has been cleared");
-```
+call on the mock will operate as usual.
  */
 use std::cell::RefCell;
 use std::sync::Mutex;

PATCH

echo "Patch applied successfully."
