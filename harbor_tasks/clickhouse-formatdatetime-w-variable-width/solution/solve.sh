#!/bin/bash
set -e

cd /workspace/ClickHouse

# Apply the fix for formatDateTime %W variable-width formatter bug
# This is the gold patch from PR #102096

patch -p1 << 'PATCH'
diff --git a/src/Functions/formatDateTime.cpp b/src/Functions/formatDateTime.cpp
index 5e1a9a210950..be288c8c4b3b 100644
--- a/src/Functions/formatDateTime.cpp
+++ b/src/Functions/formatDateTime.cpp
@@ -860,7 +860,7 @@ class FunctionFormatDateTimeImpl : public IFunction
     static bool containsOnlyFixedWidthMySQLFormatters(std::string_view format, bool mysql_M_is_month_name, bool mysql_format_ckl_without_leading_zeros, bool mysql_e_with_space_padding)
     {
         static constexpr std::array variable_width_formatter = {'W'};
-        static constexpr std::array variable_width_formatter_M_is_month_name = {'W', 'M'};
+        static constexpr std::array variable_width_formatter_M_is_month_name = {'M'};
         static constexpr std::array variable_width_formatter_leading_zeros = {'c', 'l', 'k'};
         static constexpr std::array variable_width_formatter_e_with_space_padding = {'e'};

@@ -871,6 +871,12 @@ class FunctionFormatDateTimeImpl : public IFunction
                 case '%':
                     if (i + 1 >= format.size())
                         throwLastCharacterIsPercentException();
+
+                    if (std::any_of(
+                            variable_width_formatter.begin(), variable_width_formatter.end(),
+                            [&](char c){ return c == format[i + 1]; }))
+                        return false;
+
                     if (mysql_M_is_month_name)
                     {
                         if (std::any_of(
@@ -892,13 +898,7 @@ class FunctionFormatDateTimeImpl : public IFunction
                                 [&](char c){ return c == format[i + 1]; }))
                             return false;
                     }
-                    else
-                    {
-                        if (std::any_of(
-                                variable_width_formatter.begin(), variable_width_formatter.end(),
-                                [&](char c){ return c == format[i + 1]; }))
-                            return false;
-                    }
+
                     i += 1;
                     continue;
                 default:
PATCH

# Verify the patch was applied by checking for the distinctive line
if ! grep -q "variable_width_formatter_M_is_month_name = {'M'}" src/Functions/formatDateTime.cpp; then
    echo "ERROR: Patch was not applied correctly!"
    exit 1
fi

echo "Patch applied successfully!"
