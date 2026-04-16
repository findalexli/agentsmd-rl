#!/usr/bin/env python3
"""
Apply the gold patch for PR #5807 to the Kotlin repository.
This removes the workaround mapping TestModuleKind.Source to SourceLike
and updates tests to use AnalysisApiTestConfiguratorFactoryData() with defaults.
"""

import os
import re

REPO = "/workspace/kotlin"

def read_file(path):
    with open(os.path.join(REPO, path), 'r') as f:
        return f.read()

def write_file(path, content):
    with open(os.path.join(REPO, path), 'w') as f:
        f.write(content)

def fix_analysis_api_factory():
    """Remove the workaround from AnalysisApiFirTestConfiguratorFactory.kt"""
    path = "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"

    with open(os.path.join(REPO, path), 'r') as f:
        lines = f.readlines()

    # Find and remove the workaround block (lines 13-18, 0-indexed: 12-17)
    # These are:
    # 13: // This is a workaround for the transition time to not fix non-generated tests right away
    # 14: val data = when (data.moduleKind) {
    # 15:     TestModuleKind.Source, TestModuleKind.ScriptSource -> data.copy(moduleKind = TestModuleKind.SourceLike)
    # 16:     else -> data
    # 17: }
    # 18: (blank line)

    # Remove lines 12-17 (0-indexed), keep the blank line handling
    new_lines = lines[:12] + lines[18:]

    content = ''.join(new_lines)

    # Fix indentation of arrow in the later when block
    content = content.replace(
        "TestModuleKind.SourceLike,\n                 -> true",
        "TestModuleKind.SourceLike,\n                -> true"
    )

    with open(os.path.join(REPO, path), 'w') as f:
        f.write(content)

    print(f"Fixed: {path}")

def fix_generator():
    """Fix GenerateSirTests.kt"""
    path = "generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt"
    content = read_file(path)

    # Update copyright year
    content = content.replace("2010-2023", "2010-2026")

    # Fix import - change wildcard to specific
    content = content.replace(
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*",
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData"
    )

    # Replace the explicit constructor call with empty one
    old = '''                val data = AnalysisApiTestConfiguratorFactoryData(
                    FrontendKind.Fir,
                    TestModuleKind.Source,
                    AnalysisSessionMode.Normal,
                    AnalysisApiMode.Ide
                )'''
    new = '''                val data = AnalysisApiTestConfiguratorFactoryData()'''
    content = content.replace(old, new)

    write_file(path, content)
    print(f"Fixed: {path}")

def fix_generated_test():
    """Fix SwiftExportInIdeTestGenerated.java"""
    path = "native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java"
    content = read_file(path)

    # Change Source to SourceLike
    content = content.replace(
        "TestModuleKind.Source,",
        "TestModuleKind.SourceLike,"
    )

    write_file(path, content)
    print(f"Fixed: {path}")

def fix_compose_test():
    """Fix ComposeCompilerBoxTests.kt"""
    path = "plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt"
    content = read_file(path)

    # Update copyright year
    content = content.replace("2010-2024", "2010-2026")

    # Fix imports
    content = content.replace(
        "import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory.createConfigurator",
        "import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory"
    )

    content = content.replace(
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*",
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfigurator\nimport org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData"
    )

    # Replace the configurator property
    old = '''    override val configurator: AnalysisApiTestConfigurator
        get() = createConfigurator(
            AnalysisApiTestConfiguratorFactoryData(
                FrontendKind.Fir,
                TestModuleKind.Source,
                AnalysisSessionMode.Normal,
                AnalysisApiMode.Ide
            )
        )'''
    new = '''    override val configurator: AnalysisApiTestConfigurator = AnalysisApiFirTestConfiguratorFactory.createConfigurator(
        AnalysisApiTestConfiguratorFactoryData()
    )'''
    content = content.replace(old, new)

    write_file(path, content)
    print(f"Fixed: {path}")

