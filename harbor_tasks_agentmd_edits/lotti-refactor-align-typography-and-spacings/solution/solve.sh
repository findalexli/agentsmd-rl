#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lotti

# Idempotent: skip if already applied
if grep -q 'anteMeridiemAbbreviation' lib/features/design_system/components/time_pickers/design_system_time_picker.dart 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/lib/features/design_system/README.md b/lib/features/design_system/README.md
index 0d48ccbb37..eadaa1eac2 100644
--- a/lib/features/design_system/README.md
+++ b/lib/features/design_system/README.md
@@ -9,6 +9,8 @@ This feature contains the standalone Widgetbook-first design system work.
 - Build a standalone Widgetbook-only theme
 - Build new design-system components without retrofitting existing app widgets
 - Render design-system typography with the bundled local `Inter` variable font
+- Keep component spacing and typography sourced from design-system tokens
+  instead of ad-hoc layout or font literals
 
 ## Accessibility Conventions
 
@@ -21,26 +23,38 @@ This feature contains the standalone Widgetbook-first design system work.
 
 ## Implemented Components
 
+- Avatars
 - Typography showcase
 - Buttons
 - Badges
 - Branding
 - Chips
 - Breadcrumbs
+- Captions
 - Header
 - Search
 - Toast
 - Divider
 - Dropdowns
+- Inputs
+- Lists
+- Context menus
 - Split buttons
 - Tabs
 - Navigation sidebar
 - Tab bar
 - Calendar picker
+- Time picker
 - Progress bar
 - Toggles
 - Radio buttons
 - Checkboxes
+- Scrollbars
+- Spinners
+- Task filter sheet
+- Task list items
+- Textareas
+- Tooltip icons
 
 ## Usage
 
diff --git a/lib/features/design_system/components/calendar_pickers/design_system_time_calendar_picker.dart b/lib/features/design_system/components/calendar_pickers/design_system_time_calendar_picker.dart
index 419ddd05df..b0679cabb4 100644
--- a/lib/features/design_system/components/calendar_pickers/design_system_time_calendar_picker.dart
+++ b/lib/features/design_system/components/calendar_pickers/design_system_time_calendar_picker.dart
@@ -349,8 +349,9 @@ class _MonthCalendarCard extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
+    final tokens = context.designTokens;
     final palette = _TimeCalendarPalette.fromMode(mode);
