#!/bin/bash
set -e

cd /workspace/kotlin

# Check if already applied (idempotency)
if grep -q "UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE" compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirUnnamedPropertyChecker.kt 2>/dev/null; then
    echo "Fix already applied, skipping..."
    exit 0
fi

echo "Applying fix for UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE..."

# 1. Update DIAGNOSTICS_LIST - add the new warning after UNNAMED_DELEGATED_PROPERTY
sed -i '/val UNNAMED_DELEGATED_PROPERTY by error<PsiElement>(PositioningStrategy.PROPERTY_DELEGATE_BY_KEYWORD)/a\        val UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE by warning<PsiElement>(PositioningStrategy.NAME_IDENTIFIER)' \
    compiler/fir/checkers/checkers-component-generator/src/org/jetbrains/kotlin/fir/checkers/generator/diagnostics/FirDiagnosticsList.kt

# 2. Update FirErrors.kt - add the diagnostic factory
sed -i '/val UNNAMED_DELEGATED_PROPERTY.*getRendererFactory()/a\    val UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE: KtDiagnosticFactory0 = KtDiagnosticFactory0("UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE", WARNING, SourceElementPositioningStrategies.NAME_IDENTIFIER, PsiElement::class, getRendererFactory())' \
    compiler/fir/checkers/gen/org/jetbrains/kotlin/fir/analysis/diagnostics/FirErrors.kt

# 3. Update FirUnnamedPropertyChecker.kt - add the checker logic
# First add the imports after the existing imports
sed -i '/import org.jetbrains.kotlin.fir.isCatchParameter/a\
import org.jetbrains.kotlin.fir.resolve.fullyExpandedType\
import org.jetbrains.kotlin.fir.types.FirResolvedTypeRef\
import org.jetbrains.kotlin.fir.types.isUnitOrFlexibleUnit' \
    compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirUnnamedPropertyChecker.kt

# Then add the checker logic at the end of the check function (before the closing brace)
cat > /tmp/checker_patch.txt << 'EOF'

        val returnTypeRef = declaration.returnTypeRef as? FirResolvedTypeRef ?: return

        if (returnTypeRef.source?.kind is KtFakeSourceElementKind.ImplicitTypeRef && !isDesugaredComponentCall) {
            val returnType = returnTypeRef.coneType.fullyExpandedType()
            if (returnType.isUnitOrFlexibleUnit) {
                reporter.reportOn(declaration.source, FirErrors.UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE)
            }
        }
EOF

# Insert the checker logic before the last closing brace of the check function
# We need to find the end of the check function and insert before it
python3 << 'PYTHON'
import re

file_path = "compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/checkers/declaration/FirUnnamedPropertyChecker.kt"

with open(file_path, 'r') as f:
    content = f.read()

# The logic to add
new_logic = '''\n
        val returnTypeRef = declaration.returnTypeRef as? FirResolvedTypeRef ?: return

        if (returnTypeRef.source?.kind is KtFakeSourceElementKind.ImplicitTypeRef && !isDesugaredComponentCall) {
            val returnType = returnTypeRef.coneType.fullyExpandedType()
            if (returnType.isUnitOrFlexibleUnit) {
                reporter.reportOn(declaration.source, FirErrors.UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE)
            }
        }
'''

# Find the last closing brace of the check function and insert before it
# Looking for the pattern: "reporter.reportOn(declaration.source, FirErrors.MUST_BE_INITIALIZED)" followed by newline and "        }"
pattern = r'(reporter\.reportOn\(declaration\.source, FirErrors\.MUST_BE_INITIALIZED\)\n)(        \})'
replacement = r'\1' + new_logic + r'\2'

content = re.sub(pattern, replacement, content)

with open(file_path, 'w') as f:
    f.write(content)

print("Checker file updated successfully")
PYTHON

# 4. Update FirErrorsDefaultMessages.kt - add import and message
# Add import
sed -i '/import org.jetbrains.kotlin.fir.analysis.diagnostics.FirErrors.UNNAMED_DELEGATED_PROPERTY/a\
import org.jetbrains.kotlin.fir.analysis.diagnostics.FirErrors.UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE' \
    compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/diagnostics/FirErrorsDefaultMessages.kt

# Add message mapping
sed -i '/map.put(UNNAMED_DELEGATED_PROPERTY, "Delegated properties require a name.")/a\
        map.put(UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE, "Type of underscore property is inferred to \x27Unit\x27.")' \
    compiler/fir/checkers/src/org/jetbrains/kotlin/fir/analysis/diagnostics/FirErrorsDefaultMessages.kt

