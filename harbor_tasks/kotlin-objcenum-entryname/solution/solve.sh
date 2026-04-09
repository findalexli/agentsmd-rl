#!/bin/bash
set -e

cd /workspace/kotlin

# Idempotency check - if already applied, skip
if grep -q "annotation class EntryName" libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# First, add trailing newline to Foo.kt to make patching work
echo "" >> /workspace/kotlin/native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/Foo.kt

# Apply the gold patch from the PR
git apply <<'PATCH'
diff --git a/kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt b/kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt
index 3dc5a0cae832d..7daa70852c2ae 100644
--- a/kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt
+++ b/kotlin-native/runtime/src/main/kotlin/kotlin/native/Annotations.kt
@@ -121,15 +121,26 @@ public actual annotation class ObjCName(actual val name: String = "", actual val
  * Instructs the Kotlin compiler to generate a NS_ENUM typedef for the annotated enum class. The name of the generated type will
  * be the name of the enum type with "NSEnum" appended. This name can be overridden with the "name" parameter, which is treated
  * as an exact name. Additionally, a separate name for Swift can be specified using the swiftName parameter.
- * The enum literals will be prefixed with the type name, as they live in a global namespace.
- * Swift naming will remove these disambiguation prefixes. The NSEnum values are accessible via the "nsEnum" property.
+ * For Objective-C, the enum literals will always be prefixed with the type name, always capitalizing the first character of the entry
+ * name, regardless whether they are implied or set explicitly via ObjCName or EntryName, as they live in a global namespace.
+ * For Swift, no such disambiguation prefixes will be added. The NSEnum values are accessible via the "nsEnum" property.
  */
 @Target(AnnotationTarget.CLASS)
 @Retention(AnnotationRetention.BINARY)
 @MustBeDocumented
 @ExperimentalObjCEnum
 @SinceKotlin("2.3")
-public actual annotation class ObjCEnum(actual val name: String = "", actual val swiftName: String = "")
+public actual annotation class ObjCEnum(actual val name: String = "", actual val swiftName: String = "") {
+    /**
+     * This annotation affects the names of the generated NS_ENUM enumerators. It overrides the implied enum entry name and an enum entry
+     * name set via @ObjCName. A separate name for Swift can be specified via the swiftName parameter. An EntryName annotation will
+     * always override the Swift name implied or set by other means, even if swiftName is not set explicitly. This annotation does
+     * not override the prefix implied or set by ObjCEnum.
+     */
+    @Target(AnnotationTarget.CLASS)
+    @Retention(AnnotationRetention.BINARY)
+    public actual annotation class EntryName(actual val name: String, actual val swiftName: String = "")
+}

 /**
  * Meta-annotation that instructs the Kotlin compiler to remove the annotated class, function or property from the public Objective-C API.
diff --git a/libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt b/libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt
index 471b57731705d..4497db5c4663b 100644
--- a/libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt
+++ b/libraries/stdlib/src/kotlin/annotations/NativeAnnotations.kt
@@ -76,8 +76,9 @@ public expect annotation class ObjCName(val name: String = "", val swiftName: St
  * Instructs the Kotlin compiler to generate a NS_ENUM typedef for the annotated enum class. The name of the generated type will
  * be the name of the enum type with "NSEnum" appended. This name can be overridden with the "name" parameter, which is treated
  * as an exact name. Additionally, a separate name for Swift can be specified using the swiftName parameter.
- * The enum literals will be prefixed with the type name, as they live in a global namespace.
- * Swift naming will remove these disambiguation prefixes. The NSEnum values are accessible via the "nsEnum" property.
+ * For Objective-C, the enum literals will always be prefixed with the type name, always capitalizing the first character of the entry
+ * name, regardless whether they are implied or set explicitly via ObjCName or EntryName, as they live in a global namespace.
+ * For Swift, no such disambiguation prefixes will be added. The NSEnum values are accessible via the "nsEnum" property.
  */
 @Target(AnnotationTarget.CLASS)
 @Retention(AnnotationRetention.BINARY)
@@ -85,7 +86,17 @@ public expect annotation class ObjCName(val name: String = "", val swiftName: St
 @OptionalExpectation
 @ExperimentalObjCEnum
 @SinceKotlin("2.3")
-public expect annotation class ObjCEnum(val name: String = "", val swiftName: String = "")
+public expect annotation class ObjCEnum(val name: String = "", val swiftName: String = "") {
+    /**
+     * This annotation affects the names of the generated NS_ENUM enumerators. It overrides the implied enum entry name and an enum entry
+     * name set via @ObjCName. A separate name for Swift can be specified via the swiftName parameter. An EntryName annotation will
+     * always override the Swift name implied or set by other means, even if swiftName is not set explicitly. This annotation does
+     * not override the prefix implied or set by ObjCEnum.
+     */
+    @Target(AnnotationTarget.CLASS)
+    @Retention(AnnotationRetention.BINARY)
+    public annotation class EntryName(val name: String, val swiftName: String = "")
+}

 /**
  * Meta-annotation that instructs the Kotlin compiler to remove the annotated class, function or property from the public Objective-C API.
diff --git a/libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api b/libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api
index c3302df5edb40..2f7ebf479f411 100644
--- a/libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api
+++ b/libraries/tools/binary-compatibility-validator/klib-public-api/kotlin-stdlib.api
@@ -9884,6 +9884,15 @@ open annotation class kotlin.native/ObjCEnum : kotlin/Annotation { // kotlin.nat
         final fun <get-name>(): kotlin/String // kotlin.native/ObjCEnum.name.<get-name>|<get-name>(){}[0]
     final val swiftName // kotlin.native/ObjCEnum.swiftName|{}swiftName[0]
         final fun <get-swiftName>(): kotlin/String // kotlin.native/ObjCEnum.swiftName.<get-swiftName>|<get-swiftName>(){}[0]
+
+    open annotation class EntryName : kotlin/Annotation { // kotlin.native/ObjCEnum.EntryName|null[0]
+        constructor <init>(kotlin/String, kotlin/String = ...) // kotlin.native/ObjCEnum.EntryName.<init>|<init>(kotlin.String;kotlin.String){}[0]
+
+        final val name // kotlin.native/ObjCEnum.EntryName.name|{}name[0]
+            final fun <get-name>(): kotlin/String // kotlin.native/ObjCEnum.EntryName.name.<get-name>|<get-name>(){}[0]
+        final val swiftName // kotlin.native/ObjCEnum.EntryName.swiftName|{}swiftName[0]
+            final fun <get-swiftName>(): kotlin/String // kotlin.native/ObjCEnum.EntryName.swiftName.<get-swiftName>|<get-swiftName>(){}[0]
+    }
 }

 // Targets: [native]
@@ -13813,6 +13822,15 @@ open annotation class kotlin.native/ObjCEnum : kotlin/Annotation { // kotlin.nat
         final fun <get-name>(): kotlin/String // kotlin.native/ObjCEnum.name.<get-name>|<get-name>(){}[1]
     final val swiftName // kotlin.native/ObjCEnum.swiftName|{}swiftName[1]
         final fun <get-swiftName>(): kotlin/String // kotlin.native/ObjCEnum.swiftName.<get-swiftName>|<get-swiftName>(){}[1]
+
+    open annotation class EntryName : kotlin/Annotation { // kotlin.native/ObjCEnum.EntryName|null[1]
+        constructor <init>(kotlin/String, kotlin/String = ...) // kotlin.native/ObjCEnum.EntryName.<init>|<init>(kotlin.String;kotlin.String){}[1]
+
+        final val name // kotlin.native/ObjCEnum.EntryName.name|{}name[1]
+            final fun <get-name>(): kotlin/String // kotlin.native/ObjCEnum.EntryName.name.<get-name>|<get-name>(){}[1]
+        final val swiftName // kotlin.native/ObjCEnum.EntryName.swiftName|{}swiftName[1]
+            final fun <get-swiftName>(): kotlin/String // kotlin.native/ObjCEnum.EntryName.swiftName.<get-swiftName>|<get-swiftName>(){}[1]
+    }
 }

 // Targets: [js, wasmJs, wasmWasi]
diff --git a/native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt b/native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt
index b311c5319d8fb..5de1a2f62c212 100644
--- a/native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt
+++ b/native/base/src/main/kotlin/org/jetbrains/kotlin/backend/konan/KonanFqNames.kt
@@ -39,6 +39,7 @@ object KonanFqNames {
     val noReorderFields = FqName("kotlin.native.internal.NoReorderFields")
     val objCName = FqName("kotlin.native.ObjCName")
     val objCEnum = FqName("kotlin.native.ObjCEnum")
+    val objCEnumEntryName = FqName("kotlin.native.ObjCEnum.EntryName")
     val hidesFromObjC = FqName("kotlin.native.HidesFromObjC")
     val refinesInSwift = FqName("kotlin.native.RefinesInSwift")
     val shouldRefineInSwift = FqName("kotlin.native.ShouldRefineInSwift")
diff --git a/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt b/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt
index 3eb7adfbc4c85..17d504de29fd8 100644
--- a/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt
+++ b/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/resolveObjCNameAnnotation.kt
@@ -43,6 +43,14 @@ class ObjCExportObjCNameAnnotation(
     val isExact: Boolean,
 )

+/**
+ * Represents the values resolved from the [kotlin.native.ObjCEnum.EntryName] annotation.
+ */
+class ObjCExportObjCEnumEntryNameAnnotation(
+    val objCName: String?,
+    val swiftName: String?,
+)
+
 internal fun KaAnnotatedSymbol.resolveObjCNameAnnotation(): ObjCExportObjCNameAnnotation? {
     val annotation = annotations.find { it.classId?.asSingleFqName() == KonanFqNames.objCName } ?: return null

@@ -53,6 +61,16 @@ internal fun KaAnnotatedSymbol.resolveObjCNameAnnotation(): ObjCExportObjCNameAnn
     )
 }

+internal fun KaAnnotatedSymbol.resolveObjCEnumEntryNameAnnotation(): ObjCExportObjCEnumEntryNameAnnotation? {
+    val annotation = annotations.find { it.classId?.asSingleFqName() == KonanFqNames.objCEnumEntryName } ?: return null
+
+    return ObjCExportObjCEnumEntryNameAnnotation(
+        objCName = annotation.findArgument("name")?.resolveStringConstantValue(),
+        swiftName = annotation.findArgument("swiftName")?.resolveStringConstantValue(),
+    )
+}
+
+
 internal fun KaAnnotation.findArgument(name: String): KaNamedAnnotationValue? {
     return arguments.find { it.name.identifier == name }
 }
diff --git a/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt b/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt
index a6e07dddd83af..18004d9102466 100644
--- a/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt
+++ b/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateEnumMembers.kt
@@ -75,6 +75,12 @@ private fun ObjCExportContext.getEnumEntriesProperty(symbol: KaClassSymbol): Obj
     )
 }