-    final geometry = _TimeCalendarGeometry.fromTokens(context.designTokens);
+    final geometry = _TimeCalendarGeometry.fromTokens(tokens);
     final localeTag = Localizations.localeOf(context).toLanguageTag();
     final firstDayOfWeek = MaterialLocalizations.of(
       context,
@@ -382,9 +383,7 @@ class _MonthCalendarCard extends StatelessWidget {
                 child: Center(
                   child: Text(
                     label,
-                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
-                      fontSize: 12,
-                      fontWeight: FontWeight.w400,
+                    style: tokens.typography.styles.others.caption.copyWith(
                       color: palette.lowEmphasis,
                     ),
                   ),
@@ -582,9 +581,8 @@ class _MonthHeader extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
-    final headerStyle = Theme.of(context).textTheme.titleMedium?.copyWith(
-      fontSize: 16,
-      fontWeight: FontWeight.w600,
+    final tokens = context.designTokens;
+    final headerStyle = tokens.typography.styles.subtitle.subtitle1.copyWith(
       color: palette.highEmphasis,
     );
 
@@ -705,10 +703,9 @@ class _CalendarDayButton extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
-    final geometry = _TimeCalendarGeometry.fromTokens(context.designTokens);
-    final baseStyle = Theme.of(context).textTheme.bodyLarge?.copyWith(
-      fontSize: 16,
-      fontWeight: FontWeight.w400,
+    final tokens = context.designTokens;
+    final geometry = _TimeCalendarGeometry.fromTokens(tokens);
+    final baseStyle = tokens.typography.styles.body.bodyMedium.copyWith(
       color: switch ((isSelected, isCurrentDay, palette.mode)) {
         (true, _, _) => palette.onAccent,
         (_, true, _) => palette.accent,
@@ -765,7 +762,8 @@ class _MonthButton extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
-    final geometry = _TimeCalendarGeometry.fromTokens(context.designTokens);
+    final tokens = context.designTokens;
+    final geometry = _TimeCalendarGeometry.fromTokens(tokens);
     return SizedBox(
       width: geometry.monthButtonWidth,
       height: geometry.monthButtonHeight,
@@ -777,9 +775,7 @@ class _MonthButton extends StatelessWidget {
           child: Center(
             child: Text(
               label,
-              style: Theme.of(context).textTheme.titleMedium?.copyWith(
-                fontSize: 16,
-                fontWeight: FontWeight.w500,
+              style: tokens.typography.styles.subtitle.subtitle1.copyWith(
                 color: selected ? palette.accent : palette.highEmphasis,
               ),
             ),
diff --git a/lib/features/design_system/components/navigation/design_system_navigation_tab_bar.dart b/lib/features/design_system/components/navigation/design_system_navigation_tab_bar.dart
index 105865b57b..b89e17b78b 100644
--- a/lib/features/design_system/components/navigation/design_system_navigation_tab_bar.dart
+++ b/lib/features/design_system/components/navigation/design_system_navigation_tab_bar.dart
@@ -137,8 +137,12 @@ class _DesignSystemNavigationTabBarItem extends StatelessWidget {
               minHeight: symbol ? 44 : 52,
             ),
             padding: EdgeInsets.symmetric(
-              horizontal: symbol ? 10 : 12,
-              vertical: symbol ? 10 : 8,
+              horizontal: symbol
+                  ? tokens.spacing.step4 - tokens.spacing.step1
+                  : tokens.spacing.step4,
+              vertical: symbol
+                  ? tokens.spacing.step4 - tokens.spacing.step1
+                  : tokens.spacing.step3,
             ),
             decoration: BoxDecoration(
               color: item.active
@@ -151,13 +155,11 @@ class _DesignSystemNavigationTabBarItem extends StatelessWidget {
               children: [
                 Icon(item.icon, size: 20, color: iconColor),
                 if (!symbol) ...[
-                  const SizedBox(height: 2),
+                  SizedBox(height: tokens.spacing.step1),
                   Text(
                     item.label,
                     textAlign: TextAlign.center,
-                    style: Theme.of(context).textTheme.bodySmall?.copyWith(
-                      fontSize: 12,
-                      fontWeight: FontWeight.w400,
+                    style: tokens.typography.styles.others.caption.copyWith(
                       color: labelColor,
                     ),
                   ),
diff --git a/lib/features/design_system/components/task_filters/design_system_task_filter_sheet.dart b/lib/features/design_system/components/task_filters/design_system_task_filter_sheet.dart
index cb010b304e..7f6d0c2f0d 100644
--- a/lib/features/design_system/components/task_filters/design_system_task_filter_sheet.dart
+++ b/lib/features/design_system/components/task_filters/design_system_task_filter_sheet.dart
@@ -297,6 +297,7 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
   Widget build(BuildContext context) {
     final tokens = context.designTokens;
     final palette = _TaskFilterPalette.fromTokens(tokens);
+    final spacing = tokens.spacing;
 
     return ClipRRect(
       borderRadius: BorderRadius.circular(_TaskFilterMetrics.frameRadius),
@@ -309,7 +310,12 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
             children: [
               Expanded(
                 child: SingleChildScrollView(
-                  padding: const EdgeInsets.fromLTRB(16, 12, 16, 24),
+                  padding: EdgeInsets.fromLTRB(
+                    spacing.step5,
+                    spacing.step4,
+                    spacing.step5,
+                    spacing.step6,
+                  ),
                   child: SizedBox(
                     width: _TaskFilterMetrics.contentWidth,
                     child: Column(
@@ -326,22 +332,22 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                               ),
                             ),
                           ),
-                        const SizedBox(height: 24),
+                        SizedBox(height: spacing.step6),
                         Text(
                           state.title,
                           style: tokens.typography.styles.heading.heading2
                               .copyWith(color: palette.primaryText),
                         ),
-                        const SizedBox(height: 52),
+                        SizedBox(height: spacing.step9 + spacing.step2), // 52px
                         _TaskFilterSectionLabel(
                           text: state.sortLabel,
                           color: palette.secondaryText,
                           style: tokens.typography.styles.others.caption,
                         ),
-                        const SizedBox(height: 12),
+                        SizedBox(height: spacing.step4),
                         Wrap(
-                          spacing: 8,
-                          runSpacing: 8,
+                          spacing: spacing.step3,
+                          runSpacing: spacing.step3,
                           children: [
                             for (final option in state.sortOptions)
                               _TaskFilterChoicePill(
@@ -358,7 +364,7 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                               ),
                           ],
                         ),
-                        const SizedBox(height: 24),
+                        SizedBox(height: spacing.step6),
                         _TaskFilterSelectionField(
                           key: const ValueKey(
                             'design-system-task-filter-field-status',
@@ -377,16 +383,16 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                             ),
                           ),
                         ),
-                        const SizedBox(height: 24),
+                        SizedBox(height: spacing.step6),
                         _TaskFilterSectionLabel(
                           text: state.priorityLabel,
                           color: palette.secondaryText,
                           style: tokens.typography.styles.others.caption,
                         ),
-                        const SizedBox(height: 12),
+                        SizedBox(height: spacing.step4),
                         Wrap(
-                          spacing: 8,
-                          runSpacing: 8,
+                          spacing: spacing.step3,
+                          runSpacing: spacing.step3,
                           children: [
                             for (final option in state.priorityOptions)
                               _TaskFilterChoicePill(
@@ -411,7 +417,7 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                               ),
                           ],
                         ),
-                        const SizedBox(height: 24),
+                        SizedBox(height: spacing.step6),
                         _TaskFilterSelectionField(
                           key: const ValueKey(
                             'design-system-task-filter-field-category',
@@ -430,7 +436,7 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                             ),
                           ),
                         ),
-                        const SizedBox(height: 24),
+                        SizedBox(height: spacing.step6),
                         _TaskFilterSelectionField(
                           key: const ValueKey(
                             'design-system-task-filter-field-label',
@@ -456,7 +462,12 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
               ),
               Container(height: 1, color: palette.dividerColor),
               Padding(
-                padding: const EdgeInsets.fromLTRB(16, 12, 16, 0),
+                padding: EdgeInsets.fromLTRB(
+                  spacing.step5,
+                  spacing.step4,
+                  spacing.step5,
+                  0,
+                ),
                 child: SizedBox(
                   width: _TaskFilterMetrics.contentWidth,
                   child: Row(
@@ -478,7 +489,7 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                           },
                         ),
                       ),
-                      const SizedBox(width: 16),
+                      SizedBox(width: spacing.step5),
                       Expanded(
                         child: _TaskFilterActionButton(
                           key: const ValueKey(
@@ -497,9 +508,9 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                   ),
                 ),
               ),
-              const SizedBox(height: 12),
+              SizedBox(height: spacing.step4),
               Padding(
-                padding: const EdgeInsets.only(bottom: 8),
+                padding: EdgeInsets.only(bottom: spacing.step3),
                 child: Container(
                   width: 134,
                   height: 5,
@@ -509,7 +520,10 @@ class DesignSystemTaskFilterSheet extends StatelessWidget {
                   ),
                 ),
               ),
-              const SizedBox(height: 21),
+              SizedBox(
+                height:
+                    spacing.step5 + spacing.step2 + spacing.step1 / 2, // 21px
+              ),
             ],
           ),
         ),
@@ -539,6 +553,7 @@ class _TaskFilterSelectionField extends StatelessWidget {
   @override
   Widget build(BuildContext context) {
     final tokens = context.designTokens;
+    final spacing = tokens.spacing;
 
     return Material(
       color: Colors.transparent,
@@ -556,7 +571,10 @@ class _TaskFilterSelectionField extends StatelessWidget {
               minHeight: _TaskFilterMetrics.fieldHeight,
             ),
             child: Padding(
-              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 6),
+              padding: EdgeInsets.symmetric(
+                horizontal: spacing.step5,
+                vertical: spacing.step2 + spacing.step1, // 6px
+              ),
               child: Row(
                 children: [
                   Expanded(
@@ -569,7 +587,7 @@ class _TaskFilterSelectionField extends StatelessWidget {
                           style: tokens.typography.styles.others.caption
                               .copyWith(color: palette.secondaryText),
                         ),
-                        const SizedBox(height: 4),
+                        SizedBox(height: spacing.step2),
                         if (items.isEmpty)
                           Text(
                             ' ',
@@ -589,7 +607,7 @@ class _TaskFilterSelectionField extends StatelessWidget {
                                     onRemove: () => onRemove(items[i].id),
                                   ),
                                   if (i != items.length - 1)
-                                    const SizedBox(width: 8),
+                                    SizedBox(width: spacing.step3),
                                 ],
                               ],
                             ),
@@ -597,7 +615,7 @@ class _TaskFilterSelectionField extends StatelessWidget {
                       ],
                     ),
                   ),
-                  const SizedBox(width: 8),
+                  SizedBox(width: spacing.step3),
                   Icon(
                     Icons.keyboard_arrow_down_rounded,
                     color: palette.secondaryText,
@@ -629,10 +647,16 @@ class _TaskFilterSelectedChip extends StatelessWidget {
   @override
   Widget build(BuildContext context) {
     final tokens = context.designTokens;
+    final spacing = tokens.spacing;
 
     return Container(
       height: 28,
-      padding: const EdgeInsets.fromLTRB(12, 2, 4, 2),
+      padding: EdgeInsets.fromLTRB(
+        spacing.step4,
+        spacing.step1,
+        spacing.step2,
+        spacing.step1,
+      ),
       decoration: BoxDecoration(
         color: palette.pillFill,
         borderRadius: BorderRadius.circular(16),
@@ -646,7 +670,7 @@ class _TaskFilterSelectedChip extends StatelessWidget {
               color: palette.primaryText,
             ),
           ),
-          const SizedBox(width: 6),
+          SizedBox(width: spacing.step2 + spacing.step1), // 6px
           Material(
             color: Colors.transparent,
             child: Ink(
@@ -696,6 +720,8 @@ class _TaskFilterChoicePill extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
+    final spacing = context.designTokens.spacing;
+
     return Material(
       color: Colors.transparent,
       child: Ink(
@@ -712,15 +738,18 @@ class _TaskFilterChoicePill extends StatelessWidget {
           onTap: onTap,
           child: Padding(
             padding: EdgeInsets.symmetric(
-              horizontal: leading != null ? 16 : 20,
-              vertical: 11,
+              horizontal: leading != null
+                  ? spacing.step5
+                  : spacing.step5 + spacing.step2,
+              vertical:
+                  spacing.step3 + spacing.step1 + spacing.step1 / 2, // 11px
             ),
             child: Row(
               mainAxisSize: MainAxisSize.min,
               children: [
                 if (leading != null) ...[
                   leading!,
-                  const SizedBox(width: 8),
+                  SizedBox(width: spacing.step3),
                 ],
                 Text(
                   label,
@@ -746,6 +775,8 @@ class _TaskFilterPriorityGlyph extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
+    final spacing = context.designTokens.spacing;
+
     if (glyph == DesignSystemTaskFilterGlyph.priorityP0) {
       return Icon(
         Icons.priority_high_rounded,
@@ -779,7 +810,7 @@ class _TaskFilterPriorityGlyph extends StatelessWidget {
               padding: EdgeInsets.only(
                 right: i == _TaskFilterMetrics.priorityBarHeights.length - 1
                     ? 0
-                    : 1,
+                    : spacing.step1 / 2,
               ),
               child: Container(
                 width: 4,
@@ -816,6 +847,9 @@ class _TaskFilterActionButton extends StatelessWidget {
 
   @override
   Widget build(BuildContext context) {
+    final tokens = context.designTokens;
+    final spacing = tokens.spacing;
+
     return Material(
       color: Colors.transparent,
       child: Ink(
@@ -840,7 +874,7 @@ class _TaskFilterActionButton extends StatelessWidget {
                   ),
                 ),
                 if (counter != null) ...[
-                  const SizedBox(width: 10),
+                  SizedBox(width: spacing.step4 - spacing.step1),
                   Container(
                     width: 28,
                     height: 28,
@@ -851,11 +885,12 @@ class _TaskFilterActionButton extends StatelessWidget {
                     child: Center(
                       child: Text(
                         '$counter',
-                        style: Theme.of(context).textTheme.labelLarge?.copyWith(
-                          color: highlighted
-                              ? palette.accentText
-                              : palette.primaryText,
-                        ),
+                        style: tokens.typography.styles.subtitle.subtitle2
+                            .copyWith(
+                              color: highlighted
+                                  ? palette.accentText
+                                  : palette.primaryText,
+                            ),
                       ),
                     ),
                   ),
diff --git a/lib/features/design_system/components/task_list_items/design_system_task_list_item.dart b/lib/features/design_system/components/task_list_items/design_system_task_list_item.dart
index 8b1f0c2f70..1ebd3cf83e 100644
--- a/lib/features/design_system/components/task_list_items/design_system_task_list_item.dart
+++ b/lib/features/design_system/components/task_list_items/design_system_task_list_item.dart
@@ -177,7 +177,7 @@ List<InlineSpan> _taskMetadataSpans({
       text: priorityLabel,
       style: spec.metaStyle.copyWith(
         color: priorityColor,
-        fontWeight: FontWeight.w600,
+        fontWeight: tokens.typography.weight.semiBold,
       ),
     ),
     if (timeRange != null) ...[
diff --git a/lib/features/design_system/components/time_pickers/design_system_time_picker.dart b/lib/features/design_system/components/time_pickers/design_system_time_picker.dart
index 2e6b6eaca2..0de52a5280 100644
--- a/lib/features/design_system/components/time_pickers/design_system_time_picker.dart
+++ b/lib/features/design_system/components/time_pickers/design_system_time_picker.dart
@@ -53,6 +53,9 @@ class _DesignSystemTimePickerState extends State<DesignSystemTimePicker> {
   @override
   Widget build(BuildContext context) {
     final tokens = context.designTokens;
+    final materialLocalizations = MaterialLocalizations.of(context);
+    final columnGap = // 27px
+        tokens.spacing.step6 + tokens.spacing.step1 + tokens.spacing.step1 / 2;
     final is12h = widget.format == DesignSystemTimeFormat.twelveHour;
     final hourCount = is12h ? 12 : 24;
 
@@ -81,7 +84,7 @@ class _DesignSystemTimePickerState extends State<DesignSystemTimePicker> {
                     _notifyTimeChanged();
                   },
                 ),
-                const SizedBox(width: 27),
+                SizedBox(width: columnGap),
                 _DrumColumn(
                   itemCount: 60,
                   initialItem: _selectedMinute,
@@ -92,12 +95,14 @@ class _DesignSystemTimePickerState extends State<DesignSystemTimePicker> {
                   },
                 ),
                 if (is12h) ...[
-                  const SizedBox(width: 27),
+                  SizedBox(width: columnGap),
                   _DrumColumn(
                     itemCount: 2,
                     initialItem: _selectedPeriod,
                     looping: false,
-                    labelBuilder: (index) => index == 0 ? 'AM' : 'PM',
+                    labelBuilder: (index) => index == 0
+                        ? materialLocalizations.anteMeridiemAbbreviation
+                        : materialLocalizations.postMeridiemAbbreviation,
                     onSelectedItemChanged: (index) {
                       _selectedPeriod = index;
                       _notifyTimeChanged();
diff --git a/lib/features/design_system/components/toasts/design_system_toast.dart b/lib/features/design_system/components/toasts/design_system_toast.dart
index dbe4f03647..08109a8a20 100644
--- a/lib/features/design_system/components/toasts/design_system_toast.dart
+++ b/lib/features/design_system/components/toasts/design_system_toast.dart
@@ -62,7 +62,7 @@ class DesignSystemToast extends StatelessWidget {
                 ),
                 Expanded(
                   child: Padding(
-                    padding: const EdgeInsets.all(8),
+                    padding: EdgeInsets.all(tokens.spacing.step3),
                     child: Row(
                       children: [
                         Expanded(
@@ -70,7 +70,9 @@ class DesignSystemToast extends StatelessWidget {
                             crossAxisAlignment: CrossAxisAlignment.start,
                             children: [
                               Padding(
-                                padding: const EdgeInsets.only(top: 2),
+                                padding: EdgeInsets.only(
+                                  top: tokens.spacing.step1,
+                                ),
                                 child: Icon(
                                   spec.leadingIcon,
                                   size: 20,
@@ -91,7 +93,7 @@ class DesignSystemToast extends StatelessWidget {
                                         color: spec.titleColor,
                                       ),
                                     ),
-                                    const SizedBox(height: 4),
+                                    SizedBox(height: tokens.spacing.step2),
                                     Text(
                                       description,
                                       maxLines: 1,
diff --git a/test/features/design_system/components/calendar_pickers/design_system_time_calendar_picker_test.dart b/test/features/design_system/components/calendar_pickers/design_system_time_calendar_picker_test.dart
index 9e9f7bfc0e..9c718271dc 100644
--- a/test/features/design_system/components/calendar_pickers/design_system_time_calendar_picker_test.dart
+++ b/test/features/design_system/components/calendar_pickers/design_system_time_calendar_picker_test.dart
@@ -159,6 +159,36 @@ void main() {
       expect(currentDay.style?.color, dsTokensDark.colors.interactive.enabled);
     });
 
+    testWidgets('uses token typography for header and calendar labels', (
+      tester,
+    ) async {
+      await pumpPicker(
+        tester,
+        presentation: DesignSystemTimeCalendarPickerPresentation.regular,
+        mode: DesignSystemTimeCalendarPickerMode.light,
+      );
+
+      final header = tester.widget<Text>(find.text('April 2025'));
+      final weekday = tester.widget<Text>(find.text('SUN'));
+      final selectedDay = tester.widget<Text>(find.text('17'));
+
+      expectTextStyle(
+        header.style!,
+        dsTokensLight.typography.styles.subtitle.subtitle1,
+        dsTokensLight.colors.text.highEmphasis,
+      );
+      expectTextStyle(
+        weekday.style!,
+        dsTokensLight.typography.styles.others.caption,
+        dsTokensLight.colors.text.lowEmphasis,
+      );
+      expectTextStyle(
+        selectedDay.style!,
+        dsTokensLight.typography.styles.body.bodyMedium,
+        dsTokensLight.colors.text.onInteractiveAlert,
+      );
+    });
+
     testWidgets('interactive compact picker opens the month dialog', (
       tester,
     ) async {
diff --git a/test/features/design_system/components/navigation/design_system_navigation_tab_bar_test.dart b/test/features/design_system/components/navigation/design_system_navigation_tab_bar_test.dart
new file mode 100644
index 0000000000..f2f26b6738
--- /dev/null
+++ b/test/features/design_system/components/navigation/design_system_navigation_tab_bar_test.dart
@@ -0,0 +1,67 @@
+import 'package:flutter/material.dart';
+import 'package:flutter_test/flutter_test.dart';
+import 'package:lotti/features/design_system/components/navigation/design_system_navigation_tab_bar.dart';
+import 'package:lotti/features/design_system/theme/design_system_theme.dart';
+import 'package:lotti/features/design_system/theme/design_tokens.dart';
+
+import '../../../../widget_test_utils.dart';
+
+void main() {
+  group('DesignSystemNavigationTabBar', () {
+    testWidgets('uses caption typography for tab labels', (tester) async {
+      await tester.pumpWidget(
+        makeTestableWidgetWithScaffold(
+          const DesignSystemNavigationTabBar(
+            items: [
+              DesignSystemNavigationTabBarItem(
+                label: 'Tasks',
+                icon: Icons.check_circle_outline,
+                active: true,
+              ),
+              DesignSystemNavigationTabBarItem(
+                label: 'Projects',
+                icon: Icons.folder_outlined,
+              ),
+            ],
+          ),
+          theme: DesignSystemTheme.light(),
+        ),
+      );
+
+      final activeLabel = tester.widget<Text>(find.text('Tasks'));
+      final inactiveLabel = tester.widget<Text>(find.text('Projects'));
+
+      expectTextStyle(
+        activeLabel.style!,
+        dsTokensLight.typography.styles.others.caption,
+        dsTokensLight.colors.interactive.enabled,
+      );
+      expectTextStyle(
+        inactiveLabel.style!,
+        dsTokensLight.typography.styles.others.caption,
+        dsTokensLight.colors.text.highEmphasis,
+      );
+    });
+
+    testWidgets('minimized mode hides visible labels', (tester) async {
+      await tester.pumpWidget(
+        makeTestableWidgetWithScaffold(
+          const DesignSystemNavigationTabBar(
+            minimized: true,
+            items: [
+              DesignSystemNavigationTabBarItem(
+                label: 'Tasks',
+                icon: Icons.check_circle_outline,
+                active: true,
+              ),
+            ],
+          ),
+          theme: DesignSystemTheme.light(),
+        ),
+      );
+
+      expect(find.text('Tasks'), findsNothing);
+      expect(find.byIcon(Icons.check_circle_outline), findsOneWidget);
+    });
+  });
+}
diff --git a/test/features/design_system/components/task_list_items/design_system_task_list_item_test.dart b/test/features/design_system/components/task_list_items/design_system_task_list_item_test.dart
index 1f6fef7fb8..fe1fee8fdd 100644
--- a/test/features/design_system/components/task_list_items/design_system_task_list_item_test.dart
+++ b/test/features/design_system/components/task_list_items/design_system_task_list_item_test.dart
@@ -244,6 +244,10 @@ void main() {
         richTextStyleFor(tester, 'P1')?.color,
         dsTokensLight.colors.alert.error.defaultColor,
       );
+      expect(
+        richTextStyleFor(tester, 'P1')?.fontWeight,
+        dsTokensLight.typography.weight.semiBold,
+      );
     });
 
     testWidgets('priority P2 uses warning color', (tester) async {
@@ -265,6 +269,10 @@ void main() {
         richTextStyleFor(tester, 'P2')?.color,
         dsTokensLight.colors.alert.warning.defaultColor,
       );
+      expect(
+        richTextStyleFor(tester, 'P2')?.fontWeight,
+        dsTokensLight.typography.weight.semiBold,
+      );
     });
 
     testWidgets('priority P3 uses medium emphasis color', (tester) async {

PATCH

echo "Patch applied successfully."
