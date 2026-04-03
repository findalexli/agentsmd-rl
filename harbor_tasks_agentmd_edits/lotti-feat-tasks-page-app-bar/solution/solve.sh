#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'filter_alt_outlined' lib/features/tasks/ui/filtering/task_label_quick_filter.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/lib/features/journal/ui/pages/infinite_journal_page.dart b/lib/features/journal/ui/pages/infinite_journal_page.dart
index 3bc7db2ed5..461cdb64e4 100644
--- a/lib/features/journal/ui/pages/infinite_journal_page.dart
+++ b/lib/features/journal/ui/pages/infinite_journal_page.dart
@@ -7,6 +7,7 @@ import 'package:lotti/classes/journal_entities.dart';
 import 'package:lotti/features/journal/ui/widgets/create/create_entry_action_button.dart';
 import 'package:lotti/features/journal/ui/widgets/list_cards/card_wrapper_widget.dart';
 import 'package:lotti/features/settings/ui/pages/definitions_list_page.dart';
+import 'package:lotti/features/tasks/ui/filtering/task_label_quick_filter.dart';
 import 'package:lotti/features/user_activity/state/user_activity_service.dart';
 import 'package:lotti/get_it.dart';
 import 'package:lotti/l10n/app_localizations_context.dart';
@@ -100,6 +101,31 @@ class _InfiniteJournalPageBodyState extends State<InfiniteJournalPageBody> {
               controller: _scrollController,
               slivers: <Widget>[
                 const JournalSliverAppBar(),
+                // Quick filter section below the header with content-aligned padding
+                if (snapshot.showTasks && snapshot.selectedLabelIds.isNotEmpty)
+                  SliverToBoxAdapter(
+                    child: Padding(
+                      padding: const EdgeInsets.fromLTRB(40, 8, 40, 8),
+                      child: AnimatedSize(
+                        duration: const Duration(milliseconds: 180),
+                        curve: Curves.easeInOut,
+                        alignment: Alignment.topCenter,
+                        child: Container(
+                          decoration: BoxDecoration(
+                            color: Theme.of(context)
+                                .colorScheme
+                                .surfaceContainerHigh,
+                            borderRadius: BorderRadius.circular(10),
+                          ),
+                          padding: const EdgeInsets.symmetric(
+                            horizontal: 12,
+                            vertical: 6,
+                          ),
+                          child: const TaskLabelQuickFilter(),
+                        ),
+                      ),
+                    ),
+                  ),
                 if (snapshot.pagingController != null)
                   PagingListener<int, JournalEntity>(
                     controller: snapshot.pagingController!,
diff --git a/lib/widgets/app_bar/journal_sliver_appbar.dart b/lib/widgets/app_bar/journal_sliver_appbar.dart
index 0ed4720abc..b029b67f88 100644
--- a/lib/widgets/app_bar/journal_sliver_appbar.dart
+++ b/lib/widgets/app_bar/journal_sliver_appbar.dart
@@ -5,7 +5,6 @@ import 'package:lotti/blocs/journal/journal_page_state.dart';
 import 'package:lotti/features/ai_chat/ui/widgets/ai_chat_icon.dart';
 import 'package:lotti/features/tasks/ui/filtering/task_category_filter.dart';
 import 'package:lotti/features/tasks/ui/filtering/task_filter_icon.dart';
-import 'package:lotti/features/tasks/ui/filtering/task_label_quick_filter.dart';
 import 'package:lotti/l10n/app_localizations_context.dart';
 import 'package:lotti/themes/theme.dart';
 import 'package:lotti/widgets/modal/modal_utils.dart';
@@ -36,7 +35,7 @@ class JournalSliverAppBar extends StatelessWidget {
                   Flexible(
                     child: SearchWidget(
                       margin: const EdgeInsets.symmetric(
-                        vertical: 20,
+                        vertical: 12,
                         horizontal: 40,
                       ),
                       onChanged: cubit.setSearchString,
@@ -49,7 +48,8 @@ class JournalSliverAppBar extends StatelessWidget {
                     const JournalFilterIcon(),
                 ],
               ),
-              if (showTasks) const TaskLabelQuickFilter(),
+              // Moved TaskLabelQuickFilter out of the AppBar into its own sliver
+              // below the header to avoid clipping when chips wrap.
             ],
           ),
         );
diff --git a/lib/features/tasks/ui/filtering/task_label_quick_filter.dart b/lib/features/tasks/ui/filtering/task_label_quick_filter.dart
index 1fda5b42a5..9b6f03ff38 100644
--- a/lib/features/tasks/ui/filtering/task_label_quick_filter.dart
+++ b/lib/features/tasks/ui/filtering/task_label_quick_filter.dart
@@ -49,32 +49,45 @@ class TaskLabelQuickFilter extends StatelessWidget {
           );
         }

-        return Padding(
-          padding: const EdgeInsets.only(top: 4),
-          child: Column(
-            crossAxisAlignment: CrossAxisAlignment.start,
-            children: [
-              Row(
-                children: [
-                  Text(
-                    context.messages.tasksQuickFilterLabelsActiveTitle,
-                    style: Theme.of(context).textTheme.labelSmall,
+        final theme = Theme.of(context);
+        final count = selected.length;
+        return Column(
+          crossAxisAlignment: CrossAxisAlignment.start,
+          children: [
+            Row(
+              children: [
+                Icon(
+                  Icons.filter_alt_outlined,
+                  size: 16,
+                  color: theme.colorScheme.onSurfaceVariant,
+                ),
+                const SizedBox(width: 6),
+                Text(
+                  '${context.messages.tasksQuickFilterLabelsActiveTitle} ($count)',
+                  style: theme.textTheme.labelMedium?.copyWith(
+                    color: theme.colorScheme.onSurfaceVariant,
                   ),
-                  const Spacer(),
-                  TextButton(
-                    onPressed:
-                        context.read<JournalPageCubit>().clearSelectedLabelIds,
-                    child: Text(context.messages.tasksQuickFilterClear),
+                ),
+                const Spacer(),
+                TextButton.icon(
+                  onPressed:
+                      context.read<JournalPageCubit>().clearSelectedLabelIds,
+                  icon: const Icon(Icons.backspace_outlined, size: 16),
+                  label: Text(context.messages.tasksQuickFilterClear),
+                  style: TextButton.styleFrom(
+                    visualDensity: VisualDensity.compact,
+                    textStyle: theme.textTheme.labelSmall,
                   ),
-                ],
-              ),
-              Wrap(
-                spacing: 8,
-                runSpacing: 8,
-                children: chips,
-              ),
-            ],
-          ),
+                ),
+              ],
+            ),
+            const SizedBox(height: 4),
+            Wrap(
+              spacing: 8,
+              runSpacing: 8,
+              children: chips,
+            ),
+          ],
         );
       },
     );
@@ -98,6 +111,7 @@ class _QuickFilterChip extends StatelessWidget {
       label: Text(label),
       labelStyle: Theme.of(context).textTheme.labelSmall,
       backgroundColor: color.withValues(alpha: 0.18),
+      visualDensity: VisualDensity.compact,
       onDeleted: onDeleted,
       deleteIcon: const Icon(Icons.close, size: 16),
       deleteIconColor: Theme.of(context).colorScheme.onSurfaceVariant,
diff --git a/lib/features/tasks/README.md b/lib/features/tasks/README.md
index 5c54c88b38..6a52d2ec5c 100644
--- a/lib/features/tasks/README.md
+++ b/lib/features/tasks/README.md
@@ -83,6 +83,25 @@ The main interface for viewing and editing tasks, featuring:
 - The label editor allows scoping labels to specific categories via an "Applicable categories"
   section (chips + add/remove). Labels with no categories selected are considered global.

+#### Tasks List — Active Label Filters Header
+
+When label filters are active on the Tasks page, a compact quick-filter header appears directly
+below the search bar:
+
+- Container: Rounded background using `surfaceContainerHighest` with `BorderRadius.circular(10)` and
+  `EdgeInsets.all(12)` padding.
+- Animation: Wrapped in `AnimatedSize` (~180ms, easeInOut) for smooth expand/collapse as filters
+  change.
+- Header: Leading `filter_alt_outlined` icon and title "Active label filters (n)" using
+  `labelMedium` tinted with `onSurfaceVariant`.
+- Clear: Compact `TextButton.icon` (backspace icon) using `labelSmall` typography.
+- Chips: `InputChip` with `VisualDensity.compact`; delete icon allows removing individual filters.
+- Placement and spacing: Rendered inside a `SliverToBoxAdapter` with outer padding
+  `EdgeInsets.fromLTRB(40, 8, 40, 8)` to align with the search field.
+- Visibility: Rendered only when `selectedLabelIds.isNotEmpty` to avoid an empty container when no
+  label filters are active. `TaskLabelQuickFilter` still self-hides its own content as an extra
+  guard.
+
 #### Checklist Components

 **ChecklistWidget**: Displays a single checklist with:
diff --git a/lib/features/labels/README.md b/lib/features/labels/README.md
index e51f010534..3305c1a8ed 100644
--- a/lib/features/labels/README.md
+++ b/lib/features/labels/README.md
@@ -65,6 +65,10 @@ does not reappear due to null-as-unchanged merges downstream.
   "create label" CTA, and a long-press description dialog for mobile discoverability.
 - `TaskLabelQuickFilter`: Mirrors the filter drawer selections in the task list header so users can
   quickly audit/clear active label filters.
+  - When active, the quick filter appears in a compact, rounded container below the search bar on
+    the Tasks page, shows an icon + "Active label filters (n)", compact chips, and a small Clear
+    action. It animates open/closed via `AnimatedSize` and only renders when there are active label
+    selections.

 ### Applicable Categories (Scoped Labels)

diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1180bbc235..f7551c612c 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -21,6 +21,7 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
   - i18n: English keys for labels, picker title and descriptions
   - Tests: database ordering/filtering, UI wrappers, filter UX
 ### Fixed
+- Tasks page: Active label filters are now visible below the search header (no longer clipped in the app bar).
 - AI label assignment: Prevented out-of-category labels from being assigned by AI
 - Task label selector: Now shows currently assigned out-of-scope labels to allow unassigning
   - List is strictly A–Z (case-insensitive); selection does not change ordering
@@ -66,6 +67,11 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
   - Tests: service unit tests and widget tests updated; i18n keys added with missing translations noted

 ### Changed
+- UI/Tasks: Redesigned the active label filters header below the search bar
+  - Compact card-style container (rounded, `surfaceContainerHighest`) with smooth `AnimatedSize`
+  - Header shows a subtle filter icon and "Active label filters (n)"
+  - Clear action uses compact `TextButton.icon` (smaller text) and chips use compact density
+  - Renders only when filters are active; no empty container state
 - Sync (Matrix): Client stream is now signal-driven and always triggers a catch-up via
   `forceRescan(includeCatchUp=true)` with an in-flight guard to prevent overlaps. Timeline callbacks
   continue to schedule debounced live scans and fall back to `forceRescan()` on scheduling errors.

PATCH

echo "Patch applied successfully."
