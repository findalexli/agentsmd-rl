#!/usr/bin/env bash
set -euo pipefail

cd /workspace/lightdash

# Idempotency guard
if grep -qF "Dashboards arrange charts and content in a grid layout. See [Dashboard Reference" "skills/developing-in-lightdash/SKILL.md" && grep -qF "4. **Flip colors appropriately**: Use `flipColors: true` for metrics where incre" "skills/developing-in-lightdash/resources/big-number-chart-reference.md" && grep -qF "For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0." "skills/developing-in-lightdash/resources/cartesian-chart-reference.md" && grep -qF "| `table` | Data tables with column formatting and conditional styling | [Table " "skills/developing-in-lightdash/resources/chart-types-reference.md" && grep -qF "**Warning:** The delete command will warn you if any charts being deleted are re" "skills/developing-in-lightdash/resources/cli-reference.md" && grep -qF "For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0." "skills/developing-in-lightdash/resources/custom-viz-reference.md" && grep -qF "Filters with no default value (`values: []`) mean \"any value\" - the filter is vi" "skills/developing-in-lightdash/resources/dashboard-best-practices.md" && grep -qF "For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0." "skills/developing-in-lightdash/resources/funnel-chart-reference.md" && grep -qF "For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0." "skills/developing-in-lightdash/resources/gauge-chart-reference.md" && grep -qF "> For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1." "skills/developing-in-lightdash/resources/map-chart-reference.md" && grep -qF "> **Schema Reference**: For the complete schema definition, see [chart-as-code-1" "skills/developing-in-lightdash/resources/pie-chart-reference.md" && grep -qF "1. **Freeze identifier columns**: Keep key columns like IDs or names frozen for " "skills/developing-in-lightdash/resources/table-chart-reference.md" && grep -qF "For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0." "skills/developing-in-lightdash/resources/treemap-chart-reference.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/developing-in-lightdash/SKILL.md b/skills/developing-in-lightdash/SKILL.md
@@ -5,662 +5,278 @@ description: Build, configure, and deploy Lightdash analytics projects. Supports
 
 # Developing in Lightdash
 
-Build, configure, and deploy Lightdash analytics projects. Supports both **dbt projects** (Lightdash metadata embedded in dbt YAML) and **pure Lightdash YAML projects** (standalone semantic layer without dbt). Create metrics, dimensions, charts, and dashboards using the Lightdash CLI.
+Build and deploy Lightdash analytics projects. This skill covers the **semantic layer** (metrics, dimensions, joins) and **content** (charts, dashboards).
 
-## Capabilities
+## What You Can Do
 
