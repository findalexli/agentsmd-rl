#!/bin/bash
set -e

cd /workspace/selenium

# Idempotency check - skip if already applied
if grep -q "class FieldWriter implements BiConsumer" java/src/org/openqa/selenium/json/InstanceCoercer.java 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/java/src/org/openqa/selenium/json/InstanceCoercer.java b/java/src/org/openqa/selenium/json/InstanceCoercer.java
index 87aa260e81ac2..04c18aa6e4563 100644
--- a/java/src/org/openqa/selenium/json/InstanceCoercer.java
+++ b/java/src/org/openqa/selenium/json/InstanceCoercer.java
@@ -17,6 +17,8 @@

 package org.openqa.selenium.json;

+import static java.util.stream.Collectors.toMap;
+
 import java.lang.reflect.Constructor;
 import java.lang.reflect.Field;
 import java.lang.reflect.Method;
@@ -28,7 +30,7 @@
 import java.util.Map;
 import java.util.function.BiConsumer;
 import java.util.function.BiFunction;
-import java.util.stream.Collectors;
+import java.util.function.Function;
 import java.util.stream.Stream;
 import org.openqa.selenium.internal.Require;

@@ -109,54 +111,33 @@ private Map<String, TypeAndWriter> getFieldWriters(Constructor<?> constructor) {
         .filter(field -> !Modifier.isStatic(field.getModifiers()))
         .peek(field -> field.setAccessible(true))
         .collect(
-            Collectors.toMap(
+            toMap(
                 Field::getName,
-                field -> {
-                  Type type = field.getGenericType();
-                  BiConsumer<Object, Object> writer =
-                      (instance, value) -> {
-                        try {
-                          field.set(instance, value);
-                        } catch (IllegalAccessException e) {
-                          throw new JsonException(
-                              String.format(
-                                  "Cannot set %s.%s = %s",
-                                  instance.getClass().getName(), field.getName(), value),
-                              e);
-                        }
-                      };
-                  return new TypeAndWriter(type, writer);
-                },
+                new FieldTypeAndWriter(),
                 (existing, replacement) -> {
                   throw new JsonException(
-                      "Duplicate JSON field name detected while collecting field writers");
+                      String.format(
+                          "Duplicate JSON field name detected while "
+                              + "collecting field writers: %s vs %s",
+                          existing, replacement));
                 }));
   }

   private Map<String, TypeAndWriter> getBeanWriters(Constructor<?> constructor) {
-    return Stream.of(
-            SimplePropertyDescriptor.getPropertyDescriptors(constructor.getDeclaringClass()))
+    SimplePropertyDescriptor[] propertyDescriptors =
+        SimplePropertyDescriptor.getPropertyDescriptors(constructor.getDeclaringClass());
+    return Stream.of(propertyDescriptors)
         .filter(desc -> desc.getWriteMethod() != null)
         .collect(
-            Collectors.toMap(
+            toMap(
                 SimplePropertyDescriptor::getName,
-                desc -> {
-                  Method method = desc.getWriteMethod();
-                  Type type = method.getGenericParameterTypes()[0];
-                  BiConsumer<Object, Object> writer =
-                      (instance, value) -> {
-                        method.setAccessible(true);
-                        try {
-                          method.invoke(instance, value);
-                        } catch (ReflectiveOperationException e) {
-                          throw new JsonException(
-                              String.format(
-                                  "Cannot call method %s.%s(%s)",
-                                  instance.getClass().getName(), method.getName(), value),
-                              e);
-                        }
-                      };
-                  return new TypeAndWriter(type, writer);
+                new SimplePropertyTypeAndWriter(),
+                (existing, replacement) -> {
+                  throw new JsonException(
+                      String.format(
+                          "Duplicate JSON field name detected while "
+                              + "collecting field writers: %s vs %s",
+                          existing, replacement));
                 }));
   }

@@ -189,9 +170,88 @@ private static class TypeAndWriter {
     private final Type type;
     private final BiConsumer<Object, Object> writer;

-    public TypeAndWriter(Type type, BiConsumer<Object, Object> writer) {
+    TypeAndWriter(Type type, BiConsumer<Object, Object> writer) {
       this.type = type;
       this.writer = writer;
     }
+
+    @Override
+    public String toString() {
+      return writer.toString();
+    }
+  }
+
+  private static class FieldTypeAndWriter implements Function<Field, TypeAndWriter> {
+    @Override
+    public TypeAndWriter apply(Field field) {
+      Type type = field.getGenericType();
+      return new TypeAndWriter(type, new FieldWriter(field));
+    }
+  }
+
+  private static class FieldWriter implements BiConsumer<Object, Object> {
+    private final Field field;
+
+    FieldWriter(Field field) {
+      this.field = field;
+    }
+
+    @Override
+    public void accept(Object instance, Object value) {
+      try {
+        field.set(instance, value);
+      } catch (IllegalAccessException e) {
+        throw new JsonException(
+            String.format(
+                "Cannot set %s.%s = %s", instance.getClass().getName(), field.getName(), value),
+            e);
+      }
+    }
+
+    @Override
+    public String toString() {
+      return String.format(
+          "%s(%s.%s)",
+          getClass().getSimpleName(), field.getDeclaringClass().getName(), field.getName());
+    }
+  }
+
+  private static class SimplePropertyTypeAndWriter
+      implements Function<SimplePropertyDescriptor, TypeAndWriter> {
+    @Override
+    public TypeAndWriter apply(SimplePropertyDescriptor desc) {
+      Method method = desc.getWriteMethod();
+      Type type = method.getGenericParameterTypes()[0];
+      return new TypeAndWriter(type, new SimplePropertyWriter(desc, method));
+    }
+  }
+
+  private static class SimplePropertyWriter implements BiConsumer<Object, Object> {
+    private final SimplePropertyDescriptor desc;
+    private final Method method;
+
+    SimplePropertyWriter(SimplePropertyDescriptor desc, Method method) {
+      this.desc = desc;
+      this.method = method;
+    }
+
+    @Override
+    public void accept(Object instance, Object value) {
+      method.setAccessible(true);
+      try {
+        method.invoke(instance, value);
+      } catch (ReflectiveOperationException e) {
+        throw new JsonException(
+            String.format(
+                "Cannot call method %s.%s(%s)",
+                instance.getClass().getName(), method.getName(), value),
+            e);
+      }
+    }
+
+    @Override
+    public String toString() {
+      return String.format("%s(%s)", getClass().getSimpleName(), desc);
+    }
   }
 }
diff --git a/java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java b/java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java
index 84aff4f324c09..301e33eed8742 100644
--- a/java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java
+++ b/java/src/org/openqa/selenium/json/SimplePropertyDescriptor.java
@@ -26,25 +26,18 @@

 public class SimplePropertyDescriptor {

-  private static final Function<Object, @Nullable Object> GET_CLASS_NAME =
-      obj -> {
-        if (obj == null) {
-          return null;
-        }
-
-        if (obj instanceof Class) {
-          return ((Class<?>) obj).getName();
-        }
-
-        return obj.getClass().getName();
-      };
-
+  private static final Function<Object, @Nullable Object> GET_CLASS_NAME = new GetClassName();
+  private final Class<?> clazz;
   private final String name;
   private final @Nullable Function<Object, @Nullable Object> read;
   private final @Nullable Method write;

   public SimplePropertyDescriptor(
-      String name, @Nullable Function<Object, @Nullable Object> read, @Nullable Method write) {
+      Class<?> clazz,
+      String name,
+      @Nullable Function<Object, @Nullable Object> read,
+      @Nullable Method write) {
+    this.clazz = clazz;
     this.name = name;
     this.read = read;
     this.write = write;
@@ -62,10 +55,15 @@ public String getName() {
     return write;
   }

+  @Override
+  public String toString() {
+    return String.format("%s.%s", clazz.getSimpleName(), name);
+  }
+
   public static SimplePropertyDescriptor[] getPropertyDescriptors(Class<?> clazz) {
     Map<String, SimplePropertyDescriptor> properties = new HashMap<>();

-    properties.put("class", new SimplePropertyDescriptor("class", GET_CLASS_NAME, null));
+    properties.put("class", new SimplePropertyDescriptor(clazz, "class", GET_CLASS_NAME, null));

     for (Method m : clazz.getMethods()) {
       if (Class.class.equals(m.getDeclaringClass()) || Object.class.equals(m.getDeclaringClass())) {
@@ -114,11 +112,12 @@ public static SimplePropertyDescriptor[] getPropertyDescriptors(Class<?> clazz)
       if (propertyName != null && (readMethod != null || writeMethod != null)) {
         SimplePropertyDescriptor descriptor =
             properties.getOrDefault(
-                propertyName, new SimplePropertyDescriptor(propertyName, null, null));
+                propertyName, new SimplePropertyDescriptor(clazz, propertyName, null, null));

         properties.put(
             propertyName,
             new SimplePropertyDescriptor(
+                clazz,
                 propertyName,
                 read != null ? read : descriptor.getReadMethod(),
                 writeMethod != null ? writeMethod : descriptor.getWriteMethod()));
@@ -144,4 +143,19 @@ private static boolean hasPrefix(String prefix, String methodName) {

     return Character.isUpperCase(methodName.charAt(prefix.length()));
   }
+
+  private static class GetClassName implements Function<Object, @Nullable Object> {
+    @Override
+    public @Nullable Object apply(Object obj) {
+      if (obj == null) {
+        return null;
+      }
+
+      if (obj instanceof Class) {
+        return ((Class<?>) obj).getName();
+      }
+
+      return obj.getClass().getName();
+    }
+  }
 }
PATCH

echo "Patch applied successfully."
