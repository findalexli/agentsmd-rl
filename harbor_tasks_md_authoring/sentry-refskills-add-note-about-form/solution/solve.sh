#!/usr/bin/env bash
set -euo pipefail

cd /workspace/sentry

# Idempotency guard
if grep -qF "If the legacy `JsonForm` being migrated was already indexed by SettingsSearch (i" ".agents/skills/migrate-frontend-forms/SKILL.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.agents/skills/migrate-frontend-forms/SKILL.md b/.agents/skills/migrate-frontend-forms/SKILL.md
@@ -481,6 +481,59 @@ function SlugForm({project}: {project: Project}) {
 - Large multiline text fields where you want to finish editing before saving (fingerprint rules, filters)
 - Any field where auto-save doesn't make sense
 
+## Preserving Form Search Functionality
+
+Sentry's SettingsSearch allows users to search for individual settings fields. When migrating forms, you must preserve this searchability by wrapping migrated forms with `FormSearch`.
+
+### The `FormSearch` Component
+
+`FormSearch` is a **build-time marker component** — it has zero runtime behavior and simply renders its children unchanged. Its `route` prop is read by a static extraction script to associate form fields with their navigation route, enabling them to appear in SettingsSearch results.
+
+```tsx
+import {FormSearch} from 'sentry/components/core/form';
+
+<FormSearch route="/settings/account/details/">
+  <FieldGroup title={t('Account Details')}>
+    <AutoSaveField name="name" schema={schema} initialValue={user.name} mutationOptions={...}>
+      {field => (
+        <field.Layout.Row label={t('Name')} hintText={t('Your full name')} required>
+          <field.Input />
+        </field.Layout.Row>
+      )}
+    </AutoSaveField>
+  </FieldGroup>
+</FormSearch>
+```
+
+**Props:**
+
+| Prop       | Type        | Description                                                                                          |
+| ---------- | ----------- | ---------------------------------------------------------------------------------------------------- |
+| `route`    | `string`    | The settings route for this form (e.g., `'/settings/account/details/'`). Used for search navigation. |
+| `children` | `ReactNode` | The form content — rendered unchanged at runtime.                                                    |
+
+**Rules:**
+
+- The `route` must match the settings page URL exactly (including trailing slash).
+- Wrap the **entire form section** with a single `FormSearch`, not individual fields.
+- Every `<AutoSaveField>` or `<form.AppField>` inside a `FormSearch` will be indexed. Make sure `label` and `hintText` are plain string literals or `t()` calls — computed/dynamic strings will be skipped by the extractor.
+
+### The Form Field Registry
+
+After adding or updating `FormSearch` wrappers, regenerate the field registry so that search results stay up to date:
+
+```bash
+pnpm run extract-form-fields
+```
+
+This script (`scripts/extractFormFields.ts`) scans all TSX files, finds `<FormSearch>` components, extracts field metadata (`name`, `label`, `hintText`, `route`), and writes the generated registry to `static/app/components/core/form/generatedFieldRegistry.ts`. **Commit this generated file** alongside your migration PR — it is part of the source tree.
+
+> Run the command after **any** change to forms inside a `FormSearch` wrapper (adds, removals, label changes). The generated file is checked in and should not be edited manually.
+
+### Migration: Old Forms Already Searchable
+
+If the legacy `JsonForm` being migrated was already indexed by SettingsSearch (i.e., it had entries in `sentry/data/forms`), you **must** add a `FormSearch` wrapper to the new form so search functionality is preserved. The old and new sources coexist — new registry entries take precedence over old ones for the same route + field combination — but once you remove the legacy form the old entries will disappear.
+
 ## Intentionally Not Migrated
 
 | Feature     | Usage   | Reason                                                                                |
@@ -501,3 +554,5 @@ function SlugForm({project}: {project: Project}) {
 - [ ] Handle `saveMessage` in onSuccess callback
 - [ ] Convert `saveOnBlur: false` fields to regular forms with Save button
 - [ ] Verify `onSuccess` cache updates merge with existing data (use updater function) — some API endpoints may return partial objects
+- [ ] Wrap the migrated form with `<FormSearch route="...">` if the old form was searchable in SettingsSearch
+- [ ] Run `pnpm run extract-form-fields` and commit the updated `generatedFieldRegistry.ts`
PATCH

echo "Gold patch applied."
