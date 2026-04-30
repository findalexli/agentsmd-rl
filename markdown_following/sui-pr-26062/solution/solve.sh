#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for implicit :json transform
cat <<'PATCH' | git apply -
diff --git a/crates/sui-display/src/v2/interpreter.rs b/crates/sui-display/src/v2/interpreter.rs
index de0ce05450042..f46b3715c0f02 100644
--- a/crates/sui-display/src/v2/interpreter.rs
+++ b/crates/sui-display/src/v2/interpreter.rs
@@ -55,17 +55,14 @@ impl<S: V::Store> Interpreter<S> {
                     offset,
                     alternates,
                     transform,
-                }) => {
-                    let transform = transform.unwrap_or_default();
-                    Ok(self
-                        .eval_alts(alternates)
-                        .await?
-                        .map(move |value| V::Strand::Value {
-                            value,
-                            transform,
-                            offset: *offset,
-                        }))
-                }
+                }) => Ok(self
+                    .eval_alts(alternates)
+                    .await?
+                    .map(move |value| V::Strand::Value {
+                        value,
+                        transform: *transform,
+                        offset: *offset,
+                    })),
             }
         }))
         .await
diff --git a/crates/sui-display/src/v2/mod.rs b/crates/sui-display/src/v2/mod.rs
index 3f219e23eb0e8..3e7d852affbd5 100644
--- a/crates/sui-display/src/v2/mod.rs
+++ b/crates/sui-display/src/v2/mod.rs
@@ -2527,6 +2527,82 @@ mod tests {
         "###);
     }

+    #[tokio::test]
+    async fn test_format_single_bare_expression_falls_back_to_json() {
+        #[derive(serde::Serialize)]
+        enum Status<'s> {
+            Pending(&'s str),
+        }
+
+        let bytes = bcs::to_bytes(&(
+            (42u64, "hello"),
+            Status::Pending("ready"),
+            vec![1u64, 2u64, 3u64],
+        ))
+        .unwrap();
+
+        let layout = struct_(
+            "0x1::m::S",
+            vec![
+                (
+                    "st",
+                    struct_(
+                        "0x1::m::Inner",
+                        vec![
+                            ("count", L::U64),
+                            ("label", L::Struct(Box::new(move_ascii_str_layout()))),
+                        ],
+                    ),
+                ),
+                (
+                    "en",
+                    enum_(
+                        "0x1::m::Status",
+                        vec![(
+                            "Pending",
+                            vec![("message", L::Struct(Box::new(move_ascii_str_layout())))],
+                        )],
+                    ),
+                ),
+                ("vs", vector_(L::U64)),
+            ],
+        );
+
+        let store = MockStore::default();
+        let root = OwnedSlice { bytes, layout };
+        let interpreter = Interpreter::new(root, store);
+
+        let formats = ["{st}", "{en}", "{vs}"];
+        let mut output = Vec::with_capacity(formats.len());
+        for s in formats {
+            let format = Format::parse(Limits::default(), s).unwrap();
+            output.push(
+                format
+                    .format::<serde_json::Value>(&interpreter, usize::MAX, usize::MAX)
+                    .await
+                    .unwrap(),
+            );
+        }
+
+        assert_json_snapshot!(output, @r###"
+        [
+          {
+            "count": "42",
+            "label": "hello"
+          },
+          {
+            "@variant": "Pending",
+            "message": "ready"
+          },
+          [
+            "1",
+            "2",
+            "3"
+          ]
+        ]
+        "###);
+    }
+
     #[tokio::test]
     async fn test_display_field_errors() {
         let bytes = bcs::to_bytes(&0u8).unwrap();
diff --git a/crates/sui-display/src/v2/parser.rs b/crates/sui-display/src/v2/parser.rs
index 2a44b0063c98a..5fe86899f1681 100644
--- a/crates/sui-display/src/v2/parser.rs
+++ b/crates/sui-display/src/v2/parser.rs
@@ -143,13 +143,12 @@ pub enum Fields<'s> {
 }

 /// Ways to modify a value before displaying it.
-#[derive(Default, Copy, Clone, PartialEq, Eq)]
+#[derive(Copy, Clone, PartialEq, Eq)]
 pub enum Transform {
     Base64(Base64Modifier),
     Bcs(Base64Modifier),
     Hex,
     Json,
-    #[default]
     Str,
     Timestamp,
     Url,
diff --git a/crates/sui-display/src/v2/value.rs b/crates/sui-display/src/v2/value.rs
index 1a5d45f2b598..04a2eb02665b4 100644
--- a/crates/sui-display/src/v2/value.rs
+++ b/crates/sui-display/src/v2/value.rs
@@ -55,7 +55,7 @@ pub enum Strand<'s> {
     Value {
         offset: usize,
         value: Value<'s>,
-        transform: Transform,
+        transform: Option<Transform>,
     },
 }

@@ -343,7 +343,10 @@ impl Atom<'_> {
     }

     /// Format the atom as a string.
-    fn format_as_str(&self, w: &mut writer::StringWriter<'_>) -> Result<(), FormatError> {
+    pub(crate) fn format_as_str(
+        &self,
+        w: &mut writer::StringWriter<'_>,
+    ) -> Result<(), FormatError> {
         match self {
             Atom::Address(a) => write!(w, "{}", a.to_canonical_display(true))?,
             Atom::Bool(b) => write!(w, "{b}")?,
diff --git a/crates/sui-display/src/v2/writer.rs b/crates/sui-display/src/v2/writer.rs
index f218ff8536fd9..e0b41caee0732 100644
--- a/crates/sui-display/src/v2/writer.rs
+++ b/crates/sui-display/src/v2/writer.rs
@@ -97,15 +97,34 @@ pub(crate) fn write<F: RV::Format>(
     meter: Meter<'_>,
     mut strands: Vec<V::Strand<'_>>,
 ) -> Result<F, FormatError> {
-    if matches!(&strands[..], [V::Strand::Value { transform, .. }] if *transform == Transform::Json)
-    {
-        let V::Strand::Value { offset, value, .. } = strands.pop().unwrap() else {
+    if matches!(
+        &strands[..],
+        [V::Strand::Value {
+            transform: None | Some(Transform::Json),
+            ..
+        }]
+    ) {
+        let V::Strand::Value {
+            offset,
+            value,
+            transform,
+        } = strands.pop().unwrap()
+        else {
             unreachable!();
         };

-        return value
-            .format_json(meter)
-            .map_err(|e| e.for_expr_at_offset(offset));
+        return if transform.is_none()
+            && let Ok(atom) = V::Atom::try_from(value.clone())
+        {
+            let mut writer = StringWriter::new(meter);
+            atom.format_as_str(&mut writer)
+                .map_err(|e| e.for_expr_at_offset(offset))?;
+            Ok(writer.finish())
+        } else {
+            value
+                .format_json(meter)
+                .map_err(|e| e.for_expr_at_offset(offset))
+        };
     }

     let mut writer = StringWriter::new(meter);
@@ -120,7 +139,7 @@ pub(crate) fn write<F: RV::Format>(
                 value,
                 transform,
             } => value
-                .format(transform, &mut writer)
+                .format(transform.unwrap_or(Transform::Str), &mut writer)
                 .map_err(|e| e.for_expr_at_offset(offset))?,
         }
     }
PATCH

# Idempotency check - verify a distinctive line from the patch
if ! grep -q "transform: None | Some(Transform::Json)" crates/sui-display/src/v2/writer.rs; then
    echo "ERROR: Patch did not apply correctly"
    exit 1
fi

echo "Patch applied successfully"
