#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lightdash

# Idempotency guard
if grep -qF "packages/backend/src/models/CatalogModel/CLAUDE.md" "packages/backend/src/models/CatalogModel/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/packages/backend/src/models/CatalogModel/CLAUDE.md b/packages/backend/src/models/CatalogModel/CLAUDE.md
@@ -13,31 +13,3 @@ Its core responsibilities include:
 ## The `search` Method
 
 The `search` method is the main entry point for querying the data catalog. It is designed to handle complex filtering scenarios by combining multiple parameters into a single, efficient database query.
-
-### Filtering with `yamlTags`
-
-The `yamlTags` parameter provides a mechanism to filter catalog items based on tags defined in the project's dbt YAML files. This is primarily used to control exposure for AI features.
-
-The parameter accepts an array of strings (`string[] | null`):
-
--   If `yamlTags` is `null`, no tag-based filtering is applied. This corresponds to the "No tags configured in settings UI" scenario where everything is visible by default.
--   If `yamlTags` is an empty array (`[]`), the query will correctly return no results, as no item can match a tag from an empty set.
-
-#### Filtering Logic and Visibility Rules
-
-The filtering logic follows a specific set of rules to determine which catalog items (explores, tables, and fields) are visible.
-
-**No tags are configured in settings UI:**
-
-| Tagging Scenario                  | AI Visibility                    |
-| --------------------------------- | -------------------------------- |
-| No tags configured in settings UI | Everything is visible by default |
-
-**Tags are configured in settings UI:**
-
-| Tagging Scenario                     | AI Visibility             |
-| ------------------------------------ | ------------------------- |
-| Explore only (with matching tag)     | All fields in the Explore |
-| Some fields only (with matching tag) | Only those tagged fields  |
-| Explore + some fields (with match)   | Only those tagged fields  |
-| No matching tags                     | Nothing is visible        |
PATCH

echo "Gold patch applied."
