#!/bin/bash
set -e

cd /workspace/OpenHands

# Apply the gold patch for null check fix
patch -p1 << 'PATCH'
diff --git a/frontend/__tests__/hooks/use-handle-plan-click.test.tsx b/frontend/__tests__/hooks/use-handle-plan-click.test.tsx
index fdaa4c06aa33..da99ad73cd38 100644
--- a/frontend/__tests__/hooks/use-handle-plan-click.test.tsx
+++ b/frontend/__tests__/hooks/use-handle-plan-click.test.tsx
@@ -21,6 +21,10 @@ vi.mock("react-i18next", () => ({
   useTranslation: () => ({
     t: (key: string) => key,
   }),
+  initReactI18next: {
+    type: "3rdParty",
+    init: () => {},
+  },
 }));

 const mockSetConversationMode = vi.fn();
diff --git a/frontend/__tests__/hooks/use-sandbox-recovery.test.tsx b/frontend/__tests__/hooks/use-sandbox-recovery.test.tsx
index 638fe21788e1..2a7c6abad2a8 100644
--- a/frontend/__tests__/hooks/use-sandbox-recovery.test.tsx
+++ b/frontend/__tests__/hooks/use-sandbox-recovery.test.tsx
@@ -10,6 +10,10 @@ vi.mock("react-i18next", () => ({
   useTranslation: () => ({
     t: (key: string) => key,
   }),
+  initReactI18next: {
+    type: "3rdParty",
+    init: () => {},
+  },
 }));

 vi.mock("#/hooks/use-user-providers", () => ({
diff --git a/frontend/src/utils/custom-toast-handlers.tsx b/frontend/src/utils/custom-toast-handlers.tsx
index ece6212b6bab..73a956f4edd1 100644
--- a/frontend/src/utils/custom-toast-handlers.tsx
+++ b/frontend/src/utils/custom-toast-handlers.tsx
@@ -1,6 +1,7 @@
 import { CSSProperties } from "react";
 import toast, { ToastOptions } from "react-hot-toast";
 import { calculateToastDuration } from "./toast-duration";
+import i18n from "#/i18n";

 const TOAST_STYLE: CSSProperties = {
   background: "#454545",
@@ -18,11 +19,12 @@ export const TOAST_OPTIONS: ToastOptions = {
   style: TOAST_STYLE,
 };

-export const displayErrorToast = (error: string) => {
-  const duration = calculateToastDuration(error, 4000);
+export const displayErrorToast = (error: string | null | undefined) => {
+  const errorMessage = error || i18n.t("STATUS$ERROR");
+  const duration = calculateToastDuration(errorMessage, 4000);
   toast.error(
     <span style={{ wordBreak: "break-word", overflowWrap: "anywhere" }}>
-      {error}
+      {errorMessage}
     </span>,
     { ...TOAST_OPTIONS, duration },
   );
diff --git a/frontend/src/utils/toast-duration.ts b/frontend/src/utils/toast-duration.ts
index 1c0b08c883c0..300efb6097a8 100644
--- a/frontend/src/utils/toast-duration.ts
+++ b/frontend/src/utils/toast-duration.ts
@@ -6,10 +6,15 @@
  * @returns Duration in milliseconds
  */
 export const calculateToastDuration = (
-  message: string,
+  message: string | null | undefined,
   minDuration: number = 5000,
   maxDuration: number = 10000,
 ): number => {
+  // Handle null/undefined messages - return minDuration immediately
+  if (!message) {
+    return minDuration;
+  }
+
   // Calculate duration based on reading speed (average 200 words per minute)
   // Assuming average word length of 5 characters
   const wordsPerMinute = 200;
PATCH

# Verify patch applied by checking for the distinctive line
grep -q "Handle null/undefined messages" frontend/src/utils/toast-duration.ts
echo "Patch applied successfully"
