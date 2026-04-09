# Fix Typo in Package Name

There is a typo in the Kotlin repository's package structure. The package name contains "relfection" when it should be "reflection".

## The Problem

The package `org.jetbrains.kotlin.analysis.utils.relfection` is misspelled. It should be `org.jetbrains.kotlin.analysis.utils.reflection`.

## Files Involved

1. **`analysis/analysis-internal-utils/src/org/jetbrains/kotlin/analysis/utils/relfection/toStringDataClassLike.kt`**
   - This file needs to be moved to the correctly named `reflection` directory
   - The package declaration inside needs to be updated

2. **`analysis/analysis-api/src/org/jetbrains/kotlin/analysis/api/symbols/pointers/KaSymbolPointer.kt`**
   - This file imports from the misspelled package and needs its import statement fixed

## What You Need To Do

1. Rename the directory from `relfection` to `reflection`
2. Update the package declaration in `toStringDataClassLike.kt`
3. Update the import statement in `KaSymbolPointer.kt`
4. Ensure the code compiles after the changes

## Hints

- This is a simple typo fix, but it affects multiple files
- The package declaration and import statements must be consistent
- Make sure to also update the copyright year to 2026 when you update the file
- You can use git to track the rename properly

## Expected Behavior

After the fix:
- The directory should be named `reflection`, not `relfection`
- All imports should reference `org.jetbrains.kotlin.analysis.utils.reflection`
- The Kotlin code should compile successfully
- No occurrences of "relfection" should remain in the codebase
