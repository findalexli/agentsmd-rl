#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for external keystore file creation fix
patch -p1 <<'PATCH'
diff --git a/crates/sui-keys/src/external.rs b/crates/sui-keys/src/external.rs
index 716bddf28e659..2735f53e99c44 100644
--- a/crates/sui-keys/src/external.rs
+++ b/crates/sui-keys/src/external.rs
@@ -132,7 +132,8 @@ impl External {
     pub fn load_or_create(path: &PathBuf) -> Result<Self, Error> {
         let mut aliases_store_directory = path.clone();
         aliases_store_directory.set_extension(ALIASES_FILE_EXTENSION);
-        let aliases: BTreeMap<SuiAddress, Alias> = if aliases_store_directory.exists() {
+        let aliases_file_exists = aliases_store_directory.exists();
+        let aliases: BTreeMap<SuiAddress, Alias> = if aliases_file_exists {
             let aliases_store: String = std::fs::read_to_string(&aliases_store_directory)
                 .map_err(|e| anyhow!("Failed to read aliases file: {}", e))?;
             serde_json::from_str(&aliases_store)
@@ -141,7 +142,8 @@ impl External {
             BTreeMap::default()
         };

-        let keys: BTreeMap<SuiAddress, StoredKey> = if path.exists() {
+        let keystore_file_exists = path.exists();
+        let keys: BTreeMap<SuiAddress, StoredKey> = if keystore_file_exists {
             let keys_store: String = std::fs::read_to_string(path)
                 .map_err(|e| anyhow!("Failed to read keys file: {}", e))?;
             serde_json::from_str(&keys_store)
@@ -150,6 +152,24 @@ impl External {
             BTreeMap::default()
         };

+        if !aliases_file_exists {
+            let aliases_store =
+                serde_json::to_string_pretty(&aliases).context("Error serializing keystore")?;
+            std::fs::write(&aliases_store_directory, aliases_store).with_context(|| {
+                format!(
+                    "Cannot write aliases to file: {}",
+                    aliases_store_directory.display()
+                )
+            })?;
+        }
+
+        if !keystore_file_exists {
+            let keys_store =
+                serde_json::to_string_pretty(&keys).context("Error serializing aliases")?;
+            std::fs::write(path, keys_store)
+                .with_context(|| format!("Cannot write keystore to file: {}", path.display()))?;
+        }
+
         Ok(Self {
             aliases,
             keys,
@@ -659,7 +679,7 @@ impl AccountKeystore for External {
 mod tests {
     use super::{External, MockCommandRunner, StdCommandRunner, StoredKey};
     use crate::key_identity::KeyIdentity;
-    use crate::keystore::{AccountKeystore, GenerateOptions, GeneratedKey};
+    use crate::keystore::{ALIASES_FILE_EXTENSION, AccountKeystore, GenerateOptions, GeneratedKey};
     use anyhow::anyhow;
     use fastcrypto::ed25519::Ed25519KeyPair;
     use fastcrypto::secp256k1::Secp256k1KeyPair;
@@ -695,18 +715,31 @@ mod tests {

     #[test]
     fn test_load_new_from_path() {
-        let cargo_dir = PathBuf::from(std::env::var("CARGO_MANIFEST_DIR").unwrap())
-            .join("unit_tests")
-            .join("fixtures")
-            .join("external_config");
+        let tmp_dir = TempDir::new().unwrap();
+        let keystore_path = tmp_dir.path().join("external.keystore");

-        let external = External::load_or_create(&cargo_dir).unwrap();
+        let external = External::load_or_create(&keystore_path).unwrap();

         assert!(external.aliases.is_empty());
         assert!(external.keys.is_empty());
         assert!(external.path.is_some());
     }

+    #[test]
+    fn test_load_or_create_creates_external_files() {
+        let tmp_dir = TempDir::new().unwrap();
+        let keystore_path = tmp_dir.path().join("external.keystore");
+        let mut aliases_path = keystore_path.clone();
+        aliases_path.set_extension(ALIASES_FILE_EXTENSION);
+
+        let external = External::load_or_create(&keystore_path).unwrap();
+
+        assert!(external.aliases.is_empty());
+        assert!(external.keys.is_empty());
+        assert!(keystore_path.exists());
+        assert!(aliases_path.exists());
+    }
+
     #[tokio::test]
     async fn test_serialize() {
         let tmp_dir = TempDir::new().unwrap();
diff --git a/crates/sui/src/sui_commands.rs b/crates/sui/src/sui_commands.rs
index 3ef8f6069c7be..dcc4d8c59fc9d 100644
--- a/crates/sui/src/sui_commands.rs
+++ b/crates/sui/src/sui_commands.rs
@@ -59,7 +59,7 @@ use sui_indexer_alt_reader::{
 };
 use sui_keys::key_derive::generate_new_key;
 use sui_keys::keypair_file::read_key;
-use sui_keys::keystore::{AccountKeystore, FileBasedKeystore, Keystore};
+use sui_keys::keystore::{AccountKeystore, External, FileBasedKeystore, Keystore};
 use sui_move::summary::PackageSummaryMetadata;
 use sui_move::{self, execute_move_command};
 use sui_move_build::BuildConfig as SuiBuildConfig;
@@ -523,7 +523,10 @@ impl SuiCommand {
                 cmd,
             } => {
                 let client_path = sui_config_dir()?.join(SUI_CLIENT_CONFIG);
-                let mut config = PersistedConfig::<SuiClientConfig>::read(&client_path)?;
+                prompt_if_no_config(&client_path, false).await?;
+                let config: SuiClientConfig = PersistedConfig::read(&client_path)?;
+                let mut config = config.persisted(&client_path);
+                ensure_external_keystore_config(&mut config, &client_path)?;

                 cmd.execute(config.external_keys.as_mut())
                     .await?
@@ -1575,6 +1578,9 @@ async fn prompt_if_no_config(
     let config_dir = wallet_conf_file
         .parent()
         .ok_or_else(|| anyhow!("Error: {wallet_conf_file:?} is an invalid file path"))?;
+    let external_keystore = Keystore::External(External::load_or_create(
+        &default_external_keystore_path(wallet_conf_file),
+    )?);

     let (keystore, address) =
         create_default_keystore(&config_dir.join(SUI_KEYSTORE_FILENAME)).await?;
@@ -1590,7 +1596,7 @@ async fn prompt_if_no_config(
             SuiEnv::devnet(),
             SuiEnv::localnet(),
         ],
-        external_keys: None,
+        external_keys: Some(external_keystore),
         active_address: Some(address),
         active_env: Some(default_env_name.clone()),
     }
@@ -1602,6 +1608,23 @@ async fn prompt_if_no_config(
     Ok(())
 }

+fn default_external_keystore_path(client_path: &Path) -> PathBuf {
+    client_path.with_file_name("external.keystore")
+}
+
+fn ensure_external_keystore_config(
+    config: &mut PersistedConfig<SuiClientConfig>,
+    client_path: &Path,
+) -> Result<(), anyhow::Error> {
+    if config.external_keys.is_none() {
+        config.external_keys = Some(Keystore::External(External::load_or_create(
+            &default_external_keystore_path(client_path),
+        )?));
+        config.save()?;
+    }
+    Ok(())
+}
+
 /// Create a keystore with a single key at `keystore_file`; returns the created keystore and
 /// address
 async fn create_default_keystore(keystore_file: &Path) -> anyhow::Result<(Keystore, SuiAddress)> {
PATCH

echo "Patch applied successfully"
