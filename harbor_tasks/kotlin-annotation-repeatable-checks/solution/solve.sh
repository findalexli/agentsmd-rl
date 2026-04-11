#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch for fixing annotation repeatable checks around ALL use-site target
cat <<'PATCH' | git apply -
diff --git a/compiler/fir/analysis-tests/testData/resolveWithStdlib/annotations/annotationAllRepeatable.fir.txt b/compiler/fir/analysis-tests/testData/resolveWithStdlib/annotations/annotationAllRepeatable.fir.txt
new file mode 100644
index 0000000000000..d3c19e29bdef7
--- /dev/null
+++ b/compiler/fir/analysis-tests/testData/resolveWithStdlib/annotations/annotationAllRepeatable.fir.txt
@@ -0,0 +1,42 @@
+FILE: annotationAllRepeatable.kt
+    public final annotation class A : R|kotlin/Annotation| {
+        public constructor(): R|A| {
+            super<R|kotlin/Any|>()
+        }
+
+    }
+    public final class B : R|kotlin/Any| {
+        public constructor(@CONSTRUCTOR_PARAMETER:R|A|() @ALL:R|A|() x: R|kotlin/Int|, @R|A|() @ALL:R|A|() y: R|kotlin/Int|, @ALL:R|A|() @R|A|() z: R|kotlin/Int|, @ALL:R|A|() w: R|kotlin/Int|, @ALL:R|A|() v: R|kotlin/Int|, @ALL:R|A|() t: R|kotlin/Int|, @ALL:R|A|() u: R|kotlin/Int|, @ALL:R|A|() s: R|kotlin/Int|, @ALL:R|A|() @ALL:R|A|() r: R|kotlin/Int|): R|B| {
+            super<R|kotlin/Any|>()
+        }
+
+        @ALL:R|A|() field:@R|A|() public final val x: R|kotlin/Int| = R|<local>/x|
+            @R|A|() public get(): R|kotlin/Int|
+
+        @R|A|() @ALL:R|A|() field:@R|A|() public final val y: R|kotlin/Int| = R|<local>/y|
+            @R|A|() public get(): R|kotlin/Int|
+
+        @ALL:R|A|() @R|A|() field:@R|A|() public final val z: R|kotlin/Int| = R|<local>/z|
+            @R|A|() public get(): R|kotlin/Int|
+
+        @ALL:R|A|() field:@R|A|() public final val w: R|kotlin/Int| = R|<local>/w|
+            @PROPERTY_GETTER:R|A|() @R|A|() public get(): R|kotlin/Int|
+
+        @ALL:R|A|() field:@R|A|() public final var v: R|kotlin/Int| = R|<local>/v|
+            @R|A|() public get(): R|kotlin/Int|
+            @PROPERTY_SETTER:R|A|() public set(@R|A|() value: R|kotlin/Int|): R|kotlin/Unit|
+
+        @ALL:R|A|() field:@R|A|() public final var t: R|kotlin/Int| = R|<local>/t|
+            @R|A|() public get(): R|kotlin/Int|
+            public set(@SETTER_PARAMETER:R|A|() @R|A|() value: R|kotlin/Int|): R|kotlin/Unit|
+
+        @ALL:R|A|() field:@R|A|() public final val u: R|kotlin/Int| = R|<local>/u|
+            @R|A|() public get(): R|kotlin/Int|
+
+        @PROPERTY:R|A|() @ALL:R|A|() field:@R|A|() public final val s: R|kotlin/Int| = R|<local>/s|
+            @R|A|() public get(): R|kotlin/Int|
+
+        @ALL:R|A|() @ALL:R|A|() field:@R|A|() @R|A|() public final val r: R|kotlin/Int| = R|<local>/r|
+            @R|A|() @R|A|() public get(): R|kotlin/Int|
+
+    }
diff --git a/compiler/fir/analysis-tests/testData/resolveWithStdlib/annotations/annotationAllRepeatable.kt b/compiler/fir/analysis-tests/testData/resolveWithStdlib/annotations/annotationAllRepeatable.kt
new file mode 100644
index 0000000000000..55db02aa1870f
--- /dev/null
+++ b/compiler/fir/analysis-tests/testData/resolveWithStdlib/annotations/annotationAllRepeatable.kt
@@ -0,0 +1,52 @@
+// RUN_PIPELINE_TILL: FRONTEND
+// ISSUE: KT-85005
+// FIR_DUMP
+
+annotation class A
+
+class B(
+    @param:A
+    <!REPEATED_ANNOTATION!>@all:A<!>
+    val x: Int,
+
+    // Two errors: parameter, property
+    @A
+    <!REPEATED_ANNOTATION, REPEATED_ANNOTATION!>@all:A<!>
+    val y: Int,
+
+    // Two errors: parameter, property
+    @all:A
+    <!REPEATED_ANNOTATION, REPEATED_ANNOTATION!>@A<!>
+    val z: Int,
+
+    @get:A
+    <!REPEATED_ANNOTATION!>@all:A<!>
+    val w: Int,
+
+    // No error here as @all: isn't applied to setter
+    @all:A
+    @set:A
+    var v: Int,
+
+    <!REPEATED_ANNOTATION!>@all:A<!>
+    @setparam:A
+    var t: Int,
+
+    @field:A
+    <!REPEATED_ANNOTATION!>@all:A<!>
+    val u: Int,
+
+    @property:A
+    <!REPEATED_ANNOTATION!>@all:A<!>
+    val s: Int,
+
+    // Four errors: parameter, property, getter, field
+    @all:A
+    <!REPEATED_ANNOTATION, REPEATED_ANNOTATION, REPEATED_ANNOTATION, REPEATED_ANNOTATION!>@all:A<!>
+    val r: Int,
+)
+
+/* GENERATED_FIR_TAGS: annotationDeclaration, annotationUseSiteTargetAll, annotationUseSiteTargetField,
+annotationUseSiteTargetParam, annotationUseSiteTargetProperty, annotationUseSiteTargetPropertyGetter,
+annotationUseSiteTargetPropertySetter, annotationUseSiteTargetSetterParameter, classDeclaration, primaryConstructor,
+propertyDeclaration */
diff --git a/compiler/fir/analysis-tests/testData/resolveWithStdlib/properties/backingField/explicitBackingFieldOptIns.kt b/compiler/fir/analysis-tests/testData/resolveWithStdlib/properties/backingField/explicitBackingFieldOptIns.kt
index 223aa34189481..4313447ee0fb0 100644
--- a/compiler/fir/analysis-tests/testData/resolveWithStdlib/properties/backingField/explicitBackingFieldOptIns.kt
+++ b/compiler/fir/analysis-tests/testData/resolveWithStdlib/properties/backingField/explicitBackingFieldOptIns.kt
@@ -9,7 +9,7 @@ val numbersA: List<Int>
     field = mutableListOf()

 val numbersB: List<Int>