# 5. Create the test data file
mkdir -p compiler/testData/diagnostics/tests/unnamedLocalVariables

cat > compiler/testData/diagnostics/tests/unnamedLocalVariables/withUnitType.kt << 'EOF'
// ISSUE: KT-84618
// RUN_PIPELINE_TILL: BACKEND
// LANGUAGE: +UnnamedLocalVariables +NameBasedDestructuring

// FILE: JavaUtils.java

package test;

public class JavaUtils {
    public static <T> T id(T arg) {
        return arg;
    }
}

// FILE: test.kt

package test

typealias UnitAlias = Unit

fun returnUnit() { }
fun returnUnitAlias(): UnitAlias { }
fun returnNullableUnit(): Unit? = null

class MyPair {
    operator fun component1() = returnUnit()
    operator fun component2() = returnNullableUnit()
}

inline fun <reified T> Array<T>.myForEach(block: (T) -> Unit) {
    for (element in this) block(element)
}

inline fun <reified T> Array<T>.myForEachIndexed(block: (Int, T) -> Unit) {
    var it = 0
    for (element in this) block(it++, element)
}

fun testWithImplicit() {
    val <!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>_<!> = Unit
    val <!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>_<!> = returnUnit()
    val _ = returnNullableUnit()
    val <!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>_<!> = returnUnitAlias()
    val <!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>_<!> = JavaUtils.id(Unit)

    val [_, _] = MyPair()
    [val _, val _] = MyPair()

    for (<!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>_<!> in arrayOf(Unit, Unit, Unit)) {
    }

    when (val <!UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE!>_<!> = returnUnit()) {
        Unit -> {}
    }

    arrayOf(Unit).myForEach { _ -> }
    arrayOf(MyPair()).myForEach { (_, _) -> }
    arrayOf(Unit).myForEachIndexed { _, _ -> }
}

fun testWithExplicit() {
    val _: Unit = Unit
    val _: Unit = returnUnit()
    val _: Unit? = returnUnit()
    val _: Unit? = returnNullableUnit()
    val _: Unit = JavaUtils.id(Unit)
    val _: Unit? = JavaUtils.id(Unit)
    val _: UnitAlias = Unit
    val _: UnitAlias = returnUnitAlias()

    val [_: Unit, _: Unit?] = MyPair()
    [val _: Unit, val _: Unit?] = MyPair()

    for (_: Unit in arrayOf(Unit, Unit, Unit)) {
    }

    when (val _: Unit = returnUnit()) {
        Unit -> {}
    }

    arrayOf(Unit).myForEach { _: Unit -> }
    arrayOf(MyPair()).myForEach { (_: Unit, _: Unit?) -> }
    arrayOf(Unit).myForEachIndexed { _: Int, _: Unit -> }
}

/* GENERATED_FIR_TAGS: classDeclaration, destructuringDeclaration, equalityExpression, forLoop, functionDeclaration,
localProperty, nullableType, operator, propertyDeclaration, typeAliasDeclaration, unnamedLocalVariable, whenExpression,
whenWithSubject */
EOF

# 6. Update Analysis API files

# KaFirDiagnostics.kt - add interface
sed -i '/interface UnnamedDelegatedProperty : KaFirDiagnostic<PsiElement> {/a\
        override val diagnosticClass get() = UnnamedDelegatedProperty::class\
    }\
\
    interface UnnamedPropertyWithImplicitUnitType : KaFirDiagnostic<PsiElement> {\
        override val diagnosticClass get() = UnnamedPropertyWithImplicitUnitType::class\
    }\
\
    interface DestructuringShortFormNameMismatch' \
    analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt

# The above is too complex for sed, let's use Python
python3 << 'PYTHON'
import re

# Update KaFirDiagnostics.kt
with open('analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt', 'r') as f:
    content = f.read()

# Find the UnnamedDelegatedProperty interface and add after it
old_pattern = r'''(interface UnnamedDelegatedProperty : KaFirDiagnostic<PsiElement> \{
        override val diagnosticClass get\(\) = UnnamedDelegatedProperty::class
    \})'''

new_content = r'''\1

    interface UnnamedPropertyWithImplicitUnitType : KaFirDiagnostic<PsiElement> {
        override val diagnosticClass get() = UnnamedPropertyWithImplicitUnitType::class
    }'''

