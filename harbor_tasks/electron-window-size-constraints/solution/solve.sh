#!/bin/bash
set -e

cd /workspace/electron

# Check if already patched (idempotency)
if grep -q "Clamping size before SetPosition" shell/browser/native_window.cc 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/shell/browser/native_window.cc b/shell/browser/native_window.cc
index e8e9e47fb72a7..af34bd5d87a0d 100644
--- a/shell/browser/native_window.cc
+++ b/shell/browser/native_window.cc
@@ -140,24 +140,10 @@ NativeWindow::~NativeWindow() {

 void NativeWindow::InitFromOptions(const gin_helper::Dictionary& options) {
   // Setup window from options.
-  if (int x, y; options.Get(options::kX, &x) && options.Get(options::kY, &y)) {
-    SetPosition(gfx::Point{x, y});
-
-#if BUILDFLAG(IS_WIN)
-    // FIXME(felixrieseberg): Dirty, dirty workaround for
-    // https://github.com/electron/electron/issues/10862
-    // Somehow, we need to call `SetBounds` twice to get
-    // usable results. The root root cause is still unknown.
-    SetPosition(gfx::Point{x, y});
-#endif
-  } else if (bool center; options.Get(options::kCenter, &center) && center) {
-    Center();
-  }
-
   const bool use_content_size =
       options.ValueOrDefault(options::kUseContentSize, false);

-  // On Linux and Window we may already have maximum size defined.
+  // On Linux and Windows we may already have minimum and maximum size defined.
   extensions::SizeConstraints size_constraints(
       use_content_size ? GetContentSizeConstraints() : GetSizeConstraints());

@@ -184,10 +170,32 @@ void NativeWindow::InitFromOptions(const gin_helper::Dictionary& options) {
     size_constraints.set_maximum_size(gfx::Size(max_width, max_height));

   if (use_content_size) {
+    gfx::Size clamped = size_constraints.ClampSize(GetContentSize());
+    if (clamped != GetContentSize()) {
+      SetContentSize(clamped);
+    }
     SetContentSizeConstraints(size_constraints);
   } else {
+    gfx::Size clamped = size_constraints.ClampSize(GetSize());
+    if (clamped != GetSize()) {
+      SetSize(clamped);
+    }
     SetSizeConstraints(size_constraints);
   }
+
+  // Clamping size before SetPosition ensures min/max constraints are respected on window creation.
+  if (int x, y; options.Get(options::kX, &x) && options.Get(options::kY, &y)) {
+    SetPosition(gfx::Point{x, y});
+
+#if BUILDFLAG(IS_WIN)
+    // FIXME(felixrieseberg): Dirty, dirty workaround for
+    // https://github.com/electron/electron/issues/10862
+    // Somehow, we need to call `SetBounds` twice to get
+    // usable results. The root cause is still unknown.
+    SetPosition(gfx::Point{x, y});
+#endif
+  } else if (bool center; options.Get(options::kCenter, &center) && center) {
+    Center();
+  }
 #if BUILDFLAG(IS_WIN) || BUILDFLAG(IS_LINUX)
   if (bool val; options.Get(options::kClosable, &val))
     SetClosable(val);
PATCH

echo "Patch applied successfully"