def fix_dataframe_test():
    """Fix AbstractCompilerFacilityTestForDataFrame.kt"""
    path = "plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt"
    content = read_file(path)

    # Update copyright year
    content = content.replace("2010-2025", "2010-2026")

    # Fix imports
    content = content.replace(
        "import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory.createConfigurator",
        "import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory"
    )

    content = content.replace(
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*",
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfigurator\nimport org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData"
    )

    # Replace the configurator property (note: no 'get()' in this one)
    old = '''    override val configurator: AnalysisApiTestConfigurator = createConfigurator(
        AnalysisApiTestConfiguratorFactoryData(
            FrontendKind.Fir,
            TestModuleKind.Source,
            AnalysisSessionMode.Normal,
            AnalysisApiMode.Ide
        )
    )'''
    new = '''    override val configurator: AnalysisApiTestConfigurator = AnalysisApiFirTestConfiguratorFactory.createConfigurator(
        AnalysisApiTestConfiguratorFactoryData()
    )'''
    content = content.replace(old, new)

    # Fix missing newline at end
    if not content.endswith('\n'):
        content += '\n'

    write_file(path, content)
    print(f"Fixed: {path}")

def fix_serialization_test():
    """Fix AbstractCompilerFacilityTestForSerialization.kt"""
    path = "plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt"
    content = read_file(path)

    # Update copyright year
    content = content.replace("2010-2024", "2010-2026")

    # Fix imports
    content = content.replace(
        "import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory.createConfigurator",
        "import org.jetbrains.kotlin.analysis.api.fir.test.configurators.AnalysisApiFirTestConfiguratorFactory"
    )

    content = content.replace(
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.*",
        "import org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfigurator\nimport org.jetbrains.kotlin.analysis.test.framework.test.configurators.AnalysisApiTestConfiguratorFactoryData"
    )

    # Replace the configurator property
    old = '''    override val configurator: AnalysisApiTestConfigurator
        get() = createConfigurator(
            AnalysisApiTestConfiguratorFactoryData(
                FrontendKind.Fir,
                TestModuleKind.Source,
                AnalysisSessionMode.Normal,
                AnalysisApiMode.Ide
            )
        )'''
    new = '''    override val configurator: AnalysisApiTestConfigurator = AnalysisApiFirTestConfiguratorFactory.createConfigurator(
        AnalysisApiTestConfiguratorFactoryData()
    )'''
    content = content.replace(old, new)

    # Fix missing newline at end
    if not content.endswith('\n'):
        content += '\n'

    write_file(path, content)
    print(f"Fixed: {path}")

def verify():
    """Verify the changes were applied correctly"""
    print("\nVerifying changes...")

    checks = [
        ("plugins/kotlinx-serialization/testFixtures/org/jetbrains/kotlinx/serialization/runners/AbstractCompilerFacilityTestForSerialization.kt",
         "AnalysisApiTestConfiguratorFactoryData()"),
        ("plugins/kotlin-dataframe/testFixtures/org/jetbrains/kotlin/fir/dataframe/AbstractCompilerFacilityTestForDataFrame.kt",
         "AnalysisApiTestConfiguratorFactoryData()"),
        ("plugins/compose/compiler-hosted/src/test/kotlin/androidx/compose/compiler/plugins/kotlin/ComposeCompilerBoxTests.kt",
         "AnalysisApiTestConfiguratorFactoryData()"),
        ("generators/sir-tests-generator/main/org/jetbrains/kotlin/generators/tests/native/swift/sir/GenerateSirTests.kt",
         "AnalysisApiTestConfiguratorFactoryData()"),
        ("native/swift/swift-export-ide/tests-gen/org/jetbrains/kotlin/swiftexport/ide/SwiftExportInIdeTestGenerated.java",
         "TestModuleKind.SourceLike"),
    ]

    all_passed = True
    for path, expected in checks:
        full_path = os.path.join(REPO, path)
        with open(full_path) as f:
            content = f.read()
        if expected in content:
            print(f"  ✓ {path}")
        else:
            print(f"  ✗ {path} - missing: {expected}")
            all_passed = False

    # Check that workaround is removed (specifically the "val data = when" pattern)
    factory_path = "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"
    full_factory_path = os.path.join(REPO, factory_path)
    with open(full_factory_path) as f:
        factory_content = f.read()

    if "val data = when (data.moduleKind)" not in factory_content:
        print(f"  ✓ Workaround removed from factory")
    else:
        print(f"  ✗ Workaround still present in factory")
        all_passed = False

    return all_passed

def main():
    print("Applying PR #5807 gold patch...\n")

    fix_analysis_api_factory()
    fix_generator()
    fix_generated_test()
    fix_compose_test()
    fix_dataframe_test()
    fix_serialization_test()

    if verify():
        print("\n✓ All changes applied successfully!")
        return 0
    else:
        print("\n✗ Some changes failed to apply")
        return 1

if __name__ == "__main__":
    exit(main())
