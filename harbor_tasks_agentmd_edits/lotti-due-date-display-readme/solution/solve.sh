#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'task.data.status is TaskDone || task.data.status is TaskRejected' lib/features/journal/ui/widgets/list_cards/modern_task_card.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CHANGELOG.md b/CHANGELOG.md
index 1510e215a7..10e76c02d3 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -8,6 +8,16 @@ and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0
 ### Fixed
 - Ensure SetCoverArtChip widget tests register required dependencies and fallbacks in `getIt` to keep cover-art flows testable

+## [0.9.794] - 2026-01-02
+### Changed
+- Due Date Visibility Refinements: Improved UX for completed and rejected tasks
+  - Due dates are now hidden on task cards for completed and rejected tasks
+  - Due dates in entry details view show grayed-out styling for completed/rejected tasks (no red/orange urgency colors)
+- Updated README and Flatpak metainfo to reference the launched "Meet Lotti" blog series
+
+### Added
+- Tests for due date visibility behavior based on task status
+
 ## [0.9.793] - 2025-12-31
 ### Added
 - Visual Mnemonics: Tasks can now have cover art images for memorable visual representation
diff --git a/README.md b/README.md
index 35d8484430..2f2d5e7e41 100644
--- a/README.md
+++ b/README.md
@@ -12,13 +12,13 @@ Lotti is now available on [Flathub](https://flathub.org/en/apps/com.matthiasn.lo

 [![Get it on Flathub](https://flathub.org/api/badge?locale=en)](https://flathub.org/en/apps/com.matthiasn.lotti)

-## Coming Soon: Deep Dive Series
+## Blog Series: Meet Lotti

-Coming in **December 2025**: a **10-part blog series with video walkthroughs** exploring everything Lotti can do. From task management to AI-powered insights — learn how to take control of your productivity while keeping your data private.
+The beginning of a [**multi-part blog series with video walkthroughs**](https://matthiasnehlsen.substack.com/p/meet-lotti) exploring everything Lotti can do is now live! From task management to AI-powered insights — learn how to take control of your productivity while keeping your data private.

 ![AI Assistant](https://raw.githubusercontent.com/matthiasn/lotti-docs/main/images/0.9.662+3261/tasks_category_summary.png)

-Read more on [**Substack**](https://matthiasnehlsen.substack.com) | [**Project Background**](docs/BACKGROUND.md)
+Start reading: [**Meet Lotti**](https://matthiasnehlsen.substack.com/p/meet-lotti) | [**Project Background**](docs/BACKGROUND.md)

 ## Table of Contents
 - [Why Lotti?](#why-lotti)
diff --git a/flatpak/com.matthiasn.lotti.metainfo.xml b/flatpak/com.matthiasn.lotti.metainfo.xml
index ffda2340d4..fdcf021d6c 100644
--- a/flatpak/com.matthiasn.lotti.metainfo.xml
+++ b/flatpak/com.matthiasn.lotti.metainfo.xml
@@ -19,7 +19,7 @@
       <li>Customizable dashboards and analytics</li>
     </ul>
     <p>
-      Coming in December 2025: A 10-part blog series with video walkthroughs exploring everything Lotti can do — from task management to AI-powered insights. Learn how to take control of your productivity while keeping your data private!
+      Read the <a href="https://matthiasnehlsen.substack.com/p/meet-lotti">multi-part blog series with video walkthroughs</a> exploring everything Lotti can do — from task management to AI-powered insights. Learn how to take control of your productivity while keeping your data private!
     </p>
   </description>
   <developer id="com.matthiasn">
@@ -27,10 +27,15 @@
   </developer>
   <url type="homepage">https://github.com/matthiasn/lotti</url>
   <url type="bugtracker">https://github.com/matthiasn/lotti/issues</url>
-  <url type="help">https://github.com/matthiasn/lotti</url>
+  <url type="help">https://matthiasnehlsen.substack.com/p/meet-lotti</url>
   <launchable type="desktop-id">com.matthiasn.lotti.desktop</launchable>
   <icon type="stock">com.matthiasn.lotti</icon>
   <releases>
+    <release version="0.9.794" date="2026-01-02">
+      <description>
+        <p>Due Date Visibility Refinements: Improved UX for completed and rejected tasks. Due dates are now hidden on task cards for completed/rejected tasks since they're no longer relevant. In the entry details view, due dates show grayed-out styling instead of red/orange urgency colors for completed/rejected tasks.</p>
+      </description>
+    </release>
     <release version="0.9.793" date="2025-12-31">
       <description>
         <p>Visual Mnemonics: Tasks can now have cover art images for memorable visual representation. Set any linked image as a task's cover art via the action menu. Features include cover art thumbnails on task cards (with filter toggle), a cinematic 2:1 collapsible SliverAppBar in task details, glass effect overlay buttons, and horizontal crop adjustment for positioning.</p>
diff --git a/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart b/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart
index 694f7eacf6..419f45a21f 100644
--- a/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart
+++ b/lib/features/journal/ui/widgets/list_cards/modern_task_card.dart
@@ -117,7 +117,10 @@ class ModernTaskCard extends StatelessWidget {

   Widget _buildDateRow(BuildContext context) {
     final hasCreationDate = showCreationDate;
-    final hasDueDate = showDueDate && task.data.due != null;
+    // Don't show due date for completed or rejected tasks - it's no longer relevant
+    final isCompleted =
+        task.data.status is TaskDone || task.data.status is TaskRejected;
+    final hasDueDate = showDueDate && task.data.due != null && !isCompleted;

     if (!hasCreationDate && !hasDueDate) {
       return const SizedBox.shrink();
diff --git a/lib/features/tasks/ui/header/task_due_date_wrapper.dart b/lib/features/tasks/ui/header/task_due_date_wrapper.dart
index e3ce3a6193..70564c5b8e 100644
--- a/lib/features/tasks/ui/header/task_due_date_wrapper.dart
+++ b/lib/features/tasks/ui/header/task_due_date_wrapper.dart
@@ -3,6 +3,7 @@ import 'package:flutter/material.dart';
 import 'package:flutter_riverpod/flutter_riverpod.dart';
 import 'package:intl/intl.dart';
 import 'package:lotti/classes/journal_entities.dart';
+import 'package:lotti/classes/task.dart';
 import 'package:lotti/features/journal/state/entry_controller.dart';
 import 'package:lotti/features/tasks/ui/header/task_due_date_widget.dart';
 import 'package:lotti/features/tasks/util/due_date_utils.dart';
@@ -32,6 +33,10 @@ class TaskDueDateWrapper extends ConsumerWidget {
       referenceDate: clock.now(),
     );

+    // Don't show urgency for completed/rejected tasks - they're done
+    final isCompleted =
+        task.data.status is TaskDone || task.data.status is TaskRejected;
+
     final label = dueDate != null
         ? context.messages
             .taskDueDateWithDate(DateFormat.yMMMd().format(dueDate))
@@ -54,8 +59,9 @@ class TaskDueDateWrapper extends ConsumerWidget {
       child: SubtleActionChip(
         label: label,
         icon: Icons.event_rounded,
-        isUrgent: status.isUrgent,
-        urgentColor: status.urgentColor,
+        // When task is completed/rejected, show grayed-out styling instead of urgent
+        isUrgent: !isCompleted && status.isUrgent,
+        urgentColor: isCompleted ? null : status.urgentColor,
       ),
     );
   }
diff --git a/pubspec.yaml b/pubspec.yaml
index 0f4728690d..14cc5c0d44 100644
--- a/pubspec.yaml
+++ b/pubspec.yaml
@@ -1,7 +1,7 @@
 name: lotti
 description: Achieve your goals and keep your data private with Lotti.
 publish_to: 'none'
-version: 0.9.793+3591
+version: 0.9.794+3592

 msix_config:
   display_name: LottiApp

PATCH

echo "Patch applied successfully."
