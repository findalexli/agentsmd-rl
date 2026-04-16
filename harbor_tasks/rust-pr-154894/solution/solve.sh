#!/bin/bash
set -e

cd /workspace/rust

# Idempotency check - if already patched, exit early
if grep -q "imm_ptr_to_mplace" compiler/rustc_const_eval/src/interpret/place.rs; then
    echo "Already patched, skipping"
    exit 0
fi

# Apply the gold patch
cat << 'PATCH' | git apply
From 407259b2ff7ebe66eaacd566570a7ac7d28b3e19 Mon Sep 17 00:00:00 2001
From: Waffle Lapkin <waffle.lapkin@gmail.com>
Date: Tue, 15 Jul 2025 19:08:15 +0200
Subject: [PATCH] slightly refactor mplace<->ptr conversions

---
 .../src/const_eval/machine.rs                 |  2 +-
 .../src/const_eval/type_info.rs               |  4 +--
 .../src/const_eval/type_info/adt.rs           |  2 +-
 .../rustc_const_eval/src/interpret/call.rs   |  6 ++--
 .../src/interpret/intrinsics.rs              |  2 +-
 .../rustc_const_eval/src/interpret/place.rs   | 32 ++++++++++++-------
 .../rustc_const_eval/src/interpret/validity.rs |  2 +-
 .../borrow_tracker/stacked_borrows/mod.rs    |  2 +-
 .../borrow_tracker/tree_borrows/mod.rs       |  2 +-
 src/tools/miri/src/shims/panic.rs            |  4 +--
 10 files changed, 32 insertions(+), 26 deletions(-)

