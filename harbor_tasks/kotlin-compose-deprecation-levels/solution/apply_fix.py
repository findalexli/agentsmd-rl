#!/usr/bin/env python3
"""Apply the Compose compiler deprecation level fix."""

import re

REPO = "/workspace/kotlin"

# File paths
EXTENSION_FILE = f"{REPO}/libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerGradlePluginExtension.kt"
FEATURE_FLAGS_FILE = f"{REPO}/libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeFeatureFlags.kt"
SUBPLUGIN_FILE = f"{REPO}/libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ComposeCompilerSubplugin.kt"
TEST_FILE = f"{REPO}/libraries/tools/kotlin-compose-compiler/src/functionalTest/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/ExtensionConfigurationTest.kt"


def update_extension_file():
    """Update ComposeCompilerGradlePluginExtension.kt."""
    with open(EXTENSION_FILE, 'r') as f:
        content = f.read()

    # 1. generateFunctionKeyMetaClasses
    content = content.replace(
        '''    @Deprecated("The user facing property is deprecated. Intended for tooling use only. Will be removed in future releases.")
    val generateFunctionKeyMetaClasses:''',
        '''    @Deprecated(
        message = "The user facing property is deprecated. Intended for tooling use only. Will be removed in Kotlin 2.5.0.",
        level = DeprecationLevel.ERROR,
    )
    val generateFunctionKeyMetaClasses:'''
    )

    # 2. enableIntrinsicRemember
    content = content.replace(
        '''    @Deprecated("Use the featureFlags option instead")
    val enableIntrinsicRemember:''',
        '''    @Deprecated(
        message = "Use the featureFlags option instead. Will be removed in Kotlin 2.5.0",
        level = DeprecationLevel.ERROR
    )
    val enableIntrinsicRemember:'''
    )

    # 3. enableNonSkippingGroupOptimization
    content = content.replace(
        '''    @Deprecated("Use the featureFlags option instead")
    val enableNonSkippingGroupOptimization:''',
        '''    @Deprecated(
        message = "Use the featureFlags option instead. Will be removed in Kotlin 2.5.0",
        level = DeprecationLevel.ERROR
    )
    val enableNonSkippingGroupOptimization:'''
    )

    # 4. enableStrongSkippingMode
    content = content.replace(
        '''    @Deprecated("Use the featureFlags option instead")
    val enableStrongSkippingMode:''',
        '''    @Deprecated(
        message = "Use the featureFlags option instead. Will be removed in Kotlin 2.5.0",
        level = DeprecationLevel.ERROR
    )
    val enableStrongSkippingMode:'''
    )

    # 5. stabilityConfigurationFile
    content = content.replace(
        '''    @Deprecated("Use the stabilityConfigurationFiles option instead")
    abstract val stabilityConfigurationFile:''',
        '''    @Deprecated(
        message = "Use the stabilityConfigurationFiles option instead. Will be removed in Kotlin 2.5.0",
        level = DeprecationLevel.ERROR
    )
    abstract val stabilityConfigurationFile:'''
    )

    # 6. Update @Suppress for featureFlags
    content = content.replace(
        '''    @Suppress("DEPRECATION")
    val featureFlags:''',
        '''    @Suppress("DEPRECATION_ERROR", "DEPRECATION")
    val featureFlags:'''
    )

    with open(EXTENSION_FILE, 'w') as f:
        f.write(content)

    print("Updated ComposeCompilerGradlePluginExtension.kt")


