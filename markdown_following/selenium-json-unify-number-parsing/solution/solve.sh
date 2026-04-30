#!/usr/bin/env bash
# Apply the gold patch from PR SeleniumHQ/selenium#17038. Idempotent: skips
# the apply if a distinctive marker from the patch is already present.
set -euo pipefail

cd /workspace/selenium

if grep -q "boolean mightBeDecimal" java/src/org/openqa/selenium/json/JsonInput.java 2>/dev/null; then
    echo "patch already applied"
    exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/java/src/org/openqa/selenium/json/InstantCoercer.java b/java/src/org/openqa/selenium/json/InstantCoercer.java
index d00364a41673d..3a63f75f36447 100644
--- a/java/src/org/openqa/selenium/json/InstantCoercer.java
+++ b/java/src/org/openqa/selenium/json/InstantCoercer.java
@@ -17,17 +17,22 @@

 package org.openqa.selenium.json;

+import java.io.StringReader;
 import java.lang.reflect.Type;
-import java.math.BigInteger;
 import java.time.Instant;
 import java.time.format.DateTimeFormatter;
 import java.time.format.DateTimeParseException;
 import java.time.temporal.TemporalAccessor;
 import java.util.function.BiFunction;
-import java.util.regex.Pattern;
+import org.openqa.selenium.internal.Require;

 public class InstantCoercer extends TypeCoercer<Instant> {
-  private static final Pattern DIGITS_ONLY = Pattern.compile("\\d+");
+
+  private final JsonTypeCoercer typeCoercer;
+
+  InstantCoercer(JsonTypeCoercer typeCoercer) {
+    this.typeCoercer = Require.nonNull("TypeCoercer", typeCoercer);
+  }

   @Override
   public boolean test(Class<?> aClass) {
@@ -39,28 +44,43 @@ public BiFunction<JsonInput, PropertySetting, Instant> apply(Type type) {
     return (jsonInput, setting) -> {
       JsonType token = jsonInput.peek();

-      if (JsonType.NUMBER.equals(token)) {
-        return Instant.ofEpochMilli(jsonInput.nextNumber().longValue());
-      } else if (JsonType.STRING.equals(token)) {
-        String raw = jsonInput.nextString();
-        if (DIGITS_ONLY.matcher(raw).matches()) {
+      switch (token) {
+        case NUMBER:
+          return Instant.ofEpochMilli(jsonInput.nextNumber().longValue());
+        case STRING:
+          String raw = jsonInput.nextString();
           try {
-            return Instant.ofEpochMilli(new BigInteger(raw).longValueExact());
-          } catch (NumberFormatException | ArithmeticException invalidLong) {
-            throw new JsonException(
-                String.format("\"%s\" is not a valid timestamp", raw), invalidLong);
+            TemporalAccessor parsed = DateTimeFormatter.ISO_INSTANT.parse(raw);
+            return Instant.from(parsed);
+          } catch (DateTimeParseException invalidDateTime) {
+            var failure =
+                new JsonException(
+                    String.format("\"%s\" does not look like an Instant", raw), invalidDateTime);
+
+            // any PropertySetting is okay here, as we know it won't be used
+            try (JsonInput nestedInput =
+                new JsonInput(new StringReader(raw), typeCoercer, PropertySetting.BY_NAME)) {
+              Number number = nestedInput.nextNumber();
+              // ensure the 'raw' string has been read to the end
+              nestedInput.nextEnd();
+              double doubleValue = number.doubleValue();
+              if (doubleValue % 1 != 0) {
+                throw new JsonException("unexpected decimal value");
+              } else if (doubleValue < Long.MIN_VALUE || doubleValue > Long.MAX_VALUE) {
+                throw new JsonException("value out of range");
+              }
+              return Instant.ofEpochMilli(number.longValue());
+            } catch (JsonException invalidLong) {
+              failure.addSuppressed(
+                  new JsonException(
+                      String.format("\"%s\" is not a valid timestamp", raw), invalidLong));
+            }
+
+            throw failure;
           }
-        }
-        try {
-          TemporalAccessor parsed = DateTimeFormatter.ISO_INSTANT.parse(raw);
-          return Instant.from(parsed);
-        } catch (DateTimeParseException invalidDateTime) {
-          throw new JsonException(
-              String.format("\"%s\" does not look like an Instant", raw), invalidDateTime);
-        }
+        default:
+          throw new JsonException("Unable to parse: " + token + " as Instant");
       }
-
-      throw new JsonException("Unable to parse: " + jsonInput.read(Object.class));
     };
   }
 }
diff --git a/java/src/org/openqa/selenium/json/JsonInput.java b/java/src/org/openqa/selenium/json/JsonInput.java
index e1a04f17a9b06..8ceb22329d6b8 100644
--- a/java/src/org/openqa/selenium/json/JsonInput.java
+++ b/java/src/org/openqa/selenium/json/JsonInput.java
@@ -220,7 +220,7 @@ public String nextName() {
    */
   public Number nextNumber() {
     expect(JsonType.NUMBER);
-    boolean decimal = false;
+    boolean mightBeDecimal = false;
     StringBuilder builder = new StringBuilder();
     // We know it's safe to use a do/while loop since the first character was a number
     boolean read = true;
@@ -243,7 +243,7 @@ public Number nextNumber() {
         case '.':
         case 'e':
         case 'E':
-          decimal = true;
+          mightBeDecimal = true;
           builder.append(input.read());
           break;
         default:
@@ -252,7 +252,11 @@ public Number nextNumber() {
     } while (read);

     try {
-      if (!decimal) {
+      // The JSON Schema does state the decimal point should not be used distinguish between
+      // integers and floating point values.
+      // Therefore, using a Long is only a fast path here, but we should not rely on the `double`
+      // value below is a real floating point.
+      if (!mightBeDecimal) {
         return Long.valueOf(builder.toString());
       }

@@ -277,15 +281,26 @@ public String nextString() {
   /**
    * Read the next element of the JSON input stream as an instant.
    *
+   * @deprecated Instant is not a basic JSON type, use the {@link InstantCoercer} instead.
    * @return {@link Instant} object
    * @throws JsonException if the next element isn't a {@code Long}
    * @throws UncheckedIOException if an I/O exception is encountered
    */
+  @Deprecated(forRemoval = true)
   public @Nullable Instant nextInstant() {
     Long time = read(Long.class);
     return (null != time) ? Instant.ofEpochSecond(time) : null;
   }

+  /**
+   * Read the next element of the JSON input stream and expect the end of the input.
+   *
+   * @throws JsonException if the next element isn't the end of the input
+   */
+  public void nextEnd() {
+    expect(JsonType.END);
+  }
+
   /**
    * Determine whether an element is pending for the current container from the JSON input stream.
    *
diff --git a/java/src/org/openqa/selenium/json/JsonTypeCoercer.java b/java/src/org/openqa/selenium/json/JsonTypeCoercer.java
index 249edb7e00b7a..a1cf5b8fcea40 100644
--- a/java/src/org/openqa/selenium/json/JsonTypeCoercer.java
+++ b/java/src/org/openqa/selenium/json/JsonTypeCoercer.java
@@ -71,28 +71,35 @@ private JsonTypeCoercer(Stream<TypeCoercer<?>> coercers) {
     // From java
     builder.add(new BooleanCoercer());

-    builder.add(new NumberCoercer<>(Byte.class, Number::byteValue));
-    builder.add(new NumberCoercer<>(Double.class, Number::doubleValue));
-    builder.add(new NumberCoercer<>(Float.class, Number::floatValue));
-    builder.add(new NumberCoercer<>(Integer.class, Number::intValue));
-    builder.add(new NumberCoercer<>(Long.class, Number::longValue));
+    builder.add(new NumberCoercer<>(this, Byte.class, Number::byteValue));
+    builder.add(new NumberCoercer<>(this, Double.class, Number::doubleValue));
+    builder.add(new NumberCoercer<>(this, Float.class, Number::floatValue));
+    builder.add(new NumberCoercer<>(this, Integer.class, Number::intValue));
+    builder.add(new NumberCoercer<>(this, Long.class, Number::longValue));
     builder.add(
         new NumberCoercer<>(
+            this,
             Number.class,
             num -> {
+              if (num instanceof Long) {
+                return num;
+              }
+
               double doubleValue = num.doubleValue();
-              if (doubleValue % 1 != 0 || doubleValue > Long.MAX_VALUE) {
+              if (doubleValue % 1 != 0
+                  || doubleValue < Long.MIN_VALUE
+                  || doubleValue > Long.MAX_VALUE) {
                 return doubleValue;
               }
               return num.longValue();
             }));
-    builder.add(new NumberCoercer<>(Short.class, Number::shortValue));
+    builder.add(new NumberCoercer<>(this, Short.class, Number::shortValue));
     builder.add(new StringCoercer());
     builder.add(new EnumCoercer<>());
     builder.add(new UriCoercer());
     builder.add(new UrlCoercer());
     builder.add(new UuidCoercer());
-    builder.add(new InstantCoercer());
+    builder.add(new InstantCoercer(this));

     // From Selenium
     builder.add(
diff --git a/java/src/org/openqa/selenium/json/MapCoercer.java b/java/src/org/openqa/selenium/json/MapCoercer.java
index c72c21b35c8b5..ad254741a5dbf 100644
--- a/java/src/org/openqa/selenium/json/MapCoercer.java
+++ b/java/src/org/openqa/selenium/json/MapCoercer.java
@@ -53,9 +53,9 @@ public BiFunction<JsonInput, PropertySetting, T> apply(Type type) {
     Type valueType;

     if (type instanceof ParameterizedType) {
-      ParameterizedType pt = (ParameterizedType) type;
-      keyType = pt.getActualTypeArguments()[0];
-      valueType = pt.getActualTypeArguments()[1];
+      Type[] typeArguments = ((ParameterizedType) type).getActualTypeArguments();
+      keyType = typeArguments[0];
+      valueType = typeArguments[1];
     } else if (type instanceof Class) {
       keyType = Object.class;
       valueType = Object.class;
diff --git a/java/src/org/openqa/selenium/json/NumberCoercer.java b/java/src/org/openqa/selenium/json/NumberCoercer.java
index 203bddd51bc05..748305dcad9c3 100644
--- a/java/src/org/openqa/selenium/json/NumberCoercer.java
+++ b/java/src/org/openqa/selenium/json/NumberCoercer.java
@@ -17,8 +17,8 @@

 package org.openqa.selenium.json;

+import java.io.StringReader;
 import java.lang.reflect.Type;
-import java.math.BigDecimal;
 import java.util.Map;
 import java.util.function.BiFunction;
 import java.util.function.Function;
@@ -39,10 +39,12 @@ class NumberCoercer<T extends Number> extends TypeCoercer<T> {
             Map.entry(short.class, Short.class));
   }

+  private final JsonTypeCoercer typeCoercer;
   private final Class<T> stereotype;
   private final Function<Number, T> mapper;

-  NumberCoercer(Class<T> stereotype, Function<Number, T> mapper) {
+  NumberCoercer(JsonTypeCoercer typeCoercer, Class<T> stereotype, Function<Number, T> mapper) {
+    this.typeCoercer = Require.nonNull("TypeCoercer", typeCoercer);
     this.stereotype = Require.nonNull("Stereotype", stereotype);
     this.mapper = Require.nonNull("Mapper", mapper);
   }
@@ -63,9 +65,13 @@ public BiFunction<JsonInput, PropertySetting, T> apply(Type ignored) {

         case STRING:
           String numberAsString = jsonInput.nextString();
-          try {
-            number = new BigDecimal(numberAsString);
-          } catch (NumberFormatException e) {
+          // any PropertySetting is okay here, as we know it won't be used
+          try (JsonInput nestedInput =
+              new JsonInput(new StringReader(numberAsString), typeCoercer, setting)) {
+            number = nestedInput.nextNumber();
+            // ensure the 'numberAsString' string has been read to the end
+            nestedInput.nextEnd();
+          } catch (JsonException e) {
             throw new JsonException(
                 String.format("Not a numeric value: \"%s\"", numberAsString), e);
           }
diff --git a/java/src/org/openqa/selenium/json/ObjectCoercer.java b/java/src/org/openqa/selenium/json/ObjectCoercer.java
index aeeea743a6ea2..65980294197c0 100644
--- a/java/src/org/openqa/selenium/json/ObjectCoercer.java
+++ b/java/src/org/openqa/selenium/json/ObjectCoercer.java
@@ -19,7 +19,6 @@

 import java.lang.reflect.Type;
 import java.util.List;
-import java.util.Map;
 import java.util.function.BiFunction;
 import org.openqa.selenium.internal.Require;

@@ -60,7 +59,7 @@ public BiFunction<JsonInput, PropertySetting, Object> apply(Type type) {
           break;

         case START_MAP:
-          target = Map.class;
+          target = Json.MAP_TYPE;
           break;

         default:
PATCH

echo "patch applied"