-    @ExperimentalAPI
+    <!OPT_IN_MARKER_ON_WRONG_TARGET!>@ExperimentalAPI<!>
     field = mutableListOf()

 fun test() {
@@ -19,7 +19,7 @@ fun test() {

 object MyObject {
     val x: Number
-        @ExperimentalAPI
+        <!OPT_IN_MARKER_ON_WRONG_TARGET!>@ExperimentalAPI<!>
         field = 123.4
 }

diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt
index 21910321f1fd7..f64f6ec93810a 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt
@@ -168,7 +168,10 @@ fun checkRepeatedAnnotation(
     val annotationsMap = hashMapOf<ConeKotlinType, MutableList<AnnotationUseSiteTarget?>>()

     for (annotation in annotations) {
-        val useSiteTarget = annotation.useSiteTarget ?: annotationContainer?.getDefaultUseSiteTarget(annotation)
+        // TODO: KT-85288 consider dropping use-site target checks here
+        val useSiteTarget = annotation.useSiteTarget.takeIf {
+            it != AnnotationUseSiteTarget.ALL
+        } ?: annotationContainer?.getDefaultUseSiteTarget(annotation)
         val expandedType = annotation.annotationTypeRef.coneType.fullyExpandedType()
         val existingTargetsForAnnotation = annotationsMap.getOrPut(expandedType) { arrayListOf() }

diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt
index a686dcfd07e62..131c10164e9dd 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirAnnotationChecker.kt
@@ -132,6 +132,8 @@ object FirAnnotationChecker : FirBasicDeclarationChecker(MppCheckerKind.Common)
         fun FirPropertyAccessor.hasNoReceivers() = contextParameters.isEmpty() && receiverParameter?.typeRef == null &&
                 !propertySymbol.isExtension && !propertySymbol.hasContextParameters

+        // TODO: KT-85291 consider analyzing here the type of declaration instead of use-site target
+        // (as at this stage all annotations should be on a declaration bound to its use-site target)
         val (hint, type) = when (annotation.useSiteTarget) {
             FIELD -> "fields" to ((declaration as? FirBackingField)?.returnTypeRef?.coneType ?: return)
             PROPERTY_DELEGATE_FIELD -> "delegate fields" to ((declaration as? FirBackingField)?.propertySymbol?.delegate?.resolvedType
@@ -153,7 +155,7 @@ object FirAnnotationChecker : FirBasicDeclarationChecker(MppCheckerKind.Common)
                 is FirPropertyAccessor if declaration.isGetter && declaration.hasNoReceivers() -> "getters" to declaration.returnTypeRef.coneType
                 else -> return
             }
-            ALL -> TODO() // How @all: interoperates with ValueClasses feature?
+            ALL -> return // TODO: how @all: interoperates with ValueClasses feature?
         }
         reportIfMfvc(annotation, hint, type)
     }
diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt
index d7f0acb4c860f..7bf68a43040c4 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirOptInMarkedDeclarationChecker.kt
@@ -21,21 +21,19 @@ object FirOptInMarkedDeclarationChecker : FirBasicDeclarationChecker(MppCheckerK
     context(context: CheckerContext, reporter: DiagnosticReporter)
     override fun check(declaration: FirDeclaration) {
         for (annotation in declaration.annotations) {
-            val annotationClass = annotation.getAnnotationClassForOptInMarker(context.session) ?: continue
+            if (annotation.getAnnotationClassForOptInMarker(context.session) == null) continue
+
             val useSiteTarget = annotation.useSiteTarget
-            if ((declaration is FirPropertyAccessor && declaration.isGetter) || useSiteTarget == PROPERTY_GETTER) {
+            if (declaration is FirPropertyAccessor && declaration.isGetter) {
                 reporter.reportOn(annotation.source, FirErrors.OPT_IN_MARKER_ON_WRONG_TARGET, "getter")
             }
-            if (useSiteTarget == SETTER_PARAMETER ||
-                (useSiteTarget != PROPERTY && useSiteTarget != PROPERTY_SETTER && declaration is FirValueParameter &&
-                        KotlinTarget.VALUE_PARAMETER in annotationClass.getAllowedAnnotationTargets(context.session))
-            ) {
+            if (declaration is FirValueParameter) {
                 reporter.reportOn(annotation.source, FirErrors.OPT_IN_MARKER_ON_WRONG_TARGET, "parameter")
             }
             if (declaration is FirProperty && declaration.symbol is FirLocalPropertySymbol) {
                 reporter.reportOn(annotation.source, FirErrors.OPT_IN_MARKER_ON_WRONG_TARGET, "variable")
             }
-            if (useSiteTarget == FIELD || useSiteTarget == PROPERTY_DELEGATE_FIELD) {
+            if (declaration is FirBackingField || useSiteTarget == PROPERTY_DELEGATE_FIELD) {
                 reporter.reportOn(annotation.source, FirErrors.OPT_IN_MARKER_ON_WRONG_TARGET, "field")
             }
         }
diff --git a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt
index 7e35787cd5f0b..bc6d175990448 100644
--- a/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt
+++ b/compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirSupertypesChecker.kt
@@ -133,6 +133,7 @@ object FirSupertypesChecker : FirClassChecker(MppCheckerKind.Platform) {
         superTypeRef: FirTypeRef,
     ) {
         for (annotation in superTypeRef.annotations) {
+            // Without a use-site target it can be a valid type annotation
             if (annotation.useSiteTarget != null) {
                 reporter.reportOn(annotation.source, FirErrors.ANNOTATION_ON_SUPERCLASS_ERROR)
             }
diff --git a/compiler/fir/fir-serialization/src/org/jetbrains/kotlin/fir/serialization/FirElementSerializer.kt b/compiler/fir/fir-serialization/src/org/jetbrains/kotlin/fir/serialization/FirElementSerializer.kt
index f6ff5caee009d..6ce59f7eacdfd 100644
--- a/compiler/fir/fir-serialization/src/org/jetbrains/kotlin/fir/serialization/FirElementSerializer.kt
+++ b/compiler/fir/fir-serialization/src/org/jetbrains/kotlin/fir/serialization/FirElementSerializer.kt
@@ -17,7 +17,6 @@ import org.jetbrains.kotlin.constant.ConstantValue
 import org.jetbrains.kotlin.constant.EnumValue
 import org.jetbrains.kotlin.constant.IntValue
 import org.jetbrains.kotlin.descriptors.*
-import org.jetbrains.kotlin.descriptors.annotations.AnnotationUseSiteTarget
 import org.jetbrains.kotlin.fir.*
 import org.jetbrains.kotlin.fir.declarations.*
 import org.jetbrains.kotlin.fir.declarations.comparators.FirCallableDeclarationComparator
@@ -575,12 +574,10 @@ class FirElementSerializer private constructor(
                 builder.setterFlags = accessorFlags
             }

-            val nonSourceAnnotations = setter.nonSourceAnnotations(session)
             if (Flags.IS_NOT_DEFAULT.get(accessorFlags)) {
                 val setterLocal = local.createChildSerializer(setter)
                 for ((index, valueParameterDescriptor) in setter.valueParameters.withIndex()) {
-                    val annotations = nonSourceAnnotations.filter { it.useSiteTarget == AnnotationUseSiteTarget.SETTER_PARAMETER }
-                    builder.setSetterValueParameter(setterLocal.valueParameterProto(valueParameterDescriptor, index, setter, annotations))
+                    builder.setSetterValueParameter(setterLocal.valueParameterProto(valueParameterDescriptor, index, setter))
                 }
             }

@@ -630,7 +627,6 @@ class FirElementSerializer private constructor(
             builder.addContextParameter(
                 local.valueParameterProto(
                     contextParameter,
-                    additionalAnnotations = emptyList(),
                     declaresDefaultValue = false
                 )
             )
@@ -725,7 +721,6 @@ class FirElementSerializer private constructor(
             builder.addContextParameter(
                 local.valueParameterProto(
                     contextParameter,
-                    additionalAnnotations = emptyList(),
                     declaresDefaultValue = false
                 )
             )
@@ -881,7 +876,6 @@ class FirElementSerializer private constructor(
         parameter: FirValueParameter,
         index: Int,
         function: FirFunction,
-        additionalAnnotations: List<FirAnnotation> = emptyList(),
     ): ProtoBuf.ValueParameter.Builder = whileAnalysing(session, parameter) {
         val declaresDefaultValue = if (
             stdLibCompilation &&
@@ -893,19 +887,17 @@ class FirElementSerializer private constructor(
             function.itOrExpectHasDefaultParameterValue(index)
         }

-        return valueParameterProto(parameter, additionalAnnotations, declaresDefaultValue)
+        return valueParameterProto(parameter, declaresDefaultValue)
     }

     private fun valueParameterProto(
         parameter: FirValueParameter,
-        additionalAnnotations: List<FirAnnotation>,
         declaresDefaultValue: Boolean,
     ): ProtoBuf.ValueParameter.Builder {
         val builder = ProtoBuf.ValueParameter.newBuilder()

         val flags = Flags.getValueParameterFlags(
-            additionalAnnotations.isNotEmpty()
-                    || parameter.nonSourceAnnotations(session).isNotEmpty()
+            parameter.nonSourceAnnotations(session).isNotEmpty()
                     || extension.hasAdditionalAnnotations(parameter),
             declaresDefaultValue,
             parameter.isCrossinline,
diff --git a/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotation.kt b/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotation.kt
index 2232b48aedad9..1986afbe4df90 100644
--- a/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotation.kt
+++ b/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotation.kt
@@ -18,6 +18,22 @@ import org.jetbrains.kotlin.fir.visitors.FirTransformer
 import org.jetbrains.kotlin.fir.visitors.FirVisitor

 /**
+ * A very general representation of an annotation in Kotlin, like `\`@Ann(1, 2)\``.
+ *
+ * Notable properties:
+ * - [argumentMapping] — the map "name to expression" for annotation arguments
+ * - [typeArguments] — annotation type arguments with projection (in/out) if needed
+ * - [annotationTypeRef] — type reference bound to this annotation (maybe used e.g. to find a corresponding [FirRegularClass] for the annotation)
+ * - [useSiteTarget] — annotation use-site target like GET (`\`@get:Ann\``) or PARAMETER (`\`@param:Ann\``), if any;
+ * normally annotation should be moved to corresponding element during raw FIR building phase or, in non-obvious cases,
+ * during type resolving phase. Sometimes, e.g. for [AnnotationUseSiteTarget.ALL] or for constructor properties annotation,
+ * it's copied to multiple elements. Targets [AnnotationUseSiteTarget.FIELD] and [AnnotationUseSiteTarget.PROPERTY_DELEGATE_FIELD]
+ * are indistinguishable this way, as both occupy a backing field.
+ *
+ * Note: a declaration of an annotation class, like `annotation class Ann`, is represented by [FirRegularClass].
+ *
+ * See also a very similar [FirAnnotationCall].
+ *
  * Generated from: [org.jetbrains.kotlin.fir.tree.generator.FirTree.annotation]
  */
 abstract class FirAnnotation : FirExpression() {
diff --git a/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotationCall.kt b/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotationCall.kt
index 59c5017b43923..622e8c586a1c9 100644
--- a/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotationCall.kt
+++ b/compiler/fir/tree/gen/org/jetbrains/kotlin/fir/expressions/FirAnnotationCall.kt
@@ -20,6 +20,30 @@ import org.jetbrains.kotlin.fir.visitors.FirTransformer
 import org.jetbrains.kotlin.fir.visitors.FirVisitor

 /**
+ * An extended representation of an annotation in Kotlin. See more general [FirAnnotation].
+ *
+ * [FirAnnotationCall] is a [FirCall], so it differs from [FirAnnotation] as it includes more detailed description,
+ * despite representing generally the same `\`@Ann(1, 2)\`` or something similar.
+ * [FirAnnotation] is a more light-weight, so it's used when providing [FirCall] properties is problematic,
+ * e.g. in serialization, in Java interop, or in plugins.
+ * [FirAnnotationCall] is used mainly for source-based annotation that require resolve.
+ *
+ * Notable inherited properties from [FirAnnotation]:
+ * - [argumentMapping] — the map "name to expression" for annotation arguments
+ * - [typeArguments] — annotation type arguments with projection (in/out) if needed
+ * - [annotationTypeRef] — type reference bound to this annotation (maybe used e.g. to find a corresponding [FirRegularClass] for the annotation)
+ * - [useSiteTarget] — annotation use-site target like GET (`\`@get:Ann\``) or PARAMETER (`\`@param:Ann\``), if any;
+ * normally annotation should be moved to corresponding element during raw FIR building phase or, in non-obvious cases,
+ * during type resolving phase. Sometimes, e.g. for [AnnotationUseSiteTarget.ALL] or for constructor properties annotation,
+ * it's copied to multiple elements. Targets [AnnotationUseSiteTarget.FIELD] and [AnnotationUseSiteTarget.PROPERTY_DELEGATE_FIELD]
+ * are indistinguishable this way, as both occupy a backing field.
+ *
+ * Notable inherited properties from [FirCall]:
+ * - [argumentList] — list of annotation arguments to be resolved. After resolve, they are represented as [FirResolvedArgumentList].
+ * - [calleeReference] — reference to an annotation class symbol, either unresolved [FirSimpleNamedReference] or resolved [FirResolvedNamedReference]
+ *
+ * Note: a declaration of an annotation class, like `annotation class Ann`, is represented by [FirRegularClass].
+ *
  * Generated from: [org.jetbrains.kotlin.fir.tree.generator.FirTree.annotationCall]
  */
 abstract class FirAnnotationCall : FirAnnotation(), FirCall, FirResolvable {
diff --git a/compiler/fir/tree/tree-generator/src/org/jetbrains/kotlin/fir/tree/generator/FirTree.kt b/compiler/fir/tree/tree-generator/src/org/jetbrains/kotlin/fir/tree/generator/FirTree.kt
index 7969e11dfa328..abe04fd88f888 100644
--- a/compiler/fir/tree/tree-generator/src/org/jetbrains/kotlin/fir/tree/generator/FirTree.kt
+++ b/compiler/fir/tree/tree-generator/src/org/jetbrains/kotlin/fir/tree/generator/FirTree.kt
@@ -1059,6 +1059,23 @@ object FirTree : AbstractFirTreeBuilder() {
     }

     val annotation: Element by element(Expression) {
+        kDoc = """
+            A very general representation of an annotation in Kotlin, like `\`@Ann(1, 2)\``.
+
+            Notable properties:
+            - [argumentMapping] — the map "name to expression" for annotation arguments
+            - [typeArguments] — annotation type arguments with projection (in/out) if needed
+            - [annotationTypeRef] — type reference bound to this annotation (maybe used e.g. to find a corresponding [FirRegularClass] for the annotation)
+            - [useSiteTarget] — annotation use-site target like GET (`\`@get:Ann\``) or PARAMETER (`\`@param:Ann\``), if any;
+            normally annotation should be moved to corresponding element during raw FIR building phase or, in non-under cases,
+            during type resolving phase. Sometimes, e.g. for [AnnotationUseSiteTarget.ALL] or for constructor properties annotation,
+            it's copied to multiple elements. Targets [AnnotationUseSiteTarget.FIELD] and [AnnotationUseSiteTarget.PROPERTY_DELEGATE_FIELD]
+            are indistinguishable this way, as both occupy a backing field.
+
+            Note: a declaration of an annotation class, like `annotation class Ann`, is represented by [FirRegularClass].
+
+            See also a very similar [FirAnnotationCall].
+        """.trimIndent()
         parent(expression)

         +field("useSiteTarget", annotationUseSiteTargetType, nullable = true, withReplace = true)
@@ -1070,6 +1087,31 @@ object FirTree : AbstractFirTreeBuilder() {
     }

     val annotationCall: Element by element(Expression) {
+        kDoc = """
+            An extended representation of an annotation in Kotlin. See more general [FirAnnotation].
+
+            [FirAnnotationCall] is a [FirCall], so it differs from [FirAnnotation] as it includes more detailed description,
+            despite representing generally the same `\`@Ann(1, 2)\`` or something similar.
+            [FirAnnotation] is a more light-weight, so it's used used when providing [FirCall] properties is problematic,
+            e.g. in serialization, in Java interop, or in plugins.
+            [FirAnnotationCall] is used mainly for source-based annotation that require resolve.
+
+            Notable inherited properties from [FirAnnotation]:
+            - [argumentMapping] — the map "name to expression" for annotation arguments
+            - [typeArguments] — annotation type arguments with projection (in/out) if needed
+            - [annotationTypeRef] — type reference bound to this annotation (maybe used e.g. to find a corresponding [FirRegularClass] for the annotation)
+            - [useSiteTarget] — annotation use-site target like GET (`\`@get:Ann\``) or PARAMETER (`\`@param:Ann\``), if any;
+            normally annotation should be moved to corresponding element during raw FIR building phase or, in non-obvious cases,
+            during type resolving phase. Sometimes, e.g. for [AnnotationUseSiteTarget.ALL] or for constructor properties annotation,
+            it's copied to multiple elements. Targets [AnnotationUseSiteTarget.FIELD] and [AnnotationUseSiteTarget.PROPERTY_DELEGATE_FIELD]
+            are indistinguishable this way, as both occupy a backing field.
+
+            Notable inherited properties from [FirCall]:
+            - [argumentList] — list of annotation arguments to be resolved. After resolve, they are represented as [FirResolvedArgumentList].
+            - [calleeReference] — reference to an annotation class symbol, either unresolved [FirSimpleNamedReference] or resolved [FirResolvedNamedReference]
+
+            Note: a declaration of an annotation class, like `annotation class Ann`, is represented by [FirRegularClass].
+        """.trimIndent()
         parent(annotation)
         parent(call)
         parent(resolvable)
diff --git a/plugins/parcelize/parcelize-compiler/parcelize.k2/src/org/jetbrains/kotlin/parcelize/fir/diagnostics/FirParcelizePropertyChecker.kt b/plugins/parcelize/parcelize-compiler/parcelize.k2/src/org/jetbrains/kotlin/parcelize/fir/diagnostics/FirParcelizePropertyChecker.kt
index 60d262db5db86..d142d784bd9f8 100644
--- a/plugins/parcelize/parcelize-compiler/parcelize.k2/src/org/jetbrains/kotlin/parcelize/fir/diagnostics/FirParcelizePropertyChecker.kt
+++ b/plugins/parcelize/parcelize-compiler/parcelize.k2/src/org/jetbrains/kotlin/parcelize/fir/diagnostics/FirParcelizePropertyChecker.kt
@@ -6,7 +6,6 @@
 package org.jetbrains.kotlin.parcelize.fir.diagnostics

 import org.jetbrains.kotlin.descriptors.ClassKind
-import org.jetbrains.kotlin.descriptors.annotations.AnnotationUseSiteTarget
 import org.jetbrains.kotlin.descriptors.isEnumClass
 import org.jetbrains.kotlin.diagnostics.DiagnosticReporter
 import org.jetbrains.kotlin.diagnostics.reportOn
@@ -222,9 +221,7 @@ class FirParcelizePropertyChecker(private val parcelizeAnnotations: List<ClassI

     private fun List<FirAnnotation>.hasIgnoredOnParcel(session: FirSession): Boolean {
         return this.any {
-            if (it.fqName(session) !in IGNORED_ON_PARCEL_FQ_NAMES) return@any false
-            val target = it.useSiteTarget
-            target == null || target == AnnotationUseSiteTarget.PROPERTY || target == AnnotationUseSiteTarget.PROPERTY_GETTER
+            it.fqName(session) in IGNORED_ON_PARCEL_FQ_NAMES
         }
     }

PATCH

# Idempotency check: distinctive line from the patch
grep -q "it != AnnotationUseSiteTarget.ALL" compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/FirAnnotationHelpers.kt && echo "Fix applied successfully" || (echo "Fix not applied" && exit 1)
