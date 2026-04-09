#!/bin/bash
set -e

cd /workspace/sui

# Check if patch already applied (idempotency)
if grep -q "one or both chars are multi-byte UTF-8" external-crates/move/crates/move-compiler/src/expansion/byte_string.rs; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/external-crates/move/crates/move-compiler/src/expansion/byte_string.rs b/external-crates/move/crates/move-compiler/src/expansion/byte_string.rs
index 9d3b16440058..90bbc05c33f4 100644
--- a/external-crates/move/crates/move-compiler/src/expansion/byte_string.rs
+++ b/external-crates/move/crates/move-compiler/src/expansion/byte_string.rs
@@ -136,12 +136,30 @@ fn decode_(context: &mut Context, buffer: &mut Vec<u8>, chars: Vec<char>) {
             'x' => {
                 let d0_opt = next_char_opt!();
                 let d1_opt = next_char_opt!();
-                let hex = match (d0_opt, d1_opt) {
+                match (d0_opt, d1_opt) {
                     (Some(d0), Some(d1)) => {
                         let mut hex = String::new();
                         hex.push(d0);
                         hex.push(d1);
-                        hex
+                        match hex::decode(hex) {
+                            Ok(hex_buffer) => buffer.extend(hex_buffer),
+                            Err(hex::FromHexError::InvalidHexCharacter { c, index }) => {
+                                context.char_error(cur + 2 + index, cur + 2 + index, c);
+                            }
+                            Err(
+                                hex::FromHexError::OddLength
+                                | hex::FromHexError::InvalidStringLength,
+                            ) => {
+                                // one or both chars are multi-byte UTF-8
+                                debug_assert!(!d0.is_ascii_hexdigit() || !d1.is_ascii_hexdigit());
+                                if !d0.is_ascii_hexdigit() {
+                                    context.char_error(cur + 2, cur + 2, d0);
+                                }
+                                if !d1.is_ascii_hexdigit() {
+                                    context.char_error(cur + 3, cur + 3, d1);
+                                }
+                            }
+                        }
                     }

                     // Unexpected end of text
@@ -156,13 +174,6 @@ fn decode_(context: &mut Context, buffer: &mut Vec<u8>, chars: Vec<char>) {

                     // There was a second digit but no first?
                     (None, Some(_)) => unreachable!(),
-                };
-                match hex::decode(hex) {
-                    Ok(hex_buffer) => buffer.extend(hex_buffer),
-                    Err(hex::FromHexError::InvalidHexCharacter { c, index }) => {
-                        context.char_error(cur + 2 + index, cur + 2 + index, c);
-                    }
-                    Err(_) => unreachable!("ICE unexpected error parsing hex byte string value"),
                 }
             }
             c => {
PATCH

echo "Patch applied successfully"