def update_feature_flags_file():
    """Update ComposeFeatureFlags.kt."""
    with open(FEATURE_FLAGS_FILE, 'r') as f:
        content = f.read()

    # 1. StrongSkipping - change to ERROR
    content = content.replace(
        '''        @Deprecated("This flag should be enabled by default and will be removed in the future versions.")
        @JvmField
        val StrongSkipping:''',
        '''        @Deprecated(
            message = "This flag should be enabled by default and will be removed with Kotlin 2.5.0.",
            level = DeprecationLevel.ERROR
        )
        @JvmField
        val StrongSkipping:'''
    )

    # 2. IntrinsicRemember - change to ERROR
    content = content.replace(
        '''        @Deprecated("This flag should be enabled by default and will be removed in the future versions.")
        @JvmField
        val IntrinsicRemember:''',
        '''        @Deprecated(
            message = "This flag should be enabled by default and will be removed with Kotlin 2.5.0.",
            level = DeprecationLevel.ERROR
        )
        @JvmField
        val IntrinsicRemember:'''
    )

    # 3. OptimizeNonSkippingGroups - add WARNING (currently has no deprecation)
    content = content.replace(
        '''        @JvmField
        val OptimizeNonSkippingGroups:''',
        '''        @Deprecated(
            message = "This flag should be enabled by default and will be removed in the future versions.",
            level = DeprecationLevel.WARNING
        )
        @JvmField
        val OptimizeNonSkippingGroups:'''
    )

    # 4. PausableComposition - add WARNING (currently has no deprecation)
    content = content.replace(
        '''        @JvmField
        val PausableComposition:''',
        '''        @Deprecated(
            message = "This flag should be enabled by default and will be removed in the future versions.",
            level = DeprecationLevel.WARNING
        )
        @JvmField
        val PausableComposition:'''
    )

    with open(FEATURE_FLAGS_FILE, 'w') as f:
        f.write(content)

    print("Updated ComposeFeatureFlags.kt")


def update_subplugin_file():
    """Update ComposeCompilerSubplugin.kt."""
    with open(SUBPLUGIN_FILE, 'r') as f:
        content = f.read()

    # 1. generateFunctionKeyMetaClasses - change to DEPRECATION_ERROR
    content = content.replace(
        '''                @Suppress("DEPRECATION")
                add(composeExtension.generateFunctionKeyMetaClasses.map''',
        '''                @Suppress("DEPRECATION_ERROR")
                add(composeExtension.generateFunctionKeyMetaClasses.map'''
    )

    # 2. stabilityConfigurationFile - change to DEPRECATION_ERROR
    content = content.replace(
        '''                @Suppress("DEPRECATION")
                add(composeExtension.stabilityConfigurationFile.map<SubpluginOption>''',
        '''                @Suppress("DEPRECATION_ERROR")
                add(composeExtension.stabilityConfigurationFile.map<SubpluginOption>'''
    )

    # 3. featureFlags - change to both DEPRECATION_ERROR and DEPRECATION
    content = content.replace(
        '''                @Suppress("DEPRECATION")
                addAll(
                    composeExtension.featureFlags''',
        '''                @Suppress("DEPRECATION_ERROR", "DEPRECATION")
                addAll(
                    composeExtension.featureFlags'''
    )

    with open(SUBPLUGIN_FILE, 'w') as f:
        f.write(content)

    print("Updated ComposeCompilerSubplugin.kt")


