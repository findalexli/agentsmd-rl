#!/bin/bash
set -e

cd /workspace/kotlin

# Apply the gold patch for [Swift Export] Support context parameters on functional types
cat <<'PATCH' | git apply -
diff --git a/native/swift/sir-printer/src/org/jetbrains/sir/printer/impl/SirAsSwiftSourcesPrinter.kt b/native/swift/sir-printer/src/org/jetbrains/sir/printer/impl/SirAsSwiftSourcesPrinter.kt
index 5ded7a2e5af2b..23d68b28f4eb0 100644
--- a/native/swift/sir-printer/src/org/jetbrains/sir/printer/impl/SirAsSwiftSourcesPrinter.kt
+++ b/native/swift/sir-printer/src/org/jetbrains/sir/printer/impl/SirAsSwiftSourcesPrinter.kt
@@ -567,7 +567,7 @@ internal class SirAsSwiftSourcesPrinter private constructor(
                     "[${keyType.swiftRender(SirTypeVariance.INVARIANT)}: ${valueType.swiftRender(SirTypeVariance.INVARIANT)}]"

                 is SirFunctionalType -> {
-                    val parameters = parameterTypes.render()
+                    val parameters = (listOfNotNull(contextType) + parameterTypes).render()
                     val async = " async".takeIf { isAsync } ?: ""
                     val throws = when (errorType) {
                         SirType.never -> ""
diff --git a/native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt b/native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt
index 63e6001eda915..0f0b586204614 100644
--- a/native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt
+++ b/native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt
@@ -28,16 +28,45 @@ sealed interface SirType {
 sealed interface SirWrappedType : SirType

 class SirFunctionalType(
+    val contextTypes: List<SirType> = emptyList(),
     val parameterTypes: List<SirType>,
     val isAsync: Boolean = false,
     val errorType: SirType = SirType.never,
     val returnType: SirType,
     override val attributes: List<SirAttribute> = emptyList(),
 ) : SirWrappedType {
+    val contextType: SirType? = contextTypes.takeIf { it.isNotEmpty() }?.let { types ->
+        types.singleOrNull() ?: SirTupleType(types.map { null to it })
+    }
+
     fun copyAppendingAttributes(vararg attributes: SirAttribute): SirFunctionalType {
         val attributesToAdd = attributes.filter { !this.attributes.contains(it) }
         return if (attributesToAdd.isEmpty()) this
-        else SirFunctionalType(parameterTypes, isAsync, errorType, returnType, this.attributes + attributesToAdd)
+        else SirFunctionalType(contextTypes, parameterTypes, isAsync, errorType, returnType, this.attributes + attributesToAdd)
+    }
+
+    override fun equals(other: Any?): Boolean {
+        if (this === other) return true
+        if (other == null || other !is SirFunctionalType) return false
+
+        if (contextTypes != other.contextTypes) return false
+        if (parameterTypes != other.parameterTypes) return false
+        if (isAsync != other.isAsync) return false
+        if (errorType != other.errorType) return false
+        if (returnType != other.returnType) return false
+        if (attributes != other.attributes) return false
+
+        return true
+    }
+
+    override fun hashCode(): Int {
+        var result = contextTypes.hashCode()
+        result = 31 * result + parameterTypes.hashCode()
+        result = 31 * result + isAsync.hashCode()
+        result = 31 * result + errorType.hashCode()
+        result = 31 * result + returnType.hashCode()
+        result = 31 * result + attributes.hashCode()
+        return result
     }
 }

diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
index 65510a91ef4cb..b136c802cc2e9 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/BridgeProvider/TypeBridging.kt
@@ -739,6 +739,7 @@ internal sealed class Bridge(

     class AsContravariantBlock private constructor(
         override val swiftType: SirFunctionalType,
+        private val contextParameters: List<KotlinToSwiftBridge>,
         private val parameters: List<KotlinToSwiftBridge>,
         private val returnType: SwiftToKotlinBridge,
     ) : SwiftToKotlinBridgeWithSingleType(
@@ -746,12 +747,12 @@ internal sealed class Bridge(
         kotlinType = KotlinType.KotlinObject,
         cType = CType.BlockPointer(
             // TODO: think about it, as types like ranges seems possible here making first() call illegal (?)
-            parameters = parameters.map { it.typeList.first().cType },
+            parameters = (contextParameters + parameters).map { it.typeList.first().cType },
             returnType = returnType.typeList.first().cType,
         )
     ) {
         private val kotlinFunctionTypeRendered =
-            "(${parameters.joinToString { it.typeList.single().kotlinType.repr }})->${returnType.typeList.single().kotlinType.repr}"
+            "(${(contextParameters + parameters).joinToString { it.typeList.single().kotlinType.repr }})->${returnType.typeList.single().kotlinType.repr}"

         companion object {
             context(session: SirSession)
@@ -759,6 +760,7 @@ internal sealed class Bridge(
                 swiftType: SirFunctionalType,
             ): AsContravariantBlock = AsContravariantBlock(
                 swiftType,
+                contextParameters = swiftType.contextTypes.map { bridgeReturnType(it) },
                 parameters = swiftType.parameterTypes.map { bridgeReturnType(it) },
                 returnType = bridgeParameterType(swiftType.returnType),
             )
@@ -771,6 +773,7 @@ internal sealed class Bridge(
                     parameterTypes = parameters.map { it.swiftType.escaping },
                     returnType = returnType.swiftType,
                 ),
+                emptyList(),
                 parameters,
                 returnType,
             )
@@ -779,8 +782,10 @@ internal sealed class Bridge(
         override val inKotlinSources: SwiftToKotlinValueConversion
             get() = object : ValueConversion {
                 override fun swiftToKotlin(typeNamer: SirTypeNamer, valueExpression: String): String {
-                    val argsInClosure = parameters
-                        .mapIndexed { idx, el -> "arg${idx}" to el }.takeIf { it.isNotEmpty() }
+                    val argsInClosure = buildList {
+                        addAll(contextParameters.mapIndexed { idx, el -> "ctx${idx}" to el })
+                        addAll(parameters.mapIndexed { idx, el -> "arg${idx}" to el })
+                    }.takeIf { it.isNotEmpty() }
                     val defineArgs = argsInClosure
                         ?.let {
                             " ${
@@ -808,16 +813,16 @@ internal sealed class Bridge(

         override val inSwiftSources = object : SwiftToKotlinValueConversion {
             override fun swiftToKotlin(typeNamer: SirTypeNamer, valueExpression: String): String {
-                val argsInClosure = parameters
-                    .mapIndexed { idx, el -> "arg${idx}" to el }.takeIf { it.isNotEmpty() }
-                val defineArgs = argsInClosure
-                    ?.let { " ${it.joinToString { it.first }} in" } ?: ""
-                val callArgs = argsInClosure
-                    ?.let {
-                        it.joinToString { param ->
-                            param.second.inSwiftSources.kotlinToSwift(typeNamer, param.first)
-                        }
-                    } ?: ""
+                val contextArgs = contextParameters.mapIndexed { idx, el -> "ctx${idx}" to el }
+                val regularArgs = parameters.mapIndexed { idx, el -> "arg${idx}" to el }
+                val defineArgs = (contextArgs + regularArgs).takeIf { it.isNotEmpty() }?.let { " ${it.joinToString { it.first }} in" } ?: ""
+                val callContextArg = contextArgs.map { param ->
+                    param.second.inSwiftSources.kotlinToSwift(typeNamer, param.first)
+                }.takeIf { it.isNotEmpty() }?.joinToString(separator = ",", prefix = "(", postfix = ")")
+                val callRegularArgs = regularArgs.map { param ->
+                    param.second.inSwiftSources.kotlinToSwift(typeNamer, param.first)
+                }
+                val callArgs = (listOfNotNull(callContextArg) + callRegularArgs).takeIf { it.isNotEmpty() }?.joinToString() ?: ""
                 return """{
                 |    let originalBlock = $valueExpression
                 |    return {$defineArgs ${"return ${returnType.inSwiftSources.swiftToKotlin(typeNamer, "originalBlock($callArgs)")}"} }
@@ -852,7 +857,9 @@ internal sealed class Bridge(
                             argumentName = "pointerToBlock",
                             type = SirSwiftModule.unsafeMutableRawPointer.nominalType()
                         )
-                    ) + swiftType.parameterTypes.map { SirParameter(type = it) },
+                    ) + swiftType.contextTypes.mapIndexed { idx, type ->
+                        SirParameter(argumentName = "ctx${idx}", type = type)
+                    } + swiftType.parameterTypes.map { SirParameter(type = it) },
                     returnType = swiftType.returnType,
                     kotlinFqName = FqName(""),
                     selfParameter = null,
@@ -884,12 +891,19 @@ internal sealed class Bridge(
         override val inSwiftSources = object : KotlinToSwiftValueConversion {
             override fun kotlinToSwift(typeNamer: SirTypeNamer, valueExpression: String): String {
                 val allArgs = bridgeProxy.argumentsForInvocation().applyIf(swiftType.isAsync) { dropLast(3) }
-                val defineArgs = allArgs
-                    .drop(1).takeIf { it.isNotEmpty() }
-                    ?.let { " ${it.joinToString()} in" } ?: ""
+                val defineArgs = buildList {
+                    if (swiftType.contextType != null) add("context")
+                    addAll(allArgs.drop(1 + swiftType.contextTypes.size))
+                }.takeIf { it.isNotEmpty() }?.let { " ${it.joinToString()} in" } ?: ""
+                val swiftInvocation = buildList {
+                    if (swiftType.contextType != null) {
+                        add(List(swiftType.contextTypes.size) { idx -> "ctx$idx" }.joinToString(prefix = "let (", postfix = ") = context"))
+                    }
+                    addAll(bridgeProxy.createSwiftInvocation({ "return $it" }))
+                }
                 return """{
                 |    let ${allArgs.first()} = $valueExpression
-                |    return {$defineArgs ${bridgeProxy.createSwiftInvocation({ "return $it" }).joinToString(";")} }
+                |    return {$defineArgs ${swiftInvocation.joinToString(";")} }
                 |}()""".trimMargin()
             }
         }

diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
index 4783ab100dec0..8d59b9cbb644b 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirTypeProviderImpl.kt
@@ -5,6 +5,7 @@

 package org.jetbrains.kotlin.sir.providers.impl

+import org.jetbrains.kotlin.analysis.api.KaExperimentalApi
 import org.jetbrains.kotlin.analysis.api.KaNonPublicApi
 import org.jetbrains.kotlin.analysis.api.KaSession
 import org.jetbrains.kotlin.analysis.api.components.*
@@ -118,7 +119,11 @@ public class SirTypeProviderImpl(
                         ?: SirUnsupportedType
                 }
                 is KaFunctionType -> {
+                    @OptIn(KaExperimentalApi::class)
                     SirFunctionalType(
+                        contextTypes = kaType.contextReceivers.map {
+                            it.type.translateType(ctx.copy(currentPosition = ctx.currentPosition.flip())).withEscapingIfNeeded()
+                        },
                         parameterTypes = listOfNotNull(
                             kaType.receiverType?.translateType(ctx.copy(currentPosition = ctx.currentPosition.flip()))
                                 ?.withEscapingIfNeeded()

diff --git a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt
index c8a30d5c1edfd..258112ade2c3d 100644
--- a/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt
+++ b/native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/StandaloneSirTypeNamer.kt
@@ -63,7 +63,7 @@ internal object StandaloneSirTypeNamer : SirTypeNamer {
     private fun kotlinFqName(type: SirType): String = when (type) {
         is SirNominalType -> kotlinFqName(type)
         is SirExistentialType -> kotlinFqName(type)
-        is SirFunctionalType -> "${"kotlin.coroutines.Suspend".takeIf { type.isAsync } ?: ""}Function${type.parameterTypes.count()}<${(type.parameterTypes + type.returnType).joinToString { kotlinFqName(it) }}>"
+        is SirFunctionalType -> "${"kotlin.coroutines.Suspend".takeIf { type.isAsync } ?: ""}Function${type.contextTypes.count() + type.parameterTypes.count()}<${(type.contextTypes + type.parameterTypes + type.returnType).joinToString { kotlinFqName(it) }}>"
         is SirErrorType, is SirUnsupportedType, is SirTupleType ->
             error("Type $type can not be named")
     }
PATCH

# Verify patch was applied - check for distinctive change in SirType.kt
grep -q "contextTypes: List<SirType>" native/swift/sir/src/org/jetbrains/kotlin/sir/SirType.kt && echo "Patch applied successfully"
