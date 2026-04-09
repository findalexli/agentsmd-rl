# Stop copying R8 output with AGP 9.1+

## Problem

The Compose compiler Gradle plugin's `MergeMappingFileTask` is incorrectly handling R8 output files when using Android Gradle Plugin (AGP) 9.1+. 

Starting with AGP 9.1, R8 output files are now correctly produced to the output folder. However, the current implementation always copies these files manually, which now causes issues because:
1. The files already exist in the correct location (thanks to AGP 9.1+)
2. The manual copying process was deleting the output directory before copying, which removes the correctly-placed files

## Task

Modify `libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/internal/ComposeAgpMappingFile.kt` to:

1. **Detect AGP version** - Check if the current AGP version is 9.1 or higher using `AndroidGradlePluginVersion`

2. **Conditional task registration** - Register different task types based on AGP version:
   - AGP 9.1+: Use a simpler `MergeMappingFileTask` that doesn't copy R8 outputs
   - AGP < 9.1: Use `MergeMappingFileTask.WithR8Outputs` (inner class) that copies R8 outputs manually

3. **Restructure `MergeMappingFileTask`**:
   - Rename `originalFile` property to `r8MappingFile`
   - Move the R8 output copying logic (including `deleteRecursively`, `outputDir`, `r8Outputs` FileCollection, and file copying) into a new inner class `WithR8Outputs`
   - The base `MergeMappingFileTask` should only handle merging the mapping files without copying
   - Make `taskAction()` method `open` so the inner class can override it

4. **Update task wiring** - Change the `wiredWithFiles` call to use `r8MappingFile` instead of `originalFile`

## Files to Modify

- `libraries/tools/kotlin-compose-compiler/src/common/kotlin/org/jetbrains/kotlin/compose/compiler/gradle/internal/ComposeAgpMappingFile.kt`

## Key Classes and Methods

- `Project.configureComposeMappingFile()` - Where task registration happens
- `MergeMappingFileTask` - The main task class that needs restructuring
- `MergeMappingFileTask.WithR8Outputs` - New inner class for backwards compatibility with older AGP

## Notes

- Use `@OptIn(InternalKotlinGradlePluginApi::class)` when accessing `AndroidGradlePluginVersion`
- The version check should be: `it.major >= 9 && it.minor >= 1`
- The fix is related to Google issue tracker: https://issuetracker.google.com/469745905
