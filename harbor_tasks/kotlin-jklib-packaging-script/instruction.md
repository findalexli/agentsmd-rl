# Add Packaging Script for JKLib Compiler

## Problem

The Kotlin compiler repository needs a packaging script to bundle the jklib compiler into a distributable format. Currently, there is no build configuration to produce the jklib-compiler distribution.

When the packaging script is absent:
- The `:compiler:cli-jklib` and `:compiler:ir.serialization.jklib` modules cannot be combined into a distributable JAR
- The build system cannot produce a properly configured JAR with the required manifest attributes (`Class-Path` pointing to `kotlin-compiler.jar kotlin-stdlib.jar kotlin-reflect.jar`, and `Main-Class` set to `org.jetbrains.kotlin.cli.jklib.K2JKlibCompiler`)
- The distribution directory structure (with `license/` and `lib/` subdirectories) cannot be created
- The module is not registered in the project's `settings.gradle`

## Requirements

Create a Gradle build script at `prepare/jklib-compiler/build.gradle.kts` and register the module in `settings.gradle`.

### Build Script Requirements

The build script must produce a JAR named `jklib-compiler.jar` that merges `:compiler:ir.serialization.jklib` and `:compiler:cli-jklib`. The following literal strings and values must appear in the script:

1. **Copyright Header**: Must contain both `Copyright 2010-2026 JetBrains` and `Apache 2.0 license`

2. **Description**: Must set a description containing the literal string `JKlib Classes packaging script`

3. **Plugin**: Must apply the `kotlin("jvm")` plugin

4. **Configurations**: Must create two configurations with the exact names `buildNumber` and `distContent`

5. **Dependencies**: Must declare dependencies on:
   - `:compiler:cli-jklib` (with `isTransitive = false`)
   - `:compiler:ir.serialization.jklib` (with `isTransitive = false`)
   - `:prepare:build.version` with configuration `buildVersion` (for the `buildNumber` configuration)

6. **JAR Task Requirements**:
   - Archive file name must be `jklib-compiler.jar`
   - Duplicates strategy must be `DuplicatesStrategy.EXCLUDE`
   - Must depend on the `distContent` configuration and include its contents
   - Manifest must include:
     - `Class-Path` attribute with value `kotlin-compiler.jar kotlin-stdlib.jar kotlin-reflect.jar`
     - `Main-Class` attribute with value `org.jetbrains.kotlin.cli.jklib.K2JKlibCompiler`

7. **Distribution Task Requirements**:
   - Must be a Sync-type task named `dist`
   - Destination directory must be `dist/jklib` relative to the root project
   - Duplicates strategy must be `DuplicatesStrategy.FAIL`
   - Must sync `buildNumber` configuration files to the root of the destination
   - Must sync files from the `license` directory (at root project level) into a `license/` subdirectory
   - Must sync the jar output into a `lib/` subdirectory with file permissions set to `rw-r--r--`

### Settings.gradle Registration

Add to `settings.gradle`:
- Include `":kotlin-jklib-compiler"` in the includes list
- Map `project(':kotlin-jklib-compiler').projectDir` to the `prepare/jklib-compiler` directory under the root project

## Verification

After making changes:
1. Verify `prepare/jklib-compiler/build.gradle.kts` exists
2. Run `./gradlew projects` to confirm the module is recognized
3. Run `./gradlew :kotlin-jklib-compiler:help` to verify the build script loads without errors
