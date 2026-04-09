#!/bin/bash
set -euo pipefail

cd /workspace/kotlin

# Idempotency check: if the deprecated APIs section is already removed, skip
if ! grep -q "DEPRECATED APIs" "libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt"; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply <<'PATCH'
diff --git a/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt b/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt
index 53881dfef3f32..b0530d19ab3ca 100644
--- a/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt
+++ b/libraries/tools/kotlin-tooling-core/src/main/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasProperty.kt
@@ -6,7 +6,6 @@

 package org.jetbrains.kotlin.tooling.core

-import java.util.*
 import kotlin.properties.ReadOnlyProperty
 import kotlin.properties.ReadWriteProperty
 import kotlin.reflect.KProperty
@@ -87,130 +86,3 @@ interface ExtrasLazyProperty<Receiver : HasMutableExtras, T> : ExtrasProperty<T>
         thisRef.extras[key] = value
     }
 }
-
-/*
-DEPRECATED APIs
- */
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR")
-internal val <T : Any> Extras.Key<T>.readProperty get() = extrasReadProperty(this)
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR")
-internal fun <T : Any> Extras.Key<T>.factoryProperty(factory: () -> T) = extrasFactoryProperty(this, factory)
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR")
-internal fun <Receiver : HasMutableExtras, T : Any> Extras.Key<Optional<T>>.nullableLazyProperty(factory: Receiver.() -> T?) =
-    extrasNullableLazyProperty(this, factory)
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR")
-internal fun <T : Any> extrasReadProperty(key: Extras.Key<T>): ExtrasReadOnlyProperty<T> = object : ExtrasReadOnlyProperty<T> {
-    override val key: Extras.Key<T> = key
-}
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR")
-internal fun <T : Any> extrasFactoryProperty(key: Extras.Key<T>, factory: () -> T) = object : ExtrasFactoryProperty<T> {
-    override val key: Extras.Key<T> = key
-    override val factory: () -> T = factory
-}
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR")
-internal fun <Receiver : HasMutableExtras, T : Any> extrasNullableLazyProperty(
-    key: Extras.Key<Optional<T>>, factory: Receiver.() -> T?,
-): NullableExtrasLazyProperty<Receiver, T> =
-    object : NullableExtrasLazyProperty<Receiver, T> {
-        override val key: Extras.Key<Optional<T>> = key
-        override val factory: Receiver.() -> T? = factory
-    }
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR", "UNUSED")
-internal inline fun <reified T : Any> extrasReadProperty(name: String? = null) =
-    extrasReadProperty(extrasKeyOf<T>(name))
-
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR", "UNUSED")
-internal inline fun <reified T : Any> extrasFactoryProperty(name: String? = null, noinline factory: () -> T) =
-    extrasFactoryProperty(extrasKeyOf(name), factory)
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-@Suppress("DEPRECATION_ERROR", "DeprecatedCallableAddReplaceWith")
-internal inline fun <Receiver : HasMutableExtras, reified T : Any> extrasNullableLazyProperty(
-    name: String? = null, noinline factory: Receiver.() -> T?,
-) = extrasNullableLazyProperty(extrasKeyOf(name), factory)
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-internal interface ExtrasReadOnlyProperty<T : Any> : ExtrasProperty<T>, ReadOnlyProperty<HasExtras, T?> {
-    override fun getValue(thisRef: HasExtras, property: KProperty<*>): T? {
-        return thisRef.extras[key]
-    }
-
-    fun notNull(defaultValue: T): NotNullExtrasReadOnlyProperty<T> = object : NotNullExtrasReadOnlyProperty<T> {
-        override val defaultValue: T = defaultValue
-        override val key: Extras.Key<T> = this@ExtrasReadOnlyProperty.key
-    }
-}
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-internal interface ExtrasFactoryProperty<T : Any> : ExtrasProperty<T>, ReadWriteProperty<HasMutableExtras, T> {
-    val factory: () -> T
-
-    override fun getValue(thisRef: HasMutableExtras, property: KProperty<*>): T {
-        return thisRef.extras.getOrPut(key, factory)
-    }
-
-    override fun setValue(thisRef: HasMutableExtras, property: KProperty<*>, value: T) {
-        thisRef.extras[key] = value
-    }
-}
-
-@Deprecated(
-    "Scheduled for removal in Kotlin 2.3",
-    level = DeprecationLevel.ERROR,
-)
-internal interface NullableExtrasLazyProperty<Receiver : HasMutableExtras, T : Any> : ExtrasProperty<Optional<T>>, ReadOnlyProperty<Receiver, T?> {
-    val factory: Receiver.() -> T?
-
-    override fun getValue(thisRef: Receiver, property: KProperty<*>): T? {
-        return thisRef.extras.getOrPut(key) { Optional.ofNullable(thisRef.factory()) }.let { if (it.isPresent) it.get() else null }
-    }
-}
\ No newline at end of file
diff --git a/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasPropertyTest.kt b/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasPropertyTest.kt
index 5fcbc271a5688..5f962daecd382 100644
--- a/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasPropertyTest.kt
+++ b/libraries/tools/kotlin-tooling-core/src/test/kotlin/org/jetbrains/kotlin/tooling/core/ExtrasPropertyTest.kt
@@ -8,7 +8,6 @@ package org.jetbrains.kotlin.tooling.core
 import java.util.concurrent.atomic.AtomicInteger
 import kotlin.test.*

