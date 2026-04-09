#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch to fix the digest error message
cat <<'PATCH' | git apply -
diff --git a/crates/sui-types/src/digests.rs b/crates/sui-types/src/digests.rs
index 343e852d3c42..fffff4c90f4c 100644
--- a/crates/sui-types/src/digests.rs
+++ b/crates/sui-types/src/digests.rs
@@ -371,13 +371,7 @@ impl std::str::FromStr for CheckpointDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(CheckpointDigest::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -464,13 +458,7 @@ impl std::str::FromStr for CheckpointContentsDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(CheckpointContentsDigest::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -650,13 +638,7 @@ impl std::str::FromStr for TransactionDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(TransactionDigest::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -757,13 +739,7 @@ impl std::str::FromStr for TransactionEffectsDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(TransactionEffectsDigest::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -833,13 +809,7 @@ impl std::str::FromStr for TransactionEventsDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(Self::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -897,13 +867,7 @@ impl std::str::FromStr for EffectsAuxDataDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(Self::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -1029,13 +993,7 @@ impl std::str::FromStr for ObjectDigest {
     type Err = anyhow::Error;

     fn from_str(s: &str) -> Result<Self, Self::Err> {
-        let mut result = [0; 32];
-        let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
-        if buffer.len() != 32 {
-            return Err(anyhow::anyhow!("Invalid digest length. Expected 32 bytes"));
-        }
-        result.copy_from_slice(&buffer);
-        Ok(ObjectDigest::new(result))
+        Ok(Self::new(digest_from_base58(s)?))
     }
 }

@@ -1169,9 +1127,27 @@ impl fmt::Display for CheckpointArtifactsDigest {
     }
 }

+fn digest_from_base58(s: &str) -> anyhow::Result<[u8; 32]> {
+    let mut result = [0; 32];
+    let buffer = Base58::decode(s).map_err(|e| anyhow::anyhow!(e))?;
+    let len = buffer.len();
+    if len < 32 {
+        return Err(anyhow::anyhow!(
+            "Invalid digest length. Expected base58 string that decodes into 32 bytes, but [{s}] decodes into {len} bytes"
+        ));
+    } else if len > 32 {
+        let s = &s[0..32.min(s.len())];
+        return Err(anyhow::anyhow!(
+            "Invalid digest length. Expected base58 string that decodes into 32 bytes, but [{s}] (truncated) decodes into {len} bytes"
+        ));
+    }
+    result.copy_from_slice(&buffer);
+    Ok(result)
+}
+
 #[cfg(test)]
 mod test {
-    use crate::digests::{ChainIdentifier, SUI_PROTOCOL_CONFIG_CHAIN_OVERRIDE};
+    use crate::digests::{ChainIdentifier, SUI_PROTOCOL_CONFIG_CHAIN_OVERRIDE, digest_from_base58};

     fn has_env_override() -> bool {
         SUI_PROTOCOL_CONFIG_CHAIN_OVERRIDE.is_some()
@@ -1210,4 +1186,32 @@ mod test {
         let chain_id = ChainIdentifier::from_chain_short_id(&String::from("unknown"));
         assert_eq!(chain_id, None);
     }
+
+    #[test]
+    fn test_digest_from_base58_eq_32() {
+        assert_eq!(
+            digest_from_base58("1".repeat(32).as_str()).unwrap(),
+            [0; 32]
+        );
+    }
+
+    #[test]
+    fn test_digest_from_base58_lt_32() {
+        assert_eq!(
+            digest_from_base58("1".repeat(31).as_str())
+                .unwrap_err()
+                .to_string(),
+            "Invalid digest length. Expected base58 string that decodes into 32 bytes, but [1111111111111111111111111111111] decodes into 31 bytes"
+        );
+    }
+
+    #[test]
+    fn test_digest_from_base58_gt_32() {
+        assert_eq!(
+            digest_from_base58("1".repeat(33).as_str())
+                .unwrap_err()
+                .to_string(),
+            "Invalid digest length. Expected base58 string that decodes into 32 bytes, but [11111111111111111111111111111111] (truncated) decodes into 33 bytes"
+        );
+    }
 }
PATCH

# Verify the patch was applied by checking for the new helper function
grep -q "fn digest_from_base58" crates/sui-types/src/digests.rs
echo "Patch applied successfully"
