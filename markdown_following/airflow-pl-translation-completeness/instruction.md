# Backport Polish translation completeness

The Apache Airflow `v3-2-test` branch has gaps in its Polish (`pl`) UI
translations and inconsistent terminology. Bring it to 100% translation
coverage and apply a small terminology refresh.

The repo is checked out at `/workspace/airflow`. Translation files live under
`airflow-core/src/airflow/ui/public/i18n/locales/`, with the English source in
`en/` and Polish translations in `pl/`. The locale-specific style guide is at
`.github/skills/airflow-translations/locales/pl.md` (referenced by
`.github/skills/airflow-translations/SKILL.md`).

## What is broken

Compared to the English source, the Polish locale at base has both **missing**
keys (English keys with no Polish counterpart) and **unused** keys (Polish
plural variants whose English counterpart does not pluralize). The toaster
strings for bulk operations also use older terminology that no longer matches
the project's Polish style.

## What you must do

### 1. Add the following 17 missing keys to the corresponding Polish files

Add Polish translations for each of these key paths. Use natural Polish
prose, preserve every `{{variable}}` placeholder verbatim, and follow the
diacritics, declension, and gender-agreement rules in
`locales/pl.md`. Place new entries to keep the existing alphabetical
ordering of each object.

In `airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json`:

- `pools.form.slotsHelperText` — sibling of the existing `pools.form.slots`
  ("Miejsca"). EN value: `"Use -1 for unlimited slots."`

In `airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json`:

- `errors.forbidden.title` — EN: `"Access forbidden"`
- `errors.forbidden.description` — EN: `"You don't have permission to perform this action."`
- `generateToken` — EN: `"Generate token"`
- `runTypes.asset_materialization` — EN: `"Asset Materialization"`
- `tokenGeneration.apiToken` — EN: `"API Token"`
- `tokenGeneration.cliToken` — EN: `"CLI Token"`
- `tokenGeneration.errorDescription` — EN: `"An error occurred while generating the token. Please try again."`
- `tokenGeneration.errorTitle` — EN: `"Failed to generate token"`
- `tokenGeneration.generate` — EN: `"Generate"`
- `tokenGeneration.selectType` — EN: `"Select the type of token to generate."`
- `tokenGeneration.title` — EN: `"Generate token"`
- `tokenGeneration.tokenExpiresIn` — EN: `"This token expires in {{duration}}."` (placeholder MUST be preserved)
- `tokenGeneration.tokenGenerated` — EN: `"Your token has been generated."`
- `tokenGeneration.tokenShownOnce` — EN: `"This token will only be shown once. Copy it now."`

In `airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json`:

- `grid.runTypeLegend` — EN: `"Run Type Legend"`
- `header.status.deactivated` — EN: `"Deactivated"` (must follow the
  glossary form below — NOT "Dezaktywowany")

### 2. Remove unused keys

In `airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json`,
under `dagWarnings`, remove these three plural variants. The English source
defines `dagWarnings.error_one` only (no other plural forms), so these
Polish entries are dead:

- `dagWarnings.error_few`
- `dagWarnings.error_many`
- `dagWarnings.error_other`

`dagWarnings.error_one` ("Błąd") must remain.

### 3. Add a "Terminology Glossary" section to `pl.md`

Insert a new top-level section, **between** the existing
`## Variable and Placeholder Examples` section and the
`## Terminology Reference` section, titled `## Terminology Glossary`.

The new section must:

- Open with a brief sentence explaining that it lists preferred wording.
- Contain a markdown table with three rows:
    1. **"Consuming Asset"** (in the context of an asset consumed by a Dag
       run): preferred Polish is **"Zabierający zasób"**, avoid
       "Konsumujący zasób".
    2. **"Bulk clear / delete / update"** (toaster and button labels):
       preferred Polish is **"grupowy"** (with grammatical-form variants
       such as `grupowego`, `grupowej`, `grupowe`), avoid "masowy" /
       "masowego" / "masowej" / "masowe".
    3. **"Deactivated"** (Dag header status): preferred Polish is
       **"Deaktywowany"** (with gender variants `Deaktywowana` /
       `Deaktywowane`), avoid "Dezaktywowany".
- Close with notes explaining that "bulk <verb>" must take the grammatical
  form matching its noun, and that "Deaktywowany" must agree in gender
  with the noun it describes (e.g. neuter "zadanie" → "Deaktywowane").
- Mention each "avoided" term explicitly so future contributors can find
  the rule when searching.

### 4. Apply the glossary to existing translations

Two pre-existing toaster strings in
`airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json` currently
use the old "masowy" terminology and must be updated to use "grupowego":

- `toaster.bulkDelete.error` — currently uses "żądania masowego usunięcia",
  change to "żądania grupowego usunięcia".
- `toaster.bulkDelete.success.title` — currently uses "żądanie masowego
  usunięcia", change to "żądanie grupowego usunięcia".

The pre-existing description (`toaster.bulkDelete.success.description`) does
not contain "masowy" wording and is left as-is.

For the new `header.status.deactivated` key in `dag.json`, the value must
use the **"Deaktywowany"** form (not "Dezaktywowany").

## Files you must modify (exactly five)

- `.github/skills/airflow-translations/locales/pl.md`
- `airflow-core/src/airflow/ui/public/i18n/locales/pl/admin.json`
- `airflow-core/src/airflow/ui/public/i18n/locales/pl/common.json`
- `airflow-core/src/airflow/ui/public/i18n/locales/pl/components.json`
- `airflow-core/src/airflow/ui/public/i18n/locales/pl/dag.json`

Do **not** modify any English (`en/`) source files, any other locale, the
SKILL.md, or any code/config outside the JSON locale + glossary files.

## Style rules to follow

Read `.github/skills/airflow-translations/SKILL.md` and
`.github/skills/airflow-translations/locales/pl.md` for full conventions.
The most important rules:

- **Preserve every `{{variable}}` placeholder verbatim.** Do not translate
  variable names, do not remove placeholders. Word order may be reordered
  for natural Polish.
- **Polish diacritics must be preserved** (ą, ć, ę, ł, ń, ó, ś, ź, ż). Do
  not write ASCII transliterations like "bedą" or "polaczenie".
- **Apply gender / case agreement** correctly: noun gender must match
  associated adjectives and verb forms.
- **Keep terms that should remain in English untranslated**: `Airflow`,
  `Dag`, `XCom`, `Provider`, `REST API`, `JSON`, `ID`, etc.
- **Reuse established terminology** from the existing `pl/` files where
  the same English term has already been translated (consistency over
  novelty).
- **Maintain alphabetical ordering** of keys within each JSON object,
  matching the existing convention.
- **All four PL JSON files must remain valid JSON** after your edits
  (correct comma placement, no trailing commas, correct nesting).