-@Suppress("DEPRECATION_ERROR")
 class ExtrasPropertyTest {

     class Subject : HasMutableExtras {
@@ -21,36 +20,24 @@ class ExtrasPropertyTest {
     private val keyB = extrasKeyOf<Int>("b")
     private val keyANullable = extrasKeyOf<Int?>("a")

-    private val Subject.readA: Int? by keyA.readProperty
-    private val Subject.readB: Int? by keyB.readProperty
+    private val Subject.readA: Int? by keyA.readWriteProperty
+    private val Subject.readB: Int? by keyB.readWriteProperty

     private var Subject.readWriteA: Int? by keyA.readWriteProperty
     private var Subject.readWriteB: Int? by keyB.readWriteProperty

-    private val Subject.notNullReadA: Int by keyA.readProperty.notNull(1)
-    private val Subject.notNullReadB: Int by keyB.readProperty.notNull(2)
+    private val Subject.notNullReadA: Int by keyA.readWriteProperty.notNull(1)
+    private val Subject.notNullReadB: Int by keyB.readWriteProperty.notNull(2)

     private var Subject.notNullReadWriteA: Int by keyA.readWriteProperty.notNull(3)
     private var Subject.notNullReadWriteB: Int by keyB.readWriteProperty.notNull(4)

     private val keyList = extrasKeyOf<MutableList<Dummy>>()
-    private val Subject.factoryList: MutableList<Dummy> by keyList.factoryProperty { mutableListOf() }
+    private val Subject.factoryList: MutableList<Dummy> by keyList.lazyProperty { mutableListOf() }

     private val keySubjectList = extrasKeyOf<MutableList<Subject>>()
     private val Subject.lazyList: MutableList<Subject> by keySubjectList.lazyProperty { mutableListOf(this) }

-    private val lazyNullStringInvocations = mutableListOf<Subject>()
-    private val Subject.lazyNullString: String? by extrasNullableLazyProperty("null") {
-        lazyNullStringInvocations.add(this)
-        null
-    }
-
-    private val lazyNullableStringInvocations = mutableListOf<Subject>()
-    private val Subject.lazyNullableString: String? by extrasNullableLazyProperty("not-null") {
-        lazyNullableStringInvocations.add(this)
-        "OK"
-    }
-
     @Test
     fun `test - readOnlyProperty`() {
         val subject = Subject()
@@ -151,29 +138,6 @@ class ExtrasPropertyTest {
         }
     }

-    @Test
-    fun `test - lazyNullableProperty`() {
-        val subject1 = Subject()
-        val subject2 = Subject()
-
-        assertNull(subject1.lazyNullString)
-        assertNull(subject1.lazyNullString)
-        assertEquals(listOf(subject1), lazyNullStringInvocations)
-
-        assertNull(subject2.lazyNullString)
-        assertNull(subject2.lazyNullString)
-        assertEquals(listOf(subject1, subject2), lazyNullStringInvocations)
-
-
-        assertEquals("OK", subject1.lazyNullableString)
-        assertEquals("OK", subject1.lazyNullableString)
-        assertEquals(listOf(subject1), lazyNullableStringInvocations)
-
-        assertEquals("OK", subject2.lazyNullableString)
-        assertEquals("OK", subject2.lazyNullableString)
-        assertEquals(listOf(subject1, subject2), lazyNullableStringInvocations)
-    }
-
     @Test
     fun `test - lazyProperty - with nullable key`() {
         val subject = Subject()
PATCH

echo "Patch applied successfully."
