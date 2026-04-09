#!/bin/bash
set -e

cd /workspace/sui

# Check if already patched
grep -q "Invalid {} of temporary variable" external-crates/move/crates/move-compiler/src/cfgir/borrows/state.rs 2>/dev/null && {
    echo "Already patched, skipping"
    exit 0
}

# Apply the gold patch
patch -p1 << 'PATCH'
diff --git a/external-crates/move/crates/move-compiler/src/cfgir/borrows/state.rs b/external-crates/move/crates/move-compiler/src/cfgir/borrows/state.rs
index 3dc5e8670cc7..0780774b46e5 100644
--- a/external-crates/move/crates/move-compiler/src/cfgir/borrows/state.rs
+++ b/external-crates/move/crates/move-compiler/src/cfgir/borrows/state.rs
@@ -413,11 +413,7 @@ impl BorrowState {
             &BTreeMap::new(),
             code,
             move || match display_var(local.value()) {
-                DisplayVar::Tmp => panic!(
-                    "ICE invalid use of tmp local {} with borrows {:#?}",
-                    local.value(),
-                    borrows
-                ),
+                DisplayVar::Tmp => format!("Invalid {} of temporary variable", verb),
                 DisplayVar::MatchTmp(_s) => format!("Invalid {} of temporary match variable", verb),
                 DisplayVar::Orig(s) => format!("Invalid {} of variable '{}'", verb, s),
             },
@@ -577,7 +573,10 @@ impl BorrowState {
         self.locals.add(*local, Value::NonRef).unwrap();
         match old_value {
             Value::Ref(id) => (Diagnostics::new(), Value::Ref(id)),
-            Value::NonRef if last_usage_inferred => {
+            Value::NonRef
+                if last_usage_inferred
+                    && matches!(display_var(local.value()), DisplayVar::Orig(_)) =>
+            {
                 let root_and_local_borrows = self.local_borrowed_by(local);
                 let mut diag_opt = Self::borrow_error(
                     &self.borrows,
@@ -587,31 +586,19 @@ impl BorrowState {
                     ReferenceSafety::AmbiguousVariableUsage,
                     || {
                         let vstr = match display_var(local.value()) {
-                            DisplayVar::Tmp => {
-                                panic!("ICE invalid use tmp local {}", local.value())
-                            }
-                            DisplayVar::MatchTmp(s) => {
-                                panic!("ICE invalid use match tmp {}: {}", s, local.value())
-                            }
                             DisplayVar::Orig(s) => s,
+                            DisplayVar::MatchTmp(_) | DisplayVar::Tmp => unreachable!(),
                         };
                         format!("Ambiguous usage of variable '{}'", vstr)
                     },
                 );
-                diag_opt.iter_mut().for_each(|diag| {
-                    let vstr = match display_var(local.value()) {
-                        DisplayVar::Tmp => {
-                            panic!("ICE invalid use tmp local {}", local.value())
-                        }
-                        DisplayVar::MatchTmp(s) => {
-                            panic!("ICE invalid use match tmp {}: {}", s, local.value())
-                        }
+                // add a tip for user-defined variables
+                if let Some(diag) = &mut diag_opt {
+                    let v = match display_var(local.value()) {
                         DisplayVar::Orig(s) => s,
+                        DisplayVar::MatchTmp(_) | DisplayVar::Tmp => unreachable!(),
                     };
-                    let tip = format!(
-                        "Try an explicit annotation, e.g. 'move {v}' or 'copy {v}'",
-                        v = vstr
-                    );
+                    let tip = format!("Try an explicit annotation, e.g. 'move {v}' or 'copy {v}'");
                     const EXPLANATION: &str = "Ambiguous inference of 'move' or 'copy' for a \
                                                borrowed variable's last usage: A 'move' would \
                                                invalidate the borrowing reference, but a 'copy' \
@@ -619,7 +606,7 @@ impl BorrowState {
                                                this the last direct usage of the variable.";
                     diag.add_secondary_label((loc, tip));
                     diag.add_note(EXPLANATION);
-                });
+                };
                 (diag_opt.into(), Value::NonRef)
             }
             Value::NonRef => {
diff --git a/external-crates/move/crates/move-compiler/tests/move_2024/borrows/borrow_edge_overflow_tmp.move b/external-crates/move/crates/move-compiler/tests/move_2024/borrows/borrow_edge_overflow_tmp.move
new file mode 100644
index 000000000000..ee03a05d35fb
--- /dev/null
+++ b/external-crates/move/crates/move-compiler/tests/move_2024/borrows/borrow_edge_overflow_tmp.move
@@ -0,0 +1,19 @@
+//  This specific test will improve in the borrow checker rewrite
+module 0x42::m;
+
+public fun f(test: bool): &u64 {
+    let (a, b, c, d, e, f, g, h, i, j, k) = (0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0);
+    let mut x = &a;
+    if (test) x = &b;
+    if (test) x = &c;
+    if (test) x = &d;
+    if (test) x = &e;
+    if (test) x = &f;
+    if (test) x = &g;
+    if (test) x = &h;
+    if (test) x = &i;
+    if (test) x = &j;
+    if (test) x = &k;
+    test && test;
+    x
+}
diff --git a/external-crates/move/crates/move-compiler/tests/move_2024/borrows/borrow_edge_overflow_tmp.snap b/external-crates/move/crates/move-compiler/tests/move_2024/borrows/borrow_edge_overflow_tmp.snap
new file mode 100644
index 000000000000..bfbb1d2dcf26
--- /dev/null
+++ b/external-crates/move/crates/move-compiler/tests/move_2024/borrows/borrow_edge_overflow_tmp.snap
@@ -0,0 +1,164 @@
+---
+source: crates/move-compiler/tests/move_check_testsuite.rs
+info:
+  flavor: core
+  edition: 2024.alpha
+  lint: false
+---
+error[E07003]: invalid operation, could create dangling a reference
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:17:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+17 │     test && test;
+   │     ^^^^^^^^^^^^ Invalid assignment of temporary variable
+
+error[E07003]: invalid operation, could create dangling a reference
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:17:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+17 │     test && test;
+   │     ^^^^^^^^^^^^ Invalid move of temporary variable
+
+error[E07006]: ambiguous usage of variable
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:17:13
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+17 │     test && test;
+   │             ^^^^
+   │             │
+   │             Ambiguous usage of variable 'test'
+   │             Try an explicit annotation, e.g. 'move test' or 'copy test'
+   │
+   = Ambiguous inference of 'move' or 'copy' for a borrowed variable's last usage: A 'move' would invalidate the borrowing reference, but a 'copy' might not be the expected implicit behavior since this the last direct usage of the variable.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+   ·
+18 │     x
+   │     ^ Invalid return. Local value is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+   ·
+18 │     x
+   │     ^ Invalid return. Local variable 'a' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'b' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'c' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'd' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'e' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'f' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'g' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'h' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'i' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'j' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'k' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'test' is still being borrowed.
+
+error[E07004]: invalid return of locally borrowed state
+   ┌─ tests/move_2024/borrows/borrow_edge_overflow_tmp.move:18:5
+   │
+15 │     if (test) x = &j;
+   │                   -- It is still being borrowed by this reference
+16 │     if (test) x = &k;
+18 │     x
+   │     ^ Invalid return. Local variable 'x' is still being borrowed.
PATCH

echo "Patch applied successfully"
