#!/bin/bash
set -e

cd /workspace/kotlin

python3 << 'PYTHON'
import re

# Fix 1: Update SirVisibilityCheckerImpl.kt
visibility_file = "native/swift/sir-providers/src/org/jetbrains/kotlin/sir/providers/impl/SirVisibilityCheckerImpl.kt"

with open(visibility_file, 'r') as f:
    content = f.read()

# Add containingDeclaration import
if 'import org.jetbrains.kotlin.analysis.api.components.containingDeclaration' not in content:
    content = content.replace(
        'import org.jetbrains.kotlin.analysis.api.components.KaStandardTypeClassIds',
        'import org.jetbrains.kotlin.analysis.api.components.KaStandardTypeClassIds\nimport org.jetbrains.kotlin.analysis.api.components.containingDeclaration'
    )

# Replace the deprecated annotation check
old_check = '''// Hidden declarations are, well, hidden.
        if (ktSymbol.deprecatedAnnotation?.level == DeprecationLevel.HIDDEN) {
            visibility.value = SirVisibility.PRIVATE
        }'''

new_check = '''// Hidden declarations are, well, hidden.
        val deprecatedAnnotation = ktSymbol.deprecatedAnnotation
        if (deprecatedAnnotation?.level == DeprecationLevel.HIDDEN) {
            visibility.value = SirVisibility.PRIVATE
        }
        if (deprecatedAnnotation?.level == DeprecationLevel.ERROR && (ktSymbol.containingDeclaration as? KaNamedClassSymbol)?.classKind == KaClassKind.INTERFACE) {
            return@withSessions SirAvailability.Unavailable("Protocol members with DeprecationLevel.ERROR are unsupported")
        }'''

content = content.replace(old_check, new_check)

with open(visibility_file, 'w') as f:
    f.write(content)

print(f"Updated {visibility_file}")

# Fix 2: Update SirAttribute.kt
attr_file = "native/swift/sir/src/org/jetbrains/kotlin/sir/SirAttribute.kt"

with open(attr_file, 'r') as f:
    content = f.read()

# Remove obsoleted parameter from constructor
content = re.sub(r'\s+val obsoleted: Boolean = false,?', '', content)

# Update require statements
content = content.replace(
    'require(obsoleted || deprecated || unavailable)',
    'require(deprecated || unavailable)'
)
content = content.replace(
    'require((obsoleted || deprecated) != unavailable)',
    'require(deprecated != unavailable)'
)

# Update require error message
content = content.replace(
    '{ "Declaration can not be both deprecated/obsolete and unavailable" }',
    '{ "Declaration can not be both deprecated and unavailable" }'
)

# Remove obsoleted argument from arguments list
content = re.sub(
    r'\s+SirArgument\("obsoleted", "1\.0"\)\.takeIf \{ obsoleted && !unavailable \},?\n',
    '\n',
    content
)

# Update deprecated argument
content = content.replace(
    'SirArgument("deprecated").takeIf { deprecated && !unavailable }',
    'SirArgument("deprecated").takeIf { deprecated }'
)

# Update isUnusable property
content = content.replace(
    'val isUnusable = unavailable || obsoleted',
    'val isUnusable = unavailable'
)

with open(attr_file, 'w') as f:
    f.write(content)

print(f"Updated {attr_file}")
print("All fixes applied successfully")
PYTHON