+internal fun ObjCExportContext.getNSEnumEntryName(symbol: KaEnumEntrySymbol, forSwift: Boolean): String {
+    val objCEnumEntryNameAnnotation = symbol.resolveObjCEnumEntryNameAnnotation()
+    val name = (if (forSwift) objCEnumEntryNameAnnotation?.swiftName?.ifEmpty { null } else null) ?: objCEnumEntryNameAnnotation?.objCName
+    return name?.ifEmpty { null } ?: getEnumEntryName(symbol, forSwift)
+}
+
 /**
  * See K1 implementation as [org.jetbrains.kotlin.backend.konan.objcexport.ObjCExportNamerImpl.getEnumEntryName]
  */
diff --git a/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateToNSEnum.kt b/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateToNSEnum.kt
index b123371a30137..3f560cff88dda 100644
--- a/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateToNSEnum.kt
+++ b/native/objcexport-header-generator/impl/analysis-api/src/org/jetbrains/kotlin/objcexport/translateToNSEnum.kt
@@ -37,8 +37,8 @@ private fun ObjCExportContext.getNSEnumEntries(symbol: KaClassSymbol, objCTypeNa
     // Map the enum entries in declaration order, preserving the ordinal
     return staticMembers.filterIsInstance<KaEnumEntrySymbol>().mapIndexed { ordinal, entry ->
         ObjCNSEnum.Entry(
-            getEnumEntryName(entry, true),
-            objCTypeName + getEnumEntryName(entry, false).replaceFirstChar { it.uppercaseChar() },
+            getNSEnumEntryName(entry, true),
+            objCTypeName + getNSEnumEntryName(entry, false).replaceFirstChar { it.uppercaseChar() },
             ordinal
         )
     }
diff --git a/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt b/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt
index 362263f45b388..5305f7400020f 100644
--- a/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt
+++ b/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportNamer.kt
@@ -1086,6 +1086,22 @@ private class ObjCName(
         swiftName.takeIf { forSwift } ?: objCName ?: default(kotlinName)
 }

+class ObjCEnumEntryName(
+    private val objCName: String?,
+    private val swiftName: String?,
+) {
+    /// Implements empty/null normalization and the swift/objc fallback
+    fun getName(forSwift: Boolean) = (if (forSwift) swiftName?.ifEmpty { null } else null) ?: objCName?.ifEmpty { null }
+}
+
+fun DeclarationDescriptor.getObjCEnumEntryName(): ObjCEnumEntryName {
+    val annotation = annotations.findAnnotation(KonanFqNames.objCEnumEntryName)
+    return ObjCEnumEntryName(
+        objCName = annotation?.argumentValue("name")?.value as String?,
+        swiftName = annotation?.argumentValue("swiftName")?.value as String?
+    )
+}
+
 private fun DeclarationDescriptor.getObjCName(): ObjCName {
     var objCName: String? = null
     var swiftName: String? = null
diff --git a/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportTranslator.kt b/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportTranslator.kt
index e1a7039ed2fa1..6cc390fb32aff 100644
--- a/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportTranslator.kt
+++ b/native/objcexport-header-generator/impl/k1/src/org/jetbrains/kotlin/backend/konan/objcexport/ObjCExportTranslator.kt
@@ -298,10 +298,12 @@ class ObjCExportTranslatorImpl(
                                 swiftName = nsEnumTypeName.swiftName,
                                 origin = ObjCExportStubOrigin(descriptor),
                                 entries = descriptor.enumEntries.mapIndexed { ordinal, entry ->
+                                    val objcEnumEntryName = entry.getObjCEnumEntryName()
+                                    val objCName = objcEnumEntryName.getName(forSwift = false) ?: namer.getEnumEntrySelector(entry)
+                                    val swiftName = objcEnumEntryName.getName(forSwift = true) ?: namer.getEnumEntrySwiftName(entry)
                                     ObjCNSEnum.Entry(
-                                        objCName = nsEnumTypeName.objCName + namer.getEnumEntrySelector(entry)
-                                            .replaceFirstChar { it.uppercaseChar() },
-                                        swiftName = namer.getEnumEntrySwiftName(entry),
+                                        objCName = nsEnumTypeName.objCName + objCName.replaceFirstChar { it.uppercaseChar() },
+                                        swiftName = swiftName,
                                         value = ordinal
                                     )
                                 }
diff --git a/native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h b/native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h
index 4efd738e9c81b..4ef2c7963113c 100644
--- a/native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h
+++ b/native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/!enumClassWithObjCEnumAndRenamedLiterals.h
@@ -42,8 +42,13 @@ typedef NS_ENUM(int32_t, FooNSEnum) {
   FooNSEnumAlphaBeta NS_SWIFT_NAME(alphaBeta) = 0,
   FooNSEnumAlpha NS_SWIFT_NAME(alpha) = 1,
   FooNSEnumTheCopy NS_SWIFT_NAME(theCopy) = 2,
-  FooNSEnumFooBarObjC NS_SWIFT_NAME(fooBarObjC) = 3,
-  FooNSEnumBarFooObjC NS_SWIFT_NAME(barFooSwift) = 4,
+  FooNSEnumObjCName1Renamed NS_SWIFT_NAME(objCName1Renamed) = 3,
+  FooNSEnumObjcName2Renamed NS_SWIFT_NAME(objcName2Swift) = 4,
+  FooNSEnumEntryName1Renamed NS_SWIFT_NAME(entryName1Renamed) = 5,
+  FooNSEnumEntryName2Renamed NS_SWIFT_NAME(entryName2Swift) = 6,
+  FooNSEnumCombination1Renamed NS_SWIFT_NAME(combination1Renamed) = 7,
+  FooNSEnumCombination2Renamed NS_SWIFT_NAME(combination2Renamed) = 8,
+  FooNSEnumCombination3Renamed NS_SWIFT_NAME(combination3Swift) = 9,
 } NS_SWIFT_NAME(FooNSEnum);


@@ -56,8 +61,13 @@ __attribute__((objc_subclassing_restricted))
 @property (class, readonly) Foo *alphaBeta __attribute__((swift_name("alphaBeta")));
 @property (class, readonly) Foo *alpha __attribute__((swift_name("alpha")));
 @property (class, readonly) Foo *theCopy __attribute__((swift_name("theCopy")));
-@property (class, readonly) Foo *fooBarObjC __attribute__((swift_name("fooBarObjC")));
-@property (class, readonly) Foo *barFooObjC __attribute__((swift_name("barFooSwift")));
+@property (class, readonly) Foo *objCName1Renamed __attribute__((swift_name("objCName1Renamed")));
+@property (class, readonly) Foo *objcName2Renamed __attribute__((swift_name("objcName2Swift")));
+@property (class, readonly) Foo *entryName1Original __attribute__((swift_name("entryName1Original")));
+@property (class, readonly) Foo *entryName2Swift __attribute__((swift_name("entryName2Swift")));
+@property (class, readonly) Foo *combination1Bad __attribute__((swift_name("combination1Bad")));
+@property (class, readonly) Foo *combination2BadObjC __attribute__((swift_name("combination2BadSwift")));
+@property (class, readonly) Foo *combination3BadObjC __attribute__((swift_name("combination3BadSwift")));
 + (KotlinArray<Foo *> *)values __attribute__((swift_name("values()")));
 @property (class, readonly) NSArray<Foo *> *entries __attribute__((swift_name("entries")));
 @end
PATCH

# Handle the test data file separately using direct write
cat > /workspace/kotlin/native/objcexport-header-generator/testData/headers/enumClassWithObjCEnumAndRenamedLiterals/Foo.kt << 'FOOCODE'
import kotlin.native.ObjCEnum
import kotlin.native.ObjCName
import kotlin.experimental.ExperimentalObjCEnum
import kotlin.experimental.ExperimentalObjCName

@file:OptIn(ExperimentalObjCEnum::class)

@ObjCEnum
enum class Foo {
    ALPHA_BETA,
    ALPHA,
    COPY,
    @ObjCName("objCName1Renamed") OBJC_NAME_1_ORIGINAL,
    @ObjCName(name = "objcName2Renamed", swiftName = "objcName2Swift") OBJC_NAME_2_ORIGINAL,
    @ObjCEnum.EntryName(name="entryName1Renamed") ENTRY_NAME_1_ORIGINAL,
    @ObjCEnum.EntryName(name="entryName2Renamed", swiftName="entryName2Swift") ENTRY_NAME_2_SWIFT,
    @ObjCEnum.EntryName(name="combination1Renamed") @ObjCName(name="combination1Bad") COMBINATION_1,
    @ObjCEnum.EntryName(name="combination2Renamed") @ObjCName(name="combination2BadObjC", swiftName="combination2BadSwift") COMBINATION_2,
    @ObjCEnum.EntryName(name="combination3Renamed", swiftName = "combination3Swift") @ObjCName(name="combination3BadObjC", swiftName="combination3BadSwift") COMBINATION_3
}
FOOCODE

echo "Patch applied successfully"
