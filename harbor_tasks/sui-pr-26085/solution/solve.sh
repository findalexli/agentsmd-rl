#!/bin/bash
set -e

cd /workspace/sui

# Check if already applied
if grep -q "public macro fun map_mut" crates/sui-framework/packages/move-stdlib/sources/option.move; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the source code patch
patch -p1 <<'PATCH'
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
diff --git a/crates/sui-framework/packages/move-stdlib/tests/option_tests.move b/crates/sui-framework/packages/move-stdlib/tests/option_tests.move
index 2eef10e0ec67..a8438e83a21c 100644
--- a/crates/sui-framework/packages/move-stdlib/tests/option_tests.move
+++ b/crates/sui-framework/packages/move-stdlib/tests/option_tests.move
@@ -214,6 +214,16 @@ fun map_map_ref() {
     assert_eq!(option::none<u8>().map_ref!(|x| vector[*x]), option::none());
 }

+#[test]
+fun map_mut() {
+    let mut opt = option::some(5u64);
+    assert_eq!(opt.map_mut!(|x| { *x = 100; vector[*x] }), option::some(vector[100]));
+    assert_eq!(*opt.borrow(), 100);
+
+    let mut none = option::none<u64>();
+    assert_eq!(none.map_mut!(|x| { *x = 100; vector[*x] }), option::none());
+}
+
 #[test]
 fun map_no_drop() {
     let none = option::none<NoDrop>().map!(|el| {
@@ -299,3 +309,47 @@ fun extract_or() {
     assert_eq!(some.extract_or!(10), 5u64);
     assert!(some.is_none());
 }
+
+#[test]
+fun is_none_or() {
+    assert!(option::some(5u64).is_none_or!(|x| *x == 5));
+    assert!(!option::some(5u64).is_none_or!(|x| *x == 6));
+    assert!(option::none<u64>().is_none_or!(|x| *x == 5));
+}
+
+#[test]
+fun fold() {
+    assert_eq!(option::some(5u64).fold!(0, |x| x + 1), 6);
+    assert_eq!(option::none<u64>().fold!(0, |x| x + 1), 0);
+}
+
+#[test]
+fun fold_no_drop() {
+    let some = option::some(NoDrop {}).fold!(10u64, |el| {
+        let NoDrop {} = el;
+        100
+    });
+    let none = option::none<NoDrop>().fold!(10u64, |el| {
+        let NoDrop {} = el;
+        100
+    });
+    assert_eq!(some, 100);
+    assert_eq!(none, 10);
+}
+
+#[test]
+fun fold_ref() {
+    assert_eq!(option::some(5u64).fold_ref!(0, |x| *x + 1), 6);
+    assert_eq!(option::none<u64>().fold_ref!(0, |x| *x + 1), 0);
+}
+
+#[test]
+fun fold_mut() {
+    let mut opt = option::some(5u64);
+    let result = opt.fold_mut!(0u64, |x| { *x = 100; 42u64 });
+    assert_eq!(result, 42);
+    assert_eq!(*opt.borrow(), 100);
+
+    let mut none = option::none<u64>();
+    assert_eq!(none.fold_mut!(0u64, |x| { *x = 100; 42u64 }), 0);
+}
PATCH

echo "Patch applied successfully"
