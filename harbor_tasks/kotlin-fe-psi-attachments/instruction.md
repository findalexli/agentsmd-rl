# Task: Improve Error Diagnostics with PSI Attachments

## Problem

The `checkPsiTypeConsistency()` function in the Kotlin compiler frontend currently uses a basic `require()` call when checking PSI type consistency. When this check fails, it provides only a simple error message without any contextual information about the PSI elements involved, making debugging difficult.

## Goal

Enhance the error handling in `checkPsiTypeConsistency()` to include rich PSI attachments when the consistency check fails. This will help developers debug issues by providing additional context about the PSI elements and the containing file.

## Location

File: `compiler/frontend.common/src/org/jetbrains/kotlin/diagnostics/KtDiagnostic.kt`

Function: `KtPsiDiagnostic.checkPsiTypeConsistency()`

## What You Need to Do

1. Import the necessary exception utilities from `org.jetbrains.kotlin.utils.exceptions`
2. Replace the current `require()` call with `requireWithAttachment()` which allows attaching additional context
3. Add PSI entries to the attachment for:
   - The PSI element being checked (labeled "psi")
   - The containing PSI file (labeled "file")
4. Preserve the original error message content

## Key APIs

The `requireWithAttachment()` function allows you to provide a lazy message lambda and a configuration block for attachments. The `withPsiEntry()` function can be used within the attachment block to add PSI element information.

## Expected Outcome

When the PSI type consistency check fails, the resulting exception should include detailed attachments showing:
- The PSI element that failed the type check
- The containing file for context

The error message should still indicate that the PSI element's class is not a subtype of the expected type for the diagnostic factory.
