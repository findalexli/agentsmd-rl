import os

REPO = "/workspace/kotlin"
path = "analysis/analysis-api-fir/testFixtures/org/jetbrains/kotlin/analysis/api/fir/test/configurators/AnalysisApiFirTestConfiguratorFactory.kt"
full_path = os.path.join(REPO, path)

with open(full_path) as f:
    lines = f.readlines()

# Find and remove lines 13-18 (the workaround block)
# Line 13: // This is a workaround...
# Line 14: val data = when (data.moduleKind) {
# Line 15:     TestModuleKind.Source, TestModuleKind.ScriptSource -> data.copy(moduleKind = TestModuleKind.SourceLike)
# Line 16:     else -> data
# Line 17: }
# Line 18: (blank)

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    # Check if this is the start of the workaround
    if "// This is a workaround for the transition time" in line:
        # Skip this line and the next 5 lines (the workaround block + blank line)
        i += 6
        continue
    new_lines.append(line)
    i += 1

with open(full_path, 'w') as f:
    f.writelines(new_lines)

print(f"Fixed: {path}")

# Also fix the arrow alignment
with open(full_path) as f:
    content = f.read()

# Fix the arrow indentation
content = content.replace(
    "TestModuleKind.SourceLike,\n                 -> true",
    "TestModuleKind.SourceLike,\n                -> true"
)

with open(full_path, 'w') as f:
    f.write(content)

print(f"Fixed arrow alignment")

# Verify
with open(full_path) as f:
    content = f.read()

if "when (data.moduleKind)" not in content:
    print("✓ Workaround removed successfully")
else:
    print("✗ Workaround still present")
    exit(1)
