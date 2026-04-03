#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'Automatic Link Extraction' lib/features/ai/README.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/lib/features/ai/README.md b/lib/features/ai/README.md
index dd95a7a9e0..e922ee2dea 100644
--- a/lib/features/ai/README.md
+++ b/lib/features/ai/README.md
@@ -442,6 +442,7 @@ For task summaries, the response is treated as markdown text:
 - No JSON parsing (unlike action item suggestions)
 - The complete response is saved as an `AiResponseEntry`
 - Post-processing includes automatic title extraction (see below)
+- Automatic link extraction appends a Links section (see below)
 - Displayed using `GptMarkdown` widget for proper formatting

 ### 4. Automatic Title Extraction
@@ -454,7 +455,28 @@ When generating task summaries, the system automatically extracts suggested titl
 - The extracted title updates the task entity in the database
 - When displaying summaries, the H1 title is filtered out to avoid redundancy

-### 5. Direct Task Summary Refresh with Countdown UX
+### 5. Automatic Link Extraction
+
+Task summaries include AI-driven link extraction that aggregates URLs found within the task's entries:
+
+- **Scanning**: AI is instructed to scan log entries for URLs (http://, https://, or other valid URL schemes)
+- **Unique URLs**: AI extracts every unique URL found across all entries
+- **Succinct Titles**: AI generates short, descriptive titles (2-5 words) for each link
+- **Markdown Format**: Links are formatted as `[Succinct Title](URL)` for clickable rendering
+- **Conditional Display**: Links section should be omitted if no URLs are found
+
+Example output in summaries:
+```markdown
+## Links
+- [Flutter Documentation](https://docs.flutter.dev)
+- [Linear: APP-123](https://linear.app/team/issue/APP-123)
+- [Lotti PR #456](https://github.com/matthiasn/lotti/pull/456)
+- [GitHub Issue #789](https://github.com/user/repo/issues/789)
+```
+
+**Note**: This is prompt-driven behavior relying on AI compliance. Results are best-effort and may vary by model.
+
+### 6. Direct Task Summary Refresh with Countdown UX

 The system includes a scheduled refresh mechanism that updates task summaries when checklist items are modified. Instead of triggering immediately, refreshes are scheduled with a 5-minute delay, giving users control over when summaries are generated. For a user-focused description of this feature, see the [Tasks Feature README - Automatic Task Summary Updates](../tasks/README.md#automatic-task-summary-updates).

diff --git a/lib/features/ai/ui/ai_response_summary.dart b/lib/features/ai/ui/ai_response_summary.dart
index 6fac68e8d0..011bb7d2a7 100644
--- a/lib/features/ai/ui/ai_response_summary.dart
+++ b/lib/features/ai/ui/ai_response_summary.dart
@@ -7,6 +7,7 @@ import 'package:lotti/features/ai/ui/expandable_ai_response_summary.dart';
 import 'package:lotti/features/ai/ui/generated_prompt_card.dart';
 import 'package:lotti/widgets/cards/index.dart';
 import 'package:lotti/widgets/modal/modal_utils.dart';
+import 'package:url_launcher/url_launcher.dart';

 class AiResponseSummary extends StatelessWidget {
   const AiResponseSummary(
@@ -20,6 +21,13 @@ class AiResponseSummary extends StatelessWidget {
   final String? linkedFromId;
   final bool fadeOut;

+  static Future<void> _handleLinkTap(String url, String title) async {
+    final uri = Uri.tryParse(url);
+    if (uri != null) {
+      await launchUrl(uri, mode: LaunchMode.externalApplication);
+    }
+  }
+
   @override
   Widget build(BuildContext context) {
     // Use expandable summary for task summaries
@@ -40,7 +48,10 @@ class AiResponseSummary extends StatelessWidget {

     // For other response types, use the original implementation
     final content = SelectionArea(
-      child: GptMarkdown(aiResponse.data.response),
+      child: GptMarkdown(
+        aiResponse.data.response,
+        onLinkTap: _handleLinkTap,
+      ),
     );

     return ModernBaseCard(
diff --git a/lib/features/ai/ui/ai_response_summary_modal.dart b/lib/features/ai/ui/ai_response_summary_modal.dart
index 6a02df9a12..4b8719cab6 100644
--- a/lib/features/ai/ui/ai_response_summary_modal.dart
+++ b/lib/features/ai/ui/ai_response_summary_modal.dart
@@ -2,6 +2,7 @@ import 'package:flutter/material.dart';
 import 'package:gpt_markdown/gpt_markdown.dart';
 import 'package:lotti/classes/journal_entities.dart';
 import 'package:super_clipboard/super_clipboard.dart';
+import 'package:url_launcher/url_launcher.dart';

 class AiResponseSummaryModalContent extends StatelessWidget {
   const AiResponseSummaryModalContent(
@@ -13,6 +14,13 @@ class AiResponseSummaryModalContent extends StatelessWidget {
   final AiResponseEntry aiResponse;
   final String? linkedFromId;

+  static Future<void> _handleLinkTap(String url, String title) async {
+    final uri = Uri.tryParse(url);
+    if (uri != null) {
+      await launchUrl(uri, mode: LaunchMode.externalApplication);
+    }
+  }
+
   Widget _buildInfoRow(
     String label,
     String value, {
@@ -222,7 +230,10 @@ class AiResponseSummaryModalContent extends StatelessWidget {
                 child: Padding(
                   padding: padding,
                   child: SelectionArea(
-                    child: GptMarkdown(aiResponse.data.response),
+                    child: GptMarkdown(
+                      aiResponse.data.response,
+                      onLinkTap: _handleLinkTap,
+                    ),
                   ),
                 ),
               ),
diff --git a/lib/features/ai/ui/expandable_ai_response_summary.dart b/lib/features/ai/ui/expandable_ai_response_summary.dart
index 1984ae8482..cdf5a78fc3 100644
--- a/lib/features/ai/ui/expandable_ai_response_summary.dart
+++ b/lib/features/ai/ui/expandable_ai_response_summary.dart
@@ -6,6 +6,7 @@ import 'package:lotti/features/ai/ui/ai_response_summary_modal.dart';
 import 'package:lotti/themes/theme.dart';
 import 'package:lotti/widgets/cards/index.dart';
 import 'package:lotti/widgets/modal/modal_utils.dart';
+import 'package:url_launcher/url_launcher.dart';

 class ExpandableAiResponseSummary extends StatefulWidget {
   const ExpandableAiResponseSummary(
@@ -116,6 +117,35 @@ class _ExpandableAiResponseSummaryState
     });
   }

+  Future<void> _handleLinkTap(String url, String title) async {
+    final uri = Uri.tryParse(url);
+    if (uri != null) {
+      await launchUrl(uri, mode: LaunchMode.externalApplication);
+    }
+  }
+
+  Widget _buildLink(
+    BuildContext context,
+    InlineSpan text,
+    String url,
+    TextStyle style,
+  ) {
+    final linkColor = Theme.of(context).colorScheme.primary;
+    return GestureDetector(
+      onTap: () => _handleLinkTap(url, ''),
+      child: Text.rich(
+        TextSpan(
+          children: [text],
+          style: style.copyWith(
+            color: linkColor,
+            decoration: TextDecoration.underline,
+            decorationColor: linkColor,
+          ),
+        ),
+      ),
+    );
+  }
+
   @override
   Widget build(BuildContext context) {
     return ModernBaseCard(
@@ -141,7 +171,11 @@ class _ExpandableAiResponseSummaryState
                 children: [
                   // TLDR content (always visible)
                   SelectionArea(
-                    child: GptMarkdown(_tldrContent ?? ''),
+                    child: GptMarkdown(
+                      _tldrContent ?? '',
+                      onLinkTap: _handleLinkTap,
+                      linkBuilder: _buildLink,
+                    ),
                   ),
                   // Accordion-style expanding content
                   if (_additionalContent != null &&
@@ -155,7 +189,7 @@ class _ExpandableAiResponseSummaryState
                         }
                         return ClipRect(
                           child: Align(
-                            alignment: Alignment.topCenter,
+                            alignment: Alignment.topLeft,
                             heightFactor: _expandAnimation.value,
                             child: child,
                           ),
@@ -166,7 +200,11 @@ class _ExpandableAiResponseSummaryState
                         children: [
                           const SizedBox(height: 16),
                           SelectionArea(
-                            child: GptMarkdown(_additionalContent!),
+                            child: GptMarkdown(
+                              _additionalContent!,
+                              onLinkTap: _handleLinkTap,
+                              linkBuilder: _buildLink,
+                            ),
                           ),
                         ],
                       ),
diff --git a/lib/features/ai/util/preconfigured_prompts.dart b/lib/features/ai/util/preconfigured_prompts.dart
index e8b9072686..da03eb8156 100644
--- a/lib/features/ai/util/preconfigured_prompts.dart
+++ b/lib/features/ai/util/preconfigured_prompts.dart
@@ -101,26 +101,41 @@ After the TLDR, provide the detailed summary with:
 - Any annoyances or blockers (use 🤯 emoji)

 Keep the detailed summary succinct while maintaining good structure and organization.
-If the task is done, end with a concluding statement.
+If the task is done, include a brief concluding statement before the Links section.

 Example:
-Achieved results:
+**Achieved results:**
 ✅ Completed step 1
 ✅ Completed step 2
 ✅ Completed step 3

-Remaining steps:
+**Remaining steps:**
 1. Step 1
 2. Step 2
 3. Step 3

-Learnings:
+**Learnings:**
 💡 Learned something interesting
 💡 Learned something else

-Annoyances:
+**Annoyances:**
 🤯 Annoyed by something

+Finally, at the very end of your response, include a **Links** section:
+- Scan ALL log entries in the task for URLs (http://, https://, or other valid URL schemes)
+- Extract every unique URL found across all entries
+- For each link, generate a short, succinct title (2-5 words) that describes what the link is about
+- Format each link as Markdown: `[Succinct Title](URL)`
+- If no links are found, omit the Links section entirely
+
+Example Links section (these are format examples only - never copy these URLs, only use actual URLs found in the task):
+**Links:**
+- [Flutter Documentation](https://docs.flutter.dev)
+- [Linear: APP-123](https://linear.app/team/issue/APP-123)
+- [Lotti PR #456](https://github.com/matthiasn/lotti/pull/456)
+- [GitHub Issue #789](https://github.com/user/repo/issues/789)
+- [Stack Overflow Solution](https://stackoverflow.com/questions/12345)
+
 **Task Details:**
 ```json
 {{task}}
diff --git a/lib/themes/theme.dart b/lib/themes/theme.dart
index 8e3bdd2030..6cfbd24e0c 100644
--- a/lib/themes/theme.dart
+++ b/lib/themes/theme.dart
@@ -594,6 +594,7 @@ ThemeData withOverrides(ThemeData themeData) {
         ),
         GptMarkdownThemeData(
           brightness: themeData.brightness,
+          linkColor: themeData.colorScheme.primary,
           h1: themeData.textTheme.titleLarge?.copyWith(
             fontSize: fontSizeMediumLarge,
             fontWeight: FontWeight.w600,

PATCH

echo "Patch applied successfully."