diff --git a/compiler/rustc_const_eval/src/const_eval/machine.rs b/compiler/rustc_const_eval/src/const_eval/machine.rs
index a19bf0b4da8be..316bca5a258f1 100644
--- a/compiler/rustc_const_eval/src/const_eval/machine.rs
+++ b/compiler/rustc_const_eval/src/const_eval/machine.rs
@@ -840,7 +840,7 @@ impl<'tcx> interpret::Machine<'tcx> for CompileTimeMachine<'tcx> {
         {
             // That next check is expensive, that's why we have all the guards above.
             let is_immutable = ty.is_freeze(*ecx.tcx, ecx.typing_env());
-            let place = ecx.ref_to_mplace(val)?;
+            let place = ecx.imm_ptr_to_mplace(val)?;
             let new_place = if is_immutable {
                 place.map_provenance(CtfeProvenance::as_immutable)
             } else {
diff --git a/compiler/rustc_const_eval/src/const_eval/type_info.rs b/compiler/rustc_const_eval/src/const_eval/type_info.rs
index 0ed04a5ab20b4..dffc66f731af0 100644
--- a/compiler/rustc_const_eval/src/const_eval/type_info.rs
+++ b/compiler/rustc_const_eval/src/const_eval/type_info.rs
@@ -261,7 +261,7 @@ impl<'tcx> InterpCx<'tcx, CompileTimeMachine<'tcx>> {
                         None => Cow::Owned(idx.to_string()), // For tuples
                     };
                     let name_place = self.allocate_str_dedup(&name)?;
-                    let ptr = self.mplace_to_ref(&name_place)?;
+                    let ptr = self.mplace_to_imm_ptr(&name_place, None)?;
                     self.write_immediate(*ptr, &field_place)?
                 }
                 sym::ty => {
@@ -444,7 +444,7 @@ impl<'tcx> InterpCx<'tcx, CompileTimeMachine<'tcx>> {
                     other_abi => {
                         let (variant, variant_place) = self.downcast(&field_place, sym::Named)?;
                         let str_place = self.allocate_str_dedup(other_abi.as_str())?;
-                        let str_ref = self.mplace_to_ref(&str_place)?;
+                        let str_ref = self.mplace_to_imm_ptr(&str_place, None)?;
                         let payload = self.project_field(&variant_place, FieldIdx::ZERO)?;
                         self.write_immediate(*str_ref, &payload)?;
                         self.write_discriminant(variant, &field_place)?;
diff --git a/compiler/rustc_const_eval/src/const_eval/type_info/adt.rs b/compiler/rustc_const_eval/src/const_eval/type_info/adt.rs
index 60f7b95e799a6..2143313bbbada 100644
--- a/compiler/rustc_const_eval/src/const_eval/type_info/adt.rs
+++ b/compiler/rustc_const_eval/src/const_eval/type_info/adt.rs
@@ -165,7 +165,7 @@ impl<'tcx> InterpCx<'tcx, CompileTimeMachine<'tcx>> {
             match field_def.name {
                 sym::name => {
                     let name_place = self.allocate_str_dedup(variant_def.name.as_str())?;
-                    let ptr = self.mplace_to_ref(&name_place)?;
+                    let ptr = self.mplace_to_imm_ptr(&name_place, None)?;
                     self.write_immediate(*ptr, &field_place)?
                 }
                 sym::fields => {
diff --git a/compiler/rustc_const_eval/src/interpret/call.rs b/compiler/rustc_const_eval/src/interpret/call.rs
index 0ac9f3025d48c..d948b78a0bcf9 100644
--- a/compiler/rustc_const_eval/src/interpret/call.rs
+++ b/compiler/rustc_const_eval/src/interpret/call.rs
@@ -704,7 +704,7 @@ impl<'tcx, M: Machine<'tcx>> InterpCx<'tcx, M> {
                             // actually access memory to resolve this method.
                             // Also see <https://github.com/rust-lang/miri/issues/2786>.
                             let val = self.read_immediate(&receiver)?;
-                            break self.ref_to_mplace(&val)?;
+                            break self.imm_ptr_to_mplace(&val)?;
                         }
                         ty::Dynamic(..) => break receiver.assert_mem_place(), // no immediate unsized values
                         _ => {
@@ -877,7 +877,7 @@ impl<'tcx, M: Machine<'tcx>> InterpCx<'tcx, M> {
         // then dispatches that to the normal call machinery. However, our call machinery currently
         // only supports calling `VtblEntry::Method`; it would choke on a `MetadataDropInPlace`. So
         // instead we do the virtual call stuff ourselves. It's easier here than in `eval_fn_call`
-        // since we can just get a place of the underlying type and use `mplace_to_ref`.
+        // since we can just get a place of the underlying type and use `mplace_to_imm_ptr`.
         let place = match place.layout.ty.kind() {
             ty::Dynamic(data, _) => {
                 // Dropping a trait object. Need to find actual drop fn.
@@ -898,7 +898,7 @@ impl<'tcx, M: Machine<'tcx>> InterpCx<'tcx, M> {
         };
         let fn_abi = self.fn_abi_of_instance_no_deduced_attrs(instance, ty::List::empty())?;

-        let arg = self.mplace_to_ref(&place)?;
+        let arg = self.mplace_to_imm_ptr(&place, None)?;
         let ret = MPlaceTy::fake_alloc_zst(self.layout_of(self.tcx.types.unit)?);

         self.init_fn_call(
diff --git a/compiler/rustc_const_eval/src/interpret/intrinsics.rs b/compiler/rustc_const_eval/src/interpret/intrinsics.rs
index 17311188879c1..79a9b616cfcfa 100644
--- a/compiler/rustc_const_eval/src/interpret/intrinsics.rs
+++ b/compiler/rustc_const_eval/src/interpret/intrinsics.rs
@@ -281,7 +281,7 @@ impl<'tcx, M: Machine<'tcx>> InterpCx<'tcx, M> {
             sym::align_of_val | sym::size_of_val => {
                 // Avoid `deref_pointer` -- this is not a deref, the ptr does not have to be
                 // dereferenceable!
-                let place = self.ref_to_mplace(&self.read_immediate(&args[0])?)?;
+                let place = self.imm_ptr_to_mplace(&self.read_immediate(&args[0])?)?;
                 let (size, align) = self
                     .size_and_align_of_val(&place)?
                     .ok_or_else(|| err_unsup_format!("`extern type` does not have known layout"))?;
diff --git a/compiler/rustc_const_eval/src/interpret/place.rs b/compiler/rustc_const_eval/src/interpret/place.rs
index b410e8f6c57ea..0118fd71a5975 100644
--- a/compiler/rustc_const_eval/src/interpret/place.rs
+++ b/compiler/rustc_const_eval/src/interpret/place.rs
@@ -417,36 +417,46 @@ where
         self.ptr_with_meta_to_mplace(ptr, MemPlaceMeta::None, layout, /*unaligned*/ true)
     }

-    /// Take a value, which represents a (thin or wide) reference, and make it a place.
-    /// Alignment is just based on the type. This is the inverse of `mplace_to_ref()`.
+    /// Take a value, which represents a (thin or wide) pointer, and make it a place.
+    /// Alignment is just based on the type. This is the inverse of `mplace_to_imm_ptr()`.
     ///
     /// Only call this if you are sure the place is "valid" (aligned and inbounds), or do not
     /// want to ever use the place for memory access!
     /// Generally prefer `deref_pointer`.
-    pub fn ref_to_mplace(
+    pub fn imm_ptr_to_mplace(
         &self,
         val: &ImmTy<'tcx, M::Provenance>,
     ) -> InterpResult<'tcx, MPlaceTy<'tcx, M::Provenance>> {
         let pointee_type =
-            val.layout.ty.builtin_deref(true).expect("`ref_to_mplace` called on non-ptr type");
+            val.layout.ty.builtin_deref(true).expect("`imm_ptr_to_mplace` called on non-ptr type");
         let layout = self.layout_of(pointee_type)?;
         let (ptr, meta) = val.to_scalar_and_meta();

-        // `ref_to_mplace` is called on raw pointers even if they don't actually get dereferenced;
+        // `imm_ptr_to_mplace` is called on raw pointers even if they don't actually get dereferenced;
         // we hence can't call `size_and_align_of` since that asserts more validity than we want.
         let ptr = ptr.to_pointer(self)?;
         interp_ok(self.ptr_with_meta_to_mplace(ptr, meta, layout, /*unaligned*/ false))
     }

     /// Turn a mplace into a (thin or wide) mutable raw pointer, pointing to the same space.
+    ///
     /// `align` information is lost!
-    /// This is the inverse of `ref_to_mplace`.
-    pub fn mplace_to_ref(
+    /// This is the inverse of `imm_ptr_to_mplace`.
+    ///
+    /// If `ptr_ty` is provided, the resulting pointer will be of that type. Otherwise, it defaults to `*mut _`.
+    /// `ptr_ty` must be a type with builtin deref which derefs to the type of `mplace` (`mplace.layout.ty`).
+    pub fn mplace_to_imm_ptr(
         &self,
         mplace: &MPlaceTy<'tcx, M::Provenance>,
+        ptr_ty: Option<Ty<'tcx>>,
     ) -> InterpResult<'tcx, ImmTy<'tcx, M::Provenance>> {
         let imm = mplace.mplace.to_ref(self);
-        let layout = self.layout_of(Ty::new_mut_ptr(self.tcx.tcx, mplace.layout.ty))?;
+
+        let ptr_ty = ptr_ty
+            .inspect(|t| assert_eq!(t.builtin_deref(true), Some(mplace.layout.ty)))
+            .unwrap_or_else(|| Ty::new_mut_ptr(self.tcx.tcx, mplace.layout.ty));
+
+        let layout = self.layout_of(ptr_ty)?;
         interp_ok(ImmTy::from_immediate(imm, layout))
     }

@@ -467,7 +477,7 @@ where
         let val = self.read_immediate(src)?;
         trace!("deref to {} on {:?}", val.layout.ty, *val);

-        let mplace = self.ref_to_mplace(&val)?;
+        let mplace = self.imm_ptr_to_mplace(&val)?;
         interp_ok(mplace)
     }

diff --git a/compiler/rustc_const_eval/src/interpret/validity.rs b/compiler/rustc_const_eval/src/interpret/validity.rs
index de340057d0e81..c1b72369dfadf 100644
--- a/compiler/rustc_const_eval/src/interpret/validity.rs
+++ b/compiler/rustc_const_eval/src/interpret/validity.rs
@@ -572,7 +572,7 @@ impl<'rt, 'tcx, M: Machine<'tcx>> ValidityVisitor<'rt, 'tcx, M> {
             self.add_data_range_place(val);
         }
         // Now turn it into a place.
-        self.ecx.ref_to_mplace(&imm)
+        self.ecx.imm_ptr_to_mplace(&imm)
     }

     fn check_wide_ptr_meta(
diff --git a/src/tools/miri/src/borrow_tracker/stacked_borrows/mod.rs b/src/tools/miri/src/borrow_tracker/stacked_borrows/mod.rs
index 66e804d972b76..8adb6d3127694 100644
--- a/src/tools/miri/src/borrow_tracker/stacked_borrows/mod.rs
+++ b/src/tools/miri/src/borrow_tracker/stacked_borrows/mod.rs
@@ -859,7 +859,7 @@ trait EvalContextPrivExt<'tcx, 'ecx>: crate::MiriInterpCxExt<'tcx> {
         info: RetagInfo, // diagnostics info about this retag
     ) -> InterpResult<'tcx, ImmTy<'tcx>> {
         let this = self.eval_context_mut();
-        let place = this.ref_to_mplace(val)?;
+        let place = this.imm_ptr_to_mplace(val)?;
         let new_place = this.sb_retag_place(&place, new_perm, info)?;
         interp_ok(ImmTy::from_immediate(new_place.to_ref(this), val.layout))
     }
diff --git a/src/tools/miri/src/borrow_tracker/tree_borrows/mod.rs b/src/tools/miri/src/borrow_tracker/tree_borrows/mod.rs
index a205502327307..b191359501d18 100644
--- a/src/tools/miri/src/borrow_tracker/tree_borrows/mod.rs
+++ b/src/tools/miri/src/borrow_tracker/tree_borrows/mod.rs
@@ -415,7 +415,7 @@ trait EvalContextPrivExt<'tcx>: crate::MiriInterpCxExt<'tcx> {
         new_perm: NewPermission,
     ) -> InterpResult<'tcx, ImmTy<'tcx>> {
         let this = self.eval_context_mut();
-        let place = this.ref_to_mplace(val)?;
+        let place = this.imm_ptr_to_mplace(val)?;
         let new_place = this.tb_retag_place(&place, new_perm)?;
         interp_ok(ImmTy::from_immediate(new_place.to_ref(this), val.layout))
     }
diff --git a/src/tools/miri/src/shims/panic.rs b/src/tools/miri/src/shims/panic.rs
index 85564e47685f2..50e32cffaee3f 100644
--- a/src/tools/miri/src/shims/panic.rs
+++ b/src/tools/miri/src/shims/panic.rs
@@ -20,7 +20,7 @@ pub trait EvalContextExt<'tcx>: crate::MiriInterpCxExt<'tcx> {
         this.call_function(
             panic,
             ExternAbi::Rust,
-            &[this.mplace_to_ref(&msg)?],
+            &[this.mplace_to_imm_ptr(&msg, None)?],
             None,
             ReturnContinuation::Goto { ret: None, unwind },
         )
@@ -39,7 +39,7 @@ pub trait EvalContextExt<'tcx>: crate::MiriInterpCxExt<'tcx> {
         this.call_function(
             panic,
             ExternAbi::Rust,
-            &[this.mplace_to_ref(&msg)?],
+            &[this.mplace_to_imm_ptr(&msg, None)?],
             None,
             ReturnContinuation::Goto { ret: None, unwind: mir::UnwindAction::Unreachable },
         )
PATCH

echo "Patch applied successfully"
