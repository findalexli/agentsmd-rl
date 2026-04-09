#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency)
if grep -q "AsOptionalVoid" native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
index 6b3a8e20718d6..568ebd4970b60 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
@@ -68,6 +68,7 @@ internal fun bridgeAsNSCollectionElement(type: SirType): WithSingleType = when
     is AsIs -> AsNSNumber(bridge.swiftType)
     is AsOptionalWrapper -> AsObjCBridgedOptional(bridge.wrappedObject.swiftType)
     is AsOptionalNothing -> AsObjCBridgedOptional(bridge.swiftType)
+    is AsOptionalVoid -> AsObjCBridgedOptional(bridge.swiftType)
     is AsObject,
     is AsExistential,
     is AsAnyBridgeable,
@@ -102,6 +103,7 @@ private fun bridgeNominalType(type: SirNominalType, position: SirTypeVariance):
                 -> AsOptionalWrapper(bridge)

             is AsNothing -> AsOptionalNothing
+            is AsVoid -> AsOptionalVoid

             is AsIs,
                 -> AsOptionalWrapper(
@@ -309,6 +311,28 @@ internal sealed class Bridge(
         }
     }

+    object AsOptionalVoid : WithSingleType(
+        SirNominalType(SirSwiftModule.optional, listOf(SirNominalType(SirSwiftModule.void))),
+        KotlinType.Boolean,
+        CType.Bool
+    ) {
+        override val inKotlinSources = object : ValueConversion {
+            override fun swiftToKotlin(typeNamer: SirTypeNamer, valueExpression: String): String =
+                "(if ($valueExpression) Unit else null)"
+
+            override fun kotlinToSwift(typeNamer: SirTypeNamer, valueExpression: String): String =
+                "($valueExpression != null)"
+        }
+
+        override val inSwiftSources = object : ValueConversion {
+            override fun swiftToKotlin(typeNamer: SirTypeNamer, valueExpression: String): String =
+                "($valueExpression != nil)"
+
+            override fun kotlinToSwift(typeNamer: SirTypeNamer, valueExpression: String): String =
+                "($valueExpression ? () : nil)"
+        }
+    }
+
     /**
      * A bridge that converts a Swift class-based type to the corresponding Kotlin class-based type using native pointers.
      *
@@ -728,13 +752,13 @@ internal sealed class Bridge(
                         }; } }()"
                     is AsContravariantBlock,
                     is AsIs,
-                    is AsVoid,
                     is AsOpaqueObject,
                     is AsOutError,
                         -> TODO("not yet supported")

                     is AsNothing -> error("AsOptionalNothing must be used for AsNothing")
-                    is AsOptionalWrapper, AsOptionalNothing -> error("there is not optional wrappers for optional")
+                    is AsVoid -> error("AsOptionalVoid must be used for AsVoid")
+                    is AsOptionalWrapper, AsOptionalNothing, AsOptionalVoid -> error("there is not optional wrappers for optional")
                 }
             }
         }
diff --git a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.h b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.h
index f48b43ec24bf1..60feebee1158d 100644
--- a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.h
+++ b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.h
@@ -23,6 +23,8 @@ void * __root___Foo_init_allocate();

 _Bool __root___Foo_init_initialize__TypesOfArguments__Swift_UnsafeMutableRawPointer_Swift_Optional_main_Bar___(void * __kt, void * _Nullable b);

+_Bool __root___consumeNullableUnit__TypesOfArguments__Swift_Optional_Swift_Void___(_Bool a);
+
 _Bool __root___foo__TypesOfArguments__main_Bar__(void * a);

 _Bool __root___foo__TypesOfArguments__Swift_Optional_main_Bar___(void * _Nullable a);
@@ -49,6 +51,8 @@ NSNumber * _Nullable __root___primitive_out();

 _Bool __root___primitive_set__TypesOfArguments__Swift_Optional_Swift_Double___(NSNumber * _Nullable newValue);

+_Bool __root___produceNullableUnit();
+
 NSString * _Nullable __root___str_get();

 _Bool __root___str_set__TypesOfArguments__Swift_Optional_Swift_String___(NSString * _Nullable newValue);
diff --git a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.kt b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.kt
index dbf099147269b..b363baa69c10a 100644
--- a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.kt
+++ b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.kt
@@ -77,6 +77,13 @@ public fun __root___Foo_init_initialize__TypesOfArguments__Swift_UnsafeMutableR
     return run { _result; true }
 }

+@ExportedBridge("__root___consumeNullableUnit__TypesOfArguments__Swift_Optional_Swift_Void___")
+public fun __root___consumeNullableUnit__TypesOfArguments__Swift_Optional_Swift_Void___(a: Boolean): Boolean {
+    val __a = (if (a) Unit else null)
+    val _result = run { consumeNullableUnit(__a) }
+    return run { _result; true }
+}
+
 @ExportedBridge("__root___foo__TypesOfArguments__main_Bar__")
 public fun __root___foo__TypesOfArguments__main_Bar__(a: kotlin.native.internal.NativePtr): Boolean {
     val __a = kotlin.native.internal.ref.dereferenceExternalRCRef(a) as Bar
@@ -174,6 +181,12 @@ public fun __root___primitive_set__TypesOfArguments__Swift_Optional_Swift_Double
     return run { _result; true }
 }

+@ExportedBridge("__root___produceNullableUnit")
+public fun __root___produceNullableUnit(): Boolean {
+    val _result = run { produceNullableUnit() }
+    return (_result != null)
+}
+
 @ExportedBridge("__root___str_get")
 public fun __root___str_get(): kotlin.native.internal.NativePtr {
     val _result = run { str }
diff --git a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.swift b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.swift
index c1a55dbc24c29..aa93392ace714 100644
--- a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.swift
+++ b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/golden_result/main/main.swift
@@ -78,6 +78,11 @@ public var str: Swift.String? {
         return { __root___str_set__TypesOfArguments__Swift_Optional_Swift_String___(newValue ?? nil); return () }()
     }
 }
+public func consumeNullableUnit(
+    a: Swift.Void?
+) -> Swift.Void {
+    return { __root___consumeNullableUnit__TypesOfArguments__Swift_Optional_Swift_Void___((a != nil)); return () }()
+}
 public func foo(
     a: main.Bar
 ) -> Swift.Void {
@@ -136,6 +141,9 @@ public func primitive_in(
 public func primitive_out() -> Swift.Bool? {
     return __root___primitive_out().map { it in it.boolValue }
 }
+public func produceNullableUnit() -> Swift.Void? {
+    return (__root___produceNullableUnit() ? () : nil)
+}
 public func string_in(
     a: Swift.String?
 ) -> Swift.Void {
diff --git a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/nullable_type.kt b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/nullable_type.kt
index 99b691de777aa..a965e645a559f 100644
--- a/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/nullable_type.kt
+++ b/native/swift/swift-export-standalone-integration-tests/simple/testData/generation/nullable_type/nullable_type.kt
@@ -10,6 +10,9 @@ fun foo(a: Bar?): Unit = TODO()
 fun foo_any(a: Any): Unit = TODO()
 fun foo_any(a: Any?): Unit = TODO()

+fun produceNullableUnit(): Unit? = TODO()
+fun consumeNullableUnit(a: Unit?): Unit = TODO()
+
 fun p(): Bar? = null
 fun p_any(): Any? = null

@@ -52,4 +55,3 @@ fun primitive_in(
 ): Unit = TODO()
 fun primitive_out(): Boolean? = null
 var primitive: Double? = null
-
PATCH

echo "Patch applied successfully"
