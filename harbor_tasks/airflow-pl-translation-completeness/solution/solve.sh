#!/bin/bash
set -euo pipefail

cd /workspace/airflow

# Idempotency: skip if patch already applied
if grep -q "Terminology Glossary" .github/skills/airflow-translations/locales/pl.md 2>/dev/null; then
    echo "Already applied"
    exit 0
fi

cat > /tmp/gold.patch <<'PATCH'
diff --git a/.github/skills/airflow-translations/locales/pl.md b/.github/skills/airflow-translations/locales/pl.md
index b20715a298ed1..1a38bbbb325d1 100644
--- a/.github/skills/airflow-translations/locales/pl.md
+++ b/.github/skills/airflow-translations/locales/pl.md
@@ -147,6 +147,25 @@ Preserve all `{{variable}}` placeholders. Adjust word order for natural Polish:
 "title": "Usuń {{liczba}} połączeń"  // variable name translated
 ```

+## Terminology Glossary
+
+Preferred wording for specific UI terms. Apply these to new translations and
+prefer them when reviewing existing ones.
+
+| English / context | Preferred Polish | Avoid |
+|---|---|---|
+| Consuming Asset (asset consumed by a Dag run) | **Zabierający zasób** | ~~Konsumujący zasób~~ |
+| Bulk clear / delete / update (toaster and button labels) | **grupowy / grupowego / grupowej / grupowe …** | ~~masowy / masowego / masowej / masowe~~ |
+| Deactivated (Dag header status) | **Deaktywowany** / Deaktywowana / Deaktywowane | ~~Dezaktywowany~~ |
+
+Notes:
+
+- For "bulk <verb>" always use "grupowy" with the grammatical form that
+  matches the noun — e.g. "żądanie grupowego wyczyszczenia", "żądanie
+  grupowej aktualizacji". Never use "masowy".
+- "Deactivated" / "Deaktywowany" must agree in gender with the noun it
+  describes (e.g. neuter "zadanie" → "Deaktywowane").
+
 ## Terminology Reference

 The established Polish translations are defined in the existing locale files.
diff --git a/airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json b/airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json
index 56b402e513169..eb569300a98e2 100644
--- a/airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json
+++ b/airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json
@@ -128,7 +128,8 @@
       "includeDeferred": "Uwzględnij odroczone",
       "nameMaxLength": "Nazwa może zawierać maksymalnie 256 znaków",
       "nameRequired": "Nazwa jest wymagana",
-      "slots": "Miejsca"
+      "slots": "Miejsca",
+      "slotsHelperText": "Użyj -1 dla nieograniczonej liczby miejsc."
     },
     "noPoolsFound": "Nie znaleziono pul",
     "pool_few": "Pule",
diff --git a/airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json b/airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json
index 5f8aa61e418b6..13bb00e628b5b 100644
--- a/airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json
+++ b/airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json
@@ -115,6 +115,12 @@
     "notFound": "Nie znaleziono strony",
     "title": "Błąd"
   },
+  "errors": {
+    "forbidden": {
+      "description": "Nie masz uprawnień do wykonania tej akcji.",
+      "title": "Dostęp zabroniony"
+    }
+  },
   "expand": {
     "collapse": "Zwiń",
     "expand": "Rozwiń",
@@ -140,6 +146,7 @@
     "selectDateRange": "Wybierz zakres dat",
     "startTime": "Czas rozpoczęcia"
   },
+  "generateToken": "Wygeneruj token",
   "logicalDate": "Data logiczna",
   "logout": "Wyloguj",
   "logoutConfirmation": "Zamierzasz wylogować się z aplikacji.",
@@ -187,6 +194,7 @@
   "reset": "Resetuj",
   "runId": "Identyfikator wykonania",
   "runTypes": {
+    "asset_materialization": "Materializacja zasobu",
     "asset_triggered": "Uruchomiony przez zasób",
     "backfill": "Wypełnienie wsteczne",
     "manual": "Ręcznie",
@@ -316,10 +324,10 @@
   },
   "toaster": {
     "bulkDelete": {
-      "error": "Nie udało się wykonać żądania masowego usunięcia {{resourceName}}",
+      "error": "Nie udało się wykonać żądania grupowego usunięcia {{resourceName}}",
       "success": {
         "description": "Pomyślnie usunięto {{count}} {{resourceName}}. Klucze: {{keys}}",
-        "title": "Wysłano żądanie masowego usunięcia {{resourceName}}"
+        "title": "Wysłano żądanie grupowego usunięcia {{resourceName}}"
       }
     },
     "create": {
@@ -351,6 +359,18 @@
       }
     }
   },
+  "tokenGeneration": {
+    "apiToken": "Token API",
+    "cliToken": "Token CLI",
+    "errorDescription": "Podczas generowania tokenu wystąpił błąd. Spróbuj ponownie.",
+    "errorTitle": "Nie udało się wygenerować tokenu",
+    "generate": "Wygeneruj",
+    "selectType": "Wybierz typ tokenu do wygenerowania.",
+    "title": "Wygeneruj token",
+    "tokenExpiresIn": "Ten token wygasa za {{duration}}.",
+    "tokenGenerated": "Twój token został wygenerowany.",
+    "tokenShownOnce": "Ten token zostanie wyświetlony tylko raz. Skopiuj go teraz."
+  },
   "total": "Wszystkie {{state}}",
   "triggered": "Uruchomiony",
   "tryNumber": "Numer próby",
diff --git a/airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json b/airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json
index c5cd6f930adfa..442fa6b995dd3 100644
--- a/airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json
+++ b/airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json
@@ -47,10 +47,7 @@
     "invalidJson": "Nieprawidłowy format JSON: {{errorMessage}}"
   },
   "dagWarnings": {
-    "error_few": "Błędy",
-    "error_many": "Błędów",
     "error_one": "Błąd",
-    "error_other": "Błedy",
     "errorAndWarning": "1 Błąd i {{warningText}}",
     "warning_few": "{{count}} Ostrzeżenia",
     "warning_many": "{{count}} Ostrzeżeń",
diff --git a/airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json b/airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json
index 9c8a23e35d1fb..3919b7a040089 100644
--- a/airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json
+++ b/airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json
@@ -45,12 +45,16 @@
     "buttons": {
       "resetToLatest": "Przywróć do najnowszego",
       "toggleGroup": "Przełącz grupę"
-    }
+    },
+    "runTypeLegend": "Legenda typów wykonań"
   },
   "header": {
     "buttons": {
       "advanced": "Zaawansowane",
       "dagDocs": "Dokumentacja Daga"
+    },
+    "status": {
+      "deactivated": "Deaktywowany"
     }
   },
   "logs": {
PATCH

git apply /tmp/gold.patch
echo "Gold patch applied"
