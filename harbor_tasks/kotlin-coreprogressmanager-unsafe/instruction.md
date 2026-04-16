# IJ SDK: Eliminate sun.misc.Unsafe dependency from CoreProgressManager

## Problem

The file `compiler/cli/src/com/intellij/openapi/progress/impl/CoreProgressManager.java` in the Kotlin compiler CLI module transitively depends on `sun.misc.Unsafe` through IntelliJ platform utilities (`ConcurrentLongObjectMap` backed by `Java11Shim`). The `sun.misc.Unsafe` API is being phased out in modern JDK versions (see [JEP 471](https://openjdk.org/jeps/471)), so this dependency needs to be eliminated.

## Symptom

The file currently imports and uses `com.intellij.util.Java11Shim` and `com.intellij.util.containers.ConcurrentLongObjectMap`. These internal IntelliJ APIs rely on `sun.misc.Unsafe`, which is deprecated and will be removed in future JDK releases. Code that depends on these APIs will fail to compile or run on newer JDK versions.

## Constraints

The solution must:

1. **Use only public JDK APIs** — the replacement must not use any internal JDK classes like `sun.misc.Unsafe`
2. **Maintain thread-safe map semantics** — the two concurrent map fields (`currentIndicators` and `threadTopLevelIndicators`) must remain thread-safe and keyed by thread ID (Long keys)
3. **Preserve existing class structure** — the class declaration `public class CoreProgressManager extends ProgressManager implements Disposable`, the package declaration `package com.intellij.openapi.progress.impl;`, and the overall structure must remain intact
4. **Retain sufficient fields** — the file must retain at least 4 `private static final` fields
5. **Verify syntax** — the file must have balanced braces, parentheses, and brackets; no Java syntax errors
6. **Document the historical rationale** — the class-level documentation should explain why the code uses the patterns it does, referencing the deprecated API that was previously used

## What not to do

- Do not import or use `com.intellij.util.Java11Shim`
- Do not import or use `com.intellij.util.containers.ConcurrentLongObjectMap`
- Do not reference `sun.misc.Unsafe` in any executable code (comments are acceptable)

## Verification

After the fix, the code should compile on modern JDK versions without depending on `sun.misc.Unsafe`. The two concurrent map fields should be implementable using only `java.util.concurrent.*` types.