#!/bin/bash
set -e

# Apply fix for AGENTS.md documentation
# This patch adds missing documentation about FIR (K2 Frontend)

cd /workspace/kotlin

# Create the patch file
cat > /tmp/patch.diff << 'PATCHEOF'
--- a/compiler/AGENTS.md
+++ b/compiler/AGENTS.md
@@ -7,6 +7,12 @@ Consider reading [fir-basics.md](../docs/fir/fir-basics.md).
 
 ## Two Frontends
 
+## FIR (K2 Frontend)
+
+The FIR (Frontend Intermediate Representation) is the K2 compiler frontend.
+- Use `FirElement` types for representing Kotlin code structure
+- Located in `compiler/fir/` directory
+
 1. **K1/FE 1.0 (Legacy)**: Located in `compiler/frontend/` - uses PSI and BindingContext
 2. **K2/FIR (Current)**: Located in `compiler/fir/` - Frontend IR, the new compiler frontend
 
PATCHEOF

# Apply the patch
git apply /tmp/patch.diff
echo "Patch applied successfully"
