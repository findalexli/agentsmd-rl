FROM node:22.13.0-slim

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        git=1:2.39.5-0+deb12u2 \
        ca-certificates \
        python3 \
        python3-pip \
        python3-venv \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /opt/venv
ENV PATH="/opt/venv/bin:${PATH}"
RUN pip install --no-cache-dir pytest==8.3.4 pytest-json-report==1.5.0

WORKDIR /workspace
RUN git clone --filter=blob:none https://github.com/apache/superset.git /workspace/superset \
 && cd /workspace/superset \
 && git checkout 06818008c22162cc291ca30152354a0aa6dffd7c

# tsx + typescript globally so we can run buildQuery.ts directly without
# pulling the full superset-frontend npm workspace (gigabytes of deps).
RUN npm install -g --prefix /usr/local tsx@4.19.2 typescript@5.7.3

# Hand-rolled module stubs placed under /node_modules so Node's default
# resolution algorithm (walk-up from the importing file) finds them when
# buildQuery.ts at /workspace/superset/... does `import from '@superset-ui/core'`.
RUN mkdir -p /node_modules/@superset-ui/core \
 && mkdir -p /node_modules/@apache-superset/core

# @superset-ui/core stub — only the symbols buildQuery.ts uses.
# buildQueryContext is a thin pass-through that calls the user's callback
# with a baseQueryObject derived from formData and wraps the result.
RUN cat > /node_modules/@superset-ui/core/package.json <<'EOF'
{
  "name": "@superset-ui/core",
  "version": "0.0.0-stub",
  "main": "index.js",
  "types": "index.d.ts"
}
EOF

RUN cat > /node_modules/@superset-ui/core/index.js <<'EOF'
"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.buildQueryContext = function (formData, callback) {
  var baseQueryObject = {
    columns: formData.series ? [formData.series] : [],
    metrics: formData.metric ? [formData.metric] : [],
    row_limit: formData.row_limit,
    filters: [],
  };
  var queries = callback(baseQueryObject);
  return { queries: Array.isArray(queries) ? queries : [queries] };
};
exports.VizType = { WordCloud: "word_cloud" };
exports.seed = function () { return Math.random; };
exports.CategoricalColorNamespace = {};
EOF

RUN cat > /node_modules/@superset-ui/core/index.d.ts <<'EOF'
export type QueryFormOrderBy = [string | object, boolean];
export type QueryFormColumn = string | object;
export interface QueryFormData {
  datasource: string;
  granularity_sqla?: string;
  viz_type: string;
  metric?: any;
  sort_by_metric?: boolean;
  sort_by_series?: boolean;
  row_limit?: number;
  [key: string]: any;
}
export const VizType: { WordCloud: string };
export function buildQueryContext(
  formData: QueryFormData,
  callback: (baseQueryObject: any) => any
): { queries: any[] };
EOF

RUN cat > /node_modules/@apache-superset/core/package.json <<'EOF'
{ "name": "@apache-superset/core", "version": "0.0.0-stub", "main": "index.js" }
EOF
RUN cat > /node_modules/@apache-superset/core/index.js <<'EOF'
exports.t = function (s) { return s; };
EOF

# Test harness directory with the runner that calls buildQuery
RUN mkdir -p /harness
RUN cat > /harness/tsconfig.json <<'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "CommonJS",
    "moduleResolution": "node",
    "esModuleInterop": true,
    "allowSyntheticDefaultImports": true,
    "strict": false,
    "skipLibCheck": true,
    "resolveJsonModule": true
  }
}
EOF

# Runner: imports buildQuery, exercises it with several formData inputs,
# emits a JSON object with the resulting orderby and columns for each case.
RUN cat > /harness/run_buildquery.ts <<'EOF'
import buildQuery from "/workspace/superset/superset-frontend/plugins/plugin-chart-word-cloud/src/plugin/buildQuery";

type Case = { name: string; formData: any };

const cases: Case[] = [
  {
    name: "no_sort",
    formData: {
      datasource: "5__table",
      granularity_sqla: "ds",
      series: "foo",
      viz_type: "word_cloud",
      metric: "count",
      sort_by_metric: false,
      sort_by_series: false,
      row_limit: 100,
    },
  },
  {
    name: "metric_only",
    formData: {
      datasource: "5__table",
      granularity_sqla: "ds",
      series: "foo",
      viz_type: "word_cloud",
      metric: "count",
      sort_by_metric: true,
      sort_by_series: false,
      row_limit: 100,
    },
  },
  {
    name: "series_only",
    formData: {
      datasource: "5__table",
      granularity_sqla: "ds",
      series: "foo",
      viz_type: "word_cloud",
      metric: "count",
      sort_by_metric: false,
      sort_by_series: true,
      row_limit: 100,
    },
  },
  {
    name: "both_sorts",
    formData: {
      datasource: "5__table",
      granularity_sqla: "ds",
      series: "foo",
      viz_type: "word_cloud",
      metric: "count",
      sort_by_metric: true,
      sort_by_series: true,
      row_limit: 100,
    },
  },
  {
    name: "columns_check",
    formData: {
      datasource: "5__table",
      granularity_sqla: "ds",
      series: "foo",
      viz_type: "word_cloud",
    },
  },
  {
    name: "high_cardinality_metric",
    formData: {
      datasource: "9__table",
      granularity_sqla: "ds",
      series: "country",
      viz_type: "word_cloud",
      metric: "sum_population",
      sort_by_metric: true,
      sort_by_series: false,
      row_limit: 250,
    },
  },
];

const result: Record<string, any> = {};
for (const c of cases) {
  const ctx: any = buildQuery(c.formData);
  const q: any = ctx.queries[0];
  result[c.name] = {
    orderby: q.orderby === undefined ? null : q.orderby,
    columns: q.columns,
  };
}
process.stdout.write(JSON.stringify(result));
EOF

RUN mkdir -p /logs/verifier