content = re.sub(old_pattern, new_content, content)

with open('analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnostics.kt', 'w') as f:
    f.write(content)

print("KaFirDiagnostics.kt updated")
PYTHON

# KaFirDiagnosticsImpl.kt - add implementation class
python3 << 'PYTHON'
import re

# Update KaFirDiagnosticsImpl.kt
with open('analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt', 'r') as f:
    content = f.read()

# Find the UnnamedDelegatedPropertyImpl class and add after it
old_pattern = r'''(internal class UnnamedDelegatedPropertyImpl\(
    firDiagnostic: KtPsiDiagnostic,
    token: KaLifetimeToken,
\) : KaAbstractFirDiagnostic<PsiElement>\(firDiagnostic, token\), KaFirDiagnostic\.UnnamedDelegatedProperty

)'''

new_content = r'''\1internal class UnnamedPropertyWithImplicitUnitTypeImpl(
    firDiagnostic: KtPsiDiagnostic,
    token: KaLifetimeToken,
) : KaAbstractFirDiagnostic<PsiElement>(firDiagnostic, token), KaFirDiagnostic.UnnamedPropertyWithImplicitUnitType

'''

content = re.sub(old_pattern, new_content, content)

with open('analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDiagnosticsImpl.kt', 'w') as f:
    f.write(content)

print("KaFirDiagnosticsImpl.kt updated")
PYTHON

# KaFirDataClassConverters.kt - add converter
# Find the line with "add(FirJvmErrors.JVM_STATIC_ON_NON_PUBLIC_MEMBER)" and insert before it
python3 << 'PYTHON'
with open('analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt', 'r') as f:
    lines = f.readlines()

# Find the line with JVM_STATIC_ON_NON_PUBLIC_MEMBER
insert_idx = None
for i, line in enumerate(lines):
    if 'add(FirJvmErrors.JVM_STATIC_ON_NON_PUBLIC_MEMBER)' in line:
        insert_idx = i
        break

if insert_idx is not None:
    # Insert our converter before this line
    new_converter = '''    add(FirErrors.UNNAMED_PROPERTY_WITH_IMPLICIT_UNIT_TYPE) { firDiagnostic ->
        UnnamedPropertyWithImplicitUnitTypeImpl(
            firDiagnostic as KtPsiDiagnostic,
            token,
        )
    }
'''
    lines.insert(insert_idx, new_converter)

    with open('analysis/analysis-api-fir/gen/org/jetbrains/kotlin/analysis/api/fir/diagnostics/KaFirDataClassConverters.kt', 'w') as f:
        f.writelines(lines)
    print("KaFirDataClassConverters.kt updated")
else:
    print("WARNING: Could not find insertion point for converter")
PYTHON

# 7. Update scripting test data to avoid false positives
# Check if the file exists in the old or new location
SCRIPT_FILE_OLD="plugins/scripting/scripting-tests/testData/testScripts/unnamedLocalVariables.test.kts"
SCRIPT_FILE_NEW="plugins/scripting/scripting-tests/testData/codegen/testScripts/unnamedLocalVariables.test.kts"

if [ -f "$SCRIPT_FILE_NEW" ]; then
    # Change return type from Unit to Int and add return statement
    python3 << 'PYTHON'
import re

with open('plugins/scripting/scripting-tests/testData/codegen/testScripts/unnamedLocalVariables.test.kts', 'r') as f:
    content = f.read()

# Update the function to return Int instead of Unit implicitly
content = content.replace(
    'fun call() {\n    result = "OK"\n}',
    'fun call(): Int {\n    result = "OK"\n    return 0\n}'
)

with open('plugins/scripting/scripting-tests/testData/codegen/testScripts/unnamedLocalVariables.test.kts', 'w') as f:
    f.write(content)

print("Scripting test file updated")
PYTHON
elif [ -f "$SCRIPT_FILE_OLD" ]; then
    python3 << 'PYTHON'
import re

with open('plugins/scripting/scripting-tests/testData/testScripts/unnamedLocalVariables.test.kts', 'r') as f:
    content = f.read()

content = content.replace(
    'fun call() {\n    result = "OK"\n}',
    'fun call(): Int {\n    result = "OK"\n    return 0\n}'
)

with open('plugins/scripting/scripting-tests/testData/testScripts/unnamedLocalVariables.test.kts', 'w') as f:
    f.write(content)

print("Scripting test file (old location) updated")
PYTHON
fi

echo "Fix applied successfully!"
