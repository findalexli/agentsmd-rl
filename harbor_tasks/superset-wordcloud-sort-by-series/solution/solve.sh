#!/usr/bin/env bash
set -euo pipefail

cd /workspace/superset

# Idempotency guard
if grep -q "if (sort_by_series && series)" \
    superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery.ts 2>/dev/null; then
  echo "Patch already applied"
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery.ts b/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery.ts
index faf816d5eca4..e90aab66ed76 100644
--- a/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery.ts
+++ b/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery.ts
@@ -21,7 +21,8 @@ import { buildQueryContext, QueryFormOrderBy } from '@superset-ui/core';
 import { WordCloudFormData } from '../types';

 export default function buildQuery(formData: WordCloudFormData) {
-  const { metric, sort_by_metric, series, row_limit } = formData;
+  const { metric, sort_by_metric, sort_by_series, series, row_limit } =
+    formData;
   const orderby: QueryFormOrderBy[] = [];
   const shouldApplyOrderBy =
     row_limit !== undefined && row_limit !== null && row_limit !== 0;
@@ -29,7 +30,7 @@ export default function buildQuery(formData: WordCloudFormData) {
   if (sort_by_metric && metric) {
     orderby.push([metric, false]);
   }
-  if (series) {
+  if (sort_by_series && series) {
     orderby.push([series, true]);
   }

diff --git a/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/controlPanel.tsx b/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/controlPanel.tsx
index 9098a282c08c..98e5e624b7f5 100644
--- a/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/controlPanel.tsx
+++ b/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/controlPanel.tsx
@@ -35,6 +35,22 @@ const config: ControlPanelConfig = {
         ['adhoc_filters'],
         ['row_limit'],
         ['sort_by_metric'],
+        [
+          {
+            name: 'sort_by_series',
+            config: {
+              type: 'CheckboxControl',
+              label: t('Sort by series'),
+              default: false,
+              description: t(
+                'Sort results by series name in ascending order. ' +
+                  'When combined with "Sort by metric", this acts as a tiebreaker ' +
+                  'for equal metric values. Adding this sort may reduce query ' +
+                  'performance on some databases.',
+              ),
+            },
+          },
+        ],
       ],
     },
     {
diff --git a/superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts b/superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts
index c83f8993e81b..7ce8cab7be1a 100644
--- a/superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts
+++ b/superset-frontend/plugins/plugin-chart-word-cloud/test/buildQuery.test.ts
@@ -21,17 +21,70 @@ import { VizType } from '@superset-ui/core';
 import { WordCloudFormData } from '../src';
 import buildQuery from '../src/plugin/buildQuery';

-describe('WordCloud buildQuery', () => {
-  const formData: WordCloudFormData = {
-    datasource: '5__table',
-    granularity_sqla: 'ds',
-    series: 'foo',
-    viz_type: VizType.WordCloud,
-  };
+const basicFormData: WordCloudFormData = {
+  datasource: '5__table',
+  granularity_sqla: 'ds',
+  series: 'foo',
+  viz_type: VizType.WordCloud,
+};

-  test('should build columns from series in form data', () => {
-    const queryContext = buildQuery(formData);
-    const [query] = queryContext.queries;
-    expect(query.columns).toEqual(['foo']);
+describe('plugin-chart-word-cloud', () => {
+  describe('buildQuery', () => {
+    test('should build columns from series in form data', () => {
+      const queryContext = buildQuery(basicFormData);
+      const [query] = queryContext.queries;
+      expect(query.columns).toEqual(['foo']);
+    });
+
+    test('should not include orderby when neither sort option is enabled', () => {
+      const queryContext = buildQuery({
+        ...basicFormData,
+        metric: 'count',
+        sort_by_metric: false,
+        sort_by_series: false,
+        row_limit: 100,
+      });
+      const [query] = queryContext.queries;
+      expect(query.orderby).toBeUndefined();
+    });
+
+    test('should order by metric DESC only when sort_by_metric is true', () => {
+      const queryContext = buildQuery({
+        ...basicFormData,
+        metric: 'count',
+        sort_by_metric: true,
+        sort_by_series: false,
+        row_limit: 100,
+      });
+      const [query] = queryContext.queries;
+      expect(query.orderby).toEqual([['count', false]]);
+    });
+
+    test('should order by series ASC only when sort_by_series is true', () => {
+      const queryContext = buildQuery({
+        ...basicFormData,
+        metric: 'count',
+        sort_by_metric: false,
+        sort_by_series: true,
+        row_limit: 100,
+      });
+      const [query] = queryContext.queries;
+      expect(query.orderby).toEqual([['foo', true]]);
+    });
+
+    test('should order by metric DESC then series ASC when both are true', () => {
+      const queryContext = buildQuery({
+        ...basicFormData,
+        metric: 'count',
+        sort_by_metric: true,
+        sort_by_series: true,
+        row_limit: 100,
+      });
+      const [query] = queryContext.queries;
+      expect(query.orderby).toEqual([
+        ['count', false],
+        ['foo', true],
+      ]);
+    });
   });
 });
diff --git a/superset/migrations/versions/2026-04-13_19-28_fd0c8583b46d_add_sort_by_series_to_word_cloud_charts.py b/superset/migrations/versions/2026-04-13_19-28_fd0c8583b46d_add_sort_by_series_to_word_cloud_charts.py
new file mode 100644
index 000000000000..bf66a2264f32
--- /dev/null
+++ b/superset/migrations/versions/2026-04-13_19-28_fd0c8583b46d_add_sort_by_series_to_word_cloud_charts.py
@@ -0,0 +1,89 @@
+# Licensed to the Apache Software Foundation (ASF) under one
+# or more contributor license agreements.  See the NOTICE file
+# distributed with this work for additional information
+# regarding copyright ownership.  The ASF licenses this file
+# to you under the Apache License, Version 2.0 (the
+# "License"); you may not use this file except in compliance
+# with the License.  You may obtain a copy of the License at
+#
+#   http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing,
+# software distributed under the License is distributed on an
+# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
+# KIND, either express or implied.  See the License for the
+# specific language governing permissions and limitations
+# under the License.
+"""add sort_by_series to word_cloud charts
+
+Revision ID: fd0c8583b46d
+Revises: ce6bd21901ab
+Create Date: 2026-04-13 19:28:19.021839
+
+"""
+
+from alembic import op
+from sqlalchemy import Column, Integer, String, Text
+from sqlalchemy.ext.declarative import declarative_base
+
+from superset import db
+from superset.migrations.shared.utils import paginated_update
+from superset.utils import json
+
+# revision identifiers, used by Alembic.
+revision = "fd0c8583b46d"
+down_revision = "ce6bd21901ab"
+
+Base = declarative_base()
+
+
+class Slice(Base):
+    __tablename__ = "slices"
+    id = Column(Integer, primary_key=True)
+    viz_type = Column(String(250))
+    params = Column(Text)
+
+
+def upgrade_params(params: dict) -> dict:
+    if "sort_by_series" not in params:
+        params["sort_by_series"] = True
+    return params
+
+
+def downgrade_params(params: dict) -> dict:
+    params.pop("sort_by_series", None)
+    return params
+
+
+def upgrade():
+    bind = op.get_bind()
+    session = db.Session(bind=bind)
+
+    for slc in paginated_update(
+        session.query(Slice).filter(Slice.viz_type == "word_cloud")
+    ):
+        try:
+            params = json.loads(slc.params or "{}")
+            if not isinstance(params, dict):
+                continue
+            slc.params = json.dumps(upgrade_params(params))
+        except (json.JSONDecodeError, TypeError):
+            continue
+    session.close()
+
+
+def downgrade():
+    bind = op.get_bind()
+    session = db.Session(bind=bind)
+
+    for slc in paginated_update(
+        session.query(Slice).filter(Slice.viz_type == "word_cloud")
+    ):
+        try:
+            params = json.loads(slc.params or "{}")
+            if not isinstance(params, dict):
+                continue
+            slc.params = json.dumps(downgrade_params(params))
+        except (json.JSONDecodeError, TypeError):
+            continue
+    session.close()
PATCH

echo "Gold patch applied successfully"
