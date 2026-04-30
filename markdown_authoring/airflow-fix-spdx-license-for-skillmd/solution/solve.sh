#!/usr/bin/env bash
set -euo pipefail

cd /workspace/airflow

# Idempotency guard
if grep -qF "https://www.apache.org/licenses/LICENSE-2.0 -->" ".github/skills/airflow-translations/SKILL.md" && grep -qF "https://www.apache.org/licenses/LICENSE-2.0 -->" ".github/skills/airflow-translations/locales/zh-CN.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.github/skills/airflow-translations/SKILL.md b/.github/skills/airflow-translations/SKILL.md
@@ -7,7 +7,8 @@ description: >
   Covers Airflow terminology conventions and translation guidelines.
 license: Apache-2.0
 ---
-<!-- SPDX-License-Identifier: Apache-2.0 https://www.apache.org/licenses/LICENSE-2.0 -->
+<!-- SPDX-License-Identifier: Apache-2.0
+     https://www.apache.org/licenses/LICENSE-2.0 -->
 
 # Airflow Translations
 
diff --git a/.github/skills/airflow-translations/locales/zh-CN.md b/.github/skills/airflow-translations/locales/zh-CN.md
@@ -1,4 +1,6 @@
-<!-- SPDX-License-Identifier: Apache-2.0 https://www.apache.org/licenses/LICENSE-2.0 -->
+<!-- SPDX-License-Identifier: Apache-2.0
+     https://www.apache.org/licenses/LICENSE-2.0 -->
+
 # Simplified Chinese (zh-CN)
 
 This document provides locale-specific instructions for translating English
PATCH

echo "Gold patch applied."
