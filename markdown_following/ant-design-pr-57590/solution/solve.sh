#!/bin/bash
set -euo pipefail

cd /workspace/antd

# Idempotency check - skip if already applied
if grep -q "'&:first-child'" components/notification/style/index.ts 2>/dev/null; then
    echo "Patch already applied, skipping."
    exit 0
fi

# Apply the gold patch
git apply --whitespace=fix <<'PATCH'
diff --git a/components/notification/PurePanel.tsx b/components/notification/PurePanel.tsx
index 2f3c3f7a0e..e3c6c5b3a1 100644
--- a/components/notification/PurePanel.tsx
+++ b/components/notification/PurePanel.tsx
@@ -97,9 +97,11 @@ export const PureContent: React.FC<PureContentProps> = (props) => {
   return (
     <div className={clsx({ [`${prefixCls}-with-icon`]: iconNode })} role={role}>
       {iconNode}
-      <div className={clsx(`${prefixCls}-title`, pureContentCls.title)} style={styles.title}>
-        {title}
-      </div>
+      {title && (
+        <div className={clsx(`${prefixCls}-title`, pureContentCls.title)} style={styles.title}>
+          {title}
+        </div>
+      )}
       {description && (
         <div
           className={clsx(`${prefixCls}-description`, pureContentCls.description)}
diff --git a/components/notification/__tests__/index.test.tsx b/components/notification/__tests__/index.test.tsx
index 7d8c5f8a1b..9e4c6f7a2c 100644
--- a/components/notification/__tests__/index.test.tsx
+++ b/components/notification/__tests__/index.test.tsx
@@ -511,6 +511,7 @@ describe('notification', () => {
     });
     expect(document.querySelectorAll('.ant-notification-description').length).toBe(0);
   });
+
   describe('When closeIcon is null, there is no close button', () => {
     it('Notification method', async () => {
       act(() => {
diff --git a/components/notification/style/index.ts b/components/notification/style/index.ts
index 1a2b3c4d5e..6f7a8b9c0d 100644
--- a/components/notification/style/index.ts
+++ b/components/notification/style/index.ts
@@ -175,6 +175,11 @@ export const genNoticeStyle: GenerateStyle<NotificationToken, CSSObject> = (toke
       fontSize,
       color: colorText,
       marginTop: token.marginXS,
+
+      '&:first-child': {
+        marginTop: 0,
+        marginInlineEnd: token.marginSM,
+      },
     },

     [`${noticeCls}-closable ${noticeCls}-title`]: {
PATCH

echo "Gold patch applied successfully."
