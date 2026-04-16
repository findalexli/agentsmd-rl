#!/bin/bash
set -e

cd /workspace/antd

# Check idempotency - skip if already applied
if grep -q "itemContent.*string" components/calendar/generateCalendar.tsx 2>/dev/null; then
    echo "Patch already applied, skipping..."
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/components/calendar/generateCalendar.tsx b/components/calendar/generateCalendar.tsx
index 1234567..abcdefg 100644
--- a/components/calendar/generateCalendar.tsx
+++ b/components/calendar/generateCalendar.tsx
@@ -36,13 +36,15 @@ export type CalendarSemanticType = {
     body?: string;
     content?: string;
     item?: string;
+    itemContent?: string;
   };
   styles?: {
     root?: React.CSSProperties;
     header?: React.CSSProperties;
     body?: React.CSSProperties;
     content?: React.CSSProperties;
     item?: React.CSSProperties;
+    itemContent?: React.CSSProperties;
   };
 };

@@ -167,6 +169,9 @@ const generateCalendar = <DateType extends AnyObject>(generateConfig: GenerateCo
         ] as const;
       }, [mergedClassNames, mergedStyles]);

+    const mergedItemContentClassName = mergedClassNames.itemContent;
+    const mergedItemContentStyle = mergedStyles.itemContent;
+
     const prefixCls = getPrefixCls('picker', customizePrefixCls);
     const calendarPrefixCls = `${prefixCls}-calendar`;

@@ -265,7 +270,10 @@ const generateCalendar = <DateType extends AnyObject>(generateConfig: GenerateCo
             <div className={`${calendarPrefixCls}-date-value`}>
               {String(generateConfig.getDate(date)).padStart(2, '0')}
             </div>
-            <div className={`${calendarPrefixCls}-date-content`}>
+            <div
+              className={clsx(`${calendarPrefixCls}-date-content`, mergedItemContentClassName)}
+              style={mergedItemContentStyle}
+            >
               {typeof cellRender === 'function' ? cellRender(date, info) : dateCellRender?.(date)}
             </div>
           </div>
@@ -279,6 +287,8 @@ const generateCalendar = <DateType extends AnyObject>(generateConfig: GenerateCo
         dateFullCellRender,
         cellRender,
         dateCellRender,
+        mergedItemContentClassName,
+        mergedItemContentStyle,
       ],
     );

@@ -303,7 +313,10 @@ const generateCalendar = <DateType extends AnyObject>(generateConfig: GenerateCo
             <div className={`${calendarPrefixCls}-date-value`}>
               {months[generateConfig.getMonth(date)]}
             </div>
-            <div className={`${calendarPrefixCls}-date-content`}>
+            <div
+              className={clsx(`${calendarPrefixCls}-date-content`, mergedItemContentClassName)}
+              style={mergedItemContentStyle}
+            >
               {typeof cellRender === 'function' ? cellRender(date, info) : monthCellRender?.(date)}
             </div>
           </div>
@@ -317,6 +330,8 @@ const generateCalendar = <DateType extends AnyObject>(generateConfig: GenerateCo
         monthFullCellRender,
         cellRender,
         monthCellRender,
+        mergedItemContentClassName,
+        mergedItemContentStyle,
       ],
     );
PATCH

echo "Patch applied successfully"
