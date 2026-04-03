#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'ENTRY-SCOPED DIRECTIVES (PER ENTRY)' lib/features/ai/util/preconfigured_prompts.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/lib/features/ai/README.md b/lib/features/ai/README.md
index 0a64369ac2..d782f6c658 100644
--- a/lib/features/ai/README.md
+++ b/lib/features/ai/README.md
@@ -578,6 +578,16 @@ AI can automatically create new checklist items based on content analysis:
 - **Batch Processing**: Uses conversation-based approach for efficient handling
 - **Error Recovery**: Automatic retry with corrected format on failures

+#### Per-Entry Directive Behavior (Checklist Updates)
+
+When running Checklist Updates, the user's request is provided as a list of entries. Directives are scoped per entry:
+
+- Ignore for checklist: If an entry contains phrases like "Don't consider this for checklist items" or "Ignore for checklist", that entry is ignored for item extraction.
+- Plan-only single item: If an entry contains phrases like "The rest is an implementation plan" or "Single checklist item for this plan", that entire entry collapses to at most one created item. If the entry specifies "Single checklist item: <title>", that exact title is used; otherwise a generic "Draft implementation plan" is created (in the request's language).
+- Isolation: Do not blend directives across entries; each entry is evaluated independently.
+
+This keeps long implementation plans from exploding into many items while allowing adjacent entries to produce normal actionable items.
+
 ### Language Detection

 Automatic language detection for multilingual support:
diff --git a/lib/features/ai/util/preconfigured_prompts.dart b/lib/features/ai/util/preconfigured_prompts.dart
index 7faca11f4a..88966c5f6c 100644
--- a/lib/features/ai/util/preconfigured_prompts.dart
+++ b/lib/features/ai/util/preconfigured_prompts.dart
@@ -174,6 +174,15 @@ IMPORTANT RULES:
 - If you receive an unknown function name error, use only the functions listed above
 - Do NOT use suggest_checklist_completion for creating new items

+ENTRY-SCOPED DIRECTIVES (PER ENTRY):
+The user's request is composed of multiple entries; treat each entry independently. Each entry is the unit of scope.
+Before extracting items from an entry, first check for directive phrases (case-insensitive):
+- Ignore for checklist: "Don't consider this for checklist items", "Ignore for checklist", "No checklist extraction here" → ignore that entry for item extraction entirely.
+- Plan-only single item: "The rest is an implementation plan", "Treat as plan only", "Single checklist item for this plan" → for this entry, create at most ONE new checklist item (regardless of its internal length or bullets).
+  - If the user provides an explicit title via "Single checklist item: <title>", use that exact title.
+  - Otherwise, create a single generic item such as "Draft implementation plan" (use the request's language).
+Do NOT blend directives across entries. If no directives are present on an entry, follow normal extraction rules for that entry.
+
 Tools for checklist updates:
 1. add_multiple_checklist_items: Create one or more items at once (array of objects with title, optional isChecked)
 2. suggest_checklist_completion: Suggest marking items as done when evidence exists
@@ -224,6 +233,11 @@ Available Labels (id and name):
 {{labels}}
 ```

+Directive reminder:
+- Scope directives to the entry they appear in (entries are provided separately).
+- If the request says things like "Don't consider this for checklist items" or "Ignore for checklist", skip that text for extraction.
+- If it says "The rest is an implementation plan" or "Single checklist item for this plan", produce at most one item (use explicit title if given).
+
 REMEMBER:
 - Count the items first: if 2 or more, use add_multiple_checklist_items
 - Create items in the language used in the request

PATCH

echo "Patch applied successfully."
