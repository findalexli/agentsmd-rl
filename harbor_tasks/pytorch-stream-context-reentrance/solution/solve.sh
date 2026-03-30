#!/usr/bin/env bash
set -euo pipefail
cd /workspace/pytorch

# Idempotent: skip if already applied
grep -q 'PyList_New' torch/csrc/Stream.cpp && exit 0

git apply --whitespace=fix - <<'PATCH'
diff --git a/torch/csrc/Stream.cpp b/torch/csrc/Stream.cpp
index fc1ca916cfbed..c5a8e343e6b27 100644
--- a/torch/csrc/Stream.cpp
+++ b/torch/csrc/Stream.cpp
@@ -119,6 +119,7 @@ PyObject* THPStream_Wrap(const c10::Stream& stream) {

 static void THPStream_dealloc(THPStream* self) {
   PyObject_ClearWeakRefs((PyObject*)self);
+  Py_CLEAR(self->context);
   Py_TYPE(self)->tp_free(reinterpret_cast<PyObject*>(self));
 }

@@ -277,38 +278,71 @@ static PyObject* THPStream_enter(PyObject* _self, PyObject* unused) {
   auto self = reinterpret_cast<THPStream*>(_self);
   c10::DeviceType stream_device_type =
       static_cast<c10::DeviceType>(self->device_type);
+
   // No operation is performed if the stream does not belong to an accelerator.
   if (C10_UNLIKELY(!at::accelerator::isAccelerator(stream_device_type))) {
     Py_INCREF(_self);
     return _self;
   }
+
+  if (!self->context) {
+    auto list = THPObjectPtr(PyList_New(0));
+    if (!list) {
+      throw python_error();
+    }
+    self->context = list.release();
+  }
+
   c10::DeviceIndex cur_device_idx = at::accelerator::getDeviceIndex();
   c10::DeviceIndex stream_device_idx =
       static_cast<c10::DeviceIndex>(self->device_index);
+  c10::Stream cur_stream = at::accelerator::getCurrentStream(stream_device_idx);
+
+  if (cur_stream.id() == self->stream_id &&
+      cur_stream.device_index() == stream_device_idx) {
+    if (PyList_Append(self->context, Py_None) < 0) {
+      throw python_error();
+    }
+    Py_INCREF(_self);
+    return _self;
+  }
+
   // If the stream is not on the current device, switch the current device to
   // the device of the stream.
   if (stream_device_idx != cur_device_idx) {
     at::accelerator::setDeviceIndex(stream_device_idx);
   }
-  c10::Stream cur_stream = at::accelerator::getCurrentStream(stream_device_idx);
   at::accelerator::setCurrentStream(c10::Stream::unpack3(
       self->stream_id, stream_device_idx, stream_device_type));
-  // Save the current device index and previous stream to the context.
+
   auto ctx_device_index =
       THPObjectPtr(THPUtils_packDeviceIndex(cur_device_idx));
   auto ctx_stream = THPObjectPtr(THPStream_Wrap(cur_stream));
-  TORCH_CHECK(!(self->context), "Stream's context should not be initialized.");
   auto dict = THPObjectPtr(PyDict_New());
   if (!dict) {
     throw python_error();
   }
-  self->context = dict.release();
   if (PyDict_SetItemString(
-          self->context, "_ctx_device_index", ctx_device_index.get()) < 0) {
+          dict.get(), "_ctx_device_index", ctx_device_index.get()) < 0) {
+    throw python_error();
+  }
+  if (PyDict_SetItemString(dict.get(), "_ctx_stream", ctx_stream.get()) < 0) {
     throw python_error();
   }
-  if (PyDict_SetItemString(self->context, "_ctx_stream", ctx_stream.get()) <
-      0) {
+  if (PyList_Append(self->context, dict.get()) < 0) {
     throw python_error();
   }
   Py_INCREF(_self);
@@ -319,19 +353,34 @@ static PyObject* THPStream_enter(PyObject* _self, PyObject* unused) {
 static PyObject* THPStream_exit(PyObject* _self, PyObject* unused) {
   HANDLE_TH_ERRORS
   auto self = reinterpret_cast<THPStream*>(_self);
+
   // No operation is performed if the stream does not belong to an accelerator.
   if (C10_UNLIKELY(!at::accelerator::isAccelerator(
           static_cast<c10::DeviceType>(self->device_type)))) {
     Py_RETURN_NONE;
   }
+
+  Py_ssize_t stack_size = PyList_Size(self->context);
+  TORCH_INTERNAL_ASSERT(stack_size > 0, "Stream context stack is empty.");
+  PyObject* top = PyList_GET_ITEM(self->context, stack_size - 1);
+
+  if (top == Py_None) {
+    if (PyList_SetSlice(self->context, stack_size - 1, stack_size, nullptr) <
+        0) {
+      throw python_error();
+    }
+    Py_RETURN_NONE;
+  }
+
   PyObject* py_stream = nullptr;
-  if (PyDict_GetItemStringRef(self->context, "_ctx_stream", &py_stream) < 0) {
+  if (PyDict_GetItemStringRef(top, "_ctx_stream", &py_stream) < 0) {
     throw python_error();
   }
   auto ctx_stream = THPObjectPtr(py_stream);
   PyObject* py_device_index = nullptr;
-  if (PyDict_GetItemStringRef(
-          self->context, "_ctx_device_index", &py_device_index) < 0) {
+  if (PyDict_GetItemStringRef(top, "_ctx_device_index", &py_device_index) < 0) {
     throw python_error();
   }
   auto ctx_device_index = THPObjectPtr(py_device_index);
@@ -342,6 +391,7 @@ static PyObject* THPStream_exit(PyObject* _self, PyObject* unused) {
       ctx_device_index.get(),
       "ctx_device_index should be present on the context dict.");
   auto prev_device_index = THPUtils_unpackDeviceIndex(ctx_device_index.get());
+
   at::accelerator::setCurrentStream(c10::Stream::unpack3(
       prev_stream->stream_id,
       static_cast<c10::DeviceIndex>(prev_stream->device_index),
@@ -350,7 +400,9 @@ static PyObject* THPStream_exit(PyObject* _self, PyObject* unused) {
   if (static_cast<c10::DeviceIndex>(self->device_index) != prev_device_index) {
     at::accelerator::setDeviceIndex(prev_device_index);
   }
-  Py_CLEAR(self->context);
+  if (PyList_SetSlice(self->context, stack_size - 1, stack_size, nullptr) < 0) {
+    throw python_error();
+  }
   Py_RETURN_NONE;
   END_HANDLE_TH_ERRORS
 }
PATCH
