#!/bin/bash
set -e

REPO="/workspace/ClickHouse"
cd "$REPO"

# Check if already patched (idempotency check)
if grep -q "PaddedPODArray<UInt8> pad_string" src/Functions/padString.cpp 2>/dev/null; then
    echo "Already patched, skipping"
    exit 0
fi

# Apply the fix using git apply
cat << 'PATCH' | git apply -
--- a/src/Functions/padString.cpp
+++ b/src/Functions/padString.cpp
@@ -1,7 +1,9 @@
+#include <memory>
 #include <Columns/ColumnFixedString.h>
 #include <Common/StringUtils.h>
 #include <Columns/ColumnString.h>
 #include <DataTypes/DataTypeString.h>
+#include <DataTypes/IDataType.h>
 #include <Functions/FunctionFactory.h>
 #include <Functions/FunctionHelpers.h>
 #include <Functions/GatherUtils/Algorithms.h>
@@ -15,16 +17,14 @@ using namespace GatherUtils;
 namespace ErrorCodes
 {
     extern const int ILLEGAL_COLUMN;
-    extern const int ILLEGAL_TYPE_OF_ARGUMENT;
-    extern const int NUMBER_OF_ARGUMENTS_DOESNT_MATCH;
     extern const int TOO_LARGE_STRING_SIZE;
     extern const int INDEX_OF_POSITIONAL_ARGUMENT_IS_OUT_OF_RANGE;
 }

 namespace
 {
     /// The maximum new padded length.
-    constexpr ssize_t MAX_NEW_LENGTH = 1000000;
+    constexpr ssize_t MAX_NEW_LENGTH = 1'000'000;

     /// Appends padding characters to a sink based on a pad string.
     /// Depending on how many padding characters are required to add
@@ -33,14 +33,50 @@ namespace
     class PaddingChars
     {
     public:
-        explicit PaddingChars(const String & pad_string_) : pad_string(pad_string_) { init(); }
+        explicit PaddingChars(const String & pad_string_)
+        {
+            /// Copy pad string data into PaddedPODArray which provides 15 extra bytes of read padding beyond its size.
+            /// This is a requirement of `memcpySmallAllowReadWriteOverflow15` which is called by `writeSlice` in `appendTo`.
+            pad_string.insert(pad_string_.begin(), pad_string_.end());
+
+            if constexpr (is_utf8)
+            {
+                size_t offset = 0;
+                utf8_offsets.reserve(pad_string.size() + 1);
+                while (true)
+                {
+                    utf8_offsets.push_back(offset);
+                    if (offset == pad_string.size())
+                        break;
+                    offset += UTF8::seqLength(pad_string[offset]);
+                    offset = std::min(offset, pad_string.size());
+                }
+            }
+
+            /// Not necessary, but good for performance.
+            /// We repeat `pad_string` multiple times until it's length becomes 16 or more.
+            /// It speeds up the function appendTo() because it allows to copy padding characters by portions of at least
+            /// 16 bytes instead of single bytes.
+            while (numCharsInPadString() < 16)
+            {
+                pad_string.insertFromItself(pad_string.begin(), pad_string.end());
+                if constexpr (is_utf8)
+                {
+                    size_t old_size = utf8_offsets.size();
+                    utf8_offsets.reserve((old_size - 1) * 2);
+                    size_t base = utf8_offsets.back();
+                    for (size_t i = 1; i != old_size; ++i)
+                        utf8_offsets.push_back(utf8_offsets[i] + base);
+                }
+            }
+        }

         ALWAYS_INLINE size_t numCharsInPadString() const
         {
             if constexpr (is_utf8)
                 return utf8_offsets.size() - 1;
             else
-                return pad_string.length();
+                return pad_string.size();
         }

         ALWAYS_INLINE size_t numCharsToNumBytes(size_t count) const
@@ -53,61 +89,25 @@ namespace

         void appendTo(StringSink & res_sink, size_t num_chars) const
         {
-            if (!num_chars)
+            if (num_chars == 0)
                 return;

             const size_t step = numCharsInPadString();
             while (true)
             {
                 if (num_chars <= step)
                 {
-                    writeSlice(StringSource::Slice{reinterpret_cast<const UInt8 *>(pad_string.data()), numCharsToNumBytes(num_chars)}, res_sink);
+                    writeSlice(StringSource::Slice{pad_string.data(), numCharsToNumBytes(num_chars)}, res_sink);
                     break;
                 }
-                writeSlice(StringSource::Slice{reinterpret_cast<const UInt8 *>(pad_string.data()), numCharsToNumBytes(step)}, res_sink);
+                writeSlice(StringSource::Slice{pad_string.data(), numCharsToNumBytes(step)}, res_sink);
                 num_chars -= step;
             }
         }

     private:
-        void init()
-        {
-            if (pad_string.empty())
-                pad_string = " ";
-
-            if constexpr (is_utf8)
-            {
-                size_t offset = 0;
-                utf8_offsets.reserve(pad_string.length() + 1);
-                while (true)
-                {
-                    utf8_offsets.push_back(offset);
-                    if (offset == pad_string.length())
-                        break;
-                    offset += UTF8::seqLength(pad_string[offset]);
-                    offset = std::min(offset, pad_string.length());
-                }
-            }
-
-            /// Not necessary, but good for performance.
-            /// We repeat `pad_string` multiple times until it's length becomes 16 or more.
-            /// It speeds up the function appendTo() because it allows to copy padding characters by portions of at least
-            /// 16 bytes instead of single bytes.
-            while (numCharsInPadString() < 16)
-            {
-                pad_string += pad_string;
-                if constexpr (is_utf8)
-                {
-                    size_t old_size = utf8_offsets.size();
-                    utf8_offsets.reserve((old_size - 1) * 2);
-                    size_t base = utf8_offsets.back();
-                    for (size_t i = 1; i != old_size; ++i)
-                        utf8_offsets.push_back(utf8_offsets[i] + base);
-                }
-            }
-        }
-
-        String pad_string;
+        /// Padded copy of the pad string (pun intended).
+        PaddedPODArray<UInt8> pad_string;

         /// Offsets of code points in `pad_string`:
         /// utf8_offsets[0] is the offset of the first code point in `pad_string`, it's always 0;
@@ -145,7 +145,10 @@ namespace
     {
     public:
         FunctionPadString(const char * name_, bool is_right_pad_, bool is_utf8_)
-            : function_name(name_), is_right_pad(is_right_pad_), is_utf8(is_utf8_) {}
+            : function_name(name_)
+            , is_right_pad(is_right_pad_)
+            , is_utf8(is_utf8_)
+        {}

         static FunctionPtr create(const char * name, bool is_right_pad, bool is_utf8)
         {
@@ -161,37 +164,17 @@ namespace

         bool useDefaultImplementationForConstants() const override { return false; }

-        DataTypePtr getReturnTypeImpl(const DataTypes & arguments) const override
+        DataTypePtr getReturnTypeImpl(const ColumnsWithTypeAndName & arguments) const override
         {
-            size_t number_of_arguments = arguments.size();
+            FunctionArgumentDescriptors mandatory_args{
+                {"string", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isStringOrFixedString), nullptr, "Array"},
+                {"length", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isInteger), nullptr, "const UInt*"},
+            };
+            FunctionArgumentDescriptors optional_args{
+                {"pad_string", static_cast<FunctionArgumentDescriptor::TypeValidator>(&isString), isColumnConst, "Array"}
+            };

-            if (number_of_arguments != 2 && number_of_arguments != 3)
-                throw Exception(
-                    ErrorCodes::NUMBER_OF_ARGUMENTS_DOESNT_MATCH,
-                    "Number of arguments for function {} doesn't match: passed {}, should be 2 or 3",
-                    getName(),
-                    number_of_arguments);
-
-            if (!isStringOrFixedString(arguments[0]))
-                throw Exception(
-                    ErrorCodes::ILLEGAL_TYPE_OF_ARGUMENT,
-                    "Illegal type {} of the first argument of function {}, should be string",
-                    arguments[0]->getName(),
-                    getName());
-
-            if (!isInteger(arguments[1]))
-                throw Exception(
-                    ErrorCodes::ILLEGAL_TYPE_OF_ARGUMENT,
-                    "Illegal type {} of the second argument of function {}, should be unsigned integer",
-                    arguments[1]->getName(),
-                    getName());
-
-            if (number_of_arguments == 3 && !isStringOrFixedString(arguments[2]))
-                throw Exception(
-                    ErrorCodes::ILLEGAL_TYPE_OF_ARGUMENT,
-                    "Illegal type {} of the third argument of function {}, should be const string",
-                    arguments[2]->getName(),
-                    getName());
+            validateFunctionArguments(*this, arguments, mandatory_args, optional_args);

             return std::make_shared<DataTypeString>();
         }
@@ -211,15 +194,11 @@ namespace
             {
                 auto column_pad = arguments[2].column;
                 const ColumnConst * column_pad_const = checkAndGetColumnConst<ColumnString>(column_pad.get());
-                if (!column_pad_const)
-                    throw Exception(
-                        ErrorCodes::ILLEGAL_COLUMN,
-                        "Illegal column {}, third argument of function {} must be a constant string",
-                        column_pad->getName(),
-                        getName());
-
+                chassert(column_pad_const);
                 pad_string = column_pad_const->getValue<String>();
             }
+            if (pad_string.empty())
+                pad_string = " ";

             auto col_res = ColumnString::create();
             StringSink res_sink{*col_res, input_rows_count};
@@ -235,7 +214,7 @@ namespace
             else
                 throw Exception(
                     ErrorCodes::ILLEGAL_COLUMN,
-                    "Illegal column {}, first argument of function {} must be a string",
+                    "Illegal column {}, first argument of function {} must be a String or FixedString",
                     arguments[0].column->getName(),
                     getName());

@@ -248,31 +227,40 @@ namespace
         {
             const auto & chars = strings.getElements();
             bool all_ascii = isAllASCII(reinterpret_cast<const UInt8 *>(pad_string.data()), pad_string.size())
-                && isAllASCII(chars.data(), chars.size());
+                                && isAllASCII(chars.data(), chars.size());
             bool is_actually_utf8 = is_utf8 && !all_ascii;

             if (!is_actually_utf8)
             {
                 PaddingChars<false> padding_chars{pad_string};
                 if (const auto * col_const = checkAndGetColumn<ColumnConst>(column_length.get()))
-                    executeForSourceAndLength<false>(
-                        std::forward<SourceStrings>(strings), ConstSource<GenericValueSource>{*col_const}, padding_chars, res_sink);
+                    executeForSourceAndLength<false>(std::forward<SourceStrings>(strings), ConstSource<GenericValueSource>{*col_const}, padding_chars, res_sink);
                 else
-                    executeForSourceAndLength<false>(
-                        std::forward<SourceStrings>(strings), GenericValueSource{*column_length}, padding_chars, res_sink);
+                    executeForSourceAndLength<false>(std::forward<SourceStrings>(strings), GenericValueSource{*column_length}, padding_chars, res_sink);
             }
             else
             {
                 PaddingChars<true> padding_chars{pad_string};
                 if (const auto * col_const = checkAndGetColumn<ColumnConst>(column_length.get()))
-                    executeForSourceAndLength<true>(
-                        std::forward<SourceStrings>(strings), ConstSource<GenericValueSource>{*col_const}, padding_chars, res_sink);
+                    executeForSourceAndLength<true>(std::forward<SourceStrings>(strings), ConstSource<GenericValueSource>{*col_const}, padding_chars, res_sink);
                 else
-                    executeForSourceAndLength<true>(
-                        std::forward<SourceStrings>(strings), GenericValueSource{*column_length}, padding_chars, res_sink);
+                    executeForSourceAndLength<true>(std::forward<SourceStrings>(strings), GenericValueSource{*column_length}, padding_chars, res_sink);
             }
         }

+        template <bool is_actually_utf8, typename SourceStrings, typename SourceLengths>
+        void executeForSourceAndLength(
+            SourceStrings && strings,
+            SourceLengths && lengths,
+            const PaddingChars<is_actually_utf8> & padding_chars,
+            StringSink & res_sink) const
+        {
+            if (is_right_pad)
+                executePad<true>(std::forward<SourceStrings>(strings), std::forward<SourceLengths>(lengths), padding_chars, res_sink);
+            else
+                executePad<false>(std::forward<SourceStrings>(strings), std::forward<SourceLengths>(lengths), padding_chars, res_sink);
+        }
+
         template <bool is_right_pad_, bool is_actually_utf8, typename SourceStrings, typename SourceLengths>
         static void executePad(
             SourceStrings && strings,
@@ -335,19 +323,6 @@ namespace
             }
         }

-        template <bool is_actually_utf8, typename SourceStrings, typename SourceLengths>
-        void executeForSourceAndLength(
-            SourceStrings && strings,
-            SourceLengths && lengths,
-            const PaddingChars<is_actually_utf8> & padding_chars,
-            StringSink & res_sink) const
-        {
-            if (is_right_pad)
-                executePad<true>(std::forward<SourceStrings>(strings), std::forward<SourceLengths>(lengths), padding_chars, res_sink);
-            else
-                executePad<false>(std::forward<SourceStrings>(strings), std::forward<SourceLengths>(lengths), padding_chars, res_sink);
-        }
-
         const char * const function_name;
         const bool is_right_pad;
         const bool is_utf8;
PATCH

echo "Patch applied successfully"