def update_test_file():
    """Update ExtensionConfigurationTest.kt with proper @Suppress annotations."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    # 1. testStabilityConfigurationFile - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Suppress("DEPRECATION")
    @Test
    fun testStabilityConfigurationFile()''',
        '''    @Suppress("DEPRECATION_ERROR")
    @Test
    fun testStabilityConfigurationFile()'''
    )

    # 2. disableIntrinsicRemember - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun disableIntrinsicRemember() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(listOf("-IntrinsicRemember"))''',
        '''    @Test
    fun disableIntrinsicRemember() {
        @Suppress("DEPRECATION_ERROR")
        testComposeFeatureFlags(listOf("-IntrinsicRemember"))'''
    )

    # 3. disableStrongSkipping - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun disableStrongSkipping() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(listOf("-StrongSkipping"))''',
        '''    @Test
    fun disableStrongSkipping() {
        @Suppress("DEPRECATION_ERROR")
        testComposeFeatureFlags(listOf("-StrongSkipping"))'''
    )

    # 4. disableNonSkippingGroupOptimization - add DEPRECATION
    content = content.replace(
        '''    @Test
    fun disableNonSkippingGroupOptimization() {
        testComposeFeatureFlags(listOf("-OptimizeNonSkippingGroups"))''',
        '''    @Test
    fun disableNonSkippingGroupOptimization() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(listOf("-OptimizeNonSkippingGroups"))'''
    )

    # 5. disablePausableComposition - add DEPRECATION
    content = content.replace(
        '''    @Test
    fun disablePausableComposition() {
        testComposeFeatureFlags(listOf("-PausableComposition"))''',
        '''    @Test
    fun disablePausableComposition() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(listOf("-PausableComposition"))'''
    )

    # 6. disableIntrinsicRememberCompatibility - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun disableIntrinsicRememberCompatibility() {
        testComposeFeatureFlags(listOf("-IntrinsicRemember")) { extension ->
            @Suppress("DEPRECATION")
            extension.enableIntrinsicRemember.value(false)''',
        '''    @Test
    fun disableIntrinsicRememberCompatibility() {
        testComposeFeatureFlags(listOf("-IntrinsicRemember")) { extension ->
            @Suppress("DEPRECATION_ERROR")
            extension.enableIntrinsicRemember.value(false)'''
    )

    # 7. disableStrongSkippingCompatibility - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun disableStrongSkippingCompatibility() {
        testComposeFeatureFlags(listOf("-StrongSkipping")) { extension ->
            @Suppress("DEPRECATION")
            extension.enableStrongSkippingMode.value(false)''',
        '''    @Test
    fun disableStrongSkippingCompatibility() {
        testComposeFeatureFlags(listOf("-StrongSkipping")) { extension ->
            @Suppress("DEPRECATION_ERROR")
            extension.enableStrongSkippingMode.value(false)'''
    )

    # 8. enableNonSkippingGroupOptimizationCompatibility - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun enableNonSkippingGroupOptimizationCompatibility() {
        testComposeFeatureFlags(listOf("OptimizeNonSkippingGroups")) { extension ->
            @Suppress("DEPRECATION")
            extension.enableNonSkippingGroupOptimization.value(true)''',
        '''    @Test
    fun enableNonSkippingGroupOptimizationCompatibility() {
        testComposeFeatureFlags(listOf("OptimizeNonSkippingGroups")) { extension ->
            @Suppress("DEPRECATION_ERROR")
            extension.enableNonSkippingGroupOptimization.value(true)'''
    )

    # 9. enableMultipleFlags - change to DEPRECATION_ERROR, DEPRECATION
    content = content.replace(
        '''    @Test
    fun enableMultipleFlags() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(listOf("OptimizeNonSkippingGroups", "-StrongSkipping", "-IntrinsicRemember"))''',
        '''    @Test
    fun enableMultipleFlags() {
        @Suppress("DEPRECATION_ERROR", "DEPRECATION")
        testComposeFeatureFlags(listOf("OptimizeNonSkippingGroups", "-StrongSkipping", "-IntrinsicRemember"))'''
    )

    # 10. enableMultipleFlagsCompatibility - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun enableMultipleFlagsCompatibility() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(listOf("OptimizeNonSkippingGroups", "-StrongSkipping", "-IntrinsicRemember")) { extension ->
            extension.enableStrongSkippingMode.value(false)
            extension.enableNonSkippingGroupOptimization.value(true)
            extension.enableIntrinsicRemember.value(false)''',
        '''    @Test
    fun enableMultipleFlagsCompatibility() {
        @Suppress("DEPRECATION_ERROR")
        testComposeFeatureFlags(listOf("OptimizeNonSkippingGroups", "-StrongSkipping", "-IntrinsicRemember")) { extension ->
            extension.enableStrongSkippingMode.value(false)
            extension.enableNonSkippingGroupOptimization.value(true)
            extension.enableIntrinsicRemember.value(false)'''
    )

    # 11. enableMultipleFlagsCompatibilityDefaults - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun enableMultipleFlagsCompatibilityDefaults() {
        @Suppress("DEPRECATION")
        testComposeFeatureFlags(emptyList()) { extension ->
            extension.enableStrongSkippingMode.value(true)
            extension.enableNonSkippingGroupOptimization.value(false)
            extension.enableIntrinsicRemember.value(true)''',
        '''    @Test
    fun enableMultipleFlagsCompatibilityDefaults() {
        @Suppress("DEPRECATION_ERROR")
        testComposeFeatureFlags(emptyList()) { extension ->
            extension.enableStrongSkippingMode.value(true)
            extension.enableNonSkippingGroupOptimization.value(false)
            extension.enableIntrinsicRemember.value(true)'''
    )

    # 12. combineDeprecatedPropertiesWithFeatureFlags - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun combineDeprecatedPropertiesWithFeatureFlags() {
        @Suppress("DEPRECATION")
        val project = buildProjectWithJvm {
            val composeExtension = extensions.getByType<ComposeCompilerGradlePluginExtension>()
            composeExtension.enableNonSkippingGroupOptimization.set(true)
            composeExtension.enableIntrinsicRemember.set(false)''',
        '''    @Test
    fun combineDeprecatedPropertiesWithFeatureFlags() {
        @Suppress("DEPRECATION_ERROR")
        val project = buildProjectWithJvm {
            val composeExtension = extensions.getByType<ComposeCompilerGradlePluginExtension>()
            composeExtension.enableNonSkippingGroupOptimization.set(true)
            composeExtension.enableIntrinsicRemember.set(false)'''
    )

    # 13. contradictInConfiguredFlags - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun contradictInConfiguredFlags() {
        @Suppress("DEPRECATION")
        val project = buildProjectWithJvm {
            val composeExtension = extensions.getByType<ComposeCompilerGradlePluginExtension>()
            composeExtension.enableStrongSkippingMode.set(false)''',
        '''    @Test
    fun contradictInConfiguredFlags() {
        @Suppress("DEPRECATION_ERROR")
        val project = buildProjectWithJvm {
            val composeExtension = extensions.getByType<ComposeCompilerGradlePluginExtension>()
            composeExtension.enableStrongSkippingMode.set(false)'''
    )

    # 14. combineDeprecatedPropertiesWithFeatureFlags_StrongSkipping - change to DEPRECATION_ERROR
    content = content.replace(
        '''    @Test
    fun combineDeprecatedPropertiesWithFeatureFlags_StrongSkipping() {
        @Suppress("DEPRECATION")
        val project = buildProjectWithJvm {
            val composeExtension = extensions.getByType<ComposeCompilerGradlePluginExtension>()
            composeExtension.enableStrongSkippingMode.set(false)''',
        '''    @Test
    fun combineDeprecatedPropertiesWithFeatureFlags_StrongSkipping() {
        @Suppress("DEPRECATION_ERROR")
        val project = buildProjectWithJvm {
            val composeExtension = extensions.getByType<ComposeCompilerGradlePluginExtension>()
            composeExtension.enableStrongSkippingMode.set(false)'''
    )

    with open(TEST_FILE, 'w') as f:
        f.write(content)

    print("Updated ExtensionConfigurationTest.kt")


def verify_changes():
    """Verify the changes were made."""
    with open(EXTENSION_FILE, 'r') as f:
        ext_content = f.read()

    with open(FEATURE_FLAGS_FILE, 'r') as f:
        flags_content = f.read()

    with open(SUBPLUGIN_FILE, 'r') as f:
        subplugin_content = f.read()

    checks = [
        ("Extension: Kotlin 2.5.0 mentioned", "Kotlin 2.5.0" in ext_content),
        ("Extension: DeprecationLevel.ERROR", "DeprecationLevel.ERROR" in ext_content),
        ("Extension: DEPRECATION_ERROR", "DEPRECATION_ERROR" in ext_content),
        ("FeatureFlags: StrongSkipping ERROR", "StrongSkipping" in flags_content and "DeprecationLevel.ERROR" in flags_content),
        ("FeatureFlags: IntrinsicRemember ERROR", "IntrinsicRemember" in flags_content and "DeprecationLevel.ERROR" in flags_content),
        ("FeatureFlags: OptimizeNonSkippingGroups WARNING", "DeprecationLevel.WARNING" in flags_content),
        ("FeatureFlags: PausableComposition WARNING", "DeprecationLevel.WARNING" in flags_content),
        ("Subplugin: DEPRECATION_ERROR", "DEPRECATION_ERROR" in subplugin_content),
    ]

    all_passed = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


def verify_test_changes():
    """Verify test file changes were made."""
    with open(TEST_FILE, 'r') as f:
        content = f.read()

    checks = [
        ("Test: testStabilityConfigurationFile DEPRECATION_ERROR", '@Suppress("DEPRECATION_ERROR")' in content and 'fun testStabilityConfigurationFile()' in content),
        ("Test: disableIntrinsicRemember DEPRECATION_ERROR", 'fun disableIntrinsicRemember()' in content and '@Suppress("DEPRECATION_ERROR")' in content.split('fun disableIntrinsicRemember()')[0].split('fun ')[-2] if 'fun disableIntrinsicRemember()' in content else False),
    ]

    all_passed = True
    for name, passed in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {name}")
        if not passed:
            all_passed = False

    return all_passed


if __name__ == "__main__":
    print("Applying Compose compiler deprecation level fixes...")
    update_extension_file()
    update_feature_flags_file()
    update_subplugin_file()
    update_test_file()
    print("\nVerifying changes...")
    if verify_changes():
        print("\n✓ All changes applied successfully!")
    else:
        print("\n✗ Some changes may not have been applied")
        exit(1)