-This skill enables you to:
+| Task | Commands | References |
+|------|----------|------------|
+| Define metrics & dimensions | Edit dbt YAML or Lightdash YAML | [Metrics](./resources/metrics-reference.md), [Dimensions](./resources/dimensions-reference.md) |
+| Create charts | `lightdash download`, edit YAML, `lightdash upload` | [Chart Types](#chart-types) |
+| Build dashboards | `lightdash download`, edit YAML, `lightdash upload` | [Dashboard Reference](./resources/dashboard-reference.md) |
+| Deploy changes | `lightdash deploy` (semantic layer), `lightdash upload` (content) | [CLI Reference](./resources/cli-reference.md) |
+| Test changes | `lightdash preview` | [Workflows](./resources/workflows-reference.md) |
 
-- **dbt Model Development**: Create and update dbt models with Lightdash metadata (dimensions, metrics, joins)
-- **Pure Lightdash YAML**: Define semantic layers directly without dbt
-- **Chart Creation**: Build and customize all chart types (bar, line, pie, funnel, table, big number, etc.)
-- **Dashboard Design**: Create multi-tile dashboards with filters, tabs, and interactive elements
-- **CLI Operations**: Deploy, preview, validate, and manage Lightdash projects
+## Before You Start
 
-## Project Types
+### Check Your Target Project
 
-**Before working with any Lightdash project, detect which type it is.** There are two types:
-
-| Type | Detection | YAML Syntax | Workflow |
-|------|-----------|-------------|----------|
-| **dbt Project** | Has `dbt_project.yml` | Metadata nested under `meta:` | Requires dbt compilation |
-| **Pure Lightdash** | Has `lightdash.config.yml`, no dbt | Top-level properties | Use `lightdash lint` |
-
-### How to Detect
+**Always verify which project you're deploying to.** Deploying to the wrong project can overwrite production content.
 
 ```bash
-# Check for dbt project
-ls dbt_project.yml 2>/dev/null && echo "dbt project" || echo "Not dbt"
-
-# Check for pure Lightdash
-ls lightdash.config.yml 2>/dev/null && echo "Pure Lightdash" || echo "Not pure Lightdash"
-```
-
-### Pure Lightdash YAML Projects
-
-For teams without dbt, Lightdash YAML lets you define the semantic layer directly. See `examples/snowflake-template/` for a reference project.
-
-**Project structure:**
-```
-project/
-├── lightdash.config.yml    # Required: warehouse configuration
-└── lightdash/
-    └── models/
-        └── users.yml       # Model definitions
-```
-
-**Config file** (`lightdash.config.yml`):
-```yaml
-warehouse:
-  type: snowflake  # or postgres, bigquery, redshift, databricks, trino
-```
-
-**Model file** (`lightdash/models/users.yml`):
-```yaml
-# Metadata - top level, NOT nested under meta
-type: model
-name: users
-sql_from: 'DB.SCHEMA.USERS'  # Fully qualified table name
-
-metrics:
-  user_count:
-    type: count_distinct
-    sql: ${TABLE}.USER_ID
-    description: Total unique users
+# Check current project
+lightdash config get-project
 
-dimensions:
-  - name: subscription_type
-    sql: ${TABLE}.SUBSCRIPTION
-    type: string
+# List available projects
+lightdash config list-projects
 
-  - name: signed_up_at
-    sql: ${TABLE}.SIGNED_UP
-    type: date
-    time_intervals:
-      - DAY
-      - WEEK
-      - MONTH
+# Switch to correct project
+lightdash config set-project --name "My Project"
 ```
 
-**Workflow for pure Lightdash:**
-```bash
-# 1. Validate YAML syntax locally (important - do this before deploying!)
-lightdash lint
-
-# 2. Deploy to create new project
-lightdash deploy --create "Project Name" --no-warehouse-credentials
-
-# 3. Deploy updates to existing project
-lightdash deploy --no-warehouse-credentials
-```
+### Detect Your Project Type
 
-### dbt Projects with Lightdash
+**The YAML syntax differs significantly between project types.**
 
-For dbt projects, Lightdash metadata is embedded in dbt YAML files under `meta:` tags.
+| Type | Detection | Key Difference |
+|------|-----------|----------------|
+| **dbt Project** | Has `dbt_project.yml` | Metadata nested under `meta:` |
+| **Pure Lightdash** | Has `lightdash.config.yml`, no dbt | Top-level properties |
 
-**Workflow for dbt projects:**
 ```bash
-# Option A: Let Lightdash compile dbt
-lightdash deploy
-
-# Option B: Compile dbt separately, then deploy with existing manifest
-dbt compile
-lightdash deploy --skip-dbt-compile
-```
-
-### Key Syntax Differences
-
-| Property | dbt YAML | Pure Lightdash YAML |
-|----------|----------|---------------------|
-| Metrics | Nested under `meta:` | Top-level `metrics:` |
-| Dimensions | Under `columns.[].meta.dimension:` | Top-level `dimensions:` array |
-| Table reference | Uses dbt model ref | `sql_from:` with full table name |
-| Joins | Under `meta.joins:` | Top-level `joins:` |
-
-## Workflow Components
-
-| Command | What It Does |
-|---------|--------------|
-| `lightdash deploy` | Compiles dbt models and syncs schema to Lightdash |
-| `lightdash upload` | Uploads chart/dashboard YAML files to Lightdash |
-| `lightdash download` | Downloads charts/dashboards as YAML files |
-| `lightdash preview` | Creates a temporary project for testing |
-| `lightdash validate` | Validates project against Lightdash server |
-| `lightdash lint` | Validates YAML files locally (offline) |
-
-### Key Concepts
-
-**dbt Target**: `lightdash deploy` uses `--target` to determine which warehouse schemas to use. Check with `dbt debug` before deploying.
-
-**Credentials**: Only `deploy --create` uploads credentials from dbt profiles. Deploying to existing projects does NOT update credentials. In CI (`CI=true`), permission prompts are auto-approved.
-
-**Preview**: `lightdash preview` creates a temporary, isolated project using your current dbt target's schemas.
-
-## Common Workflow Patterns
-
-| Pattern | Description | When to Use |
-|---------|-------------|-------------|
-| **Direct Deployment** | `deploy` + `upload` straight to project | Solo dev, rapid iteration |
-| **Preview-First** | Test in `preview`, then deploy to main | Team, complex changes |
-| **CI/CD Pipeline** | Automated deploy on merge to main | PRs, reproducible deploys |
-| **PR Previews** | Create preview per pull request | Review workflows |
-| **Download-Edit-Upload** | Pull UI content into code | Migrating to GitOps |
-| **Multi-Environment** | Separate dev/staging/prod projects | Formal promotion process |
-
-### Detecting Your Workflow
-
-| Clue in Repository | Likely Pattern |
-|--------------------|----------------|
-| `.github/workflows/` with Lightdash steps | CI/CD Pipeline |
-| `lightdash/` directory with YAML files | Code-based content |
-| Multiple projects configured | Multi-Environment |
-| No CI, small team | Direct Deployment |
-
-See [Workflows Reference](./resources/workflows-reference.md) for detailed examples and CI/CD configurations.
-
-### Exploring the Warehouse with SQL
-
-When creating or editing dbt models and YAML files, use `lightdash sql` to explore the warehouse directly. This is invaluable for:
-
-- **Discovering available columns**: Query `INFORMATION_SCHEMA` or run `SELECT *` with a limit to see what data exists
-- **Testing SQL snippets**: Validate custom SQL for metrics or dimensions before adding to YAML
-- **Verifying data types**: Check column types to choose the right dimension/metric configurations
-- **Exploring relationships**: Investigate foreign keys and join conditions between tables
-
-**Example exploration workflow:**
-
-```bash
-# See what tables exist (PostgreSQL/Redshift)
-lightdash sql "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'" -o tables.csv
-
-# Explore columns in a table (PostgreSQL/Redshift)
-lightdash sql "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'orders'" -o columns.csv
-
-# Preview data to understand the schema
-lightdash sql "SELECT * FROM orders LIMIT 5" -o preview.csv
-
-# Test a metric calculation before adding to YAML
-lightdash sql "SELECT customer_id, SUM(amount) as total_spent FROM orders GROUP BY 1 LIMIT 10" -o test.csv
-
-# Check distinct values for a potential dimension
-lightdash sql "SELECT DISTINCT status FROM orders" -o statuses.csv
+# Quick detection
+ls dbt_project.yml 2>/dev/null && echo "dbt project" || echo "Not dbt"
+ls lightdash.config.yml 2>/dev/null && echo "Pure Lightdash" || echo "Not pure Lightdash"
 ```
 
-**Tip:** The SQL runner uses credentials from your current Lightdash project, so you're querying the same warehouse that Lightdash uses. This ensures your explorations match what will work in production.
-
-## Quick Reference
-
-### dbt YAML Structure
+### Syntax Comparison
 
+**dbt YAML** (metadata under `meta:`):
 ```yaml
-version: 2
-
 models:
   - name: orders
-    description: "Order transactions"
     meta:
-      label: "Orders"
-      order_fields_by: "label"  # or "index"
-      group_label: "Sales"
-
-      # Joins to other models
-      joins:
-        - join: customers
-          sql_on: "${orders.customer_id} = ${customers.customer_id}"
-          type: left  # inner, left, right, full
-
-      # Model-level metrics
       metrics:
         total_revenue:
           type: sum
           sql: "${TABLE}.amount"
-          description: "Total order revenue"
-          format: "usd"
-
     columns:
-      - name: order_id
-        description: "Primary key"
+      - name: status
         meta:
           dimension:
             type: string
-            hidden: false
-
-      - name: amount
-        description: "Order amount in USD"
-        meta:
-          dimension:
-            type: number
-            format: "usd"
-          metrics:
-            total_amount:
-              type: sum
-            average_amount:
-              type: average
-              round: 2
-
-      - name: created_at
-        description: "Order timestamp"
-        meta:
-          dimension:
-            type: timestamp
-            time_intervals:
-              - DAY
-              - WEEK
-              - MONTH
-              - YEAR
 ```
 
-### Metric Types
-
-| Type | Description | Example |
-|------|-------------|---------|
-| `count` | Count all rows | Total orders |
-| `count_distinct` | Count unique values | Unique customers |
-| `sum` | Sum numeric values | Total revenue |
-| `average` | Average of values | Avg order value |
-| `min` | Minimum value | First order date |
-| `max` | Maximum value | Largest order |
-| `percentile` | Percentile (requires `percentile: 95`) | P95 response time |
-| `median` | Median value | Median order value |
-| `number` | Custom SQL returning number | `sql: "SUM(${amount}) / COUNT(*)"` |
-
-### Dimension Types
-
-| Type | Description |
-|------|-------------|
-| `string` | Text values |
-| `number` | Numeric values |
-| `boolean` | True/false |
-| `date` | Date only |
-| `timestamp` | Date and time |
-
-### Time Intervals
-
-For `timestamp` and `date` dimensions:
-- `RAW`, `YEAR`, `QUARTER`, `MONTH`, `WEEK`, `DAY`
-- `HOUR`, `MINUTE`, `SECOND` (timestamp only)
-- `YEAR_NUM`, `MONTH_NUM`, `DAY_OF_WEEK_INDEX` (numeric extractions)
-- `MONTH_NAME`, `DAY_OF_WEEK_NAME` (text extractions)
-
-### Join Configuration
-
+**Pure Lightdash YAML** (top-level):
 ```yaml
-joins:
-  - join: customers           # Model name to join
-    sql_on: "${orders.customer_id} = ${customers.customer_id}"
-    type: left                # inner, left, right, full
-    alias: customer           # Optional alias
-    label: "Customer Info"    # Display label
-    hidden: false             # Hide from UI
-    always: false             # Always include in queries
-    relationship: many-to-one # one-to-one, one-to-many, many-to-one, many-to-many
-    fields:                   # Limit which fields to include
-      - name
-      - email
-```
-
-## CLI Commands
-
-### Authentication
-
-```bash
-# Login to Lightdash instance
-lightdash login https://app.lightdash.cloud
-
-# Login with token (non-interactive)
-lightdash login https://app.lightdash.cloud --token YOUR_API_TOKEN
-
-# List available projects (excludes preview projects)
-lightdash config list-projects
+type: model
+name: orders
+sql_from: 'DB.SCHEMA.ORDERS'
 
-# Show currently selected project
-lightdash config get-project
+metrics:
+  total_revenue:
+    type: sum
+    sql: ${TABLE}.amount
 
-# Set active project
-lightdash config set-project --name "My Project"
-lightdash config set-project --uuid abc123-def456
+dimensions:
+  - name: status
+    sql: ${TABLE}.STATUS
+    type: string
 ```
 
-### Compilation & Deployment
+## Core Workflows
 
-```bash
-# Compile dbt models and validate
-lightdash compile --project-dir ./dbt --profiles-dir ./profiles
+### Editing Metrics & Dimensions
 
-# Deploy to Lightdash
-lightdash deploy --project-dir ./dbt --profiles-dir ./profiles
+1. **Find the model YAML file** (dbt: `models/*.yml`, pure Lightdash: `lightdash/models/*.yml`)
+2. **Edit metrics/dimensions** using the appropriate syntax for your project type
+3. **Validate**: `lightdash lint` (pure Lightdash) or `dbt compile` (dbt projects)
+4. **Deploy**: `lightdash deploy`
 
-# Create new project on deploy
-lightdash deploy --create "New Project Name"
+See [Metrics Reference](./resources/metrics-reference.md) and [Dimensions Reference](./resources/dimensions-reference.md) for configuration options.
 
-# Deploy ignoring validation errors
-lightdash deploy --ignore-errors
-
-# Skip dbt compilation (use existing manifest)
-lightdash deploy --skip-dbt-compile
-```
+### Editing Charts
 
-### Preview Projects
+1. **Download**: `lightdash download --charts chart-slug`
+2. **Edit** the YAML file in `lightdash/` directory
+3. **Upload**: `lightdash upload --charts chart-slug`
 
-```bash
-# Create preview environment (watches for changes)
-lightdash preview --name "feature-branch-preview"
+### Editing Dashboards
 
-# Start preview without watching
-lightdash start-preview --name "my-preview"
+1. **Download**: `lightdash download --dashboards dashboard-slug`
+2. **Edit** the YAML file in `lightdash/` directory
+3. **Upload**: `lightdash upload --dashboards dashboard-slug`
 
-# Stop preview
-lightdash stop-preview --name "my-preview"
-```
+### Creating New Content
 
-### Generate YAML
+Charts and dashboards are typically created in the UI first, then managed as code:
 
-```bash
-# Generate schema for all models
-lightdash generate
+1. Create in UI
+2. `lightdash download` to pull as YAML
+3. Edit and version control
+4. `lightdash upload` to sync changes
 
-# Generate for specific models
-lightdash generate -s my_model
-lightdash generate -s tag:sales
-lightdash generate -s +my_model  # Include parents
-```
+### Testing with Preview
 
-### Validation
+For larger changes, test in isolation:
 
 ```bash
-# Lint chart and dashboard YAML files
-lightdash lint --path ./lightdash
-
-# Validate against Lightdash server
-lightdash validate --project my-project-uuid
-
-# Output lint results as JSON/SARIF
-lightdash lint --format json
+lightdash preview --name "my-feature"
+# Make changes and iterate
+lightdash stop-preview --name "my-feature"
 ```
 
-### Download & Upload Content
-
-```bash
-# Download all charts and dashboards
-lightdash download
-
-# Download specific content
-lightdash download --charts chart-slug-1 chart-slug-2
-lightdash download --dashboards dashboard-slug
-
-# Download with nested folder structure
-lightdash download --nested
+## CLI Quick Reference
 
-# Upload modified content
-lightdash upload
+| Command | Purpose |
+|---------|---------|
+| `lightdash deploy` | Sync semantic layer (metrics, dimensions) |
+| `lightdash upload` | Upload charts/dashboards |
+| `lightdash download` | Download charts/dashboards as YAML |
+| `lightdash lint` | Validate YAML locally |
+| `lightdash preview` | Create temporary test project |
+| `lightdash sql "..." -o file.csv` | Run SQL queries against warehouse |
 
-# Force upload (ignore timestamps)
-lightdash upload --force
+See [CLI Reference](./resources/cli-reference.md) for full command documentation.
 
-# Upload specific items
-lightdash upload --charts my-chart --dashboards my-dashboard
-```
-
-### Delete Content
+## Semantic Layer Overview
 
-Permanently delete charts and dashboards from the server and remove their local YAML files. This action cannot be undone.
+The semantic layer defines your data model: what can be queried and how.
 
-```bash
-# Delete a chart by slug
-lightdash delete -c my-chart
+### Tables (Explores)
 
-# Delete a dashboard by slug
-lightdash delete -d my-dashboard
+Tables are dbt models or Lightdash YAML models that define queryable entities.
 
-# Delete multiple items at once
-lightdash delete -c chart1 chart2 -d dashboard1
-
-# Delete by UUID
-lightdash delete -c abc123-def456
+```yaml
+# dbt example
+models:
+  - name: orders
+    meta:
+      label: "Orders"
+      joins:
+        - join: customers
+          sql_on: "${orders.customer_id} = ${customers.customer_id}"
+```
 
-# Delete by URL
-lightdash delete -c "https://app.lightdash.cloud/projects/xxx/saved/abc123"
+See [Tables Reference](./resources/tables-reference.md) for all options.
 
-# Skip confirmation prompt (use with caution)
-lightdash delete -c my-chart --force
+### Metrics
 
-# Use custom path for local files
-lightdash delete -c my-chart --path ./custom-lightdash
+Aggregated calculations (sum, count, average, etc.) on your data.
 
-# Delete from a specific project
-lightdash delete -c my-chart --project <project-uuid>
+```yaml
+metrics:
+  total_revenue:
+    type: sum
+    sql: "${TABLE}.amount"
+    format: "usd"
 ```
 
-**Options:**
-- `-c, --charts <charts...>` - Chart slugs, UUIDs, or URLs to delete
-- `-d, --dashboards <dashboards...>` - Dashboard slugs, UUIDs, or URLs to delete
-- `-f, --force` - Skip confirmation prompt
-- `-p, --path <path>` - Custom path where local chart-as-code files are stored
-- `--project <uuid>` - Specify a project UUID
-
-**Warning:** The delete command will warn you if any charts being deleted are referenced by dashboards. Those dashboard tiles will break after deletion.
-
-### SQL Runner
+**Common types:** `count`, `count_distinct`, `sum`, `average`, `min`, `max`, `number` (custom SQL)
 
-Execute raw SQL queries against the warehouse using the current project's credentials. Results are exported to CSV.
-
-```bash
-# Run a query and save results to CSV
-lightdash sql "SELECT * FROM orders LIMIT 10" -o results.csv
+See [Metrics Reference](./resources/metrics-reference.md) for all types and options.
 
-# Limit rows returned
-lightdash sql "SELECT * FROM customers" -o customers.csv --limit 1000
+### Dimensions
 
-# Adjust pagination for large results (default 500, max 5000)
-lightdash sql "SELECT * FROM events" -o events.csv --page-size 2000
+Attributes for grouping and filtering data.
 
-# Verbose output for debugging
-lightdash sql "SELECT COUNT(*) FROM users" -o count.csv --verbose
+```yaml
+columns:
+  - name: created_at
+    meta:
+      dimension:
+        type: timestamp
+        time_intervals: [DAY, WEEK, MONTH, YEAR]
 ```
 
-**Options:**
-- `<query>` - SQL query to execute (required)
-- `-o, --output <file>` - Output CSV file path (required)
-- `--limit <number>` - Maximum rows to return
-- `--page-size <number>` - Rows per page (default: 500, max: 5000)
-- `--verbose` - Show detailed output
-
-**Note:** Uses the warehouse credentials from your currently selected Lightdash project. Run `lightdash config get-project` to see which project is active.
-
-## Chart Configuration
+**Types:** `string`, `number`, `boolean`, `date`, `timestamp`
 
-### Chart Types
+See [Dimensions Reference](./resources/dimensions-reference.md) for all options including time intervals.
 
-Lightdash supports 9 chart types. Each has detailed configuration options documented in its own reference file:
-
-| Type | Description | Reference |
-|------|-------------|-----------|
-| `cartesian` | Bar, line, area, scatter charts | [Cartesian Chart Reference](./resources/cartesian-chart-reference.md) |
-| `pie` | Pie and donut charts | [Pie Chart Reference](./resources/pie-chart-reference.md) |
-| `table` | Data tables with formatting and conditional styling | [Table Chart Reference](./resources/table-chart-reference.md) |
-| `big_number` | Single KPI display with comparison | [Big Number Reference](./resources/big-number-chart-reference.md) |
-| `funnel` | Conversion funnel visualization | [Funnel Chart Reference](./resources/funnel-chart-reference.md) |
-| `gauge` | Gauge/dial visualization with colored sections | [Gauge Chart Reference](./resources/gauge-chart-reference.md) |
-| `treemap` | Hierarchical treemap | [Treemap Chart Reference](./resources/treemap-chart-reference.md) |
-| `map` | Geographic scatter, area, and heatmaps | [Map Chart Reference](./resources/map-chart-reference.md) |
-| `custom` | Custom Vega-Lite visualizations | [Custom Viz Reference](./resources/custom-viz-reference.md) |
-
-### Basic Chart YAML Structure
+### Joins
 
-All charts share this common structure. The `chartConfig` section varies by chart type.
+Connect related tables for cross-table analysis.
 
 ```yaml
-version: 1
-name: "Chart Name"
-slug: chart-slug
-spaceSlug: space-name
-tableName: explore_name
-description: "Optional description"
-
-metricQuery:
-  exploreName: explore_name
-  dimensions:
-    - dimension_field_id
-  metrics:
-    - metric_field_id
-  filters:
-    dimensions:
-      and:
-        - target:
-            fieldId: field_id
-          operator: equals
-          values:
-            - value
-  sorts:
-    - fieldId: field_id
-      descending: false
-  limit: 500
-
-chartConfig:
-  type: cartesian  # or pie, table, big_number, funnel, gauge, treemap, map, custom
-  config:
-    # Type-specific configuration - see individual references
+joins:
+  - join: customers
+    sql_on: "${orders.customer_id} = ${customers.customer_id}"
+    type: left
 ```
 
-See the chart type references above for detailed `chartConfig.config` options for each type.
+See [Joins Reference](./resources/joins-reference.md) for configuration options.
 
-## Dashboard Configuration
+## Chart Types
 
-```yaml
-version: 1
-name: "Sales Dashboard"
-slug: sales-dashboard
-spaceSlug: sales
-description: "Overview of sales performance"
-
-tiles:
-  # Chart tile
-  - type: saved_chart
-    x: 0
-    y: 0
-    w: 12
-    h: 6
-    properties:
-      chartSlug: monthly-revenue
-      title: "Revenue Trend"
-
-  # Markdown tile
-  - type: markdown
-    x: 0
-    y: 6
-    w: 6
-    h: 3
-    properties:
-      title: "Notes"
-      content: |
-        ## Key Insights
-        - Revenue up 15% MoM
-        - Focus on enterprise segment
-
-  # Big number (KPI)
-  - type: saved_chart
-    x: 6
-    y: 6
-    w: 3
-    h: 3
-    properties:
-      chartSlug: total-revenue-kpi
-
-tabs:
-  - uuid: "tab-1"
-    name: "Overview"
-    order: 0
-  - uuid: "tab-2"
-    name: "Details"
-    order: 1
-
-filters:
-  dimensions:
-    - target:
-        fieldId: orders_created_at_month
-        tableName: orders
-      operator: inThePast
-      values: [12]
-      settings:
-        unitOfTime: months
-        completed: true
-```
+Lightdash supports 9 chart types. Each has a dedicated reference:
 
-## Best Practices
+| Type | Use Case | Reference |
+|------|----------|-----------|
+| `cartesian` | Bar, line, area, scatter | [Cartesian](./resources/cartesian-chart-reference.md) |
+| `pie` | Parts of whole | [Pie](./resources/pie-chart-reference.md) |
+| `table` | Data tables | [Table](./resources/table-chart-reference.md) |
+| `big_number` | KPIs | [Big Number](./resources/big-number-chart-reference.md) |
+| `funnel` | Conversion funnels | [Funnel](./resources/funnel-chart-reference.md) |
+| `gauge` | Progress indicators | [Gauge](./resources/gauge-chart-reference.md) |
+| `treemap` | Hierarchical data | [Treemap](./resources/treemap-chart-reference.md) |
+| `map` | Geographic data | [Map](./resources/map-chart-reference.md) |
+| `custom` | Vega-Lite | [Custom Viz](./resources/custom-viz-reference.md) |
 
-### Metrics
+See individual chart type references for YAML structure and configuration options.
 
-1. **Use descriptive names**: `total_revenue` not `sum1`
-2. **Add descriptions**: Help users understand what metrics measure
-3. **Set appropriate rounding**: Use `round: 2` for currency
-4. **Format for readability**: Use `format: "usd"` or `compact: "millions"`
-5. **Define `show_underlying_values`**: List fields users can drill into
+## Dashboards
 
-### Dimensions
+Dashboards arrange charts and content in a grid layout. See [Dashboard Reference](./resources/dashboard-reference.md) for YAML structure, tile types, tabs, and filters.
 
-1. **Choose correct types**: Use `timestamp` for datetime, `date` for date-only
-2. **Configure time intervals**: Only include intervals users need
-3. **Group related fields**: Use `group_label` for organization
-4. **Add colors**: Map categorical values to consistent colors
+## Exploring the Warehouse
 
-### Joins
+Use `lightdash sql` to explore data when building models:
 
-1. **Specify relationships**: Helps Lightdash optimize queries
-2. **Use descriptive labels**: Clear join names in the UI
-3. **Limit fields**: Use `fields` to reduce clutter
-4. **Choose correct join type**: `left` preserves base table rows
+```bash
+# Preview table structure
+lightdash sql "SELECT * FROM orders LIMIT 5" -o preview.csv
 
-### Charts
+# Check distinct values for a dimension
+lightdash sql "SELECT DISTINCT status FROM orders" -o statuses.csv
 
-1. **Sort data logically**: Time ascending, rankings descending
-2. **Limit data points**: Use appropriate limits (avoid 10,000+ rows)
-3. **Use filters**: Pre-filter to relevant data
-4. **Match chart to data**: Line for trends, bar for comparisons, pie for parts-of-whole
+# Test metric calculations
+lightdash sql "SELECT SUM(amount) FROM orders" -o test.csv
+```
 
-### Dashboards
+## Workflow Patterns
 
-1. **Organize with tabs**: Group related charts
-2. **Use markdown for context**: Explain insights
-3. **Set dashboard filters**: Allow users to slice data
-4. **Consistent sizing**: Align tiles to grid
+| Pattern | When to Use |
+|---------|-------------|
+| **Direct** (`deploy` + `upload`) | Solo dev, rapid iteration |
+| **Preview-First** | Team, complex changes |
+| **CI/CD** | Automated on merge |
 
-## Resources
+See [Workflows Reference](./resources/workflows-reference.md) for detailed examples and CI/CD configurations.
 
-For detailed reference documentation:
+## Resources
 
 ### Semantic Layer
-- [Dimensions Reference](./resources/dimensions-reference.md) - Complete dimension configuration
-- [Metrics Reference](./resources/metrics-reference.md) - All metric types and options
-- [Tables Reference](./resources/tables-reference.md) - Table/model configuration
-- [Joins Reference](./resources/joins-reference.md) - Join configuration guide
-
-### Chart Types
-- [Cartesian Chart Reference](./resources/cartesian-chart-reference.md) - Bar, line, area, scatter charts
-- [Pie Chart Reference](./resources/pie-chart-reference.md) - Pie and donut charts
-- [Table Chart Reference](./resources/table-chart-reference.md) - Data tables with conditional formatting
-- [Big Number Reference](./resources/big-number-chart-reference.md) - KPI displays with comparison
-- [Funnel Chart Reference](./resources/funnel-chart-reference.md) - Conversion funnels
-- [Gauge Chart Reference](./resources/gauge-chart-reference.md) - Gauge/dial visualizations
-- [Treemap Chart Reference](./resources/treemap-chart-reference.md) - Hierarchical treemaps
-- [Map Chart Reference](./resources/map-chart-reference.md) - Geographic visualizations
-- [Custom Viz Reference](./resources/custom-viz-reference.md) - Vega-Lite custom charts
-
-### Dashboards & Workflows
-- [Dashboard Reference](./resources/dashboard-reference.md) - Dashboard configuration
-- [Workflows Reference](./resources/workflows-reference.md) - CI/CD and deployment patterns
+- [Dimensions Reference](./resources/dimensions-reference.md)
+- [Metrics Reference](./resources/metrics-reference.md)
+- [Tables Reference](./resources/tables-reference.md)
+- [Joins Reference](./resources/joins-reference.md)
 
-## JSON Schemas
-
-The skill includes JSON schemas for validation:
-
-- `chart-as-code-1.0.json` - Chart YAML validation
-- `dashboard-as-code-1.0.json` - Dashboard YAML validation
-- `model-as-code-1.0.json` - Model YAML validation
+### Charts
+- [Cartesian Chart Reference](./resources/cartesian-chart-reference.md) - Bar, line, area, scatter
+- [Pie Chart Reference](./resources/pie-chart-reference.md)
+- [Table Chart Reference](./resources/table-chart-reference.md)
+- [Big Number Reference](./resources/big-number-chart-reference.md)
+- [Funnel Chart Reference](./resources/funnel-chart-reference.md)
+- [Gauge Chart Reference](./resources/gauge-chart-reference.md)
+- [Treemap Chart Reference](./resources/treemap-chart-reference.md)
+- [Map Chart Reference](./resources/map-chart-reference.md)
+- [Custom Viz Reference](./resources/custom-viz-reference.md)
 
-## External Documentation
+### Dashboards & Workflows
+- [Dashboard Reference](./resources/dashboard-reference.md)
+- [Dashboard Best Practices](./resources/dashboard-best-practices.md)
+- [CLI Reference](./resources/cli-reference.md)
+- [Workflows Reference](./resources/workflows-reference.md)
 
-- [Lightdash Docs](https://docs.lightdash.com) - Official documentation
-- [Metrics Reference](https://docs.lightdash.com/references/metrics)
-- [Dimensions Reference](https://docs.lightdash.com/references/dimensions)
-- [Tables Reference](https://docs.lightdash.com/references/tables)
-- [Joins Reference](https://docs.lightdash.com/references/joins)
+### External
+- [Lightdash Docs](https://docs.lightdash.com)
diff --git a/skills/developing-in-lightdash/resources/big-number-chart-reference.md b/skills/developing-in-lightdash/resources/big-number-chart-reference.md
@@ -12,6 +12,10 @@ Big number charts (also called KPI displays) in Lightdash provide a prominent di
 
 Big number charts display a single numeric value prominently, with optional comparison to show change over time and customizable number formatting.
 
+## Schema Reference
+
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/bigNumber`.
+
 ## Basic Structure
 
 ```yaml
@@ -33,63 +37,32 @@ metricQuery:
 chartConfig:
   type: "big_number"
   config:
-    bigNumber:
-      selectedField: "my_explore_total_revenue"
-      label: "Total Revenue"
-      showBigNumberLabel: true
+    selectedField: "my_explore_total_revenue"
+    label: "Total Revenue"
+    showBigNumberLabel: true
 ```
 
-## Configuration Options
-
-### `bigNumber` (object, optional)
-
-The main configuration object for big number chart settings. All properties are optional.
-
-#### Core Settings
-
-- **`selectedField`** (string): Field ID to display as the big number. This should be a metric from your `metricQuery`.
-
-- **`label`** (string): Custom label for the big number. If not provided, the field name will be used.
-
-#### Display Settings
-
-- **`showBigNumberLabel`** (boolean): Whether to show the label above the number. Default is typically `true`.
-
-- **`showTableNamesInLabel`** (boolean): Whether to include the table name in the label (e.g., "Sales Metrics - Revenue" vs. "Revenue").
+## Key Configuration Properties
 
-#### Number Formatting
+The `config` object supports these key properties:
 
-- **`style`** (string): Number formatting style for compact notation. Converts large numbers to more readable formats.
-  - Options: `"thousands"`, `"millions"`, `"billions"`, `"trillions"`, `"K"`, `"M"`, `"B"`, `"T"`
-  - Examples:
-    - `"thousands"` or `"K"`: 1500 → 1.5K
-    - `"millions"` or `"M"`: 1500000 → 1.5M
-    - `"billions"` or `"B"`: 1500000000 → 1.5B
-    - `"trillions"` or `"T"`: 1500000000000 → 1.5T
-
-#### Comparison Settings
-
-- **`showComparison`** (boolean): Whether to show comparison with a previous value (period-over-period change).
-
-- **`comparisonFormat`** (string): Format for the comparison value.
-  - `"raw"`: Show absolute change (e.g., +500)
-  - `"percentage"`: Show percentage change (e.g., +12.5%)
-
-- **`comparisonLabel`** (string): Custom label for the comparison value (e.g., "vs. Last Month").
-
-- **`flipColors`** (boolean): Reverse the color scheme for comparison indicators. By default:
-  - Green = increase (positive change)
-  - Red = decrease (negative change)
-
-  When `flipColors: true`:
-  - Red = increase (useful for cost/error metrics where increases are bad)
-  - Green = decrease (useful for cost/error metrics where decreases are good)
+| Property | Type | Description |
+|----------|------|-------------|
+| `selectedField` | string | Field ID to display as the big number (should be a metric from your `metricQuery`) |
+| `label` | string | Custom label for the big number (defaults to field name if not provided) |
+| `showBigNumberLabel` | boolean | Whether to show the label above the number |
+| `showTableNamesInLabel` | boolean | Whether to include the table name in the label |
+| `style` | string | Number formatting style: `"K"`, `"M"`, `"B"`, `"T"` (or `"thousands"`, `"millions"`, `"billions"`, `"trillions"`) |
+| `showComparison` | boolean | Whether to show comparison with a previous value |
+| `comparisonFormat` | string | Format for comparison: `"raw"` (absolute change) or `"percentage"` |
+| `comparisonLabel` | string | Custom label for the comparison value (e.g., "vs. Last Month") |
+| `flipColors` | boolean | Reverse color scheme (red for increase, green for decrease) |
 
 ## Examples
 
-### Example 1: Basic KPI
+### Example 1: Basic KPI with Compact Formatting
 
-Simple big number showing total revenue:
+Simple big number showing total revenue in millions:
 
 ```yaml
 version: 1
@@ -110,122 +83,15 @@ metricQuery:
 chartConfig:
   type: "big_number"
   config:
-    bigNumber:
-      selectedField: "orders_total_revenue"
-      label: "Total Revenue"
-      showBigNumberLabel: true
-```
-
-### Example 2: Compact Number Formatting
-
-Display large numbers in millions with M suffix:
-
-```yaml
-version: 1
-name: "Monthly Active Users"
-slug: "monthly-active-users"
-spaceSlug: "product"
-tableName: "users"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "users_monthly_active_count"
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "big_number"
-  config:
-    bigNumber:
-      selectedField: "users_monthly_active_count"
-      label: "Monthly Active Users"
-      style: "M"  # Display as millions (e.g., 2.5M)
-      showBigNumberLabel: true
-```
-
-### Example 3: Period-over-Period Comparison (Percentage)
-
-Show current revenue with percentage change vs. previous period:
-
-```yaml
-version: 1
-name: "Revenue with Growth"
-slug: "revenue-growth"
-spaceSlug: "sales"
-tableName: "orders"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "orders_total_revenue"
-  filters:
-    - target:
-        fieldId: "orders_created_at"
-      operator: "inThePast"
-      values: [30]
-      settings:
-        unitOfTime: "days"
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "big_number"
-  config:
-    bigNumber:
-      selectedField: "orders_total_revenue"
-      label: "Monthly Revenue"
-      style: "M"
-      showBigNumberLabel: true
-      showComparison: true
-      comparisonFormat: "percentage"  # Show % change
-      comparisonLabel: "vs. Last Month"
-```
-
-### Example 4: Raw Value Comparison
-
-Show customer count with absolute change:
-
-```yaml
-version: 1
-name: "New Customers"
-slug: "new-customers"
-spaceSlug: "sales"
-tableName: "customers"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "customers_count"
-  filters:
-    - target:
-        fieldId: "customers_created_at"
-      operator: "inThePast"
-      values: [7]
-      settings:
-        unitOfTime: "days"
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "big_number"
-  config:
-    bigNumber:
-      selectedField: "customers_count"
-      label: "New Customers This Week"
-      showBigNumberLabel: true
-      showComparison: true
-      comparisonFormat: "raw"  # Show absolute change (e.g., +42)
-      comparisonLabel: "vs. Last Week"
+    selectedField: "orders_total_revenue"
+    label: "Total Revenue"
+    style: "M"  # Display as millions (e.g., 2.5M)
+    showBigNumberLabel: true
 ```
 
-### Example 5: Flipped Colors for Cost Metrics
+### Example 2: Period-over-Period Comparison with Flipped Colors
 
-Show costs where increases are bad (red) and decreases are good (green):
+Show costs with percentage change where increases are highlighted as negative (red):
 
 ```yaml
 version: 1
@@ -252,126 +118,25 @@ metricQuery:
 chartConfig:
   type: "big_number"
   config:
-    bigNumber:
-      selectedField: "expenses_total_cost"
-      label: "Monthly Infrastructure Costs"
-      style: "K"
-      showBigNumberLabel: true
-      showComparison: true
-      comparisonFormat: "percentage"
-      comparisonLabel: "vs. Last Month"
-      flipColors: true  # Red for increase, green for decrease
-```
-
-### Example 6: Error Rate with Flipped Colors
-
-Monitor error rates where increases are problematic:
-
-```yaml
-version: 1
-name: "Error Rate"
-slug: "error-rate"
-spaceSlug: "engineering"
-tableName: "api_logs"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "api_logs_error_rate"
-  filters:
-    - target:
-        fieldId: "api_logs_timestamp"
-      operator: "inThePast"
-      values: [24]
-      settings:
-        unitOfTime: "hours"
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "big_number"
-  config:
-    bigNumber:
-      selectedField: "api_logs_error_rate"
-      label: "API Error Rate (24h)"
-      showBigNumberLabel: true
-      showComparison: true
-      comparisonFormat: "percentage"
-      comparisonLabel: "vs. Yesterday"
-      flipColors: true  # Higher error rate = red (bad)
-```
-
-### Example 7: Multiple Format Styles
-
-Show billions with compact notation:
-
-```yaml
-version: 1
-name: "Market Capitalization"
-slug: "market-cap"
-spaceSlug: "finance"
-tableName: "company_metrics"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "company_metrics_market_cap"
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "big_number"
-  config:
-    bigNumber:
-      selectedField: "company_metrics_market_cap"
-      label: "Market Cap"
-      style: "B"  # Display as billions (e.g., 1.2B)
-      showBigNumberLabel: true
-```
-
-### Example 8: Without Custom Label
-
-Use the default field name as the label:
-
-```yaml
-version: 1
-name: "Active Sessions"
-slug: "active-sessions"
-spaceSlug: "product"
-tableName: "sessions"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "sessions_active_count"
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "big_number"
-  config:
-    bigNumber:
-      selectedField: "sessions_active_count"
-      showBigNumberLabel: true
-      showTableNamesInLabel: false  # Hide "Sessions - " prefix
+    selectedField: "expenses_total_cost"
+    label: "Monthly Infrastructure Costs"
+    style: "K"
+    showBigNumberLabel: true
+    showComparison: true
+    comparisonFormat: "percentage"
+    comparisonLabel: "vs. Last Month"
+    flipColors: true  # Red for increase, green for decrease
 ```
 
 ## Common Patterns
 
 ### Executive Dashboard KPI
 
-For high-level metrics on executive dashboards:
-
 ```yaml
-bigNumber:
+config:
   selectedField: "revenue_total"
   label: "Total Revenue"
-  style: "M"  # Compact millions format
+  style: "M"
   showBigNumberLabel: true
   showComparison: true
   comparisonFormat: "percentage"
@@ -380,101 +145,59 @@ bigNumber:
 
 ### Cost Monitoring
 
-For tracking costs where increases are concerning:
-
 ```yaml
-bigNumber:
+config:
   selectedField: "costs_total"
   label: "Monthly Cloud Costs"
   style: "K"
   showBigNumberLabel: true
   showComparison: true
   comparisonFormat: "percentage"
-  comparisonLabel: "vs. Last Month"
   flipColors: true  # Red for increase
 ```
 
 ### Simple Metric Display
 
-For straightforward metric display without comparison:
-
 ```yaml
-bigNumber:
+config:
   selectedField: "users_count"
   label: "Total Users"
   showBigNumberLabel: true
 ```
 
-### Growth Metric with Raw Change
-
-Show absolute change in addition to the current value:
-
-```yaml
-bigNumber:
-  selectedField: "signups_count"
-  label: "New Signups This Week"
-  showBigNumberLabel: true
-  showComparison: true
-  comparisonFormat: "raw"  # Show +42 instead of +12%
-  comparisonLabel: "vs. Last Week"
-```
-
 ## Tips
 
 1. **Limit to 1 row**: Big number charts display a single value, so always use `limit: 1` in your `metricQuery`.
 
-2. **Use aggregated metrics**: Big numbers work best with aggregated values (totals, counts, averages, etc.).
+2. **Use aggregated metrics**: Big numbers work best with aggregated values (totals, counts, averages).
 
-3. **Choose the right style**: Use compact notation (`K`, `M`, `B`) for large numbers to improve readability:
+3. **Choose the right style**: Use compact notation for large numbers:
    - Revenue in millions? Use `"M"`
    - User counts in thousands? Use `"K"`
    - Market cap in billions? Use `"B"`
 
-4. **Flip colors appropriately**: Use `flipColors: true` for metrics where:
-   - Increases are negative (costs, errors, response times)
-   - Decreases are positive (churn rate, ticket backlog)
+4. **Flip colors appropriately**: Use `flipColors: true` for metrics where increases are negative (costs, errors, response times, churn rate).
 
-5. **Comparison context**: Always provide a `comparisonLabel` when using `showComparison` to make the context clear (e.g., "vs. Last Month", "vs. Yesterday").
+5. **Comparison context**: Always provide a `comparisonLabel` when using `showComparison` to make the context clear.
 
 6. **Percentage vs. raw**: Choose comparison format based on your audience:
-   - **Percentage** (`comparisonFormat: "percentage"`): Better for understanding relative change
-   - **Raw** (`comparisonFormat: "raw"`): Better when absolute numbers matter
-
-7. **Label clarity**: Use clear, concise labels. Avoid redundant information:
-   - Good: "Monthly Revenue"
-   - Avoid: "Total Monthly Revenue Amount"
-
-8. **Period-over-period setup**: For comparison to work properly, your query should:
-   - Include appropriate time filters
-   - Use metrics that support comparison (some metrics may need special configuration)
-   - Have sufficient historical data for the comparison period
-
-## Number Format Style Reference
-
-| Style Value | Alias | Example Input | Example Output | Use Case |
-|-------------|-------|---------------|----------------|----------|
-| `"thousands"` | `"K"` | 1500 | 1.5K | Small numbers in thousands |
-| `"millions"` | `"M"` | 1500000 | 1.5M | Revenue, large user counts |
-| `"billions"` | `"B"` | 1500000000 | 1.5B | Market cap, large financials |
-| `"trillions"` | `"T"` | 1500000000000 | 1.5T | National economies, huge datasets |
-
-## Comparison Format Reference
-
-| Format | Description | Example Display | Best For |
-|--------|-------------|-----------------|----------|
-| `"raw"` | Absolute change | +500 or -200 | Count changes, absolute growth |
-| `"percentage"` | Percentage change | +12.5% or -8.3% | Relative growth, trends |
+   - **Percentage**: Better for understanding relative change
+   - **Raw**: Better when absolute numbers matter
 
-## Color Scheme Reference
+## Quick Reference Tables
 
-### Default Colors (flipColors: false)
-- **Green**: Positive change (increase)
-- **Red**: Negative change (decrease)
+### Number Format Styles
 
-**Use for**: Revenue, users, signups, conversions (where more is better)
+| Style | Example Input | Example Output | Use Case |
+|-------|---------------|----------------|----------|
+| `"K"` | 1500 | 1.5K | Small numbers in thousands |
+| `"M"` | 1500000 | 1.5M | Revenue, large user counts |
+| `"B"` | 1500000000 | 1.5B | Market cap, large financials |
+| `"T"` | 1500000000000 | 1.5T | National economies |
 
-### Flipped Colors (flipColors: true)
-- **Red**: Positive change (increase)
-- **Green**: Negative change (decrease)
+### Color Scheme
 
-**Use for**: Costs, errors, churn, response times (where less is better)
+| flipColors | Increase | Decrease | Use For |
+|------------|----------|----------|---------|
+| `false` (default) | Green | Red | Revenue, users, signups |
+| `true` | Red | Green | Costs, errors, churn |
diff --git a/skills/developing-in-lightdash/resources/cartesian-chart-reference.md b/skills/developing-in-lightdash/resources/cartesian-chart-reference.md
@@ -16,6 +16,8 @@ Cartesian charts support:
 - Reference lines for highlighting thresholds or targets
 - Flexible axis configuration and styling
 
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/cartesianChart`.
+
 ## Basic Structure
 
 ```yaml
@@ -52,322 +54,42 @@ chartConfig:
               field: "my_explore_total_sales"
 ```
 
-## Configuration Options
-
-### `layout` (object)
-
-Core layout configuration for chart axes and orientation.
-
-- **`xField`** (string): Field ID to use for the X axis. Typically a dimension.
-
-- **`yField`** (array of strings): Field IDs to use for the Y axis. Can include metrics, dimensions, or table calculations.
-
-- **`flipAxes`** (boolean): Swap X and Y axes to create horizontal bar charts. Default: `false`.
-
-- **`showGridX`** (boolean): Show vertical grid lines. Default varies by chart type.
-
-- **`showGridY`** (boolean): Show horizontal grid lines. Default varies by chart type.
-
-- **`showXAxis`** (boolean): Show the X axis. Default: `true`.
-
-- **`showYAxis`** (boolean): Show the Y axis. Default: `true`.
-
-- **`stack`** (boolean | string): Stack series together. Use `true` for default stacking, or a string for a specific stack group name.
-
-### `eChartsConfig` (object)
-
-ECharts-specific configuration for advanced customization.
-
-#### `series` (array of objects, required)
-
-Array of series configurations. Each series represents a visualization layer. See [Series Configuration](#series-configuration) below.
-
-#### `xAxis` (array of objects)
-
-X axis configuration array. See [X Axis Configuration](#x-axis-configuration).
-
-#### `yAxis` (array of objects)
-
-Y axis configuration array. See [Y Axis Configuration](#y-axis-configuration).
-
-#### `legend` (object)
-
-Legend configuration. See [Legend Configuration](#legend-configuration).
-
-#### `grid` (object)
-
-Grid (chart area) configuration. See [Grid Configuration](#grid-configuration).
-
-#### `tooltip` (string)
-
-Tooltip formatter template string.
-
-#### `tooltipSort` (enum)
-
-How to sort tooltip items. Options:
-- `"default"`: Default sorting
-- `"alphabetical"`: Sort alphabetically by series name
-- `"value_ascending"`: Sort by value (lowest to highest)
-- `"value_descending"`: Sort by value (highest to lowest)
-
-#### `showAxisTicks` (boolean)
-
-Show tick marks on axes.
-
-#### `axisLabelFontSize` (number)
-
-Font size for axis labels in pixels.
-
-#### `axisTitleFontSize` (number)
-
-Font size for axis titles in pixels.
-
-### `metadata` (object)
-
-Metadata for series configuration, keyed by field ID.
-
-```yaml
-metadata:
-  my_field_id:
-    color: "#FF6B6B"
-```
-
-## Series Configuration
-
-Each series in the `series` array represents a data visualization layer.
-
-### Required Properties
-
-- **`type`** (enum, required): Series visualization type. Options: `"bar"`, `"line"`, `"area"`, `"scatter"`.
-
-- **`encode`** (object, required): Field references for this series.
-  - **`xRef`** (object, required): X axis field reference. See [Pivot Reference](#pivot-reference).
-  - **`yRef`** (object, required): Y axis field reference. See [Pivot Reference](#pivot-reference).
-
-### Optional Properties
-
-- **`name`** (string): Display name for the series in the legend.
-
-- **`color`** (string): Color for the series as a hex code (e.g., `"#FF6B6B"`).
-
-- **`yAxisIndex`** (number): Index of Y axis to use (0 or 1 for dual Y-axis charts). Default: `0`.
-
-- **`hidden`** (boolean): Hide this series from the chart. Default: `false`.
-
-- **`stack`** (string): Stack group name. Series with the same stack name are stacked together.
-
-- **`stackLabel`** (object): Stack total label configuration.
-  - **`show`** (boolean): Show stack total labels above stacked bars/areas.
-
-- **`label`** (object): Data label configuration.
-  - **`show`** (boolean): Show data labels on points.
-  - **`position`** (enum): Label position. Options: `"left"`, `"top"`, `"right"`, `"bottom"`, `"inside"`.
-  - **`showOverlappingLabels`** (boolean): Show labels even when they overlap.
-
-- **`areaStyle`** (object): Area fill style. Presence of this object (even empty `{}`) indicates an area chart.
-
-- **`showSymbol`** (boolean): Show symbols/markers on data points (for line/area charts).
-
-- **`smooth`** (boolean): Use smooth curves for line/area charts. Default: `false`.
-
-- **`markLine`** (object): Reference line configuration. See [Mark Line Configuration](#mark-line-configuration).
-
-### Pivot Reference
-
-References a field, optionally with pivot values for pivoted data.
-
-```yaml
-encode:
-  xRef:
-    field: "dimension_field_id"
-  yRef:
-    field: "metric_field_id"
-    pivotValues:
-      - field: "pivot_dimension_id"
-        value: "Category A"
-```
-
-- **`field`** (string, required): Field ID being referenced.
-
-- **`pivotValues`** (array): Array of pivot value objects for pivoted data.
-  - **`field`** (string, required): Pivot field ID.
-  - **`value`** (any, required): Pivot value to filter for this series.
-
-## X Axis Configuration
-
-Extends basic axis configuration with X-axis-specific options.
-
-```yaml
-xAxis:
-  - name: "Month"
-    rotate: 45
-    sortType: "default"
-    enableDataZoom: false
-```
-
-- **`name`** (string): Axis title.
-
-- **`min`** (string): Minimum value (or `"dataMin"` for auto).
-
-- **`max`** (string): Maximum value (or `"dataMax"` for auto).
-
-- **`minOffset`** (string): Offset from minimum value.
-
-- **`maxOffset`** (string): Offset from maximum value.
-
-- **`inverse`** (boolean): Reverse the axis direction.
-
-- **`rotate`** (number): Rotation angle for axis labels in degrees (e.g., `45` for diagonal labels).
-
-- **`sortType`** (enum): How to sort the X axis. Options:
-  - `"default"`: Default sorting (as data appears)
-  - `"category"`: Sort alphabetically by category
-  - `"bar_totals"`: Sort by bar totals (descending)
-
-- **`enableDataZoom`** (boolean): Enable data zoom slider for this axis. Allows users to pan/zoom the X axis.
-
-## Y Axis Configuration
-
-Basic axis configuration for Y axes.
-
-```yaml
-yAxis:
-  - name: "Revenue ($)"
-    min: "0"
-    max: "dataMax"
-```
-
-- **`name`** (string): Axis title.
-
-- **`min`** (string): Minimum value (or `"dataMin"` for auto).
-
-- **`max`** (string): Maximum value (or `"dataMax"` for auto).
-
-- **`minOffset`** (string): Offset from minimum value.
-
-- **`maxOffset`** (string): Offset from maximum value.
-
-- **`inverse`** (boolean): Reverse the axis direction.
-
-- **`rotate`** (number): Rotation angle for axis labels in degrees.
-
-## Legend Configuration
-
-Controls the display and positioning of the chart legend.
-
-```yaml
-legend:
-  show: true
-  type: "scroll"
-  orient: "horizontal"
-  top: "10px"
-  left: "center"
-```
-
-- **`show`** (boolean): Show the legend. Default: `true`.
-
-- **`type`** (enum): Legend type. Options:
-  - `"plain"`: Standard legend
-  - `"scroll"`: Scrollable legend (for many series)
-
-- **`orient`** (enum): Legend orientation. Options: `"horizontal"`, `"vertical"`.
-
-- **`top`** (string): Top position (e.g., `"10px"`, `"10%"`).
-
-- **`right`** (string): Right position.
-
-- **`bottom`** (string): Bottom position.
-
-- **`left`** (string): Left position.
-
-- **`width`** (string): Legend width.
-
-- **`height`** (string): Legend height.
-
-- **`align`** (enum): Legend alignment. Options: `"auto"`, `"left"`, `"right"`.
-
-- **`icon`** (enum): Legend icon shape. Options: `"circle"`, `"rect"`, `"roundRect"`, `"triangle"`, `"diamond"`, `"pin"`, `"arrow"`, `"none"`.
-
-## Grid Configuration
-
-Controls the chart area padding and positioning.
-
-```yaml
-grid:
-  containLabel: true
-  top: "60px"
-  right: "40px"
-  bottom: "60px"
-  left: "40px"
-```
-
-- **`containLabel`** (boolean): Whether the grid area contains axis labels. Set to `true` to prevent label clipping.
-
-- **`top`** (string): Top padding.
-
-- **`right`** (string): Right padding.
-
-- **`bottom`** (string): Bottom padding.
-
-- **`left`** (string): Left padding.
+## Key Configuration Properties
 
-- **`width`** (string): Grid width.
+### `layout`
 
-- **`height`** (string): Grid height.
+- **`xField`**: Field ID for the X axis (typically a dimension)
+- **`yField`**: Array of field IDs for the Y axis
+- **`flipAxes`**: Swap X and Y axes for horizontal bar charts (default: `false`)
+- **`showGridX`** / **`showGridY`**: Show grid lines
+- **`stack`**: Stack series together (`true` or stack group name)
 
-## Mark Line Configuration
+### `eChartsConfig`
 
-Reference lines to highlight thresholds, targets, or averages.
+- **`series`**: Array of series configurations (required)
+- **`xAxis`** / **`yAxis`**: Axis configuration arrays
+- **`legend`**: Legend display and positioning
+- **`grid`**: Chart area padding
+- **`tooltip`** / **`tooltipSort`**: Tooltip behavior
 
-```yaml
-markLine:
-  data:
-    - uuid: "unique-id-1"
-      name: "Target"
-      yAxis: "1000"
-      lineStyle:
-        color: "#FF0000"
-      label:
-        formatter: "Target: {c}"
-        position: "end"
-  symbol: "none"
-  lineStyle:
-    type: "dashed"
-    color: "#000000"
-    width: 2
-```
-
-### `markLine` Properties
-
-- **`data`** (array): Array of reference line data points.
-  - **`uuid`** (string, required): Unique identifier for this mark line.
-  - **`name`** (string): Name of the reference line.
-  - **`yAxis`** (string): Y axis value for horizontal line.
-  - **`xAxis`** (string): X axis value for vertical line.
-  - **`value`** (string): Value to display.
-  - **`type`** (string): Point type (e.g., `"average"`).
-  - **`dynamicValue`** (enum): Dynamic value type. Options: `"average"`.
-  - **`lineStyle`** (object):
-    - **`color`** (string): Line color.
-  - **`label`** (object):
-    - **`formatter`** (string): Label text formatter.
-    - **`position`** (enum): Label position. Options: `"start"`, `"middle"`, `"end"`.
+### Series Configuration
 
-- **`symbol`** (string): Symbol at line endpoints (e.g., `"none"`, `"circle"`).
+Each series requires:
+- **`type`**: `"bar"`, `"line"`, `"area"`, or `"scatter"`
+- **`encode`**: Field references with `xRef` and `yRef`
 
-- **`lineStyle`** (object): Default line style for all mark lines.
-  - **`color`** (string): Line color.
-  - **`width`** (number): Line width in pixels.
-  - **`type`** (string): Line style (e.g., `"solid"`, `"dashed"`).
-
-- **`label`** (object): Default label configuration.
-  - **`formatter`** (string): Label text formatter.
+Optional properties:
+- **`name`**: Display name in legend
+- **`color`**: Hex color code
+- **`yAxisIndex`**: Which Y axis (0 or 1)
+- **`stack`**: Stack group name
+- **`smooth`**: Smooth curves for line/area
+- **`areaStyle`**: Presence indicates area chart
+- **`markLine`**: Reference line configuration
 
 ## Examples
 
-### Example 1: Simple Bar Chart
-
-Basic vertical bar chart comparing values across categories:
+### Bar Chart
 
 ```yaml
 version: 1
@@ -403,12 +125,9 @@ chartConfig:
               field: "orders_partner_name"
             yRef:
               field: "orders_total_sales"
-          yAxisIndex: 0
 ```
 
-### Example 2: Line Chart with Trend
-
-Line chart showing a trend over time with smooth curves:
+### Line Chart with Trend
 
 ```yaml
 version: 1
@@ -451,17 +170,14 @@ chartConfig:
               field: "orders_total_revenue"
           smooth: true
           showSymbol: true
-          yAxisIndex: 0
 ```
 
-### Example 3: Stacked Area Chart
-
-Area chart with multiple series stacked together:
+### Stacked Area Chart
 
 ```yaml
 version: 1
-name: "Revenue by Product Category"
-slug: "revenue-by-product-category"
+name: "Revenue by Category"
+slug: "revenue-by-category"
 spaceSlug: "sales"
 tableName: "orders"
 updatedAt: "2024-01-01T00:00:00.000Z"
@@ -490,13 +206,8 @@ chartConfig:
       yField:
         - "orders_total_revenue"
     eChartsConfig:
-      xAxis:
-        - name: "Month"
-      yAxis:
-        - name: "Revenue ($)"
       legend:
         show: true
-        type: "scroll"
       series:
         - type: "line"
           stack: "total"
@@ -509,109 +220,50 @@ chartConfig:
               pivotValues:
                 - field: "orders_product_category"
                   value: "Electronics"
-          yAxisIndex: 0
-        - type: "line"
-          stack: "total"
-          areaStyle: {}
-          encode:
-            xRef:
-              field: "orders_order_date_month"
-            yRef:
-              field: "orders_total_revenue"
-              pivotValues:
-                - field: "orders_product_category"
-                  value: "Clothing"
-          yAxisIndex: 0
-        - type: "line"
-          stack: "total"
-          areaStyle: {}
-          encode:
-            xRef:
-              field: "orders_order_date_month"
-            yRef:
-              field: "orders_total_revenue"
-              pivotValues:
-                - field: "orders_product_category"
-                  value: "Home Goods"
-          yAxisIndex: 0
 ```
 
-### Example 4: Stacked Bar Chart with Stack Labels
-
-Stacked bar chart showing monthly revenue by partner with total labels:
+### Scatter Chart
 
 ```yaml
 version: 1
-name: "Monthly Revenue by Partner"
-slug: "monthly-revenue-by-partner"
-spaceSlug: "sales"
+name: "Order Value vs Profit"
+slug: "order-value-vs-profit"
+spaceSlug: "analytics"
 tableName: "orders"
 updatedAt: "2024-01-01T00:00:00.000Z"
 
 metricQuery:
   dimensions:
-    - "orders_order_date_month"
-    - "orders_partner_name"
+    - "orders_order_id"
   metrics:
-    - "orders_total_revenue"
+    - "orders_basket_total"
+    - "orders_profit"
   filters: {}
-  sorts:
-    - fieldId: "orders_order_date_month"
-      descending: false
-  limit: 500
-
-pivotConfig:
-  columns:
-    - "orders_partner_name"
+  sorts: []
+  limit: 1000
 
 chartConfig:
   type: "cartesian"
   config:
     layout:
-      xField: "orders_order_date_month"
+      xField: "orders_basket_total"
       yField:
-        - "orders_total_revenue"
+        - "orders_profit"
     eChartsConfig:
       xAxis:
-        - name: "Month"
+        - name: "Order Value ($)"
       yAxis:
-        - name: "Total Revenue ($)"
-      legend:
-        show: true
-      grid:
-        containLabel: true
+        - name: "Profit ($)"
       series:
-        - type: "bar"
-          stack: "revenue_stack"
-          stackLabel:
-            show: true
-          encode:
-            xRef:
-              field: "orders_order_date_month"
-            yRef:
-              field: "orders_total_revenue"
-              pivotValues:
-                - field: "orders_partner_name"
-                  value: "Partner A"
-          yAxisIndex: 0
-        - type: "bar"
-          stack: "revenue_stack"
-          stackLabel:
-            show: true
+        - type: "scatter"
           encode:
             xRef:
-              field: "orders_order_date_month"
+              field: "orders_basket_total"
             yRef:
-              field: "orders_total_revenue"
-              pivotValues:
-                - field: "orders_partner_name"
-                  value: "Partner B"
-          yAxisIndex: 0
+              field: "orders_profit"
 ```
 
-### Example 5: Dual Y-Axis Chart (Bar + Line)
-
-Combine bars and lines with different Y-axis scales:
+### Dual Y-Axis Chart
 
 ```yaml
 version: 1
@@ -645,15 +297,9 @@ chartConfig:
         - "orders_total_revenue"
         - "profit_margin"
     eChartsConfig:
-      xAxis:
-        - name: "Month"
       yAxis:
         - name: "Revenue ($)"
-          type: "value"
         - name: "Profit Margin (%)"
-          type: "value"
-      legend:
-        show: true
       series:
         - type: "bar"
           name: "Revenue"
@@ -663,7 +309,6 @@ chartConfig:
             yRef:
               field: "orders_total_revenue"
           yAxisIndex: 0
-          color: "#3B82F6"
         - type: "line"
           name: "Profit Margin"
           encode:
@@ -672,434 +317,25 @@ chartConfig:
             yRef:
               field: "profit_margin"
           yAxisIndex: 1
-          color: "#10B981"
-          smooth: true
-          showSymbol: true
-          label:
-            show: true
-            position: "top"
-```
-
-### Example 6: Scatter Chart
-
-Scatter chart showing correlation between two metrics:
-
-```yaml
-version: 1
-name: "Order Value vs Profit"
-slug: "order-value-vs-profit"
-spaceSlug: "analytics"
-tableName: "orders"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions:
-    - "orders_order_id"
-  metrics:
-    - "orders_basket_total"
-    - "orders_profit"
-  filters: {}
-  sorts: []
-  limit: 1000
-
-chartConfig:
-  type: "cartesian"
-  config:
-    layout:
-      xField: "orders_basket_total"
-      yField:
-        - "orders_profit"
-    eChartsConfig:
-      xAxis:
-        - name: "Order Value ($)"
-      yAxis:
-        - name: "Profit ($)"
-      series:
-        - type: "scatter"
-          encode:
-            xRef:
-              field: "orders_basket_total"
-            yRef:
-              field: "orders_profit"
-          yAxisIndex: 0
-```
-
-### Example 7: Horizontal Bar Chart
-
-Horizontal bar chart using `flipAxes`:
-
-```yaml
-version: 1
-name: "Top 10 Products by Sales"
-slug: "top-10-products"
-spaceSlug: "sales"
-tableName: "orders"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions:
-    - "orders_product_name"
-  metrics:
-    - "orders_total_sales"
-  filters: {}
-  sorts:
-    - fieldId: "orders_total_sales"
-      descending: true
-  limit: 10
-
-chartConfig:
-  type: "cartesian"
-  config:
-    layout:
-      xField: "orders_product_name"
-      yField:
-        - "orders_total_sales"
-      flipAxes: true
-    eChartsConfig:
-      xAxis:
-        - name: "Product"
-      yAxis:
-        - name: "Sales ($)"
-      series:
-        - type: "bar"
-          encode:
-            xRef:
-              field: "orders_product_name"
-            yRef:
-              field: "orders_total_sales"
-          yAxisIndex: 0
-```
-
-### Example 8: Chart with Reference Lines
-
-Bar chart with target threshold reference line:
-
-```yaml
-version: 1
-name: "Weekly Sales with Target"
-slug: "weekly-sales-target"
-spaceSlug: "sales"
-tableName: "orders"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions:
-    - "orders_order_date_week"
-  metrics:
-    - "orders_total_sales"
-  filters: {}
-  sorts:
-    - fieldId: "orders_order_date_week"
-      descending: true
-  limit: 52
-
-chartConfig:
-  type: "cartesian"
-  config:
-    layout:
-      xField: "orders_order_date_week"
-      yField:
-        - "orders_total_sales"
-    eChartsConfig:
-      xAxis:
-        - name: "Week"
-      yAxis:
-        - name: "Sales ($)"
-      series:
-        - type: "bar"
-          encode:
-            xRef:
-              field: "orders_order_date_week"
-            yRef:
-              field: "orders_total_sales"
-          yAxisIndex: 0
-          markLine:
-            data:
-              - uuid: "target-line"
-                name: "Weekly Target"
-                yAxis: "50000"
-                lineStyle:
-                  color: "#DC2626"
-                label:
-                  formatter: "Target: $50k"
-                  position: "end"
-            symbol: "none"
-            lineStyle:
-              type: "dashed"
-              color: "#DC2626"
-              width: 2
-```
-
-### Example 9: Mixed Chart Types
-
-Combine multiple series types in one chart:
-
-```yaml
-version: 1
-name: "Sales Performance Overview"
-slug: "sales-performance-overview"
-spaceSlug: "sales"
-tableName: "orders"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions:
-    - "orders_order_date_month"
-  metrics:
-    - "orders_total_sales"
-    - "orders_total_profit"
-    - "orders_order_count"
-  filters: {}
-  sorts:
-    - fieldId: "orders_order_date_month"
-      descending: false
-  limit: 12
-
-chartConfig:
-  type: "cartesian"
-  config:
-    layout:
-      xField: "orders_order_date_month"
-      yField:
-        - "orders_total_sales"
-        - "orders_total_profit"
-        - "orders_order_count"
-    eChartsConfig:
-      xAxis:
-        - name: "Month"
-      yAxis:
-        - name: "Sales & Profit ($)"
-          type: "value"
-        - name: "Order Count"
-          type: "value"
-      legend:
-        show: true
-      series:
-        - type: "bar"
-          name: "Sales"
-          encode:
-            xRef:
-              field: "orders_order_date_month"
-            yRef:
-              field: "orders_total_sales"
-          yAxisIndex: 0
-          color: "#3B82F6"
-        - type: "bar"
-          name: "Profit"
-          encode:
-            xRef:
-              field: "orders_order_date_month"
-            yRef:
-              field: "orders_total_profit"
-          yAxisIndex: 0
-          color: "#10B981"
-        - type: "line"
-          name: "Orders"
-          encode:
-            xRef:
-              field: "orders_order_date_month"
-            yRef:
-              field: "orders_order_count"
-          yAxisIndex: 1
-          color: "#F59E0B"
           smooth: true
-          showSymbol: true
-```
-
-### Example 10: Advanced Styling and Customization
-
-Chart with custom fonts, rotated labels, and custom legend positioning:
-
-```yaml
-version: 1
-name: "Quarterly Revenue Analysis"
-slug: "quarterly-revenue-analysis"
-spaceSlug: "finance"
-tableName: "orders"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions:
-    - "orders_order_date_quarter"
-  metrics:
-    - "orders_total_revenue"
-  filters: {}
-  sorts:
-    - fieldId: "orders_order_date_quarter"
-      descending: false
-  limit: 500
-
-chartConfig:
-  type: "cartesian"
-  config:
-    layout:
-      xField: "orders_order_date_quarter"
-      yField:
-        - "orders_total_revenue"
-      showGridY: true
-    eChartsConfig:
-      xAxis:
-        - name: "Quarter"
-          rotate: 0
-          sortType: "default"
-      yAxis:
-        - name: "Revenue ($)"
-          min: "0"
-      legend:
-        show: true
-        type: "plain"
-        orient: "horizontal"
-        top: "10px"
-        left: "center"
-      grid:
-        containLabel: true
-        top: "60px"
-        right: "40px"
-        bottom: "60px"
-        left: "60px"
-      series:
-        - type: "bar"
-          encode:
-            xRef:
-              field: "orders_order_date_quarter"
-            yRef:
-              field: "orders_total_revenue"
-          yAxisIndex: 0
-          label:
-            show: true
-            position: "top"
-          color: "#6366F1"
-      axisLabelFontSize: 12
-      axisTitleFontSize: 14
-      tooltipSort: "value_descending"
-      showAxisTicks: true
-```
-
-## Common Patterns
-
-### Time Series Line Chart
-
-For tracking metrics over time:
-
-```yaml
-layout:
-  xField: "date_dimension"
-  yField:
-    - "metric_field"
-  showGridY: true
-eChartsConfig:
-  series:
-    - type: "line"
-      smooth: true
-      showSymbol: false
-      encode:
-        xRef:
-          field: "date_dimension"
-        yRef:
-          field: "metric_field"
-```
-
-### Comparison Bar Chart
-
-For comparing categories side-by-side:
-
-```yaml
-layout:
-  xField: "category_dimension"
-  yField:
-    - "metric_1"
-    - "metric_2"
-eChartsConfig:
-  series:
-    - type: "bar"
-      encode:
-        xRef:
-          field: "category_dimension"
-        yRef:
-          field: "metric_1"
-    - type: "bar"
-      encode:
-        xRef:
-          field: "category_dimension"
-        yRef:
-          field: "metric_2"
-```
-
-### Stacked Percentage Area Chart
-
-For showing composition over time:
-
-```yaml
-layout:
-  xField: "date_dimension"
-  yField:
-    - "metric_field"
-eChartsConfig:
-  series:
-    - type: "line"
-      stack: "total"
-      areaStyle: {}
-      encode:
-        xRef:
-          field: "date_dimension"
-        yRef:
-          field: "metric_field"
-          pivotValues:
-            - field: "category_dimension"
-              value: "Category A"
 ```
 
 ## Tips
 
 1. **Choose the right chart type**:
    - Bar: Comparing discrete categories
-   - Line: Showing trends over continuous data (especially time)
-   - Area: Emphasizing cumulative totals or stacked composition
-   - Scatter: Exploring correlations between two continuous variables
-
-2. **Stacking considerations**:
-   - Use the same `stack` value for all series you want to stack
-   - Only bar and area charts support stacking
-   - Stacked charts work best when showing parts of a whole
-
-3. **Dual Y-axis guidelines**:
-   - Use when comparing metrics with vastly different scales
-   - Set `yAxisIndex: 0` for left axis, `yAxisIndex: 1` for right axis
-   - Clearly label both axes with units
-   - Limit to 2 Y-axes for readability
-
-4. **Performance optimization**:
-   - Limit data points for line/scatter charts (use `limit` in `metricQuery`)
-   - For many series, use `legend.type: "scroll"`
-   - Disable `showSymbol` on dense line charts for better performance
+   - Line: Showing trends over time
+   - Area: Emphasizing cumulative totals or composition
+   - Scatter: Exploring correlations between variables
 
-5. **Accessibility**:
-   - Use high-contrast colors for series
-   - Enable axis labels and titles
-   - Consider color-blind-friendly palettes
-   - Add descriptive series names
+2. **Stacking**: Use the same `stack` value for series you want stacked. Only bar and area charts support stacking.
 
-6. **Pivot data handling**:
-   - When pivoting dimensions, each pivot value becomes a separate series
-   - Use `pivotValues` in `yRef` to specify which pivot value each series represents
-   - Pivot columns are defined in `pivotConfig.columns`
+3. **Dual Y-axis**: Use `yAxisIndex: 0` for left axis, `yAxisIndex: 1` for right axis.
 
-7. **Reference lines**:
-   - Use for targets, thresholds, or averages
-   - Set `dynamicValue: "average"` for auto-calculated averages
-   - Position labels carefully to avoid overlapping data
+4. **Horizontal bars**: Set `flipAxes: true` in layout.
 
-8. **Grid and spacing**:
-   - Use `grid.containLabel: true` to prevent axis labels from being cut off
-   - Adjust grid padding for long axis labels or titles
-   - Increase `bottom` padding if X-axis labels are rotated
+5. **Pivot data**: Use `pivotValues` in `yRef` to create series from pivoted dimensions.
 
-9. **Sorting data**:
-   - Use `metricQuery.sorts` to control data order
-   - Use `xAxis.sortType` for additional X-axis sorting options
-   - For bar charts showing rankings, sort by the metric in descending order
+6. **Reference lines**: Add `markLine` to series for targets or thresholds.
 
-10. **Label positioning**:
-    - Use `label.show: true` and `label.position` to show data values
-    - For stacked bars, use `stackLabel.show: true` for totals
-    - Be cautious with labels on dense data (may overlap)
+7. **Grid spacing**: Use `grid.containLabel: true` to prevent label clipping.
diff --git a/skills/developing-in-lightdash/resources/chart-types-reference.md b/skills/developing-in-lightdash/resources/chart-types-reference.md
@@ -1,31 +1,55 @@
 # Chart Types Reference
 
-This document has been split into individual chart type references for more detailed coverage.
+This document provides an overview of all chart types available in Lightdash charts-as-code.
 
-## Chart Type References
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json).
+
+## Chart Type Index
+
+Each chart type has its own detailed reference document with configuration options, examples, and best practices.
 
 | Type | Description | Reference |
 |------|-------------|-----------|
-| `cartesian` | Bar, line, area, scatter charts | [Cartesian Chart Reference](./cartesian-chart-reference.md) |
-| `pie` | Pie and donut charts | [Pie Chart Reference](./pie-chart-reference.md) |
-| `table` | Data tables with formatting | [Table Chart Reference](./table-chart-reference.md) |
-| `big_number` | Single KPI display | [Big Number Reference](./big-number-chart-reference.md) |
-| `funnel` | Conversion funnels | [Funnel Chart Reference](./funnel-chart-reference.md) |
-| `gauge` | Gauge/dial visualizations | [Gauge Chart Reference](./gauge-chart-reference.md) |
-| `treemap` | Hierarchical treemaps | [Treemap Chart Reference](./treemap-chart-reference.md) |
-| `map` | Geographic visualizations | [Map Chart Reference](./map-chart-reference.md) |
-| `custom` | Vega-Lite custom charts | [Custom Viz Reference](./custom-viz-reference.md) |
-
-## Quick Chart Type Selection
-
-| Data Pattern | Recommended Chart |
-|--------------|-------------------|
-| Trends over time | Line or area (cartesian) |
-| Category comparisons | Bar (cartesian) |
-| Part-of-whole | Pie or treemap |
-| Single KPI metric | Big number |
-| Conversion stages | Funnel |
-| Progress toward target | Gauge |
-| Geographic data | Map |
-| Detailed records | Table |
-| Advanced custom needs | Custom (Vega-Lite) |
+| `cartesian` | Bar, line, area, scatter charts with X/Y axes | [Cartesian Chart Reference](./cartesian-chart-reference.md) |
+| `pie` | Pie and donut charts for part-of-whole visualization | [Pie Chart Reference](./pie-chart-reference.md) |
+| `table` | Data tables with column formatting and conditional styling | [Table Chart Reference](./table-chart-reference.md) |
+| `big_number` | Single KPI display with optional comparison | [Big Number Reference](./big-number-chart-reference.md) |
+| `funnel` | Conversion funnels for tracking stage progression | [Funnel Chart Reference](./funnel-chart-reference.md) |
+| `gauge` | Gauge/dial visualizations for progress toward targets | [Gauge Chart Reference](./gauge-chart-reference.md) |
+| `treemap` | Hierarchical treemaps for nested categorical data | [Treemap Chart Reference](./treemap-chart-reference.md) |
+| `map` | Geographic visualizations with markers or regions | [Map Chart Reference](./map-chart-reference.md) |
+| `custom` | Vega-Lite custom charts for advanced visualizations | [Custom Viz Reference](./custom-viz-reference.md) |
+
+## Quick Chart Type Selection Guide
+
+Use this table to choose the right chart type based on your data pattern:
+
+| Data Pattern | Recommended Chart | Why |
+|--------------|-------------------|-----|
+| Trends over time | Line or area (`cartesian`) | Shows continuous change with time on X-axis |
+| Category comparisons | Bar (`cartesian`) | Easy visual comparison between discrete categories |
+| Part-of-whole relationships | `pie` or `treemap` | Shows proportions summing to 100% |
+| Single KPI metric | `big_number` | Focuses attention on one important value |
+| Conversion stages | `funnel` | Visualizes drop-off between sequential steps |
+| Progress toward target | `gauge` | Shows current value relative to goal |
+| Geographic data | `map` | Plots data points or regions on a map |
+| Detailed records | `table` | Displays raw data with sorting and formatting |
+| Advanced custom needs | `custom` | Full Vega-Lite spec for custom visualizations |
+
+## Common Chart Configuration
+
+All chart types share a common base structure:
+
+```yaml
+version: "1.0"
+name: "Chart Name"
+slug: unique-chart-slug
+spaceSlug: target-space
+chartType: <type>  # One of the types listed above
+query:
+  # Query configuration (explore, dimensions, metrics, filters)
+config:
+  # Type-specific visualization configuration
+```
+
+See individual chart reference files for type-specific `config` options.
diff --git a/skills/developing-in-lightdash/resources/cli-reference.md b/skills/developing-in-lightdash/resources/cli-reference.md
@@ -0,0 +1,188 @@
+# CLI Reference
+
+Complete reference for Lightdash CLI commands.
+
+## Authentication
+
+```bash
+# Login to Lightdash instance
+lightdash login https://app.lightdash.cloud
+
+# Login with token (non-interactive)
+lightdash login https://app.lightdash.cloud --token YOUR_API_TOKEN
+
+# List available projects (excludes preview projects)
+lightdash config list-projects
+
+# Show currently selected project
+lightdash config get-project
+
+# Set active project
+lightdash config set-project --name "My Project"
+lightdash config set-project --uuid abc123-def456
+```
+
+## Compilation & Deployment
+
+```bash
+# Compile dbt models and validate
+lightdash compile --project-dir ./dbt --profiles-dir ./profiles
+
+# Deploy to Lightdash
+lightdash deploy --project-dir ./dbt --profiles-dir ./profiles
+
+# Create new project on deploy
+lightdash deploy --create "New Project Name"
+
+# Deploy ignoring validation errors
+lightdash deploy --ignore-errors
+
+# Skip dbt compilation (use existing manifest)
+lightdash deploy --skip-dbt-compile
+
+# Pure Lightdash YAML (no dbt)
+lightdash deploy --no-warehouse-credentials
+```
+
+## Preview Projects
+
+```bash
+# Create preview environment (watches for changes)
+lightdash preview --name "feature-branch-preview"
+
+# Start preview without watching
+lightdash start-preview --name "my-preview"
+
+# Stop preview
+lightdash stop-preview --name "my-preview"
+```
+
+## Generate YAML
+
+```bash
+# Generate schema for all models
+lightdash generate
+
+# Generate for specific models
+lightdash generate -s my_model
+lightdash generate -s tag:sales
+lightdash generate -s +my_model  # Include parents
+```
+
+## Validation
+
+```bash
+# Lint chart and dashboard YAML files locally (offline)
+lightdash lint --path ./lightdash
+
+# Validate against Lightdash server
+lightdash validate --project my-project-uuid
+
+# Output lint results as JSON/SARIF
+lightdash lint --format json
+```
+
+## Download & Upload Content
+
+```bash
+# Download all charts and dashboards
+lightdash download
+
+# Download specific content
+lightdash download --charts chart-slug-1 chart-slug-2
+lightdash download --dashboards dashboard-slug
+
+# Download with nested folder structure
+lightdash download --nested
+
+# Upload modified content
+lightdash upload
+
+# Force upload (ignore timestamps)
+lightdash upload --force
+
+# Upload specific items
+lightdash upload --charts my-chart --dashboards my-dashboard
+```
+
+## Delete Content
+
+Permanently delete charts and dashboards from the server and remove their local YAML files.
+
+```bash
+# Delete a chart by slug
+lightdash delete -c my-chart
+
+# Delete a dashboard by slug
+lightdash delete -d my-dashboard
+
+# Delete multiple items at once
+lightdash delete -c chart1 chart2 -d dashboard1
+
+# Delete by UUID
+lightdash delete -c abc123-def456
+
+# Delete by URL
+lightdash delete -c "https://app.lightdash.cloud/projects/xxx/saved/abc123"
+
+# Skip confirmation prompt (use with caution)
+lightdash delete -c my-chart --force
+
+# Use custom path for local files
+lightdash delete -c my-chart --path ./custom-lightdash
+
+# Delete from a specific project
+lightdash delete -c my-chart --project <project-uuid>
+```
+
+**Options:**
+- `-c, --charts <charts...>` - Chart slugs, UUIDs, or URLs to delete
+- `-d, --dashboards <dashboards...>` - Dashboard slugs, UUIDs, or URLs to delete
+- `-f, --force` - Skip confirmation prompt
+- `-p, --path <path>` - Custom path where local chart-as-code files are stored
+- `--project <uuid>` - Specify a project UUID
+
+**Warning:** The delete command will warn you if any charts being deleted are referenced by dashboards.
+
+## SQL Runner
+
+Execute raw SQL queries against the warehouse using the current project's credentials.
+
+```bash
+# Run a query and save results to CSV
+lightdash sql "SELECT * FROM orders LIMIT 10" -o results.csv
+
+# Limit rows returned
+lightdash sql "SELECT * FROM customers" -o customers.csv --limit 1000
+
+# Adjust pagination for large results (default 500, max 5000)
+lightdash sql "SELECT * FROM events" -o events.csv --page-size 2000
+
+# Verbose output for debugging
+lightdash sql "SELECT COUNT(*) FROM users" -o count.csv --verbose
+```
+
+**Options:**
+- `<query>` - SQL query to execute (required)
+- `-o, --output <file>` - Output CSV file path (required)
+- `--limit <number>` - Maximum rows to return
+- `--page-size <number>` - Rows per page (default: 500, max: 5000)
+- `--verbose` - Show detailed output
+
+**Note:** Uses warehouse credentials from your currently selected Lightdash project.
+
+## Command Summary
+
+| Command | Purpose |
+|---------|---------|
+| `lightdash login` | Authenticate with Lightdash |
+| `lightdash config` | Manage project selection |
+| `lightdash deploy` | Sync semantic layer to Lightdash |
+| `lightdash upload` | Upload charts/dashboards |
+| `lightdash download` | Download charts/dashboards |
+| `lightdash delete` | Remove charts/dashboards |
+| `lightdash preview` | Create temporary test project |
+| `lightdash validate` | Validate against server |
+| `lightdash lint` | Validate YAML locally |
+| `lightdash generate` | Generate YAML from dbt models |
+| `lightdash sql` | Run SQL queries |
diff --git a/skills/developing-in-lightdash/resources/custom-viz-reference.md b/skills/developing-in-lightdash/resources/custom-viz-reference.md
@@ -2,6 +2,8 @@
 
 Custom visualizations in Lightdash allow you to create advanced, bespoke charts using Vega-Lite specifications. This is an advanced feature for users who need visualization types not covered by Lightdash's built-in chart types.
 
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/customVis`.
+
 ## Overview
 
 Custom visualizations integrate with Vega-Lite, a declarative grammar for creating interactive visualizations. Lightdash automatically provides your query results to the Vega-Lite specification, allowing you to define exactly how the data should be visualized.
@@ -15,51 +17,7 @@ Custom visualizations integrate with Vega-Lite, a declarative grammar for creati
 - Familiarity with Vega-Lite specifications (see [Vega-Lite documentation](https://vega.github.io/vega-lite/))
 - Understanding of your data structure and field names
 
-## YAML Structure
-
-```yaml
-version: 1
-name: Custom Visualization Name
-slug: custom-viz-slug
-spaceSlug: analytics/custom
-tableName: orders
-updatedAt: '2024-01-15T10:30:00Z'
-
-metricQuery:
-  dimensions:
-    - orders_status
-    - orders_created_date
-  metrics:
-    - orders_count
-  filters: {}
-  sorts:
-    - fieldId: orders_created_date
-      descending: false
-  limit: 100
-  tableCalculations: []
-
-chartConfig:
-  type: custom
-  config:
-    spec:
-      $schema: https://vega.github.io/schema/vega-lite/v5.json
-      mark: bar
-      encoding:
-        x:
-          field: orders_status
-          type: nominal
-          axis:
-            labelColor: '#6e7079'
-            tickColor: '#6e7079'
-        y:
-          field: orders_count
-          type: quantitative
-          axis:
-            labelColor: '#6e7079'
-            tickColor: '#6e7079'
-```
-
-## Configuration Options
+## Configuration
 
 ### chartConfig.type
 Must be set to `"custom"` for custom visualizations.
@@ -79,18 +37,7 @@ The complete Vega-Lite specification object. This object defines how your data w
 
 ## How Lightdash Provides Data
 
-Lightdash automatically provides your query results to the Vega-Lite specification in a specific format:
-
-**Data structure:**
-```javascript
-{
-  values: [
-    { field_name_1: value, field_name_2: value, ... },
-    { field_name_1: value, field_name_2: value, ... },
-    ...
-  ]
-}
-```
+Lightdash automatically provides your query results to the Vega-Lite specification:
 
 - Data is available as an array of objects under the `values` key
 - Field names in your Vega-Lite spec must match the field names from your `metricQuery` (dimensions, metrics, and table calculations)
@@ -152,66 +99,6 @@ chartConfig:
             scheme: blues
 ```
 
-### Bubble Plot
-
-A scatter plot with size encoding:
-
-```yaml
-chartConfig:
-  type: custom
-  config:
-    spec:
-      $schema: https://vega.github.io/schema/vega-lite/v5.json
-      mark: point
-      encoding:
-        x:
-          field: customers_lifetime_value
-          type: quantitative
-        y:
-          field: customers_order_count
-          type: quantitative
-        size:
-          field: customers_total_spent
-          type: quantitative
-        color:
-          field: customers_status
-          type: nominal
-```
-
-### Advanced: Layered Chart with Transformations
-
-A more complex example with data transformations and multiple layers:
-
-```yaml
-chartConfig:
-  type: custom
-  config:
-    spec:
-      $schema: https://vega.github.io/schema/vega-lite/v5.json
-      transform:
-        - calculate: "datum.orders_revenue / datum.orders_count"
-          as: avg_order_value
-      layer:
-        - mark: bar
-          encoding:
-            x:
-              field: orders_created_month
-              type: temporal
-            y:
-              field: orders_count
-              type: quantitative
-        - mark:
-            type: line
-            color: red
-          encoding:
-            x:
-              field: orders_created_month
-              type: temporal
-            y:
-              field: avg_order_value
-              type: quantitative
-```
-
 ## Tips and Best Practices
 
 1. **Start with templates**: Use Lightdash's UI template gallery when creating custom visualizations interactively, then export to YAML
diff --git a/skills/developing-in-lightdash/resources/dashboard-best-practices.md b/skills/developing-in-lightdash/resources/dashboard-best-practices.md
@@ -0,0 +1,371 @@
+# Dashboard Best Practices
+
+A guide to building effective, user-friendly dashboards in Lightdash based on data visualization principles and BI best practices.
+
+## Data Visualization Fundamentals
+
+### Choose the Right Chart Type
+
+Match your visualization to the type of insight you're communicating:
+
+| Insight Type | Recommended Charts | Avoid |
+|-------------|-------------------|-------|
+| **Trends over time** | Line chart, area chart | Pie chart |
+| **Comparisons** | Bar chart (horizontal for many categories) | Overloaded charts |
+| **Parts of a whole** | Pie/donut (max 5 segments), stacked bar | Too many segments |
+| **Correlations** | Scatter plot | Line chart |
+| **Single KPI** | Big number | Complex charts |
+| **Detailed data** | Table | Charts with too much data |
+
+### Visual Hierarchy
+
+1. **Most important metrics at the top**: Users scan top-to-bottom, left-to-right
+2. **KPIs before details**: Start with summary metrics, then supporting charts
+3. **Largest tiles for key insights**: Size indicates importance
+4. **Use headings to create sections**: Guide the eye through the story
+
+### Keep It Simple
+
+- **Limit to 5-10 charts per view/tab**: More causes cognitive overload
+- **One insight per chart**: Don't overload with multiple y-axes
+- **Remove chart junk**: Avoid gridlines, borders, and decorations that don't add meaning
+- **Use consistent colors**: Same metric = same color across all charts
+
+### Data Ink Ratio
+
+Maximize the ratio of data to non-data ink:
+
+**Do:**
+- Remove unnecessary gridlines
+- Use subtle axis lines
+- Let data stand out
+
+**Don't:**
+- Add heavy borders around charts
+- Use gradient fills
+- Include decorative images
+
+## Dashboard Layout Principles
+
+### The Inverted Pyramid
+
+Structure dashboards like a news article:
+
+1. **Top**: Critical KPIs and headlines (big numbers)
+2. **Middle**: Supporting trends and breakdowns (charts)
+3. **Bottom**: Detailed data and drill-downs (tables)
+
+### Common Layout Patterns
+
+**Executive Dashboard:**
+```
+┌─────────────────────────────────────────────┐
+│  KPI  │  KPI  │  KPI  │  KPI  │  (w: 9 each)
+├───────────────────────┬─────────────────────┤
+│   Main Trend Chart    │   Key Insights      │
+│      (w: 24)          │     (w: 12)         │
+├───────────────────────┴─────────────────────┤
+│           Supporting Charts/Table           │
+│                  (w: 36)                    │
+└─────────────────────────────────────────────┘
+```
+
+**Operational Dashboard:**
+```
+┌─────────────────────────────────────────────┐
+│              Filters Bar                     │
+├─────────────────────────────────────────────┤
+│  Status KPI │ Status KPI │ Status KPI       │
+├─────────────────────────────────────────────┤
+│           Real-time/Recent Data Table       │
+├─────────────────────────────────────────────┤
+│   Trend 1    │   Trend 2    │   Trend 3    │
+└─────────────────────────────────────────────┘
+```
+
+**Analytical Dashboard:**
+```
+┌─────────────────────────────────────────────┐
+│              Summary Metrics                 │
+├─────────────────────────────────────────────┤
+│         Primary Analysis Chart              │
+├──────────────────────┬──────────────────────┤
+│   Breakdown 1        │    Breakdown 2       │
+├──────────────────────┴──────────────────────┤
+│           Detailed Data Table               │
+└─────────────────────────────────────────────┘
+```
+
+## Lightdash-Specific Best Practices
+
+### Using Tabs Effectively
+
+Tabs help organize complex dashboards without overwhelming users:
+
+```yaml
+tabs:
+  - uuid: "overview"
+    name: "Overview"      # Start with high-level view
+    order: 0
+  - uuid: "trends"
+    name: "Trends"        # Time-based analysis
+    order: 1
+  - uuid: "breakdown"
+    name: "Breakdown"     # Dimensional analysis
+    order: 2
+  - uuid: "details"
+    name: "Details"       # Detailed data tables
+    order: 3
+```
+
+**When to use tabs:**
+- Dashboard has more than 8-10 tiles
+- Content naturally groups into themes
+- Different audiences need different views
+- Analysis flows from summary to detail
+
+**Tab naming tips:**
+- Keep names short (1-2 words)
+- Use nouns, not verbs ("Overview" not "View Overview")
+- Order logically (general → specific)
+
+### Using Headings for Organization
+
+Headings create visual sections within a tab:
+
+```yaml
+tiles:
+  - type: heading
+    x: 0
+    y: 0
+    w: 36
+    h: 1
+    properties:
+      text: "Revenue Performance"
+
+  # Revenue charts below...
+
+  - type: heading
+    x: 0
+    y: 8
+    w: 36
+    h: 1
+    properties:
+      text: "Customer Metrics"
+
+  # Customer charts below...
+```
+
+**When to use headings:**
+- Grouping related charts within a tab
+- Separating logical sections
+- Creating a table of contents feel
+
+### Using Markdown Tiles
+
+Markdown tiles add context, explanations, and guidance:
+
+**Use markdown for:**
+- Explaining what the dashboard shows
+- Highlighting key insights
+- Providing interpretation guidance
+- Adding links to related resources
+- Documenting data sources or caveats
+
+```yaml
+- type: markdown
+  x: 24
+  y: 0
+  w: 12
+  h: 6
+  properties:
+    title: "About This Dashboard"
+    content: |
+      ## Purpose
+
+      This dashboard tracks **weekly sales performance**
+      against targets.
+
+      ## Key Metrics
+
+      - **Revenue**: Total invoiced amount
+      - **Pipeline**: Weighted opportunity value
+
+      ## Data Freshness
+
+      Updated every 4 hours from Salesforce.
+
+      ---
+
+      Questions? Contact [analytics@company.com](mailto:analytics@company.com)
+```
+
+**Markdown tips:**
+- Don't overdo it: Keep explanations concise
+- Use formatting: Bold for emphasis, headers for structure
+- Include links: To documentation, related dashboards, or contacts
+- Consider collapsible sections for lengthy explanations
+
+**Rich HTML in markdown:**
+Lightdash supports HTML within markdown for advanced formatting:
+
+```yaml
+content: |
+  <div style="background: #f0f9ff; padding: 16px; border-radius: 8px;">
+    <strong>Note:</strong> Q4 data includes estimated values for December.
+  </div>
+```
+
+### Filter Best Practices
+
+#### Choose Appropriate Filter Defaults
+
+Filters with no default value (`values: []`) mean "any value" - the filter is visible but not applied. This is useful for **suggested filters** that users can optionally apply without affecting the initial dashboard view.
+
+Filters with default values are better when the filter **should be active** on load:
+
+```yaml
+filters:
+  dimensions:
+    # Filter WITH default - active on load
+    - target:
+        fieldId: orders_created_at
+        tableName: orders
+      operator: inThePast
+      values: [90]              # Default: Last 90 days
+      settings:
+        unitOfTime: days
+        completed: false
+      label: "Date Range"
+
+    # Filter WITHOUT default - suggested but not applied
+    - target:
+        fieldId: orders_region
+        tableName: orders
+      operator: equals
+      values: []                # No default = show all regions
+      label: "Region"
+```
+
+**When to use default values:**
+- Time filters that should constrain data (e.g., last 90 days)
+- Status filters where you want to show active/open items by default
+- Any filter that meaningfully improves the initial view
+
+**When to omit default values:**
+- Suggested filters users might want but aren't essential
+- Filters where "all" is the sensible starting point
+- Exploratory dashboards where users should choose their own scope
+
+**Tip:** Prefer a filter with a sensible default over a required filter with no value - it's a better user experience to show data immediately rather than forcing a selection.
+
+#### Use Required Filters When Appropriate
+
+Required filters ensure the dashboard only shows when context is provided:
+
+```yaml
+filters:
+  dimensions:
+    - target:
+        fieldId: customers_account_id
+        tableName: customers
+      operator: equals
+      values: []
+      required: true           # User must select
+      label: "Select Account"
+```
+
+**When to require filters:**
+- Dashboard only makes sense for a specific context (e.g., account, region)
+- Data volume is too large without filtering
+- Security/privacy requires explicit selection
+
+#### Limit Filter Count
+
+- 3-5 primary filters is ideal
+- Too many filters confuse users
+- Use tabs to separate different filter contexts
+- Consider which filters apply to all charts vs. specific tiles
+
+### Content Organization Tips
+
+#### Tell a Story
+
+Structure the dashboard to answer questions in order:
+
+1. **What happened?** (KPIs, summary metrics)
+2. **Why did it happen?** (Breakdowns, trends)
+3. **What should we do?** (Insights, recommendations in markdown)
+4. **What's the detail?** (Tables for drill-down)
+
+#### Design for Your Audience
+
+| Audience | Focus On | Avoid |
+|----------|----------|-------|
+| **Executives** | KPIs, trends, summaries | Technical details, too many charts |
+| **Analysts** | Breakdowns, filters, drill-downs | Oversimplification |
+| **Operations** | Current status, exceptions, actions | Historical trends |
+| **Self-serve users** | Clear labels, explanations | Jargon, assumed knowledge |
+
+#### Maintain Consistency
+
+- **Same metric, same name**: Don't call it "Revenue" in one place and "Sales" in another
+- **Same color scheme**: Use consistent colors for the same dimensions across charts
+- **Same time grain**: If one chart shows monthly data, don't mix in daily without explanation
+- **Same filters**: Dashboard filters should apply consistently (use `tileTargets` for exceptions)
+
+## Performance Considerations
+
+### Optimize for Load Time
+
+1. **Limit tile count**: Each tile is a query
+2. **Use appropriate limits**: Don't return 10,000 rows for a chart
+3. **Pre-filter in the model**: Remove irrelevant historical data
+4. **Use tabs**: Only visible tab queries run initially
+
+### Query Efficiency
+
+- **Avoid SELECT ***: Only include needed dimensions and metrics
+- **Use date filters**: Time-bound queries are faster
+- **Consider aggregation**: Pre-aggregate in dbt for common views
+
+## Common Mistakes to Avoid
+
+### Layout Mistakes
+
+- **Using w: 24 or less for full-width**: The grid is 36 columns, use `w: 36`
+- **Cramming too much**: Leave visual breathing room
+- **Inconsistent heights**: Charts at the same level should have the same height
+- **Poor mobile experience**: Test on smaller screens
+
+### Visualization Mistakes
+
+- **Pie charts with too many segments**: Max 5, use bar chart otherwise
+- **Truncated y-axes**: Can exaggerate small changes
+- **Missing context**: Numbers without comparison are meaningless
+- **Dual y-axes**: Hard to interpret, use separate charts
+
+### Content Mistakes
+
+- **No explanations**: Users shouldn't have to guess what metrics mean
+- **Stale data without indication**: Show data freshness
+- **Missing time filter defaults**: Dashboard loads with too much data when a date range should be applied
+- **Mixing audiences**: Exec summary next to analyst deep-dive
+
+## Dashboard Checklist
+
+Before publishing, verify:
+
+- [ ] KPIs are at the top
+- [ ] Chart types match the data/insight
+- [ ] Filters that should be active have sensible defaults
+- [ ] Required filters are set where needed
+- [ ] Tabs are used if >10 tiles
+- [ ] Headings separate logical sections
+- [ ] Markdown explains purpose and key insights
+- [ ] Colors are consistent across charts
+- [ ] Full width (w: 36) is used where appropriate
+- [ ] Dashboard loads in reasonable time
+- [ ] Works on different screen sizes
+- [ ] All charts have clear titles
+- [ ] Data freshness is indicated if relevant
diff --git a/skills/developing-in-lightdash/resources/funnel-chart-reference.md b/skills/developing-in-lightdash/resources/funnel-chart-reference.md
@@ -2,6 +2,8 @@
 
 Funnel charts visualize stages in a sequential process, showing how values decrease from one stage to the next. Common use cases include conversion funnels, sales pipelines, and multi-step user flows.
 
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/funnelChart`.
+
 ## When to Use Funnel Charts
 
 - **Conversion funnels**: Website visitors → signups → paid customers
@@ -33,26 +35,19 @@ metricQuery:
 chartConfig:
   type: funnel
   config:
-    fieldId: leads_count
+    selectedField: leads_count
     dataInput: row
 ```
 
-### Configuration Options
+### Key Configuration Options
 
-#### `dataInput` (optional)
+#### `dataInput`
 
 How the data is structured in your query results.
 
 - `row` (default): Each row represents a funnel stage
 - `column`: Each column represents a funnel stage
 
-```yaml
-config:
-  dataInput: row    # Use when stages are in different rows
-  # OR
-  dataInput: column # Use when stages are in different columns
-```
-
 **Row-based example** (recommended):
 ```
 | stage          | count |
@@ -70,141 +65,45 @@ config:
 | 10000     | 5000     | 2000          | 500      |
 ```
 
-#### `fieldId` (required)
+#### `selectedField`
 
 The field ID (metric or dimension) to display as the funnel values.
 
-```yaml
-config:
-  fieldId: leads_count  # Metric to show in funnel
-```
-
-## Label Configuration
-
-### Label Position
-
-Control where stage labels appear relative to the funnel segments.
-
-```yaml
-config:
-  labels:
-    position: inside    # inside, left, right, hidden
-    showValue: true
-    showPercentage: true
-```
-
-**Position options**:
-- `inside`: Labels appear within funnel segments (default)
-- `left`: Labels appear to the left of segments
-- `right`: Labels appear to the right of segments
-- `hidden`: No labels shown
-
-### Label Content
-
-```yaml
-config:
-  labels:
-    showValue: true        # Show actual values (e.g., "5,000")
-    showPercentage: true   # Show percentage of max (e.g., "50%")
-```
+#### `labels`
 
-**Label format examples**:
-- Both true: `"Interest: 50% - 5,000"`
-- Only percentage: `"Interest: 50%"`
-- Only value: `"Interest: 5,000"`
-- Both false: `"Interest"`
+Control label display:
+- `position`: `inside` (default), `left`, `right`, or `hidden`
+- `showValue`: Show actual values (e.g., "5,000")
+- `showPercentage`: Show percentage of max (e.g., "50%")
 
-### Label Overrides
+#### `labelOverrides`
 
-Provide custom labels for specific stages.
+Provide custom labels for specific stages:
 
 ```yaml
 config:
   labelOverrides:
     leads_stage_awareness: "Top of Funnel"
     leads_stage_interest: "Engaged Users"
-    leads_stage_consideration: "Hot Leads"
-    leads_stage_purchase: "Converted Customers"
 ```
 
-## Styling Configuration
+#### `colorOverrides`
 
-### Color Overrides
-
-Customize colors for individual funnel stages.
+Customize colors for individual funnel stages:
 
 ```yaml
 config:
   colorOverrides:
-    leads_stage_awareness: "#3b82f6"      # Blue
-    leads_stage_interest: "#10b981"       # Green
-    leads_stage_consideration: "#f59e0b"  # Amber
-    leads_stage_purchase: "#8b5cf6"       # Purple
-```
-
-### Metadata
-
-Alternative way to set colors using metadata (less common in charts-as-code).
-
-```yaml
-config:
-  metadata:
-    leads_stage_awareness:
-      color: "#3b82f6"
-    leads_stage_interest:
-      color: "#10b981"
-```
-
-## Legend Configuration
-
-### Show/Hide Legend
-
-```yaml
-config:
-  showLegend: true          # Show legend (default: true)
-  legendPosition: vertical  # horizontal, vertical
+    leads_stage_awareness: "#3b82f6"
+    leads_stage_interest: "#10b981"
 ```
 
-**Legend position options**:
-- `horizontal`: Legend appears at the top, centered
-- `vertical`: Legend appears on the left side, vertically aligned
+#### Legend Options
 
-## Complete Examples
+- `showLegend`: Show or hide the legend (default: true)
+- `legendPosition`: `horizontal` or `vertical`
 
-### Example 1: Basic Conversion Funnel
-
-```yaml
-version: 1
-name: "Website Conversion Funnel"
-slug: website-conversion-funnel
-spaceSlug: marketing
-tableName: events
-
-metricQuery:
-  exploreName: events
-  dimensions:
-    - events_stage
-  metrics:
-    - events_user_count
-  sorts:
-    - fieldId: events_stage
-      descending: false
-  limit: 10
-
-chartConfig:
-  type: funnel
-  config:
-    fieldId: events_user_count
-    dataInput: row
-    labels:
-      position: inside
-      showValue: true
-      showPercentage: true
-    showLegend: true
-    legendPosition: horizontal
-```
-
-### Example 2: Custom Stage Colors and Labels
+## Complete Example
 
 ```yaml
 version: 1
@@ -227,7 +126,7 @@ metricQuery:
 chartConfig:
   type: funnel
   config:
-    fieldId: opportunities_count
+    selectedField: opportunities_count
     dataInput: row
 
     # Custom stage labels
@@ -255,137 +154,6 @@ chartConfig:
     legendPosition: vertical
 ```
 
-### Example 3: With Percentages Only (Clean Layout)
-
-```yaml
-version: 1
-name: "Checkout Flow Drop-off"
-slug: checkout-drop-off
-spaceSlug: product
-tableName: checkout_events
-
-metricQuery:
-  exploreName: checkout_events
-  dimensions:
-    - checkout_events_step
-  metrics:
-    - checkout_events_session_count
-  sorts:
-    - fieldId: checkout_events_step
-      descending: false
-
-chartConfig:
-  type: funnel
-  config:
-    fieldId: checkout_events_session_count
-    dataInput: row
-
-    labelOverrides:
-      checkout_events_step_cart: "Cart"
-      checkout_events_step_shipping: "Shipping Info"
-      checkout_events_step_payment: "Payment"
-      checkout_events_step_confirmation: "Order Complete"
-
-    labels:
-      position: inside
-      showValue: false        # Hide raw values for cleaner look
-      showPercentage: true    # Show only percentages
-
-    showLegend: false         # Hide legend to focus on funnel
-```
-
-### Example 4: Row vs Column Data Input
-
-**Row-based (recommended)**:
-
-```yaml
-version: 1
-name: "Funnel (Row Data)"
-slug: funnel-row-data
-spaceSlug: analytics
-tableName: user_journey
-
-metricQuery:
-  exploreName: user_journey
-  dimensions:
-    - user_journey_stage  # Different stages in rows
-  metrics:
-    - user_journey_users
-  sorts:
-    - fieldId: user_journey_stage
-      descending: false
-
-chartConfig:
-  type: funnel
-  config:
-    fieldId: user_journey_users
-    dataInput: row    # Each row is a stage
-```
-
-**Column-based**:
-
-```yaml
-version: 1
-name: "Funnel (Column Data)"
-slug: funnel-column-data
-spaceSlug: analytics
-tableName: funnel_metrics
-
-metricQuery:
-  exploreName: funnel_metrics
-  metrics:
-    - funnel_stage_1_count
-    - funnel_stage_2_count
-    - funnel_stage_3_count
-    - funnel_stage_4_count
-
-chartConfig:
-  type: funnel
-  config:
-    fieldId: null  # Not used for column-based
-    dataInput: column  # Each metric/column is a stage
-```
-
-### Example 5: External Labels for Long Names
-
-```yaml
-version: 1
-name: "Detailed Sales Stages"
-slug: detailed-sales-stages
-spaceSlug: sales
-tableName: deals
-
-metricQuery:
-  exploreName: deals
-  dimensions:
-    - deals_detailed_stage
-  metrics:
-    - deals_opportunity_count
-  sorts:
-    - fieldId: deals_detailed_stage
-      descending: false
-
-chartConfig:
-  type: funnel
-  config:
-    fieldId: deals_opportunity_count
-    dataInput: row
-
-    labelOverrides:
-      deals_detailed_stage_1: "Initial Contact & Discovery"
-      deals_detailed_stage_2: "Needs Analysis & Qualification"
-      deals_detailed_stage_3: "Proposal & Presentation"
-      deals_detailed_stage_4: "Contract Negotiation"
-      deals_detailed_stage_5: "Closed Won"
-
-    labels:
-      position: right     # Labels outside for long text
-      showValue: true
-      showPercentage: true
-
-    showLegend: false
-```
-
 ## Best Practices
 
 ### Data Preparation
@@ -398,19 +166,12 @@ chartConfig:
 
 1. **Limit stages**: 4-7 stages for optimal readability
 2. **Show percentages**: Help viewers understand conversion rates between stages
-3. **Use sequential colors**: Colors should suggest progression (e.g., blue → purple → green)
+3. **Use sequential colors**: Colors should suggest progression
 4. **Position labels appropriately**:
    - Use `inside` for short stage names and wide funnels
    - Use `left` or `right` for long stage names
    - Use `hidden` when legend provides sufficient context
 
-### Color Guidelines
-
-1. **Avoid using red/green for funnel stages**: These colors imply good/bad, which doesn't fit sequential processes
-2. **Use color gradients**: Show progression with shades of the same color or a logical color sequence
-3. **Maintain contrast**: Ensure labels are readable against segment colors
-4. **Be consistent**: Use the same colors for the same stages across related charts
-
 ### When Not to Use Funnel Charts
 
 - **Non-sequential processes**: Use pie or bar charts instead
@@ -433,68 +194,12 @@ metricQuery:
 
 ### Issue: Labels are cut off or overlapping
 
-**Solution**: Change label position:
-
-```yaml
-config:
-  labels:
-    position: right  # or left
-```
+**Solution**: Change label position to `left` or `right`.
 
 ### Issue: Colors don't show up
 
-**Solution**: Ensure you're using valid hex color codes:
-
-```yaml
-config:
-  colorOverrides:
-    stage_1: "#3b82f6"  # Include # prefix
-```
+**Solution**: Ensure you're using valid hex color codes with the `#` prefix.
 
 ### Issue: Legend shows internal field IDs
 
-**Solution**: Use label overrides:
-
-```yaml
-config:
-  labelOverrides:
-    internal_field_id: "User-Friendly Name"
-```
-
-## Schema Reference
-
-Based on `chart-as-code-1.0.json`, the complete schema for funnel chart configuration:
-
-```yaml
-chartConfig:
-  type: funnel  # ChartType.FUNNEL
-  config:
-    # Data structure
-    dataInput: row | column  # How data is organized
-
-    # Field selection
-    fieldId: string  # Metric/dimension to display
-
-    # Label customization
-    labelOverrides:
-      <fieldId>: string  # Custom label for stage
-
-    # Color customization
-    colorOverrides:
-      <fieldId>: string  # Hex color for stage
-
-    # Alternative color definition
-    metadata:
-      <fieldId>:
-        color: string
-
-    # Label display
-    labels:
-      position: inside | left | right | hidden
-      showValue: boolean
-      showPercentage: boolean
-
-    # Legend
-    showLegend: boolean
-    legendPosition: horizontal | vertical
-```
+**Solution**: Use `labelOverrides` to provide user-friendly names.
diff --git a/skills/developing-in-lightdash/resources/gauge-chart-reference.md b/skills/developing-in-lightdash/resources/gauge-chart-reference.md
@@ -11,115 +11,40 @@ Gauge charts in Lightdash provide a visual representation of a single metric val
 
 Gauge charts display a single numeric value on a semi-circular dial with optional colored sections to indicate different ranges or performance zones.
 
-## Basic Structure
+## Schema Reference
 
-```yaml
-version: 1
-name: "My Gauge Chart"
-slug: "my-gauge-chart"
-spaceSlug: "analytics"
-tableName: "my_explore"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "my_explore_current_value"
-    - "my_explore_target_value"  # Optional: for dynamic max
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "gauge"
-  config:
-    gaugeChart:
-      selectedField: "my_explore_current_value"
-      min: 0
-      max: 100
-      showAxisLabels: true
-```
-
-## Configuration Options
-
-### `gaugeChart` (object, optional)
-
-The main configuration object for gauge chart settings. All properties are optional.
-
-#### Core Value Settings
-
-- **`selectedField`** (string): Field ID for the gauge value. This should be a metric from your `metricQuery`.
-
-- **`min`** (number): Minimum value for the gauge scale. Default is typically 0.
-
-- **`max`** (number): Maximum value for the gauge scale. Use this for a fixed maximum.
-
-- **`maxFieldId`** (string): Field ID to use as the maximum value. Use this when the max should be dynamic based on query results (e.g., a target metric). Mutually exclusive with `max`.
-
-#### Display Settings
-
-- **`showAxisLabels`** (boolean): Whether to show min/max labels on the gauge axis. Default is typically `true`.
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/gaugeChart`.
 
-- **`customLabel`** (string): Custom label to display with the gauge value instead of the field name.
+## Key Configuration Properties
 
-- **`showPercentage`** (boolean): Display the value as a percentage of the max value.
+The `gaugeChart` configuration object supports these key properties:
 
-- **`customPercentageLabel`** (string): Custom label for the percentage display when `showPercentage` is `true`.
+### Core Value Settings
 
-#### Sections (Color Ranges)
+- **`selectedField`**: Field ID for the gauge value (a metric from your `metricQuery`)
+- **`min`**: Minimum value for the gauge scale (default: 0)
+- **`max`**: Fixed maximum value for the gauge scale
+- **`maxFieldId`**: Field ID to use as dynamic maximum (mutually exclusive with `max`)
 
-- **`sections`** (array): Define colored sections/ranges on the gauge to indicate different performance zones. Each section is a `gaugeSection` object (see below).
+### Display Settings
 
-### `gaugeSection` (object)
+- **`showAxisLabels`**: Show min/max labels on the gauge axis
+- **`customLabel`**: Custom label to display instead of the field name
+- **`showPercentage`**: Display the value as a percentage of max
+- **`customPercentageLabel`**: Custom label for percentage display
 
-Defines a colored range on the gauge. Required properties: `min`, `max`, `color`.
+### Sections (Color Ranges)
 
-- **`min`** (number, required): Start value for this section.
-
-- **`max`** (number, required): End value for this section.
-
-- **`minFieldId`** (string, optional): Field ID to use as the section's min value (dynamic min).
-
-- **`maxFieldId`** (string, optional): Field ID to use as the section's max value (dynamic max).
-
-- **`color`** (string, required): Color for this section as a hex code (e.g., `"#FF0000"` for red).
+- **`sections`**: Array of colored ranges indicating performance zones. Each section requires:
+  - `min` / `minFieldId`: Start value (fixed or dynamic)
+  - `max` / `maxFieldId`: End value (fixed or dynamic)
+  - `color`: Hex color code (e.g., `"#DC2626"`)
 
 ## Examples
 
-### Example 1: Basic Gauge with Fixed Range
+### Example 1: Gauge with Color-Coded Sections
 
-Simple gauge showing current revenue vs. a fixed target:
-
-```yaml
-version: 1
-name: "Monthly Revenue"
-slug: "monthly-revenue"
-spaceSlug: "sales"
-tableName: "sales_metrics"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "sales_metrics_current_revenue"
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "gauge"
-  config:
-    gaugeChart:
-      selectedField: "sales_metrics_current_revenue"
-      min: 0
-      max: 100000
-      showAxisLabels: true
-      customLabel: "Current Revenue ($)"
-```
-
-### Example 2: Multiple Colored Sections (Red/Yellow/Green Zones)
-
-Gauge with color-coded performance zones:
+Gauge with red/yellow/green performance zones:
 
 ```yaml
 version: 1
@@ -161,41 +86,9 @@ chartConfig:
           color: "#10B981"
 ```
 
-### Example 3: Dynamic Max from Field
+### Example 2: Dynamic Max with Percentage Display
 
-Gauge showing progress against a dynamic target value:
-
-```yaml
-version: 1
-name: "Sales Progress vs Target"
-slug: "sales-progress"
-spaceSlug: "sales"
-tableName: "sales_metrics"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "sales_metrics_current_sales"
-    - "sales_metrics_quarterly_target"
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "gauge"
-  config:
-    gaugeChart:
-      selectedField: "sales_metrics_current_sales"
-      min: 0
-      maxFieldId: "sales_metrics_quarterly_target"  # Dynamic max
-      showAxisLabels: true
-      customLabel: "Current Sales"
-```
-
-### Example 4: Percentage Display with Custom Label
-
-Display value as percentage with a custom label:
+Progress gauge against a dynamic target:
 
 ```yaml
 version: 1
@@ -236,59 +129,10 @@ chartConfig:
           color: "#22C55E"
 ```
 
-### Example 5: Advanced with Dynamic Sections
-
-Dynamic sections using field values for boundaries:
-
-```yaml
-version: 1
-name: "Performance Score"
-slug: "performance-score"
-spaceSlug: "analytics"
-tableName: "performance_metrics"
-updatedAt: "2024-01-01T00:00:00.000Z"
-
-metricQuery:
-  dimensions: []
-  metrics:
-    - "performance_metrics_current_score"
-    - "performance_metrics_warning_threshold"
-    - "performance_metrics_critical_threshold"
-    - "performance_metrics_max_score"
-  filters: []
-  sorts: []
-  limit: 1
-
-chartConfig:
-  type: "gauge"
-  config:
-    gaugeChart:
-      selectedField: "performance_metrics_current_score"
-      min: 0
-      maxFieldId: "performance_metrics_max_score"
-      showAxisLabels: true
-      customLabel: "Performance"
-      sections:
-        # Critical zone: 0 to critical_threshold
-        - min: 0
-          maxFieldId: "performance_metrics_critical_threshold"
-          color: "#DC2626"
-        # Warning zone: critical_threshold to warning_threshold
-        - minFieldId: "performance_metrics_critical_threshold"
-          maxFieldId: "performance_metrics_warning_threshold"
-          color: "#F59E0B"
-        # Healthy zone: warning_threshold to max
-        - minFieldId: "performance_metrics_warning_threshold"
-          maxFieldId: "performance_metrics_max_score"
-          color: "#10B981"
-```
-
 ## Common Patterns
 
 ### KPI Dashboard Gauge
 
-For executive dashboards showing current performance vs. target:
-
 ```yaml
 gaugeChart:
   selectedField: "kpi_current_value"
@@ -309,8 +153,6 @@ gaugeChart:
 
 ### Simple Progress Indicator
 
-For tracking completion without color zones:
-
 ```yaml
 gaugeChart:
   selectedField: "completed_count"
@@ -319,28 +161,6 @@ gaugeChart:
   showAxisLabels: true
 ```
 
-### Health Status Gauge
-
-For monitoring system health with thresholds:
-
-```yaml
-gaugeChart:
-  selectedField: "health_score"
-  min: 0
-  max: 100
-  showAxisLabels: true
-  sections:
-    - min: 0
-      max: 50
-      color: "#DC2626"  # Critical
-    - min: 50
-      max: 80
-      color: "#FBBF24"  # Warning
-    - min: 80
-      max: 100
-      color: "#10B981"  # Healthy
-```
-
 ## Tips
 
 1. **Limit to 1 row**: Gauge charts display a single value, so use `limit: 1` in your `metricQuery`.
diff --git a/skills/developing-in-lightdash/resources/map-chart-reference.md b/skills/developing-in-lightdash/resources/map-chart-reference.md
@@ -1,18 +1,18 @@
 # Map Chart Reference
 
-Comprehensive guide to creating map visualizations in Lightdash charts-as-code.
+Guide to creating map visualizations in Lightdash charts-as-code.
 
-## Overview
+> For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/mapChart`.
 
-Map charts allow you to visualize geographical data in Lightdash. They support three visualization types (scatter, area/choropleth, and heatmap) across predefined regions (USA, world, europe) or custom GeoJSON boundaries.
+## Overview
 
-### Use Cases
+Map charts visualize geographical data with three location types:
 
 | Location Type | Description | Best For |
 |--------------|-------------|----------|
-| `scatter` | Points plotted at lat/lon coordinates | Store locations, event locations, customer addresses |
-| `area` | Regions colored by metric value | Sales by state/country, regional performance |
-| `heatmap` | Density visualization of point data | User activity hotspots, incident concentrations |
+| `scatter` | Points at lat/lon coordinates | Store locations, customer addresses |
+| `area` | Regions colored by metric (choropleth) | Sales by state/country |
+| `heatmap` | Density visualization | Activity hotspots |
 
 ### Map Types
 
@@ -23,191 +23,69 @@ Map charts allow you to visualize geographical data in Lightdash. They support t
 | `europe` | European countries | Country names or ISO codes |
 | `custom` | Custom GeoJSON regions | Custom property key |
 
-## Basic Structure
-
-```yaml
-chartConfig:
-  type: map
-  config:
-    # Map type and location visualization
-    mapType: "USA"              # USA, world, europe, custom
-    locationType: "scatter"     # scatter, area, heatmap
-
-    # Data field mappings (depends on locationType)
-    latitudeFieldId: "stores_latitude"
-    longitudeFieldId: "stores_longitude"
-    valueFieldId: "stores_total_sales"
-
-    # Display options
-    showLegend: true
-    tileBackground: "light"
-```
-
-## Configuration Options
+## Key Configuration Properties
 
-### Required Fields by Location Type
+### Location Type Settings
 
-**Scatter Maps** (lat/lon points):
+**Scatter Maps** require latitude and longitude fields:
 ```yaml
 config:
   locationType: "scatter"
-  latitudeFieldId: "field_with_latitude"
-  longitudeFieldId: "field_with_longitude"
-  valueFieldId: "metric_to_display"      # Optional: for coloring
-  sizeFieldId: "metric_for_size"         # Optional: for bubble size
+  latitudeFieldId: "stores_latitude"
+  longitudeFieldId: "stores_longitude"
+  valueFieldId: "metric_for_color"      # Optional
+  sizeFieldId: "metric_for_bubble_size" # Optional
 ```
 
-**Area Maps** (choropleth):
+**Area Maps** match region names to GeoJSON:
 ```yaml
 config:
   locationType: "area"
-  locationFieldId: "field_with_region_names"
-  valueFieldId: "metric_to_display"
-  geoJsonPropertyKey: "name"             # Property in GeoJSON to match against
+  locationFieldId: "orders_state"
+  valueFieldId: "orders_total_sales"
+  geoJsonPropertyKey: "name"
 ```
 
-**Heatmap** (density visualization):
+**Heatmaps** show point density:
 ```yaml
 config:
   locationType: "heatmap"
-  latitudeFieldId: "field_with_latitude"
-  longitudeFieldId: "field_with_longitude"
-  valueFieldId: "metric_for_intensity"   # Optional: affects heat intensity
-```
-
-### Map Type Configuration
-
-```yaml
-# Predefined maps
-config:
-  mapType: "USA"                  # Built-in US states map
-  # OR
-  mapType: "world"                # Built-in world countries map
-  # OR
-  mapType: "europe"               # Built-in European countries map
-```
-
-```yaml
-# Custom GeoJSON map
-config:
-  mapType: "custom"
-  customGeoJsonUrl: "https://example.com/regions.geojson"
-  geoJsonPropertyKey: "region_code"      # Property to match against locationFieldId
-```
-
-### Tile Background
-
-```yaml
-config:
-  tileBackground: "light"         # none, openstreetmap, light, dark, satellite
+  latitudeFieldId: "events_latitude"
+  longitudeFieldId: "events_longitude"
+  valueFieldId: "metric_for_intensity"  # Optional
 ```
 
-| Value | Description |
-|-------|-------------|
-| `none` | No background tiles (regions only) |
-| `openstreetmap` | OpenStreetMap tiles |
-| `light` | Light theme map tiles |
-| `dark` | Dark theme map tiles |
-| `satellite` | Satellite imagery |
-
-### Color Configuration
+### Visual Settings
 
 ```yaml
 config:
-  # Color gradient (2-5 colors)
+  tileBackground: "light"       # none, openstreetmap, light, dark, satellite
+  showLegend: true
   colorRange:
-    - "#fee2e2"                   # Low values (light red)
-    - "#fca5a5"
-    - "#f87171"
-    - "#dc2626"
-    - "#991b1b"                   # High values (dark red)
-
-  # Background and no-data colors
-  backgroundColor: "#ffffff"      # Map background color
-  noDataColor: "#e5e7eb"         # Color for regions without data (area maps)
+    - "#fee2e2"                 # Low values
+    - "#dc2626"                 # High values
+  backgroundColor: "#ffffff"
+  noDataColor: "#e5e7eb"        # For area maps
 ```
 
-### Map View Settings
+### View Settings
 
 ```yaml
 config:
-  # Default view (initial position and zoom)
   defaultZoom: 4
   defaultCenterLat: 39.8283
   defaultCenterLon: -98.5795
-
-  # Save user's current view
-  saveMapExtent: true             # Preserve zoom/pan when saving
-```
-
-### Scatter Map Options
-
-```yaml
-config:
-  locationType: "scatter"
-
-  # Bubble size configuration
-  minBubbleSize: 5                # Minimum bubble radius (pixels)
-  maxBubbleSize: 30               # Maximum bubble radius (pixels)
-  sizeFieldId: "stores_revenue"   # Metric to determine bubble size
-
-  # Color by metric
-  valueFieldId: "stores_profit_margin"
-  colorRange:
-    - "#dc2626"                   # Negative/low
-    - "#fbbf24"                   # Medium
-    - "#22c55e"                   # Positive/high
+  saveMapExtent: true
 ```
 
-### Heatmap Options
-
-```yaml
-config:
-  locationType: "heatmap"
-
-  heatmapConfig:
-    radius: 25                    # Radius of each heat point (pixels)
-    blur: 15                      # Blur amount (pixels)
-    opacity: 0.6                  # Layer opacity (0-1)
-
-  colorRange:
-    - "#3b82f6"                   # Low density (blue)
-    - "#fbbf24"                   # Medium density (yellow)
-    - "#ef4444"                   # High density (red)
-```
-
-### Field Configuration (Tooltips)
-
-```yaml
-config:
-  fieldConfig:
-    stores_store_name:
-      visible: true
-      label: "Store Name"
-    stores_total_sales:
-      visible: true
-      label: "Total Sales"
-    stores_employee_count:
-      visible: false              # Hide from tooltip
-```
-
-### Legend
-
-```yaml
-config:
-  showLegend: true                # Show/hide color scale legend
-```
-
-## Complete Examples
+## Examples
 
 ### Example 1: Store Locations (Scatter Map)
 
-Visualize store locations with bubble size representing revenue.
-
 ```yaml
 version: 1
-name: "Store Locations and Revenue"
-slug: store-locations-revenue
+name: "Store Locations"
+slug: store-locations
 spaceSlug: sales/maps
 tableName: stores
 
@@ -216,74 +94,33 @@ metricQuery:
   dimensions:
     - stores_store_name
     - stores_city
-    - stores_state
   metrics:
     - stores_total_revenue
-    - stores_customer_count
-  filters:
-    stores_is_active:
-      operator: equals
-      values: [true]
   limit: 500
 
 chartConfig:
   type: map
   config:
-    # Map setup
     mapType: "USA"
     locationType: "scatter"
     tileBackground: "light"
-
-    # Location data
     latitudeFieldId: "stores_latitude"
     longitudeFieldId: "stores_longitude"
-
-    # Bubble sizing by revenue
     sizeFieldId: "stores_total_revenue"
     minBubbleSize: 8
     maxBubbleSize: 40
-
-    # Color by customer count
-    valueFieldId: "stores_customer_count"
     colorRange:
       - "#dbeafe"
-      - "#3b82f6"
       - "#1e40af"
-
-    # Display options
     showLegend: true
-    backgroundColor: "#f9fafb"
-
-    # Default view (centered on US)
     defaultZoom: 4
     defaultCenterLat: 39.8283
     defaultCenterLon: -98.5795
-    saveMapExtent: true
-
-    # Tooltip configuration
-    fieldConfig:
-      stores_store_name:
-        visible: true
-        label: "Store"
-      stores_city:
-        visible: true
-        label: "City"
-      stores_state:
-        visible: true
-        label: "State"
-      stores_total_revenue:
-        visible: true
-        label: "Revenue"
-      stores_customer_count:
-        visible: true
-        label: "Customers"
 
 updatedAt: "2024-01-30T12:00:00Z"
 ```
 
-### Example 2: Sales by State (Choropleth/Area Map)
-
-Color US states by total sales volume.
+### Example 2: Sales by State (Choropleth)
 
 ```yaml
 version: 1
@@ -298,247 +135,22 @@ metricQuery:
     - orders_state
   metrics:
     - orders_total_sales
-    - orders_order_count
-  sorts:
-    - fieldId: orders_total_sales
-      descending: true
   limit: 50
 
 chartConfig:
   type: map
   config:
-    # Map setup
     mapType: "USA"
     locationType: "area"
-    tileBackground: "none"        # No tiles for cleaner area map
-
-    # Region matching
+    tileBackground: "none"
     locationFieldId: "orders_state"
-    geoJsonPropertyKey: "name"    # Match against state names
-
-    # Color by sales
+    geoJsonPropertyKey: "name"
     valueFieldId: "orders_total_sales"
     colorRange:
-      - "#f0f9ff"                 # Very low sales (light blue)
-      - "#bfdbfe"
-      - "#60a5fa"
+      - "#f0f9ff"
       - "#2563eb"
-      - "#1e40af"                 # High sales (dark blue)
-
-    # Display options
-    showLegend: true
-    backgroundColor: "#ffffff"
-    noDataColor: "#f3f4f6"        # Light gray for states without data
-
-    # Tooltip configuration
-    fieldConfig:
-      orders_state:
-        visible: true
-        label: "State"
-      orders_total_sales:
-        visible: true
-        label: "Total Sales"
-      orders_order_count:
-        visible: true
-        label: "Orders"
-
-updatedAt: "2024-01-30T12:00:00Z"
-```
-
-### Example 3: Customer Activity Heatmap
-
-Show concentration of customer activity across a region.
-
-```yaml
-version: 1
-name: "Customer Activity Heatmap"
-slug: customer-activity-heatmap
-spaceSlug: analytics/maps
-tableName: events
-
-metricQuery:
-  exploreName: events
-  dimensions:
-    - events_user_id
-  metrics:
-    - events_event_count
-  filters:
-    events_event_type:
-      operator: equals
-      values: ["purchase", "add_to_cart"]
-    events_created_date:
-      operator: inThePast
-      values: [30, "days"]
-  limit: 10000
-
-chartConfig:
-  type: map
-  config:
-    # Map setup
-    mapType: "USA"
-    locationType: "heatmap"
-    tileBackground: "dark"        # Dark background for better contrast
-
-    # Location data
-    latitudeFieldId: "events_latitude"
-    longitudeFieldId: "events_longitude"
-
-    # Heatmap intensity
-    valueFieldId: "events_event_count"
-
-    # Heatmap visual settings
-    heatmapConfig:
-      radius: 20
-      blur: 15
-      opacity: 0.7
-
-    # Color gradient (blue -> yellow -> red)
-    colorRange:
-      - "#3b82f6"
-      - "#10b981"
-      - "#fbbf24"
-      - "#f59e0b"
-      - "#ef4444"
-
-    # Display options
-    showLegend: true
-    backgroundColor: "#1f2937"
-
-    # Default view
-    defaultZoom: 5
-    defaultCenterLat: 37.7749
-    defaultCenterLon: -122.4194
-    saveMapExtent: false
-
-updatedAt: "2024-01-30T12:00:00Z"
-```
-
-### Example 4: Global Sales (World Map)
-
-Visualize sales across countries.
-
-```yaml
-version: 1
-name: "Global Sales by Country"
-slug: global-sales
-spaceSlug: sales/international
-tableName: orders
-
-metricQuery:
-  exploreName: orders
-  dimensions:
-    - orders_country
-  metrics:
-    - orders_total_revenue
-    - orders_order_count
-  sorts:
-    - fieldId: orders_total_revenue
-      descending: true
-  limit: 200
-
-chartConfig:
-  type: map
-  config:
-    # Map setup
-    mapType: "world"
-    locationType: "area"
-    tileBackground: "light"
-
-    # Region matching
-    locationFieldId: "orders_country"
-    geoJsonPropertyKey: "name"    # Match against country names
-    # Alternative: use "ISO3166-1-Alpha-3" for ISO country codes
-
-    # Color by revenue
-    valueFieldId: "orders_total_revenue"
-    colorRange:
-      - "#dcfce7"
-      - "#86efac"
-      - "#22c55e"
-      - "#16a34a"
-      - "#15803d"
-
-    # Display options
-    showLegend: true
-    backgroundColor: "#f0f9ff"
-    noDataColor: "#e5e7eb"
-
-    # Default view (world view)
-    defaultZoom: 2
-    defaultCenterLat: 20
-    defaultCenterLon: 0
-    saveMapExtent: true
-
-    # Tooltip
-    fieldConfig:
-      orders_country:
-        visible: true
-        label: "Country"
-      orders_total_revenue:
-        visible: true
-        label: "Revenue"
-      orders_order_count:
-        visible: true
-        label: "Orders"
-
-updatedAt: "2024-01-30T12:00:00Z"
-```
-
-### Example 5: Custom Regional Map
-
-Use custom GeoJSON for specific regions (e.g., sales territories).
-
-```yaml
-version: 1
-name: "Sales by Territory"
-slug: sales-by-territory
-spaceSlug: sales/maps
-tableName: orders
-
-metricQuery:
-  exploreName: orders
-  dimensions:
-    - orders_territory_code
-  metrics:
-    - orders_total_sales
-  limit: 100
-
-chartConfig:
-  type: map
-  config:
-    # Custom GeoJSON map
-    mapType: "custom"
-    customGeoJsonUrl: "https://storage.example.com/maps/sales-territories.geojson"
-    geoJsonPropertyKey: "territory_code"
-
-    # Area visualization
-    locationType: "area"
-    tileBackground: "openstreetmap"
-
-    # Region matching
-    locationFieldId: "orders_territory_code"
-
-    # Color by sales
-    valueFieldId: "orders_total_sales"
-    colorRange:
-      - "#fef3c7"
-      - "#fde047"
-      - "#facc15"
-      - "#eab308"
-
-    # Display
     showLegend: true
-    backgroundColor: "#ffffff"
-    noDataColor: "#d1d5db"
-
-    # Tooltip
-    fieldConfig:
-      orders_territory_code:
-        visible: true
-        label: "Territory"
-      orders_total_sales:
-        visible: true
-        label: "Sales"
+    noDataColor: "#f3f4f6"
 
 updatedAt: "2024-01-30T12:00:00Z"
 ```
@@ -547,319 +159,62 @@ updatedAt: "2024-01-30T12:00:00Z"
 
 ### For Scatter and Heatmap Maps
 
-Your data must include:
 - Latitude field (numeric, -90 to 90)
 - Longitude field (numeric, -180 to 180)
-- Optional: metric for coloring points
-- Optional: metric for sizing points (scatter only)
-
-```sql
--- Example dbt model for scatter map data
-SELECT
-    store_id,
-    store_name,
-    latitude,
-    longitude,
-    total_revenue,
-    customer_count
-FROM {{ ref('stores') }}
-WHERE is_active = true
-```
+- Optional metric for coloring or sizing
 
 ### For Area/Choropleth Maps
 
-Your data must include:
-- Location field matching GeoJSON properties
-  - For USA map: State names (e.g., "California", "Texas") or codes
-  - For World map: Country names or ISO codes
-  - For Custom maps: Values matching your `geoJsonPropertyKey`
+- Location field matching GeoJSON properties:
+  - USA map: State names ("California", "Texas")
+  - World map: Country names or ISO codes
+  - Custom maps: Values matching `geoJsonPropertyKey`
 - Metric for coloring regions
 
-```sql
--- Example dbt model for area map data
-SELECT
-    state_name,
-    SUM(order_total) as total_sales,
-    COUNT(*) as order_count
-FROM {{ ref('orders') }}
-GROUP BY state_name
-```
-
 ## GeoJSON Property Keys
 
-### USA Map
-
-Match against state names:
-```yaml
-geoJsonPropertyKey: "name"        # "California", "Texas", etc.
-```
-
-### World Map
-
-Match against country names or ISO codes:
-```yaml
-geoJsonPropertyKey: "name"        # "United States", "France", etc.
-# OR
-geoJsonPropertyKey: "ISO3166-1-Alpha-3"  # "USA", "FRA", etc.
-```
-
-### Europe Map
-
-Match against country names or codes:
-```yaml
-geoJsonPropertyKey: "name"        # "Germany", "France", etc.
-```
-
-### Custom Maps
-
-Specify the property in your GeoJSON that contains the identifier:
-```yaml
-geoJsonPropertyKey: "region_code"
-# Matches against a property in your GeoJSON like:
-# { "type": "Feature", "properties": { "region_code": "NE-1" } }
-```
+| Map Type | Property Key | Example Values |
+|----------|--------------|----------------|
+| USA | `name` | "California", "Texas" |
+| World | `name` | "United States", "France" |
+| World | `ISO3166-1-Alpha-3` | "USA", "FRA" |
+| Europe | `name` | "Germany", "France" |
+| Custom | User-defined | Matches your GeoJSON |
 
 ## Best Practices
 
 ### Choosing Location Type
 
-**Use Scatter When:**
-- You have precise lat/lon coordinates
-- Visualizing individual locations (stores, customers, events)
-- Want to show size variation (bubble map)
-- Point density varies significantly
-
-**Use Area/Choropleth When:**
-- Comparing metrics across regions
-- Data aggregated by political boundaries
-- Showing distribution patterns
-- Region comparison is the goal
-
-**Use Heatmap When:**
-- Showing density/concentration of points
-- Many overlapping points
-- Identifying activity hotspots
-- Precise locations less important than patterns
-
-### Color Range Guidelines
-
-1. **Sequential** (low to high):
-   ```yaml
-   colorRange:
-     - "#f0f9ff"  # Light
-     - "#0284c7"  # Dark
-   ```
-
-2. **Diverging** (negative to positive):
-   ```yaml
-   colorRange:
-     - "#dc2626"  # Negative (red)
-     - "#f3f4f6"  # Neutral (gray)
-     - "#22c55e"  # Positive (green)
-   ```
-
-3. **Multi-class** (categories):
-   ```yaml
-   colorRange:
-     - "#3b82f6"  # Blue
-     - "#10b981"  # Green
-     - "#f59e0b"  # Orange
-     - "#ef4444"  # Red
-   ```
-
-### Performance Tips
-
-1. **Limit data points**:
-   - Scatter: 500-1000 points max for smooth interaction
-   - Heatmap: Can handle more (5000+) but test performance
-   - Area: Limited by number of regions (usually fine)
-
-2. **Use appropriate aggregation**:
-   ```yaml
-   metricQuery:
-     limit: 1000  # Reasonable limit for maps
-   ```
-
-3. **Filter to relevant data**:
-   ```yaml
-   metricQuery:
-     filters:
-       stores_is_active:
-         operator: equals
-         values: [true]
-   ```
-
-### Accessibility
-
-1. **Use colorblind-friendly palettes**:
-   ```yaml
-   colorRange:
-     - "#fee2e2"  # Red tints
-     - "#dbeafe"  # Blue tints
-   ```
-
-2. **Include tooltips with context**:
-   ```yaml
-   fieldConfig:
-     location_name:
-       visible: true
-       label: "Location"
-     metric_value:
-       visible: true
-       label: "Sales ($)"
-   ```
-
-3. **Provide legend**:
-   ```yaml
-   showLegend: true
-   ```
-
-### Data Matching Tips
-
-**For area maps**, ensure your location values match GeoJSON properties:
-
-```yaml
-# If your data has "CA" but GeoJSON has "California"
-# Transform in dbt:
-CASE
-  WHEN state_code = 'CA' THEN 'California'
-  WHEN state_code = 'TX' THEN 'Texas'
-  ...
-END as state_name
-```
-
-**For international data**, standardize country names:
-
-```yaml
-# Use ISO codes for reliability
-SELECT
-  country_iso_code,  -- Use ISO 3166-1 Alpha-3
-  SUM(revenue) as total_revenue
-FROM orders
-GROUP BY country_iso_code
-```
+- **Scatter**: Precise coordinates, individual locations, bubble sizing needed
+- **Area**: Comparing metrics across regions, political boundary analysis
+- **Heatmap**: Density patterns, many overlapping points
 
-## Common Issues and Solutions
+### Performance
 
-### Issue: Regions not showing data
+- Scatter: Limit to 500-1000 points
+- Heatmap: Can handle 5000+ points
+- Area: Limited by number of regions (usually fine)
 
-**Solution**: Check `geoJsonPropertyKey` matches your data field values exactly (case-sensitive).
+### Color Guidelines
 
+**Sequential** (low to high): Light to dark of same hue
 ```yaml
-# Debug by listing unique values in your data
-SELECT DISTINCT state_name FROM orders;
-
-# Compare with GeoJSON property
-# USA map uses full state names: "California", not "CA"
-geoJsonPropertyKey: "name"
-locationFieldId: "orders_state_name"  # Must match exactly
+colorRange: ["#f0f9ff", "#0284c7"]
 ```
 
-### Issue: Points not appearing on scatter map
-
-**Solution**: Verify latitude/longitude are valid numbers in correct ranges.
-
+**Diverging** (negative to positive): Two colors through neutral
 ```yaml
-# Latitude: -90 to 90
-# Longitude: -180 to 180
-
-# Check in dbt:
-SELECT *
-FROM stores
-WHERE latitude < -90 OR latitude > 90
-   OR longitude < -180 OR longitude > 180
+colorRange: ["#dc2626", "#f3f4f6", "#22c55e"]
 ```
 
-### Issue: Map shows but no colors
+## Common Issues
 
-**Solution**: Ensure `valueFieldId` is in your metric query and contains data.
-
-```yaml
-metricQuery:
-  metrics:
-    - orders_total_sales  # Must be included
-
-chartConfig:
-  type: map
-  config:
-    valueFieldId: "orders_total_sales"  # Must match exactly
-```
-
-### Issue: Bubbles all same size
-
-**Solution**: Add `sizeFieldId` or check the field has variation.
-
-```yaml
-config:
-  sizeFieldId: "stores_revenue"  # Must have varying values
-  minBubbleSize: 5
-  maxBubbleSize: 30
-```
-
-## Map Type Reference
-
-| Map Type | GeoJSON Properties Available | Common Use Cases |
-|----------|----------------------------|------------------|
-| `USA` | `name` (full state names) | US state-level analysis |
-| `world` | `name`, `ISO3166-1-Alpha-3` | Country comparisons |
-| `europe` | `name`, country codes | European regional analysis |
-| `custom` | User-defined | Sales territories, custom regions |
-
-## Complete Configuration Reference
-
-```yaml
-chartConfig:
-  type: map
-  config:
-    # Core configuration
-    mapType: "USA"                      # USA, world, europe, custom
-    locationType: "scatter"             # scatter, area, heatmap
-
-    # Custom map (if mapType: "custom")
-    customGeoJsonUrl: "https://..."
-    geoJsonPropertyKey: "property_name"
-
-    # Data field mappings
-    latitudeFieldId: "field_name"       # For scatter/heatmap
-    longitudeFieldId: "field_name"      # For scatter/heatmap
-    locationFieldId: "field_name"       # For area maps
-    valueFieldId: "field_name"          # Metric for coloring
-    sizeFieldId: "field_name"           # Metric for sizing (scatter)
-
-    # Visual settings
-    tileBackground: "light"             # none, openstreetmap, light, dark, satellite
-    backgroundColor: "#ffffff"
-    noDataColor: "#e5e7eb"             # For area maps
-    showLegend: true
-
-    # Color gradient
-    colorRange:
-      - "#color1"
-      - "#color2"
-      - "#color3"
-
-    # View settings
-    defaultZoom: 4
-    defaultCenterLat: 39.8283
-    defaultCenterLon: -98.5795
-    saveMapExtent: false
-
-    # Scatter-specific
-    minBubbleSize: 5
-    maxBubbleSize: 30
-
-    # Heatmap-specific
-    heatmapConfig:
-      radius: 25
-      blur: 15
-      opacity: 0.6
-
-    # Tooltip configuration
-    fieldConfig:
-      field_name:
-        visible: true
-        label: "Display Label"
-```
+| Issue | Solution |
+|-------|----------|
+| Regions not showing data | Check `geoJsonPropertyKey` matches data exactly (case-sensitive) |
+| Points not appearing | Verify lat/lon are valid (-90 to 90, -180 to 180) |
+| No colors showing | Ensure `valueFieldId` is in your metric query |
+| Bubbles all same size | Add `sizeFieldId` with varying values |
 
 ## Related Resources
 
diff --git a/skills/developing-in-lightdash/resources/pie-chart-reference.md b/skills/developing-in-lightdash/resources/pie-chart-reference.md
@@ -1,6 +1,8 @@
 # Pie Chart Reference
 
-Comprehensive guide for configuring pie and donut charts in Lightdash charts-as-code.
+Guide for configuring pie and donut charts in Lightdash charts-as-code.
+
+> **Schema Reference**: For the complete schema definition, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/pieChart`.
 
 ## Overview
 
@@ -12,13 +14,11 @@ Pie charts display part-to-whole relationships by dividing a circle into slices
 - Showing proportions of a whole (percentages that sum to 100%)
 - Comparing 3-7 categories
 - When exact values are less important than relative proportions
-- Simple categorical breakdowns
 
 **Avoid when:**
 - Comparing many categories (>7 slices)
 - Precise comparisons are needed (use bar chart instead)
 - Showing changes over time (use line chart instead)
-- Values don't represent parts of a whole
 
 ### Pie vs Donut
 
@@ -27,8 +27,6 @@ Pie charts display part-to-whole relationships by dividing a circle into slices
 | Visual | Solid circle | Ring with hole |
 | Use case | Single metric focus | Better for comparisons |
 | Center space | None | Can display total/summary |
-| Readability | Good for few slices | Better for many slices |
-| When to use | Traditional preference | Modern dashboards, multiple charts |
 
 ## Basic Structure
 
@@ -67,265 +65,40 @@ chartConfig:
 
 ### Core Settings
 
-```yaml
-chartConfig:
-  type: pie
-  config:
-    # Required fields
-    groupFieldIds:
-      - orders_product_category        # Array of field IDs for slicing
-    metricId: orders_total_revenue     # The metric to display
-
-    # Pie vs Donut
-    isDonut: false                     # true = donut chart with hollow center
-```
+| Property | Type | Description |
+|----------|------|-------------|
+| `groupFieldIds` | `string[]` | Array of field IDs for slicing (required) |
+| `metricId` | `string` | The metric to display (required) |
+| `isDonut` | `boolean` | `true` = donut chart with hollow center |
 
 ### Value Labels
 
-Control what information appears on each slice:
+| Property | Type | Description |
+|----------|------|-------------|
+| `valueLabel` | `"hidden" \| "inside" \| "outside"` | Position of labels on slices |
+| `showValue` | `boolean` | Show actual numeric values |
+| `showPercentage` | `boolean` | Show percentage of total |
 
-```yaml
-config:
-  # Label position
-  valueLabel: inside                   # Options: hidden, inside, outside
+### Legend
 
-  # What to show
-  showValue: true                      # Show actual numeric values
-  showPercentage: true                 # Show percentage of total
-```
+| Property | Type | Description |
+|----------|------|-------------|
+| `showLegend` | `boolean` | Show/hide legend |
+| `legendPosition` | `"horizontal" \| "vertical"` | Legend orientation |
+| `legendMaxItemLength` | `number` | Max characters before truncation |
 
-**Label Position Options:**
-- `hidden` - No labels on slices (legend only)
-- `inside` - Labels appear within each slice
-- `outside` - Labels appear outside with connecting lines
+### Customization
 
-**Example combinations:**
-```yaml
-# Show both value and percentage inside slices
-valueLabel: inside
-showValue: true
-showPercentage: true
-# Result: "Electronics\n$45,230 (32%)"
-
-# Show only percentages outside
-valueLabel: outside
-showValue: false
-showPercentage: true
-# Result: "32%"
-
-# No slice labels (use legend only)
-valueLabel: hidden
-```
+| Property | Type | Description |
+|----------|------|-------------|
+| `groupLabelOverrides` | `Record<string, string>` | Custom display labels for slices |
+| `groupColorOverrides` | `Record<string, string>` | Custom hex colors for slices |
+| `groupSortOverrides` | `string[]` | Custom sort order (clockwise from top) |
+| `groupValueOptionOverrides` | `Record<string, {...}>` | Per-slice display options |
 
-### Legend Configuration
+## Complete Example
 
-```yaml
-config:
-  # Legend visibility and position
-  showLegend: true                     # Show/hide legend
-  legendPosition: vertical             # Options: horizontal, vertical
-
-  # Legend text wrapping
-  legendMaxItemLength: 50              # Max characters before truncation
-```
-
-**Legend Position:**
-- `horizontal` - Legend appears below chart, items flow left-to-right
-- `vertical` - Legend appears to the right, items stack top-to-bottom
-
-### Custom Labels
-
-Override the default labels for specific slices:
-
-```yaml
-config:
-  groupLabelOverrides:
-    "NA": "North America"              # Key: original value, Value: display label
-    "EU": "Europe"
-    "APAC": "Asia Pacific"
-```
-
-**Use cases:**
-- Expand abbreviations
-- Add context to codes
-- Translate technical names to business terms
-- Add emojis or special characters
-
-### Custom Colors
-
-Override default colors for specific slices:
-
-```yaml
-config:
-  groupColorOverrides:
-    "Electronics": "#3b82f6"           # Blue
-    "Furniture": "#10b981"             # Green
-    "Office Supplies": "#f59e0b"       # Orange
-    "Other": "#94a3b8"                 # Gray
-```
-
-**Color format:** Hex color codes (`#RRGGBB`)
-
-**Best practices:**
-- Use brand colors for key categories
-- Use semantic colors (green = good, red = bad)
-- Use muted colors for "Other" or less important slices
-- Maintain sufficient contrast between adjacent slices
-
-### Metadata Colors
-
-Alternative way to set colors using metadata structure:
-
-```yaml
-config:
-  metadata:
-    orders_product_category:
-      Electronics:
-        color: "#3b82f6"
-      Furniture:
-        color: "#10b981"
-```
-
-**Note:** `groupColorOverrides` is simpler and recommended for most cases.
-
-### Per-Slice Display Options
-
-Override label settings for individual slices:
-
-```yaml
-config:
-  groupValueOptionOverrides:
-    "Other":                           # Hide labels for "Other" category
-      valueLabel: hidden
-    "Electronics":                     # Show value but not percentage
-      showValue: true
-      showPercentage: false
-    "Furniture":                       # Show outside for largest slice
-      valueLabel: outside
-      showValue: true
-      showPercentage: true
-```
-
-**Use cases:**
-- Hide labels for very small slices
-- Show detailed info only for key categories
-- Position labels outside for largest slices to avoid overlap
-- Simplify cluttered charts
-
-### Custom Sort Order
-
-Control the order slices appear (clockwise from top):
-
-```yaml
-config:
-  groupSortOverrides:
-    - "Electronics"                    # First slice (12 o'clock position)
-    - "Furniture"
-    - "Office Supplies"
-    - "Other"                          # Last slice
-```
-
-**Default behavior:** Slices are ordered by the `metricQuery.sorts` configuration.
-
-**Best practices:**
-- Put largest slice at top (12 o'clock)
-- Group related categories together
-- Put "Other" or miscellaneous categories last
-- Consider clockwise reading pattern (top → right → bottom → left)
-
-## Complete Examples
-
-### Basic Pie Chart
-
-Simple revenue breakdown by category:
-
-```yaml
-version: 1
-name: "Revenue by Category"
-slug: revenue-by-category
-spaceSlug: sales
-tableName: orders
-updatedAt: 2026-01-30T10:00:00Z
-
-metricQuery:
-  exploreName: orders
-  dimensions:
-    - orders_product_category
-  metrics:
-    - orders_total_revenue
-  sorts:
-    - fieldId: orders_total_revenue
-      descending: true
-  limit: 10
-
-chartConfig:
-  type: pie
-  config:
-    groupFieldIds:
-      - orders_product_category
-    metricId: orders_total_revenue
-    isDonut: false
-    valueLabel: inside
-    showValue: true
-    showPercentage: true
-    showLegend: true
-    legendPosition: vertical
-```
-
-### Donut Chart with Custom Colors
-
-Modern donut chart with brand colors:
-
-```yaml
-version: 1
-name: "Customer Segments"
-slug: customer-segments
-spaceSlug: marketing
-tableName: customers
-updatedAt: 2026-01-30T10:00:00Z
-
-metricQuery:
-  exploreName: customers
-  dimensions:
-    - customers_segment
-  metrics:
-    - customers_total_lifetime_value
-  sorts:
-    - fieldId: customers_total_lifetime_value
-      descending: true
-  limit: 5
-
-chartConfig:
-  type: pie
-  config:
-    groupFieldIds:
-      - customers_segment
-    metricId: customers_total_lifetime_value
-
-    # Donut style
-    isDonut: true
-
-    # Labels
-    valueLabel: outside
-    showValue: false
-    showPercentage: true
-
-    # Legend
-    showLegend: true
-    legendPosition: horizontal
-
-    # Custom colors
-    groupColorOverrides:
-      "Enterprise": "#7c3aed"          # Purple
-      "Mid-Market": "#3b82f6"          # Blue
-      "SMB": "#10b981"                 # Green
-      "Startup": "#f59e0b"             # Orange
-      "Other": "#6b7280"               # Gray
-```
-
-### Advanced Configuration
-
-Comprehensive example with all customization options:
+Donut chart with custom colors and labels:
 
 ```yaml
 version: 1
@@ -356,15 +129,14 @@ chartConfig:
     # Donut chart
     isDonut: true
 
-    # Default label settings
+    # Labels
     valueLabel: inside
     showValue: true
     showPercentage: true
 
     # Legend
     showLegend: true
     legendPosition: vertical
-    legendMaxItemLength: 30
 
     # Custom labels for region codes
     groupLabelOverrides:
@@ -375,423 +147,81 @@ chartConfig:
 
     # Brand colors for regions
     groupColorOverrides:
-      "NA": "#3b82f6"                  # Blue
-      "EMEA": "#10b981"                # Green
-      "APAC": "#f59e0b"                # Orange
-      "LATAM": "#ef4444"               # Red
-      "Other": "#94a3b8"               # Gray
+      "NA": "#3b82f6"
+      "EMEA": "#10b981"
+      "APAC": "#f59e0b"
+      "LATAM": "#ef4444"
+      "Other": "#94a3b8"
 
-    # Custom display for specific slices
+    # Hide labels for small "Other" slice
     groupValueOptionOverrides:
-      "Other":                         # Hide "Other" labels
+      "Other":
         valueLabel: hidden
-      "NA":                            # Show NA outside (largest)
-        valueLabel: outside
-        showValue: true
-        showPercentage: true
 
     # Custom sort order
     groupSortOverrides:
-      - "NA"                           # Largest first
+      - "NA"
       - "EMEA"
       - "APAC"
       - "LATAM"
-      - "Other"                        # Smallest last
-```
-
-### Multi-Dimension Grouping
-
-Using multiple dimensions for nested grouping:
-
-```yaml
-version: 1
-name: "Sales by Region and Channel"
-slug: sales-region-channel
-spaceSlug: sales
-tableName: orders
-updatedAt: 2026-01-30T10:00:00Z
-
-metricQuery:
-  exploreName: orders
-  dimensions:
-    - orders_region
-    - orders_sales_channel
-  metrics:
-    - orders_total_revenue
-  sorts:
-    - fieldId: orders_total_revenue
-      descending: true
-  limit: 15
-
-chartConfig:
-  type: pie
-  config:
-    groupFieldIds:
-      - orders_region                  # Primary grouping
-      - orders_sales_channel           # Secondary grouping
-    metricId: orders_total_revenue
-
-    isDonut: true
-    valueLabel: outside
-    showValue: false
-    showPercentage: true
-    showLegend: true
-    legendPosition: vertical
-    legendMaxItemLength: 40
+      - "Other"
 ```
 
-**Note:** When using multiple group fields, slices represent unique combinations (e.g., "North America - Online", "North America - Retail", "Europe - Online", etc.)
-
 ## Best Practices
 
 ### Data Preparation
 
 1. **Limit categories**: 3-7 slices for best readability
-   ```yaml
-   metricQuery:
-     limit: 7                          # Limit to top 7 categories
-   ```
-
-2. **Group small values**: Combine small slices into "Other"
-   ```sql
-   -- In your dbt model
-   CASE
-     WHEN category IN ('Electronics', 'Furniture', 'Office Supplies') THEN category
-     ELSE 'Other'
-   END AS category_grouped
-   ```
-
-3. **Sort by value**: Largest slice first
-   ```yaml
-   metricQuery:
-     sorts:
-       - fieldId: orders_total_revenue
-         descending: true
-   ```
+2. **Sort by value**: Largest slice first using `metricQuery.sorts`
+3. **Group small values**: Combine small slices into "Other" in your dbt model
 
 ### Visual Design
 
-1. **Use donut for modern look**: Better for dashboards
-   ```yaml
-   config:
-     isDonut: true
-   ```
-
-2. **Position largest slice at 12 o'clock**: Use `groupSortOverrides`
-
-3. **Avoid too many labels**: Use `hidden` or selective `groupValueOptionOverrides` for small slices
-
-4. **Show percentages**: More meaningful than raw values for pie charts
-   ```yaml
-   config:
-     showValue: false
-     showPercentage: true
-   ```
-
-5. **Use consistent colors**: Same category = same color across charts
-   ```yaml
-   config:
-     groupColorOverrides:
-       "Electronics": "#3b82f6"        # Use same blue everywhere
-   ```
+1. **Use donut for modern look**: Set `isDonut: true`
+2. **Show percentages over values**: More meaningful for pie charts
+3. **Use consistent colors**: Same category = same color across charts
+4. **Mute "Other"**: Use gray (`#94a3b8`) for miscellaneous categories
 
 ### Label Placement
 
-**Use `inside` when:**
-- Few slices (3-5)
-- Slices are relatively large
-- Space is limited
-
-**Use `outside` when:**
-- Many slices (6-7)
-- Some slices are very small
-- Labels are long
-- Exact values are important
-
-**Use `hidden` when:**
-- More than 7 slices
-- Using comprehensive legend
-- Chart is part of dashboard with other context
+| Position | Best for |
+|----------|----------|
+| `inside` | Few slices (3-5), large slices |
+| `outside` | Many slices (6-7), long labels |
+| `hidden` | 7+ slices, comprehensive legend |
 
 ### Color Selection
 
-1. **Sequential palette**: For ordered categories (low → high)
-   ```yaml
-   groupColorOverrides:
-     "Small": "#dbeafe"               # Light blue
-     "Medium": "#3b82f6"              # Blue
-     "Large": "#1e40af"               # Dark blue
-   ```
-
-2. **Categorical palette**: For unordered categories
-   ```yaml
-   groupColorOverrides:
-     "Electronics": "#3b82f6"         # Blue
-     "Furniture": "#10b981"           # Green
-     "Supplies": "#f59e0b"            # Orange
-   ```
-
-3. **Semantic colors**: For meaningful categories
-   ```yaml
-   groupColorOverrides:
-     "Profit": "#22c55e"              # Green
-     "Break-even": "#eab308"          # Yellow
-     "Loss": "#ef4444"                # Red
-   ```
-
-4. **Accessibility**: Ensure sufficient contrast
-   - Avoid similar colors next to each other
-   - Don't rely on color alone (use labels)
-   - Test with color blindness simulators
-
-## Common Patterns
-
-### Top N with Other
-
-Show top categories, group rest as "Other":
-
-```yaml
-# In dbt model
-SELECT
-  CASE
-    WHEN rank <= 5 THEN category
-    ELSE 'Other'
-  END AS category,
-  SUM(revenue) as revenue
-FROM (
-  SELECT
-    category,
-    RANK() OVER (ORDER BY SUM(revenue) DESC) as rank,
-    revenue
-  FROM orders
-  GROUP BY 1
-)
-GROUP BY 1
-
-# In chart
-config:
-  groupColorOverrides:
-    "Other": "#94a3b8"                 # Gray for Other
-  groupValueOptionOverrides:
-    "Other":
-      valueLabel: hidden               # Hide Other label
-```
-
-### Regional Comparison
-
-Consistent colors across regional charts:
-
-```yaml
-# Define color scheme once, reuse across charts
-config:
-  groupColorOverrides:
-    "North America": "#3b82f6"
-    "Europe": "#10b981"
-    "Asia Pacific": "#f59e0b"
-    "Latin America": "#ef4444"
-    "Middle East": "#8b5cf6"
-    "Africa": "#ec4899"
-```
-
-### Status/Health Indicators
-
-Use semantic colors:
-
-```yaml
-config:
-  groupLabelOverrides:
-    "active": "Active"
-    "warning": "Needs Attention"
-    "critical": "Critical"
-
-  groupColorOverrides:
-    "active": "#22c55e"                # Green
-    "warning": "#f59e0b"               # Orange
-    "critical": "#ef4444"              # Red
-
-  groupSortOverrides:
-    - "active"                         # Green first
-    - "warning"
-    - "critical"                       # Red last
-```
+- **Sequential**: Light to dark for ordered categories
+- **Categorical**: Distinct colors for unordered categories
+- **Semantic**: Green for good, red for bad, yellow for warning
 
 ## Troubleshooting
 
 ### Slices Too Small to Read
 
-**Problem:** Many small slices with overlapping labels
-
-**Solutions:**
-```yaml
-# Option 1: Hide labels for small slices
-config:
-  groupValueOptionOverrides:
-    "Small Category":
-      valueLabel: hidden
-
-# Option 2: Use outside labels
-config:
-  valueLabel: outside
-
-# Option 3: Limit categories in query
-metricQuery:
-  limit: 5
-```
-
-### Legend Items Truncated
-
-**Problem:** Long category names cut off
-
-**Solution:**
+Hide labels for small slices:
 ```yaml
-config:
-  legendMaxItemLength: 100             # Increase from default 50
-  legendPosition: vertical             # More space than horizontal
+groupValueOptionOverrides:
+  "Small Category":
+    valueLabel: hidden
 ```
 
 ### Colors Not Applying
 
-**Problem:** Custom colors don't appear
+- Check spelling (case-sensitive)
+- Verify hex format (`#RRGGBB`)
+- Ensure values match data exactly
 
-**Checklist:**
-1. Check spelling of category values (case-sensitive)
-2. Verify hex color format (`#RRGGBB`)
-3. Ensure keys match exact values from data
-4. Check that values appear in query results
+### Legend Truncated
 
 ```yaml
-# Debug: Check exact values
-metricQuery:
-  dimensions:
-    - orders_category                  # Check actual values returned
-
-config:
-  groupColorOverrides:
-    "Electronics": "#3b82f6"           # Must match exactly (case-sensitive)
-```
-
-### Percentages Don't Sum to 100%
-
-**Problem:** Chart shows percentages that don't total 100%
-
-**Explanation:** This is expected when:
-- Using `limit` in query (excludes some data)
-- Filtering reduces total
-- Rounding differences
-
-**Solution:** Add context in description or include "Other" category
-
-## Schema Reference
-
-Complete JSON schema definition:
-
-```json
-{
-  "type": ["object", "null"],
-  "description": "Configuration for pie and donut charts",
-  "additionalProperties": false,
-  "properties": {
-    "groupFieldIds": {
-      "type": "array",
-      "description": "Field IDs used for grouping/slicing the pie",
-      "items": {
-        "type": "string"
-      }
-    },
-    "metricId": {
-      "type": "string",
-      "description": "Field ID of the metric to display"
-    },
-    "isDonut": {
-      "type": "boolean",
-      "description": "Display as donut chart with hole in center"
-    },
-    "valueLabel": {
-      "type": "string",
-      "enum": ["hidden", "inside", "outside"],
-      "description": "Position of value labels on slices"
-    },
-    "showValue": {
-      "type": "boolean",
-      "description": "Show the actual value on slices"
-    },
-    "showPercentage": {
-      "type": "boolean",
-      "description": "Show percentage on slices"
-    },
-    "groupLabelOverrides": {
-      "type": "object",
-      "description": "Custom labels for each group/slice",
-      "additionalProperties": {
-        "type": "string"
-      }
-    },
-    "groupColorOverrides": {
-      "type": "object",
-      "description": "Custom colors for each group/slice",
-      "additionalProperties": {
-        "type": "string"
-      }
-    },
-    "groupValueOptionOverrides": {
-      "type": "object",
-      "description": "Per-slice value display options",
-      "additionalProperties": {
-        "type": "object",
-        "additionalProperties": false,
-        "properties": {
-          "valueLabel": {
-            "type": "string",
-            "enum": ["hidden", "inside", "outside"]
-          },
-          "showValue": {
-            "type": "boolean"
-          },
-          "showPercentage": {
-            "type": "boolean"
-          }
-        }
-      }
-    },
-    "groupSortOverrides": {
-      "type": "array",
-      "description": "Custom sort order for groups/slices",
-      "items": {
-        "type": "string"
-      }
-    },
-    "showLegend": {
-      "type": "boolean",
-      "description": "Show the chart legend"
-    },
-    "legendPosition": {
-      "type": "string",
-      "enum": ["horizontal", "vertical"],
-      "description": "Legend orientation"
-    },
-    "legendMaxItemLength": {
-      "type": "number",
-      "description": "Maximum character length for legend items"
-    },
-    "metadata": {
-      "type": "object",
-      "description": "Metadata for series (colors, etc.)",
-      "additionalProperties": {
-        "type": "object",
-        "properties": {
-          "color": {
-            "type": "string"
-          }
-        }
-      }
-    }
-  }
-}
+legendMaxItemLength: 100
+legendPosition: vertical
 ```
 
 ## Related Documentation
 
-- [Chart Types Reference](chart-types-reference.md) - Overview of all chart types
-- [Metrics Reference](metrics-reference.md) - Defining metrics for pie charts
-- [Dimensions Reference](dimensions-reference.md) - Configuring grouping dimensions
-- [Dashboard Reference](dashboard-reference.md) - Adding pie charts to dashboards
+- [Chart Types Reference](chart-types-reference.md)
+- [Metrics Reference](metrics-reference.md)
+- [Dimensions Reference](dimensions-reference.md)
diff --git a/skills/developing-in-lightdash/resources/table-chart-reference.md b/skills/developing-in-lightdash/resources/table-chart-reference.md
@@ -4,12 +4,13 @@
 
 Table visualizations display your query results in a tabular format with powerful configuration options for customization, conditional formatting, and data presentation. Tables support features like frozen columns, bar visualizations within cells, custom column names, and sophisticated conditional formatting rules.
 
-## YAML Structure
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/tableChart`.
+
+## Basic YAML Structure
 
 ```yaml
 version: 1
 name: "My Table Chart"
-description: "Optional description"
 slug: "my-table-chart"
 spaceSlug: "my-space"
 tableName: "my_explore"
@@ -18,340 +19,85 @@ updatedAt: "2024-01-30T12:00:00Z"
 metricQuery:
   dimensions:
     - field_id_1
-    - field_id_2
   metrics:
     - metric_id_1
-    - metric_id_2
 
 chartConfig:
   type: "table"
   config:
-    # Display options
     showColumnCalculation: true
-    showRowCalculation: false
-    showTableNames: false
     hideRowNumbers: false
-    showResultsTotal: true
-    showSubtotals: false
-    metricsAsRows: false
-
-    # Column-specific configuration
     columns:
       field_id_1:
         visible: true
         name: "Custom Column Name"
         frozen: true
-        displayStyle: "text"
-      metric_id_1:
-        visible: true
-        displayStyle: "bar"
-        color: "#4A90E2"
-
-    # Conditional formatting
-    conditionalFormattings:
-      - target:
-          fieldId: "metric_id_1"
-        color: "#FF0000"
-        rules:
-          - id: "rule-1"
-            operator: "greaterThan"
-            values: [100]
-        applyTo: "cell"
+    conditionalFormattings: []
 ```
 
-## Table Configuration Options
+## Key Configuration Options
 
 ### Display Options
 
-#### `showColumnCalculation`
-- **Type**: `boolean`
-- **Description**: Show column totals/calculations at the bottom of the table
-- **Default**: Varies by configuration
-- **Example**:
-  ```yaml
-  showColumnCalculation: true
-  ```
-
-#### `showRowCalculation`
-- **Type**: `boolean`
-- **Description**: Show row totals/calculations in an additional column
-- **Default**: Varies by configuration
-- **Example**:
-  ```yaml
-  showRowCalculation: false
-  ```
-
-#### `showTableNames`
-- **Type**: `boolean`
-- **Description**: Show table names in column headers (e.g., "users.name" vs "name")
-- **Default**: Varies by configuration
-- **Example**:
-  ```yaml
-  showTableNames: false
-  ```
-
-#### `hideRowNumbers`
-- **Type**: `boolean`
-- **Description**: Hide the row number column on the left
-- **Default**: `false`
-- **Example**:
-  ```yaml
-  hideRowNumbers: true
-  ```
-
-#### `showResultsTotal`
-- **Type**: `boolean`
-- **Description**: Show total count of results
-- **Default**: Varies by configuration
-- **Example**:
-  ```yaml
-  showResultsTotal: true
-  ```
-
-#### `showSubtotals`
-- **Type**: `boolean`
-- **Description**: Show subtotal rows for grouped data
-- **Default**: Varies by configuration
-- **Example**:
-  ```yaml
-  showSubtotals: true
-  ```
-
-#### `metricsAsRows`
-- **Type**: `boolean`
-- **Description**: Display metrics as rows instead of columns (pivoted view)
-- **Default**: `false`
-- **Example**:
-  ```yaml
-  metricsAsRows: true
-  ```
+| Property | Type | Description |
+|----------|------|-------------|
+| `showColumnCalculation` | boolean | Show column totals at the bottom |
+| `showRowCalculation` | boolean | Show row totals in an additional column |
+| `showTableNames` | boolean | Show table names in column headers (e.g., "users.name" vs "name") |
+| `hideRowNumbers` | boolean | Hide the row number column |
+| `showResultsTotal` | boolean | Show total count of results |
+| `showSubtotals` | boolean | Show subtotal rows for grouped data |
+| `metricsAsRows` | boolean | Display metrics as rows instead of columns (pivoted view) |
 
 ### Column Configuration
 
-The `columns` object allows per-column customization using the field ID as the key.
+The `columns` object allows per-column customization using the field ID as the key:
 
-```yaml
-columns:
-  <fieldId>:
-    visible: true
-    name: "Custom Name"
-    frozen: false
-    displayStyle: "text"
-    color: "#4A90E2"
-```
+| Property | Type | Description |
+|----------|------|-------------|
+| `visible` | boolean | Whether the column is visible |
+| `name` | string | Custom display name for the column |
+| `frozen` | boolean | Freeze column to left side when scrolling |
+| `displayStyle` | `"text"` \| `"bar"` | How to display cell values |
+| `color` | string (hex) | Color for bar display style |
 
-#### `visible`
-- **Type**: `boolean`
-- **Description**: Whether the column is visible in the table
-- **Example**:
-  ```yaml
-  columns:
-    old_field:
-      visible: false
-  ```
-
-#### `name`
-- **Type**: `string`
-- **Description**: Custom display name for the column (overrides default field name)
-- **Example**:
-  ```yaml
-  columns:
-    user_first_name:
-      name: "First Name"
-  ```
-
-#### `frozen`
-- **Type**: `boolean`
-- **Description**: Freeze the column so it sticks to the left side when scrolling horizontally
-- **Example**:
-  ```yaml
-  columns:
-    customer_id:
-      frozen: true
-  ```
-
-#### `displayStyle`
-- **Type**: `string`
-- **Enum**: `"text"` | `"bar"`
-- **Description**: How to display the cell value
-  - `"text"`: Standard text display
-  - `"bar"`: Horizontal bar chart visualization
-- **Example**:
-  ```yaml
-  columns:
-    revenue:
-      displayStyle: "bar"
-      color: "#10B981"
-  ```
-
-#### `color`
-- **Type**: `string` (hex color code)
-- **Description**: Color for bar display style
-- **Required when**: `displayStyle: "bar"`
-- **Example**:
-  ```yaml
-  columns:
-    sales:
-      displayStyle: "bar"
-      color: "#3B82F6"
-  ```
-
-## Conditional Formatting
-
-Conditional formatting allows you to highlight cells based on their values using colors, gradients, and comparison rules.
-
-### Basic Structure
+### Conditional Formatting
 
-```yaml
-conditionalFormattings:
-  - target:
-      fieldId: "field_to_format"
-    color: "#FF0000"  # or { start: "#FFFFFF", end: "#FF0000" }
-    rules: []  # for single-color rules
-    rule: {}   # for gradient range rules
-    applyTo: "cell"  # or "text"
-```
+Conditional formatting highlights cells based on their values. Each rule consists of:
 
-### Conditional Formatting Properties
-
-#### `target`
-- **Type**: `object`
-- **Description**: Target field for the formatting rule
-- **Properties**:
-  - `fieldId` (string): Field ID to apply formatting to
-- **Example**:
-  ```yaml
-  target:
-    fieldId: "revenue"
-  ```
-
-#### `color`
-- **Type**: `string` | `object`
-- **Description**: Color for formatting
-  - **Single color** (string): Hex color code (e.g., `"#FF0000"`)
-  - **Gradient** (object): Start and end colors for range-based formatting
-- **Example (single color)**:
-  ```yaml
-  color: "#EF4444"
-  ```
-- **Example (gradient)**:
-  ```yaml
-  color:
-    start: "#FFFFFF"
-    end: "#10B981"
-  ```
-
-#### `rules`
-- **Type**: `array`
-- **Description**: Array of conditional formatting rules for single-color formatting
-- **Items**: See [Conditional Formatting Rules](#conditional-formatting-rules)
-- **Example**:
-  ```yaml
-  rules:
-    - id: "high-value"
-      operator: "greaterThan"
-      values: [1000]
-  ```
-
-#### `rule`
-- **Type**: `object`
-- **Description**: Rule for color range formatting (used with gradient colors)
-- **Properties**:
-  - `min`: Minimum value (number or `"auto"`)
-  - `max`: Maximum value (number or `"auto"`)
-- **Example**:
-  ```yaml
-  rule:
-    min: 0
-    max: 1000
-  ```
-  ```yaml
-  rule:
-    min: "auto"
-    max: "auto"
-  ```
-
-#### `applyTo`
-- **Type**: `string`
-- **Enum**: `"cell"` | `"text"`
-- **Description**: Where to apply the formatting
-  - `"cell"`: Apply color to cell background
-  - `"text"`: Apply color to text
-- **Example**:
-  ```yaml
-  applyTo: "cell"
-  ```
-
-### Conditional Formatting Rules
-
-Each rule in the `rules` array defines a condition for applying formatting.
+| Property | Type | Description |
+|----------|------|-------------|
+| `target.fieldId` | string | Field to apply formatting to |
+| `color` | string or `{start, end}` | Single color or gradient |
+| `rules` | array | Conditions for single-color formatting |
+| `rule` | `{min, max}` | Range for gradient formatting (values or `"auto"`) |
+| `applyTo` | `"cell"` \| `"text"` | Apply to background or text |
 
-```yaml
-- id: "unique-rule-id"
-  operator: "greaterThan"
-  values: [100]
-  compareTarget: null  # or { fieldId: "other_field" }
-```
+### Conditional Formatting Operators
 
-#### `id`
-- **Type**: `string`
-- **Description**: Unique identifier for the rule
-- **Example**:
-  ```yaml
-  id: "rule-1"
-  ```
-
-#### `operator`
-- **Type**: `string`
-- **Description**: Comparison operator
-- **Enum values**:
-  - **Null checks**: `"isNull"`, `"notNull"`
-  - **Equality**: `"equals"`, `"notEquals"`
-  - **String operations**: `"startsWith"`, `"endsWith"`, `"include"`, `"doesNotInclude"`
-  - **Numeric comparisons**: `"lessThan"`, `"lessThanOrEqual"`, `"greaterThan"`, `"greaterThanOrEqual"`
-  - **Date operations**: `"inThePast"`, `"notInThePast"`, `"inTheNext"`, `"inTheCurrent"`, `"notInTheCurrent"`
-  - **Range operations**: `"inBetween"`, `"notInBetween"`
-
-#### `values`
-- **Type**: `array`
-- **Description**: Values to compare against
-- **Example**:
-  ```yaml
-  values: [100, 500]  # for inBetween operator
-  ```
-  ```yaml
-  values: ["urgent"]  # for string comparison
-  ```
-
-#### `compareTarget`
-- **Type**: `object` | `null`
-- **Description**: Target field to compare against (for field-to-field comparisons)
-- **Properties**:
-  - `fieldId` (string): Field ID to compare against
-- **Example**:
-  ```yaml
-  compareTarget:
-    fieldId: "budget"
-  ```
-
-## Practical Examples
-
-### Basic Table
-
-Simple table with all default settings:
+- **Null checks**: `isNull`, `notNull`
+- **Equality**: `equals`, `notEquals`
+- **String**: `startsWith`, `endsWith`, `include`, `doesNotInclude`
+- **Numeric**: `lessThan`, `lessThanOrEqual`, `greaterThan`, `greaterThanOrEqual`
+- **Range**: `inBetween`, `notInBetween`
+- **Date**: `inThePast`, `notInThePast`, `inTheNext`, `inTheCurrent`, `notInTheCurrent`
+
+## Example: Full-Featured Table
+
+This example demonstrates frozen columns, bar visualization, and conditional formatting:
 
 ```yaml
 version: 1
-name: "Sales Overview"
-slug: "sales-overview"
+name: "Sales Performance"
+slug: "sales-performance"
 spaceSlug: "sales"
 tableName: "orders"
 updatedAt: "2024-01-30T12:00:00Z"
 
 metricQuery:
   dimensions:
-    - orders_customer_name
-    - orders_order_date
+    - orders_region
+    - orders_sales_rep
   metrics:
     - orders_total_revenue
     - orders_order_count
@@ -361,100 +107,24 @@ chartConfig:
   config:
     showColumnCalculation: true
     hideRowNumbers: false
-```
-
-### Frozen Columns
-
-Keep key columns visible while scrolling:
+    showResultsTotal: true
 
-```yaml
-chartConfig:
-  type: "table"
-  config:
     columns:
-      orders_customer_name:
+      orders_region:
         frozen: true
-        name: "Customer"
-      orders_customer_id:
+        name: "Region"
+      orders_sales_rep:
         frozen: true
-        name: "ID"
-      orders_total_revenue:
-        name: "Revenue"
-```
-
-### Bar Visualization in Cells
-
-Display metrics as horizontal bars:
-
-```yaml
-chartConfig:
-  type: "table"
-  config:
-    columns:
+        name: "Sales Rep"
       orders_total_revenue:
-        name: "Revenue"
+        name: "Total Revenue"
         displayStyle: "bar"
         color: "#10B981"
       orders_order_count:
-        name: "Orders"
-        displayStyle: "bar"
-        color: "#3B82F6"
-      orders_avg_order_value:
-        name: "Avg Order"
-        displayStyle: "bar"
-        color: "#8B5CF6"
-```
-
-### Conditional Formatting with Rules
-
-Highlight cells based on conditions:
-
-```yaml
-chartConfig:
-  type: "table"
-  config:
-    conditionalFormattings:
-      # Highlight high revenue in green
-      - target:
-          fieldId: "orders_total_revenue"
-        color: "#10B981"
-        rules:
-          - id: "high-revenue"
-            operator: "greaterThanOrEqual"
-            values: [10000]
-        applyTo: "cell"
-
-      # Highlight low order count in red
-      - target:
-          fieldId: "orders_order_count"
-        color: "#EF4444"
-        rules:
-          - id: "low-orders"
-            operator: "lessThan"
-            values: [5]
-        applyTo: "cell"
-
-      # Highlight status text
-      - target:
-          fieldId: "orders_status"
-        color: "#F59E0B"
-        rules:
-          - id: "pending-status"
-            operator: "equals"
-            values: ["pending"]
-        applyTo: "text"
-```
-
-### Color Gradients
-
-Create smooth color transitions based on value ranges:
+        name: "# Orders"
 
-```yaml
-chartConfig:
-  type: "table"
-  config:
     conditionalFormattings:
-      # Auto-range gradient (white to green)
+      # Gradient based on revenue
       - target:
           fieldId: "orders_total_revenue"
         color:
@@ -465,75 +135,32 @@ chartConfig:
           max: "auto"
         applyTo: "cell"
 
-      # Fixed range gradient (red to yellow to green)
+      # Highlight low order counts in red
       - target:
-          fieldId: "orders_profit_margin"
-        color:
-          start: "#EF4444"
-          end: "#10B981"
-        rule:
-          min: 0
-          max: 100
-        applyTo: "cell"
-```
-
-### Multiple Conditional Formatting Rules
-
-Apply different colors for different conditions:
-
-```yaml
-chartConfig:
-  type: "table"
-  config:
-    conditionalFormattings:
-      # Revenue tiers
-      - target:
-          fieldId: "orders_total_revenue"
-        color: "#10B981"
-        rules:
-          - id: "excellent"
-            operator: "greaterThanOrEqual"
-            values: [50000]
-        applyTo: "cell"
-
-      - target:
-          fieldId: "orders_total_revenue"
-        color: "#3B82F6"
-        rules:
-          - id: "good"
-            operator: "inBetween"
-            values: [20000, 50000]
-        applyTo: "cell"
-
-      - target:
-          fieldId: "orders_total_revenue"
-        color: "#F59E0B"
-        rules:
-          - id: "fair"
-            operator: "inBetween"
-            values: [10000, 20000]
-        applyTo: "cell"
-
-      - target:
-          fieldId: "orders_total_revenue"
+          fieldId: "orders_order_count"
         color: "#EF4444"
         rules:
-          - id: "poor"
+          - id: "low-volume"
             operator: "lessThan"
-            values: [10000]
+            values: [10]
         applyTo: "cell"
 ```
 
-### Field-to-Field Comparison
+## Example: Field-to-Field Comparison
 
-Compare values between fields:
+Compare values between fields to highlight over/under budget:
 
 ```yaml
 chartConfig:
   type: "table"
   config:
+    columns:
+      orders_actual_spend:
+        name: "Actual Spend"
+      orders_budget:
+        visible: false  # Hide but use for comparison
+
     conditionalFormattings:
-      # Highlight when actual exceeds budget
       - target:
           fieldId: "orders_actual_spend"
         color: "#EF4444"
@@ -544,164 +171,18 @@ chartConfig:
             compareTarget:
               fieldId: "orders_budget"
         applyTo: "cell"
-
-      # Highlight when actual is under budget
-      - target:
-          fieldId: "orders_actual_spend"
-        color: "#10B981"
-        rules:
-          - id: "under-budget"
-            operator: "lessThanOrEqual"
-            values: []
-            compareTarget:
-              fieldId: "orders_budget"
-        applyTo: "cell"
-```
-
-### Complex Example
-
-Combining multiple features:
-
-```yaml
-version: 1
-name: "Sales Performance Dashboard"
-slug: "sales-performance"
-spaceSlug: "sales/reports"
-tableName: "orders"
-updatedAt: "2024-01-30T12:00:00Z"
-
-metricQuery:
-  dimensions:
-    - orders_region
-    - orders_sales_rep
-  metrics:
-    - orders_total_revenue
-    - orders_order_count
-    - orders_avg_order_value
-    - orders_target_revenue
-
-chartConfig:
-  type: "table"
-  config:
-    # Display settings
-    showColumnCalculation: true
-    showRowCalculation: false
-    hideRowNumbers: false
-    showResultsTotal: true
-
-    # Column configuration
-    columns:
-      # Frozen identification columns
-      orders_region:
-        frozen: true
-        name: "Region"
-      orders_sales_rep:
-        frozen: true
-        name: "Sales Rep"
-
-      # Bar visualization for revenue
-      orders_total_revenue:
-        name: "Total Revenue"
-        displayStyle: "bar"
-        color: "#10B981"
-
-      # Standard display for count
-      orders_order_count:
-        name: "# Orders"
-
-      # Bar visualization for average
-      orders_avg_order_value:
-        name: "Avg Order Value"
-        displayStyle: "bar"
-        color: "#3B82F6"
-
-      # Hide target column but use it for comparison
-      orders_target_revenue:
-        visible: false
-
-    # Conditional formatting
-    conditionalFormattings:
-      # Revenue gradient
-      - target:
-          fieldId: "orders_total_revenue"
-        color:
-          start: "#FEF3C7"
-          end: "#10B981"
-        rule:
-          min: "auto"
-          max: "auto"
-        applyTo: "cell"
-
-      # Highlight if revenue exceeds target
-      - target:
-          fieldId: "orders_total_revenue"
-        color: "#DBEAFE"
-        rules:
-          - id: "exceeded-target"
-            operator: "greaterThanOrEqual"
-            values: []
-            compareTarget:
-              fieldId: "orders_target_revenue"
-        applyTo: "cell"
-
-      # Highlight low order counts
-      - target:
-          fieldId: "orders_order_count"
-        color: "#FEE2E2"
-        rules:
-          - id: "low-volume"
-            operator: "lessThan"
-            values: [10]
-        applyTo: "cell"
 ```
 
-## Operator Reference
-
-### Null Checks
-- `isNull`: Value is null/empty
-- `notNull`: Value is not null/empty
-
-### Equality
-- `equals`: Value equals the comparison value
-- `notEquals`: Value does not equal the comparison value
-
-### String Operations
-- `startsWith`: String starts with the comparison value
-- `endsWith`: String ends with the comparison value
-- `include`: String contains the comparison value
-- `doesNotInclude`: String does not contain the comparison value
-
-### Numeric Comparisons
-- `lessThan`: Value is less than comparison value
-- `lessThanOrEqual`: Value is less than or equal to comparison value
-- `greaterThan`: Value is greater than comparison value
-- `greaterThanOrEqual`: Value is greater than or equal to comparison value
-
-### Range Operations
-- `inBetween`: Value is between two comparison values (inclusive)
-- `notInBetween`: Value is not between two comparison values
-
-### Date Operations
-- `inThePast`: Date is in the past (relative to now)
-- `notInThePast`: Date is not in the past
-- `inTheNext`: Date is in the next N days/weeks/months
-- `inTheCurrent`: Date is in the current day/week/month/year
-- `notInTheCurrent`: Date is not in the current day/week/month/year
-
 ## Tips and Best Practices
 
-1. **Use frozen columns for identifiers**: Keep key columns like IDs, names, or dates frozen for easier data navigation.
+1. **Freeze identifier columns**: Keep key columns like IDs or names frozen for easier navigation when scrolling horizontally.
 
 2. **Combine bar visualization with conditional formatting**: Use bar display for quick visual comparison and conditional formatting to highlight outliers.
 
-3. **Use "auto" for gradient ranges**: When values can vary significantly, use `min: "auto"` and `max: "auto"` for gradient rules.
+3. **Use "auto" for gradient ranges**: When values vary significantly, use `min: "auto"` and `max: "auto"` for gradient rules.
 
-4. **Hide comparison columns**: When using field-to-field comparisons, consider hiding the target field with `visible: false`.
+4. **Hide comparison columns**: When using field-to-field comparisons, hide the target field with `visible: false`.
 
 5. **Apply formatting to cell vs text**: Use `applyTo: "cell"` for background highlights and `applyTo: "text"` for text color changes.
 
-6. **Layer formatting rules**: Apply multiple formatting rules to create sophisticated visualizations (e.g., gradient + threshold highlights).
-
-7. **Custom column names**: Use the `name` property to make column headers more user-friendly than raw field IDs.
-
-8. **Metrics as rows**: Use `metricsAsRows: true` for pivoted views when you have many metrics but few dimensions.
+6. **Custom column names**: Use the `name` property to make column headers more user-friendly than raw field IDs.
diff --git a/skills/developing-in-lightdash/resources/treemap-chart-reference.md b/skills/developing-in-lightdash/resources/treemap-chart-reference.md
@@ -2,6 +2,8 @@
 
 Treemap charts visualize hierarchical data using nested rectangles. Each rectangle's size represents a quantitative metric (like revenue or count), and the nesting shows hierarchical relationships (like category > subcategory > product).
 
+For full schema details, see [chart-as-code-1.0.json](schemas/chart-as-code-1.0.json) under `$defs/treemapChart`.
+
 ## When to Use Treemap Charts
 
 Treemap charts are ideal for:
@@ -34,63 +36,24 @@ chartConfig:
     sizeMetricId: size_metric
 ```
 
-## Configuration Options
-
-### Core Settings
+## Key Properties
 
 | Property | Type | Description | Required |
 |----------|------|-------------|----------|
 | `groupFieldIds` | array | Field IDs for hierarchical grouping (1-3 levels) | Yes |
 | `sizeMetricId` | string | Field ID that determines rectangle size | Yes |
 | `colorMetricId` | string | Field ID that determines rectangle color value | No |
 | `visibleMin` | number | Minimum size threshold for displaying nodes | No |
-| `leafDepth` | number | Depth level to display as leaf nodes | No |
-
-### Color Configuration
-
-| Property | Type | Description | Default |
-|----------|------|-------------|---------|
-| `startColor` | string | Start color for gradient (hex code) | System default |
-| `endColor` | string | End color for gradient (hex code) | System default |
-| `useDynamicColors` | boolean | Enable dynamic color scaling based on values | false |
-| `startColorThreshold` | number | Value threshold for start color | Auto |
-| `endColorThreshold` | number | Value threshold for end color | Auto |
+| `maxLeafDepth` | number | Depth level to display as leaf nodes | No |
+| `startColor` | string | Start color for gradient (hex code) | No |
+| `endColor` | string | End color for gradient (hex code) | No |
+| `useDynamicColors` | boolean | Enable dynamic color scaling based on values | No |
+| `startColorThreshold` | number | Value threshold for start color | No |
+| `endColorThreshold` | number | Value threshold for end color | No |
 
 ## Examples
 
-### Example 1: Basic Single-Level Treemap
-
-Visualize revenue by product category with a simple one-level hierarchy.
-
-```yaml
-version: 1
-name: "Revenue by Category"
-slug: revenue-by-category
-spaceSlug: sales
-tableName: products
-
-metricQuery:
-  exploreName: products
-  dimensions:
-    - products_category
-  metrics:
-    - products_total_revenue
-  sorts:
-    - fieldId: products_total_revenue
-      descending: true
-  limit: 20
-
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - products_category
-    sizeMetricId: products_total_revenue
-```
-
-**Use case**: Quick overview of which product categories generate the most revenue.
-
-### Example 2: Two-Level Hierarchical Treemap
+### Example 1: Two-Level Hierarchical Treemap
 
 Show category and subcategory revenue with nested rectangles.
 
@@ -125,44 +88,7 @@ chartConfig:
 
 **Use case**: Understand revenue composition at both category and subcategory levels. The `visibleMin` setting prevents tiny rectangles from cluttering the view.
 
-### Example 3: Three-Level Deep Hierarchy
-
-Display category > subcategory > product with maximum depth.
-
-```yaml
-version: 1
-name: "Product Hierarchy Revenue"
-slug: product-hierarchy-revenue
-spaceSlug: sales
-tableName: products
-
-metricQuery:
-  exploreName: products
-  dimensions:
-    - products_category
-    - products_subcategory
-    - products_product_name
-  metrics:
-    - products_total_revenue
-  sorts:
-    - fieldId: products_total_revenue
-      descending: true
-  limit: 100
-
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - products_category
-      - products_subcategory
-      - products_product_name
-    sizeMetricId: products_total_revenue
-    leafDepth: 2               # Show subcategory level as leaves
-```
-
-**Use case**: Drill down from high-level categories to individual products. Setting `leafDepth: 2` controls which level shows as final leaf nodes.
-
-### Example 4: Color Gradient Based on Metric
+### Example 2: Color Gradient Based on Second Metric
 
 Size by revenue, color by profit margin to show profitability.
 
@@ -198,176 +124,31 @@ chartConfig:
 
 **Use case**: Quickly identify large revenue categories (big rectangles) with poor margins (red color) that need attention.
 
-### Example 5: Dynamic Color Thresholds
-
-Use specific thresholds to highlight performance ranges.
-
-```yaml
-version: 1
-name: "Sales Performance by Region"
-slug: sales-performance-by-region
-spaceSlug: sales
-tableName: sales
-
-metricQuery:
-  exploreName: sales
-  dimensions:
-    - sales_region
-    - sales_territory
-  metrics:
-    - sales_total_revenue
-    - sales_quota_attainment
-  sorts:
-    - fieldId: sales_total_revenue
-      descending: true
-  limit: 40
-
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - sales_region
-      - sales_territory
-    sizeMetricId: sales_total_revenue
-    colorMetricId: sales_quota_attainment
-    useDynamicColors: true
-    startColor: "#fef3c7"      # Light yellow
-    endColor: "#166534"        # Dark green
-    startColorThreshold: 0     # 0% quota attainment
-    endColorThreshold: 150     # 150% quota attainment
-```
-
-**Use case**: See both revenue size and quota performance. Territories with large revenue (big rectangles) below quota (yellow/light color) need intervention.
-
-### Example 6: Customer Segmentation Treemap
-
-Visualize customer segments and their sub-segments by customer count.
-
-```yaml
-version: 1
-name: "Customer Segmentation"
-slug: customer-segmentation
-spaceSlug: marketing
-tableName: customers
-
-metricQuery:
-  exploreName: customers
-  dimensions:
-    - customers_segment
-    - customers_subsegment
-  metrics:
-    - customers_customer_count
-    - customers_lifetime_value
-  sorts:
-    - fieldId: customers_customer_count
-      descending: true
-  limit: 30
-
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - customers_segment
-      - customers_subsegment
-    sizeMetricId: customers_customer_count
-    colorMetricId: customers_lifetime_value
-    startColor: "#dbeafe"      # Light blue
-    endColor: "#1e3a8a"        # Dark blue
-    visibleMin: 5              # Hide segments with fewer than 5 customers
-```
-
-**Use case**: Understand customer distribution (count) while identifying high-value segments (color intensity).
-
 ## Best Practices
 
 ### Hierarchy Design
 
 1. **Limit depth to 2-3 levels**: More levels become unreadable
 2. **Order groups logically**: Most important or largest first
 3. **Use meaningful groupings**: Natural hierarchies (Geography > State > City)
-4. **Ensure complete hierarchy**: All levels should have parent-child relationships
 
 ### Size Metric Selection
 
 1. **Choose additive metrics**: Sum, count (not averages or ratios)
 2. **Use positive values**: Negative values don't render well
-3. **Consider data range**: Very small or very large ranges can be hard to compare
-4. **Add `visibleMin`**: Hide tiny rectangles that clutter the view
+3. **Add `visibleMin`**: Hide tiny rectangles that clutter the view
 
 ### Color Strategy
 
 1. **Single color for simple hierarchy**: Let size tell the story
 2. **Gradient for performance metrics**: Red-to-green for good/bad ranges
-3. **Sequential for magnitude**: Light-to-dark for low-to-high values
-4. **Diverging for comparison**: Two colors meeting at a midpoint (target, average)
-5. **Set explicit thresholds**: `startColorThreshold` and `endColorThreshold` for clear ranges
+3. **Set explicit thresholds**: `startColorThreshold` and `endColorThreshold` for clear ranges
 
 ### Data Preparation
 
 1. **Limit total rectangles**: 20-100 for readability (use `limit` in metricQuery)
 2. **Sort by size metric**: Largest first for visual hierarchy
 3. **Filter outliers**: Very small or large values can distort visualization
-4. **Use consistent granularity**: All leaf nodes at same hierarchy level
-
-### Labeling
-
-1. **Top levels show labels**: Category names appear in larger rectangles
-2. **Small rectangles omit labels**: Below `visibleMin` threshold
-3. **Tooltips show details**: Hover for exact values
-4. **Keep names concise**: Long names get truncated
-
-## Common Patterns
-
-### Portfolio Analysis
-
-Size by assets under management, color by performance:
-
-```yaml
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - portfolio_asset_class
-      - portfolio_fund
-    sizeMetricId: portfolio_aum
-    colorMetricId: portfolio_ytd_return
-    startColor: "#dc2626"
-    endColor: "#16a34a"
-```
-
-### Inventory Management
-
-Size by stock quantity, color by days of supply:
-
-```yaml
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - inventory_warehouse
-      - inventory_product_category
-    sizeMetricId: inventory_units_on_hand
-    colorMetricId: inventory_days_of_supply
-    startColor: "#22c55e"      # Green = healthy stock
-    endColor: "#ef4444"        # Red = low stock
-```
-
-### Website Analytics
-
-Size by page views, color by bounce rate:
-
-```yaml
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - pages_section
-      - pages_page_name
-    sizeMetricId: pages_page_views
-    colorMetricId: pages_bounce_rate
-    startColor: "#10b981"      # Low bounce = good
-    endColor: "#f59e0b"        # High bounce = needs attention
-```
 
 ## Troubleshooting
 
@@ -378,16 +159,14 @@ chartConfig:
 - Increase `visibleMin` to hide small values
 - Reduce `limit` in metricQuery
 - Add filters to exclude low-value categories
-- Aggregate small categories into "Other"
 
 ### Hierarchy Not Displaying
 
 **Problem**: Only showing flat categories, not nested
 **Solutions**:
 - Verify `groupFieldIds` array has multiple fields
 - Check that dimensions are in metricQuery
-- Ensure parent-child relationships exist in data
-- Confirm `leafDepth` setting if specified
+- Confirm `maxLeafDepth` setting if specified
 
 ### Colors Not Showing
 
@@ -396,16 +175,6 @@ chartConfig:
 - Verify `colorMetricId` is in metricQuery metrics
 - Check that color metric has varying values
 - Set explicit `startColor` and `endColor`
-- Confirm thresholds align with actual data range
-
-### Rectangles Too Large/Small
-
-**Problem**: Size proportions seem off
-**Solutions**:
-- Check for outliers in size metric
-- Use filters to remove extreme values
-- Verify `sizeMetricId` uses appropriate aggregation
-- Consider log scale for wide value ranges (requires custom config)
 
 ## Comparison: Treemap vs Other Charts
 
@@ -418,39 +187,6 @@ chartConfig:
 | Dual metrics | Yes | Bubble chart (for 2 metrics + category) |
 | Trends over time | No | Line/Area chart |
 
-## Advanced: Dynamic Color Ranges
-
-For metrics where you want precise control over color mapping:
-
-```yaml
-chartConfig:
-  type: treemap
-  config:
-    groupFieldIds:
-      - products_category
-    sizeMetricId: products_sales
-    colorMetricId: products_growth_rate
-    useDynamicColors: true
-    startColor: "#dc2626"      # Red for negative growth
-    endColor: "#16a34a"        # Green for high growth
-    startColorThreshold: -10   # -10% growth
-    endColorThreshold: 20      # +20% growth
-```
-
-**How thresholds work:**
-- Values below `startColorThreshold` get `startColor`
-- Values above `endColorThreshold` get `endColor`
-- Values between interpolate along the gradient
-- Without `useDynamicColors`, colors map to min/max in dataset
-
-## Performance Considerations
-
-1. **Limit data points**: 100-200 rectangles maximum for performance
-2. **Use aggregated data**: Pre-aggregate at appropriate level
-3. **Set appropriate `limit`**: Query only what can be displayed
-4. **Avoid deep hierarchies**: 3+ levels slow rendering
-5. **Cache results**: Treemaps on dashboards with refresh schedules
-
 ## Related Documentation
 
 - [Chart Types Reference](./chart-types-reference.md) - Overview of all chart types
PATCH

echo "Gold patch applied."
