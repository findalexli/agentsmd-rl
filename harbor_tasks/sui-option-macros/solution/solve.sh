#!/bin/bash
set -e

cd /workspace/sui

# Apply the gold patch for PR #26085 - Add option macros
patch -p1 << 'PATCH'
diff --git a/crates/sui-framework/packages/move-stdlib/sources/option.move b/crates/sui-framework/packages/move-stdlib/sources/option.move
index 1dd7d5b25a69..6df9a28eefb3 100644
--- a/crates/sui-framework/packages/move-stdlib/sources/option.move
+++ b/crates/sui-framework/packages/move-stdlib/sources/option.move
@@ -213,6 +213,13 @@ public macro fun map_ref<$T, $U>($o: &Option<$T>, $f: |&$T| -> $U): Option<$U> {
     if (o.is_some()) some($f(o.borrow())) else none()
 }

+/// Map an `Option<T>` value to `Option<U>` by applying a function to a contained value by mutable
+/// reference. Original `Option<T>` is preserved, although potentially modified.
+public macro fun map_mut<$T, $U>($o: &mut Option<$T>, $f: |&mut $T| -> $U): Option<$U> {
+    let o = $o;
+    if (o.is_some()) some($f(o.borrow_mut())) else none()
+}
+
 /// Return `None` if the value is `None`, otherwise return `Option<T>` if the predicate `f` returns true.
 public macro fun filter<$T: drop>($o: Option<$T>, $f: |&$T| -> bool): Option<$T> {
     let o = $o;
@@ -225,6 +232,41 @@ public macro fun is_some_and<$T>($o: &Option<$T>, $f: |&$T| -> bool): bool {
     o.is_some() && $f(o.borrow())
 }

+/// Return `true` if the value is `None`, or if the predicate `f` returns `true` for the contained
+/// value.
+public macro fun is_none_or<$T>($o: &Option<$T>, $f: |&$T| -> bool): bool {
+    let o = $o;
+    o.is_none() || $f(o.borrow())
+}
+
+/// Consume the option and return `$none` if it is `None`, otherwise apply `$some` to the contained
+/// value.
+/// Note `$none` is evaluated only if the option is `None`.
+public macro fun fold<$T, $R>($o: Option<$T>, $none: $R, $some: |$T| -> $R): $R {
+    let o = $o;
+    if (o.is_some()) {
+        $some(o.destroy_some())
+    } else {
+        o.destroy_none();
+        $none
+    }
+}
+
+/// Apply `$some` to the borrowed value if `Some`, otherwise return `$none`.
+/// Original option is preserved.
+/// Note `$none` is evaluated only if the option is `None`.
+public macro fun fold_ref<$T, $R>($o: &Option<$T>, $none: $R, $some: |&$T| -> $R): $R {
+    let o = $o;
+    if (o.is_some()) $some(o.borrow()) else $none
+}
+
+/// Apply `$some` to the mutably borrowed value if `Some`, otherwise return `$none`.
+/// Note `$none` is evaluated only if the option is `None`.
+public macro fun fold_mut<$T, $R>($o: &mut Option<$T>, $none: $R, $some: |&mut $T| -> $R): $R {
+    let o = $o;
+    if (o.is_some()) $some(o.borrow_mut()) else $none
+}
+
 /// Extract the value inside `Option<T>` if it holds one, or `default` otherwise.
 /// Similar to `destroy_or`, but modifying the input `Option` via a mutable reference.
 public macro fun extract_or<$T>($o: &mut Option<$T>, $default: $T): $T {
PATCH

echo "Patch applied successfully"
