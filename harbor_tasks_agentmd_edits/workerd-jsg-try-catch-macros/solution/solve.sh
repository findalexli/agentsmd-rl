#!/usr/bin/env bash
set -euo pipefail

cd /workspace/workerd

# Idempotent: skip if already applied
if grep -q 'JSG_TRY' src/workerd/jsg/jsg.h 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/src/workerd/api/crypto/crypto.c++ b/src/workerd/api/crypto/crypto.c++
index f17b69f397e..cd0db80ffe8 100644
--- a/src/workerd/api/crypto/crypto.c++
+++ b/src/workerd/api/crypto/crypto.c++
@@ -806,13 +806,16 @@ DigestStream::DigestStream(kj::Own<WritableStreamController> controller,
       state(Ready(kj::mv(algorithm), kj::mv(resolver))) {}

 void DigestStream::dispose(jsg::Lock& js) {
-  js.tryCatch([&] {
+  JSG_TRY(js) {
     KJ_IF_SOME(ready, state.tryGet<Ready>()) {
       auto reason = js.typeError("The DigestStream was disposed.");
       ready.resolver.reject(js, reason);
       state.init<StreamStates::Errored>(js.v8Ref<v8::Value>(reason));
     }
-  }, [&](jsg::Value exception) { js.throwException(kj::mv(exception)); });
+  }
+  JSG_CATCH(exception) {
+    js.throwException(kj::mv(exception));
+  }
 }

 void DigestStream::visitForMemoryInfo(jsg::MemoryTracker& tracker) const {
diff --git a/src/workerd/api/memory-cache.c++ b/src/workerd/api/memory-cache.c++
index 703e23bf47d..5cbf1684cae 100644
--- a/src/workerd/api/memory-cache.c++
+++ b/src/workerd/api/memory-cache.c++
@@ -430,11 +430,12 @@ void SharedMemoryCache::Use::delete_(const kj::String& key) const {
 // Attempts to serialize a JavaScript value. If that fails, this function throws
 // a tunneled exception, see jsg::createTunneledException().
 static kj::Own<CacheValue> hackySerialize(jsg::Lock& js, jsg::JsRef<jsg::JsValue>& value) {
-  return js.tryCatch([&]() -> kj::Own<CacheValue> {
+  JSG_TRY(js) {
     jsg::Serializer serializer(js);
     serializer.write(js, value.getHandle(js));
     return kj::atomicRefcounted<CacheValue>(serializer.release().data);
-  }, [&](jsg::Value&& exception) -> kj::Own<CacheValue> {
+  }
+  JSG_CATCH(exception) {
     // We run into big problems with tunneled exceptions here. When
     // the toString() function of the JavaScript error is not marked
     // as side effect free, tunneling the exception fails entirely
@@ -450,7 +451,7 @@ static kj::Own<CacheValue> hackySerialize(jsg::Lock& js, jsg::JsRef<jsg::JsValue
     // This is still pretty bad. We lose the original error stack.
     // TODO(later): remove string-based error tunneling
     throw js.exceptionToKj(kj::mv(exception));
-  });
+  }
 }

 jsg::Promise<jsg::JsRef<jsg::JsValue>> MemoryCache::read(jsg::Lock& js,
diff --git a/src/workerd/api/messagechannel.c++ b/src/workerd/api/messagechannel.c++
index 7313a35c254..224a69d948b 100644
--- a/src/workerd/api/messagechannel.c++
+++ b/src/workerd/api/messagechannel.c++
@@ -42,17 +42,18 @@ MessagePort::MessagePort()
 }

 void MessagePort::dispatchMessage(jsg::Lock& js, const jsg::JsValue& value) {
-  js.tryCatch([&] {
+  JSG_TRY(js) {
     auto message = js.alloc<MessageEvent>(js, kj::str("message"), value, kj::String(), JSG_THIS);
     dispatchEventImpl(js, kj::mv(message));
-  }, [&](jsg::Value exception) {
+  }
+  JSG_CATCH(exception) {
     // There was an error dispatching the message event.
     // We will dispatch a messageerror event instead.
     auto message = js.alloc<MessageEvent>(
         js, kj::str("message"), jsg::JsValue(exception.getHandle(js)), kj::String(), JSG_THIS);
     dispatchEventImpl(js, kj::mv(message));
     // Now, if this dispatchEventImpl throws, we just blow up. Don't try to catch it.
-  });
+  }
 }

 // Deliver the message to this port, buffering if necessary if the port
diff --git a/src/workerd/api/streams/standard.c++ b/src/workerd/api/streams/standard.c++
index 495840356e0..0e84590bb2c 100644
--- a/src/workerd/api/streams/standard.c++
+++ b/src/workerd/api/streams/standard.c++
@@ -505,31 +505,43 @@ jsg::Promise<void> maybeRunAlgorithm(
   // throws synchronously, we have to convert that synchronous throw
   // into a proper rejected jsg::Promise.
   KJ_IF_SOME(algorithm, maybeAlgorithm) {
-    // We need two layers of tryCatch here, unfortunately. The inner layer
+    // We need two layers of JSG_TRY here, unfortunately. The inner layer
     // covers the algorithm implementation itself and is our typical error
     // handling path. It ensures that if the algorithm throws an exception,
     // that is properly converted in to a rejected promise that is *then*
-    // handled by the onFailure handler that is passed in. The outer tryCatch
+    // handled by the onFailure handler that is passed in. The outer JSG_TRY
     // handles the rare and generally unexpected failure of the calls to
     // .then() itself, which can throw JS exceptions synchronously in certain
     // rare cases. For those we return a rejected promise but do not call the
     // onFailure case since such errors are generally indicative of a fatal
     // condition in the isolate (e.g. out of memory, other fatal exception, etc).
-    return js.tryCatch([&] {
+    JSG_TRY(js) {
       KJ_IF_SOME(ioContext, IoContext::tryCurrent()) {
-        return js
-            .tryCatch([&] { return algorithm(js, kj::fwd<decltype(args)>(args)...); },
-                [&](jsg::Value&& exception) { return js.rejectedPromise<void>(kj::mv(exception)); })
-            .then(js, ioContext.addFunctor(kj::mv(onSuccess)),
-                ioContext.addFunctor(kj::mv(onFailure)));
+        auto getInnerPromise = [&]() -> jsg::Promise<void> {
+          JSG_TRY(js) {
+            return algorithm(js, kj::fwd<decltype(args)>(args)...);
+          }
+          JSG_CATCH(exception) {
+            return js.rejectedPromise<void>(kj::mv(exception));
+          }
+        };
+        return getInnerPromise().then(
+            js, ioContext.addFunctor(kj::mv(onSuccess)), ioContext.addFunctor(kj::mv(onFailure)));
       } else {
-        return js
-            .tryCatch([&] { return algorithm(js, kj::fwd<decltype(args)>(args)...); },
-                [&](jsg::Value&& exception) {
-          return js.rejectedPromise<void>(kj::mv(exception));
-        }).then(js, kj::mv(onSuccess), kj::mv(onFailure));
+        auto getInnerPromise = [&]() -> jsg::Promise<void> {
+          JSG_TRY(js) {
+            return algorithm(js, kj::fwd<decltype(args)>(args)...);
+          }
+          JSG_CATCH(exception) {
+            return js.rejectedPromise<void>(kj::mv(exception));
+          }
+        };
+        return getInnerPromise().then(js, kj::mv(onSuccess), kj::mv(onFailure));
       }
-    }, [&](jsg::Value&& exception) { return js.rejectedPromise<void>(kj::mv(exception)); });
+    }
+    JSG_CATCH(exception) {
+      return js.rejectedPromise<void>(kj::mv(exception));
+    }
   }

   // If the algorithm does not exist, we just handle it as a success and move on.
@@ -1628,10 +1640,13 @@ jsg::Promise<void> WritableImpl<Self>::write(
   size_t size = 1;
   KJ_IF_SOME(sizeFunc, algorithms.size) {
     kj::Maybe<jsg::Value> failure;
-    js.tryCatch([&] { size = sizeFunc(js, value); }, [&](jsg::Value exception) {
+    JSG_TRY(js) {
+      size = sizeFunc(js, value);
+    }
+    JSG_CATCH(exception) {
       startErroring(js, self.addRef(), exception.getHandle(js));
       failure = kj::mv(exception);
-    });
+    }
     KJ_IF_SOME(exception, failure) {
       return js.rejectedPromise<void>(kj::mv(exception));
     }
diff --git a/src/workerd/api/urlpattern-standard.c++ b/src/workerd/api/urlpattern-standard.c++
index 2f4f7200567..011b67c13f9 100644
--- a/src/workerd/api/urlpattern-standard.c++
+++ b/src/workerd/api/urlpattern-standard.c++
@@ -19,9 +19,12 @@ std::optional<URLPattern::URLPatternRegexEngine::regex_type> URLPattern::URLPatt
   // std::string_view is not guaranteed to be null-terminated, but kj::StringPtr requires it.
   // We need to create a null-terminated copy.
   auto str = kj::str(kj::arrayPtr(pattern.data(), pattern.size()));
-  return js.tryCatch([&]() -> std::optional<regex_type> {
+  JSG_TRY(js) {
     return jsg::JsRef(js, js.regexp(str, flags));
-  }, [&](auto reason) -> std::optional<regex_type> { return std::nullopt; });
+  }
+  JSG_CATCH(_) {
+    return std::nullopt;
+  }
 }

 bool URLPattern::URLPatternRegexEngine::regex_match(
diff --git a/src/workerd/api/urlpattern.c++ b/src/workerd/api/urlpattern.c++
index 0cbe5a141f2..2ac1f2dfe77 100644
--- a/src/workerd/api/urlpattern.c++
+++ b/src/workerd/api/urlpattern.c++
@@ -13,16 +13,17 @@ namespace workerd::api {
 namespace {
 jsg::JsRef<jsg::JsRegExp> compileRegex(
     jsg::Lock& js, const jsg::UrlPattern::Component& component, bool ignoreCase) {
-  return js.tryCatch([&] {
+  JSG_TRY(js) {
     jsg::Lock::RegExpFlags flags = jsg::Lock::RegExpFlags::kUNICODE;
     if (ignoreCase) {
       flags = static_cast<jsg::Lock::RegExpFlags>(
           flags | static_cast<int>(jsg::Lock::RegExpFlags::kIGNORE_CASE));
     }
     return jsg::JsRef<jsg::JsRegExp>(js, js.regexp(component.getRegex(), flags));
-  }, [&](auto reason) -> jsg::JsRef<jsg::JsRegExp> {
+  }
+  JSG_CATCH(_) {
     JSG_FAIL_REQUIRE(TypeError, "Invalid regular expression syntax.");
-  });
+  }
 }

 jsg::Ref<URLPattern> create(jsg::Lock& js, jsg::UrlPattern pattern) {
diff --git a/src/workerd/jsg/README.md b/src/workerd/jsg/README.md
index dbf11bd3892..5a07fac8662 100644
--- a/src/workerd/jsg/README.md
+++ b/src/workerd/jsg/README.md
@@ -37,7 +37,8 @@ built around them.

 In order to execute JavaScript on the current thread, a lock must be acquired on the `v8::Isolate`.
 The `jsg::Lock&` represents the current lock. It is passed as an argument to many methods that
-require access to the JavaScript isolate and context.
+require access to the JavaScript isolate and context. By convention, this argument is always named
+`js`.

 The `jsg::Lock` interface itself provides access to basic JavaScript functionality, such as the
 ability to construct basic JavaScript values and call JavaScript functions.
@@ -2534,14 +2535,11 @@ The `jsErrorType` parameter can be one of:
 Unlike `KJ_REQUIRE`, `JSG_REQUIRE` passes all message arguments through `kj::str()`, so you are
 responsible for formatting the entire message string.

-#### `JsExceptionThrown`
+#### `js.error()`, `js.throwException()`, and `JsExceptionThrown`

-When C++ code needs to throw a JavaScript exception, it should:
-1. Call `isolate->ThrowException()` to set the JavaScript error value
-2. Throw `JsExceptionThrown()` as a C++ exception
-
-This C++ exception is caught by JSG's callback glue before returning to V8. This approach is
-more ergonomic than V8's convention of returning `v8::Maybe` values.
+When C++ code needs to throw a JavaScript exception:
+1. Create the error object with `js.error("Error reason")`
+2. Throw using `js.throwException()`

 ```cpp
 void someMethod(jsg::Lock& js) {
@@ -2554,6 +2552,36 @@ void someMethod(jsg::Lock& js) {
 }
 ```

+Under the hood, `js.throwException()` uses V8's lower level API, `isolate->ThrowException()`, to
+throw the exception in the V8 engine. It then throws a special C++ object of type
+`JsExceptionThrown`, whose purpose is to unwind the C++ stack back to the point where JavaScript
+called into C++. This C++ exception is caught by JSG's callback glue before returning to V8. This
+approach is more ergonomic than V8's convention of returning `v8::Maybe` values.
+
+#### `JSG_TRY` and `JSG_CATCH`
+
+JSG provides `JSG_TRY` and `JSG_CATCH` macros which replace the normal `try` and `catch` keywords
+when you need to catch exceptions as JavaScript exceptions. Each take one argument: `JSG_TRY` takes
+the `jsg::Lock&` reference, and `JSG_CATCH` takes your desired variable name for the caught
+exception.
+
+```cpp
+void someMethod(jsg::Lock& js) {
+  JSG_TRY(js) {
+    someThrowyCode();
+  }
+  JSG_CATCH(e) {
+    // Just rethrow.
+    js.throwException(kj::mv(e));
+  }
+}
+```
+
+The example above actually illustrates a common, useful scenario of coercing any exception thrown
+into a JavaScript Error object. That is, if `someThrowyCode()` in the example above throws a KJ C++
+exception, `JSG_CATCH(e)` will catch it and convert it to a JavaScript error by calling
+`js.exceptionToJs()`.
+
 #### `makeInternalError()` and `throwInternalError()`

 These functions create JavaScript errors from internal C++ exceptions while obfuscating
diff --git a/src/workerd/jsg/function-test.c++ b/src/workerd/jsg/function-test.c++
index 4761eeb9c0d..59f3485358b 100644
--- a/src/workerd/jsg/function-test.c++
+++ b/src/workerd/jsg/function-test.c++
@@ -191,10 +191,76 @@ struct FunctionContext: public ContextGlobalObject {
     });
   }

+  kj::String testTryCatch2(Lock& js, jsg::Function<int()> thrower) {
+    // Here we prove that the macro is if-else friendly.
+    if (true) JSG_TRY(js) {
+        return kj::str(thrower(js));
+      }
+    JSG_CATCH(exception) {
+      auto handle = exception.getHandle(js);
+      return kj::str("caught: ", handle);
+    }
+    else {
+      KJ_UNREACHABLE;
+    }
+  }
+
+  kj::String testTryCatchWithOptions(Lock& js, jsg::Function<void()> thrower) {
+    // Test that JSG_CATCH can accept ExceptionToJsOptions.
+    JSG_TRY(js) {
+      thrower(js);
+      return kj::str("no exception");
+    }
+    JSG_CATCH(exception, {.ignoreDetail = true}) {
+      auto handle = exception.getHandle(js);
+      return kj::str("caught with options: ", handle);
+    }
+  }
+
+  kj::String testNestedTryCatchInnerCatches(Lock& js, jsg::Function<void()> thrower) {
+    // Test nested JSG_TRY/JSG_CATCH where inner catches, outer doesn't see exception.
+    JSG_TRY(js) {
+      kj::String innerResult;
+      JSG_TRY(js) {
+        thrower(js);
+        innerResult = kj::str("inner: no exception");
+      }
+      JSG_CATCH(innerException) {
+        innerResult = kj::str("inner caught: ", innerException.getHandle(js));
+      }
+      return kj::str("outer: no exception, ", innerResult);
+    }
+    JSG_CATCH(outerException) {
+      return kj::str("outer caught: ", outerException.getHandle(js));
+    }
+  }
+
+  kj::String testNestedTryCatchOuterCatches(Lock& js, jsg::Function<void()> thrower) {
+    // Test nested JSG_TRY/JSG_CATCH where inner rethrows, outer catches.
+    JSG_TRY(js) {
+      JSG_TRY(js) {
+        thrower(js);
+        return kj::str("inner: no exception");
+      }
+      JSG_CATCH(innerException) {
+        // Rethrow so outer can catch
+        js.throwException(kj::mv(innerException));
+      }
+      return kj::str("outer: no exception");
+    }
+    JSG_CATCH(outerException) {
+      return kj::str("outer caught: ", outerException.getHandle(js));
+    }
+  }
+
   JSG_RESOURCE_TYPE(FunctionContext) {
     JSG_METHOD(test);
     JSG_METHOD(test2);
     JSG_METHOD(testTryCatch);
+    JSG_METHOD(testTryCatch2);
+    JSG_METHOD(testTryCatchWithOptions);
+    JSG_METHOD(testNestedTryCatchInnerCatches);
+    JSG_METHOD(testNestedTryCatchOuterCatches);

     JSG_READONLY_PROTOTYPE_PROPERTY(square, getSquare);
     JSG_READONLY_PROTOTYPE_PROPERTY(gcLambda, getGcLambda);
@@ -220,6 +286,57 @@ KJ_TEST("jsg::Function<T>") {

   e.expectEval("testTryCatch(() => { return 123; })", "string", "123");
   e.expectEval("testTryCatch(() => { throw new Error('foo'); })", "string", "caught: Error: foo");
+
+  e.expectEval("testTryCatch2(() => { return 123; })", "string", "123");
+  e.expectEval("testTryCatch2(() => { throw new Error('foo'); })", "string", "caught: Error: foo");
+
+  e.expectEval("testTryCatchWithOptions(() => {})", "string", "no exception");
+  e.expectEval("testTryCatchWithOptions(() => { throw new Error('bar'); })", "string",
+      "caught with options: Error: bar");
+
+  // Nested JSG_TRY/JSG_CATCH tests
+  e.expectEval("testNestedTryCatchInnerCatches(() => {})", "string",
+      "outer: no exception, inner: no exception");
+  e.expectEval("testNestedTryCatchInnerCatches(() => { throw new Error('inner'); })", "string",
+      "outer: no exception, inner caught: Error: inner");
+
+  e.expectEval("testNestedTryCatchOuterCatches(() => {})", "string", "inner: no exception");
+  e.expectEval("testNestedTryCatchOuterCatches(() => { throw new Error('rethrown'); })", "string",
+      "outer caught: Error: rethrown");
+}
+
+KJ_TEST("JSG_TRY/JSG_CATCH with TerminateExecution") {
+  Evaluator<FunctionContext, FunctionIsolate> e(v8System);
+
+  // TerminateExecution should propagate through JSG_CATCH without being caught.
+  // The Evaluator's run() method will detect the termination and throw.
+  KJ_EXPECT_THROW_MESSAGE("TerminateExecution() was called", e.run([](auto& js) {
+    // Test single-level JSG_TRY/JSG_CATCH with TerminateExecution
+    JSG_TRY(js) {
+      js.terminateExecutionNow();
+    }
+    JSG_CATCH(exception) {
+      (void)exception;
+      KJ_FAIL_ASSERT("TerminateExecution was caught by JSG_CATCH");
+    }
+  }));
+
+  KJ_EXPECT_THROW_MESSAGE("TerminateExecution() was called", e.run([](auto& js) {
+    // Test nested JSG_TRY/JSG_CATCH with TerminateExecution - should propagate through both
+    JSG_TRY(js) {
+      JSG_TRY(js) {
+        js.terminateExecutionNow();
+      }
+      JSG_CATCH(innerException) {
+        (void)innerException;
+        KJ_FAIL_ASSERT("TerminateExecution was caught by inner JSG_CATCH");
+      }
+    }
+    JSG_CATCH(outerException) {
+      (void)outerException;
+      KJ_FAIL_ASSERT("TerminateExecution was caught by outer JSG_CATCH");
+    }
+  }));
 }

 }  // namespace
diff --git a/src/workerd/jsg/jsg.c++ b/src/workerd/jsg/jsg.c++
index e2af4923d8b..3caa71e2557 100644
--- a/src/workerd/jsg/jsg.c++
+++ b/src/workerd/jsg/jsg.c++
@@ -583,4 +583,32 @@ MemoryProtectionKeyScope::PkeyScope::~PkeyScope() {
 }
 #endif

+namespace _ {
+
+JsgCatchScope::JsgCatchScope(Lock& js): js(js) {
+  tryCatchHolder.emplace(js.v8Isolate);
+}
+
+void JsgCatchScope::catchException(ExceptionToJsOptions options) {
+  // Be sure to release our TryCatch on the way out.
+  KJ_DEFER(tryCatchHolder = kj::none);
+
+  auto& tryCatch = KJ_ASSERT_NONNULL(tryCatchHolder).tryCatch;
+
+  // Same logic as that found in `jsg::Lock::tryCatch()`.
+  try {
+    throw;
+  } catch (JsExceptionThrown&) {
+    if (!tryCatch.CanContinue() || !tryCatch.HasCaught() || tryCatch.Exception().IsEmpty()) {
+      tryCatch.ReThrow();
+      throw;
+    }
+    caughtException.emplace(js.v8Isolate, tryCatch.Exception());
+  } catch (kj::Exception& e) {
+    caughtException.emplace(js.exceptionToJs(kj::mv(e), options));
+  }
+}
+
+}  // namespace _
+
 }  // namespace workerd::jsg
diff --git a/src/workerd/jsg/jsg.h b/src/workerd/jsg/jsg.h
index f4a0d15e314..2dfa660a24d 100644
--- a/src/workerd/jsg/jsg.h
+++ b/src/workerd/jsg/jsg.h
@@ -2996,6 +2996,101 @@ inline Value SelfRef::asValue(Lock& js) const {
   return Value(js.v8Isolate, getHandle(js).As<v8::Value>());
 }

+namespace _ {
+
+// Helper class for JSG_TRY / JSG_CATCH macros.
+//
+// Sets up a v8::TryCatch on construction and converts caught exceptions to jsg::Value.
+// Handles both JsExceptionThrown (returns V8 exception directly) and kj::Exception
+// (converts via Lock::exceptionToJs()).
+//
+// This class is an implementation detail of the JSG_TRY / JSG_CATCH macros and should
+// not be used directly.
+class JsgCatchScope {
+ public:
+  explicit JsgCatchScope(Lock& js);
+
+  // Converts the in-flight exception to a jsg::Value and stores it.
+  // Called by JSG_CATCH macro.
+  void catchException(ExceptionToJsOptions options = {});
+
+  // Returns the caught exception. Must be called after catchException().
+  Value& getCaughtException() {
+    return KJ_ASSERT_NONNULL(caughtException);
+  }
+
+ private:
+  Lock& js;
+
+  // Simple wrapper to work around v8::TryCatch's deleted operator new.
+  struct Holder {
+    v8::TryCatch tryCatch;
+    explicit Holder(v8::Isolate* isolate): tryCatch(isolate) {}
+  };
+
+  // We use two separate Maybe members rather than kj::OneOf<Holder, Value> because v8::TryCatch
+  // has deleted copy/move constructors, making it incompatible with OneOf's internal storage.
+  // The tryCatchHolder is active during the try block and released by catchException(), which
+  // then populates caughtException.
+
+  // Active during the try block, consumed by catchException().
+  kj::Maybe<Holder> tryCatchHolder;
+
+  // Populated by catchException(), returned by getCaughtException().
+  kj::Maybe<Value> caughtException;
+};
+
+}  // namespace _
+
+// JSG_TRY / JSG_CATCH macros for exception handling in JSG code.
+//
+// These macros provide clean exception handling that automatically converts both JavaScript
+// exceptions (JsExceptionThrown) and KJ exceptions (kj::Exception) to jsg::Value. This is
+// the recommended way to handle exceptions in JSG code.
+//
+// Usage:
+//   JSG_TRY(js) {
+//     someCodeThatMightThrow();
+//   } JSG_CATCH(exception) {
+//     // `exception` is a jsg::Value& containing the caught exception
+//     return js.rejectedPromise<void>(kj::mv(exception));
+//   }
+//
+// With ExceptionToJsOptions:
+//   JSG_TRY(js) {
+//     someCodeThatMightThrow();
+//   } JSG_CATCH(exception, {.ignoreDetail = true}) {
+//     // Handle exception with custom conversion options
+//   }
+//
+// JSG_TRY(js): Sets up exception handling with the given jsg::Lock. The `js` parameter makes
+// the isolate explicit and enables future coroutine support.
+//
+// JSG_CATCH(name, ...): Catches any exception and converts it to a jsg::Value. The `name`
+// parameter is a user-chosen identifier that will be a `jsg::Value&` in the handler block.
+// Optional ExceptionToJsOptions can be passed as a second argument.
+//
+// IMPORTANT: The code block following JSG_CATCH is NOT a true catch handler:
+// - You CANNOT rethrow with `throw` (there is no current exception)
+//
+// To rethrow the exception, use: js.throwException(kj::mv(exception));
+
+// Since we have two macros -- JSG_TRY and JSG_CATCH -- which must both access the same state,
+// we use a hard-coded variable name. This causes benign shadowing in nested JSG_TRY/JSG_CATCHes,
+// so we disable shadowing warnings. The `_jsg` prefix makes name collision unlikely.
+#define JSG_TRY(js)                                                                                \
+  KJ_SILENCE_SHADOWING_BEGIN                                                                       \
+  if (::workerd::jsg::_::JsgCatchScope _jsgTryCatch(js); true) try KJ_SILENCE_SHADOWING_END
+
+#define JSG_CATCH(exception, ...)                                                                  \
+  catch (...) {                                                                                    \
+    _jsgTryCatch.catchException(__VA_ARGS__);                                                      \
+    goto KJ_UNIQUE_NAME(_jsgTryCatchHandler);                                                      \
+  }                                                                                                \
+  else KJ_UNIQUE_NAME(_jsgTryCatchHandler)                                                         \
+      : if (auto& exception = _jsgTryCatch.getCaughtException(); false) {}                         \
+  else
+
 }  // namespace workerd::jsg

 // clang-format off
diff --git a/src/workerd/jsg/modules-new.c++ b/src/workerd/jsg/modules-new.c++
index ea0022adc26..68823ddccd9 100644
--- a/src/workerd/jsg/modules-new.c++
+++ b/src/workerd/jsg/modules-new.c++
@@ -1699,25 +1699,29 @@ kj::ArrayPtr<const kj::StringPtr> Module::ModuleNamespace::getNamedExports() con
 Module::EvaluateCallback Module::newTextModuleHandler(kj::ArrayPtr<const char> data) {
   return [data](Lock& js, const Url& id, const ModuleNamespace& ns,
              const CompilationObserver&) -> bool {
-    return js.tryCatch([&] { return ns.setDefault(js, js.str(data)); }, [&](Value exception) {
+    JSG_TRY(js) {
+      return ns.setDefault(js, js.str(data));
+    }
+    JSG_CATCH(exception) {
       js.v8Isolate->ThrowException(exception.getHandle(js));
       return false;
-    });
+    }
   };
 }

 Module::EvaluateCallback Module::newDataModuleHandler(kj::ArrayPtr<const kj::byte> data) {
   return [data](Lock& js, const Url& id, const ModuleNamespace& ns,
              const CompilationObserver&) -> bool {
-    return js.tryCatch([&] {
+    JSG_TRY(js) {
       auto backing = jsg::BackingStore::alloc<v8::ArrayBuffer>(js, data.size());
       backing.asArrayPtr().copyFrom(data);
       auto buffer = jsg::BufferSource(js, kj::mv(backing));
       return ns.setDefault(js, JsValue(buffer.getHandle(js)));
-    }, [&](Value exception) {
+    }
+    JSG_CATCH(exception) {
       js.v8Isolate->ThrowException(exception.getHandle(js));
       return false;
-    });
+    }
   };
 }

PATCH

echo "Patch applied successfully."
