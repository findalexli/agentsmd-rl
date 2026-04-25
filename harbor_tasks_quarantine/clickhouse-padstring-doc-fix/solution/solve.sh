#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the fix for padString argument descriptions
patch -p1 <<'PATCH'
diff --git a/src/Functions/padString.cpp b/src/Functions/padString.cpp
index 038dbb995c66..6dbea916075f 100644
--- a/src/Functions/padString.cpp
+++ b/src/Functions/padString.cpp
@@ -167,11 +167,11 @@ namespace
         DataTypePtr getReturnTypeImpl(const ColumnsWithTypeAndName & arguments) const override
         {
             FunctionArgumentDescriptors mandatory_args{
-                {"string", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isStringOrFixedString), nullptr, "Array"},
-                {"length", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isInteger), nullptr, "const UInt*"},
+                {"string", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isStringOrFixedString), nullptr, "String or FixedString"},
+                {"length", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isInteger), nullptr, "UInt*"},
             };
             FunctionArgumentDescriptors optional_args{
-                {"pad_string", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isString), isColumnConst, "Array"}
+                {"pad_string", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isString), isColumnConst, "String"}
             };

             validateFunctionArguments(*this, arguments, mandatory_args, optional_args);
PATCH

# Verify the patch was applied
if ! grep -q "String or FixedString" src/Functions/padString.cpp; then
    echo "ERROR: Patch was not applied correctly"
    exit 1
fi

echo "Patch applied successfully"
