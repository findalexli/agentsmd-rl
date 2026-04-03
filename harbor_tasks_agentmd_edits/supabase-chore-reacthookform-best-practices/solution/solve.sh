#!/usr/bin/env bash
set -euo pipefail

cd /workspace/supabase

# Idempotent: skip if already applied
if grep -q 'destructuring.*isDirty.*from.*formState\|const { isDirty } = form.formState' .cursor/rules/studio/forms/RULE.md 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply - <<'PATCH'
diff --git a/.cursor/rules/studio/forms/RULE.md b/.cursor/rules/studio/forms/RULE.md
index b9b729111b5dc..74f8383f86289 100644
--- a/.cursor/rules/studio/forms/RULE.md
+++ b/.cursor/rules/studio/forms/RULE.md
@@ -1,5 +1,5 @@
 ---
-description: "Studio: form patterns (page layouts + side panels) and react-hook-form conventions"
+description: 'Studio: form patterns (page layouts + side panels) and react-hook-form conventions'
 globs:
   - apps/studio/**/*.{ts,tsx}
 alwaysApply: false
@@ -29,7 +29,6 @@ Use the Design System UI pattern docs as the source of truth:

 ## Actions and state

-- Handle dirty state (`form.formState.isDirty`) to show Cancel and to disable Save.
+- Handle dirty state by destructuring `isDirty` from `formState` (`const { isDirty } = form.formState`) then use it to show Cancel and to disable Save.
 - Show loading on submit buttons via `loading`.
 - When submit button is outside the `<form>`, set a stable `formId` and use the button's `form` prop.
-
diff --git a/apps/design-system/content/docs/ui-patterns/forms.mdx b/apps/design-system/content/docs/ui-patterns/forms.mdx
index 8e02ea0f90fc3..f37ab471ce961 100644
--- a/apps/design-system/content/docs/ui-patterns/forms.mdx
+++ b/apps/design-system/content/docs/ui-patterns/forms.mdx
@@ -49,7 +49,7 @@ Use the shared [Key/Value Field Array](../fragments/key-value-field-array) fragm

 4. **Use Cards for grouping**: Wrap form sections in `Card` components with `CardContent` and `CardFooter` for actions.

-5. **Handle dirty state**: Show cancel buttons and disable save buttons based on `form.formState.isDirty`.
+5. **Handle dirty state**: Show cancel buttons and disable save buttons based on `form.formState.isDirty`. Make sure you destructure `isDirty` from `form.formState` (see https://react-hook-form.com/docs/useform/formstate)

 6. **Error handling**: Always use mutations with `onSuccess` and `onError` callbacks that show toast notifications.

diff --git a/apps/design-system/content/docs/ui-patterns/modality.mdx b/apps/design-system/content/docs/ui-patterns/modality.mdx
index 9c4358cce0c8e..63938e858f5af 100644
--- a/apps/design-system/content/docs/ui-patterns/modality.mdx
+++ b/apps/design-system/content/docs/ui-patterns/modality.mdx
@@ -104,8 +104,13 @@ Studio implementation (preferred in Studio code):
 import { DiscardChangesConfirmationDialog } from 'components/ui-patterns/Dialogs/DiscardChangesConfirmationDialog'
 import { useConfirmOnClose } from 'hooks/ui/useConfirmOnClose'

+const form = useForm(...)
+// Always destructure formState values otherwise they won't be updated
+// See https://react-hook-form.com/docs/useform/formstate
+const { isDirty } = form.formState
+
 const { confirmOnClose, handleOpenChange, modalProps } = useConfirmOnClose({
-  checkIsDirty: () => form.formState.isDirty,
+  checkIsDirty: () => isDirty,
   onClose,
 })

PATCH

echo "Patch applied successfully."
