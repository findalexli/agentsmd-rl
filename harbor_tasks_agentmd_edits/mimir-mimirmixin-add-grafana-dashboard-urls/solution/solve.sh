#!/usr/bin/env bash
set -euo pipefail

cd /workspace/mimir

# Idempotent: skip if already applied
if grep -q 'externalDashboardURL' operations/mimir-mixin/alerts/alerts-utils.libsonnet 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/CHANGELOG.md b/CHANGELOG.md
index d26c7529295..219fe3e9e97 100644
--- a/CHANGELOG.md
+++ b/CHANGELOG.md
@@ -230,6 +230,7 @@
 * [ENHANCEMENT] Dashboards: Add panels showing the distribution of estimated query memory consumption and rate of fallback to Prometheus' query engine in query-frontends to the Queries dashboard. #14029
 * [ENHANCEMENT] Dashboards: Add "Forced TSDB head compactions in progress" panel to "Mimir / Writes" dashboard. #14248
 * [ENHANCEMENT] Dashboards: Improve "Last successful run per-compactor replica" table in the compactor dashboard to show time since process start for compactors that haven't completed their first run yet. #14285
+* [ENHANCEMENT] Alerts: Add dashboard_url annotations to Prometheus alerts. #14458
 * [BUGFIX] Dashboards: Fix issue where throughput dashboard panels would group all gRPC requests that resulted in a status containing an underscore into one series with no name. #13184
 * [BUGFIX] Dashboards: Filter out 0s from `max_series` limit on Writes Resources > Ingester > In-memory series panel. #13419
 * [BUGFIX] Dashboards: Fix issue where the "Tenant gateway requests" panels on Tenants dashboard would show data from all components. #13940
diff --git a/docs/internal/contributing/README.md b/docs/internal/contributing/README.md
index 1a2105bfdcf..aa3bb8a9561 100644
--- a/docs/internal/contributing/README.md
+++ b/docs/internal/contributing/README.md
@@ -27,12 +27,40 @@ Please see the dedicated "[Contributing to Grafana Mimir helm chart](contributin

 ## Formatting

-Grafana Mimir uses `goimports` tool (`go get golang.org/x/tools/cmd/goimports` to install) to format the Go files, and sort imports. We use goimports with `-local github.com/grafana/mimir` parameter, to put Grafana Mimir internal imports into a separate group. We try to keep imports sorted into three groups: imports from standard library, imports of 3rd party packages and internal Grafana Mimir imports. Goimports will fix the order, but will keep existing newlines between imports in the groups. We try to avoid extra newlines like that.
+### Go
+
+Grafana Mimir uses `goimports` tool (`go get golang.org/x/tools/cmd/goimports` to install) to format the Go files, and sort imports.
+We use goimports with `-local github.com/grafana/mimir` parameter, to put Grafana Mimir internal imports into a separate group.
+
+We try to keep imports sorted into three groups:
+
+- imports from standard library
+- imports of 3rd party packages and
+- internal Grafana Mimir imports.
+
+Goimports will fix the order, but will keep existing newlines between imports in the groups. We try to avoid extra newlines like that.

 You're using an IDE you may find useful the following settings for the Grafana Mimir project:

 - [VSCode](vscode-goimports-settings.json)

+**Always run `make format` before creating commits**, or configure your IDE to run goimports on save. This prevents formatting-only commits and keeps the git history clean.
+
+### Jsonnet
+
+When making changes to jsonnet/libsonnet files, always format before creating commits:
+
+- **Mixin files** (`operations/mimir-mixin/`): Run `make format-mixin` then `make build-mixin` to render compiled YAML outputs
+- **Other jsonnet files** (`operations/mimir`, `operations/mimir-tests`, `development/`): Run `make format-jsonnet-manifests`
+
+This prevents formatting-only commits and ensures your jsonnet changes compile correctly.
+
+### Other formatters
+
+- **Makefiles**: Run `make format-makefiles` for any Makefile changes
+- **Protobuf files**: Run `make format-protobuf` for `.proto` file changes
+- **PromQL test files**: Run `make format-promql-tests` for PromQL test changes
+
 ## Building Grafana Mimir

 To build:
diff --git a/docs/sources/mimir/manage/mimir-runbooks/_index.md b/docs/sources/mimir/manage/mimir-runbooks/_index.md
index 1ed8b9627b4..74eab13f35e 100644
--- a/docs/sources/mimir/manage/mimir-runbooks/_index.md
+++ b/docs/sources/mimir/manage/mimir-runbooks/_index.md
@@ -899,7 +899,7 @@ This alert fires if queries are piling up in the query-scheduler.

 #### Dashboard Panels

-The size of the queue is shown on the `Queue Length` dashboard panel on the [`Mimir / Reads`](https://admin-ops-eu-south-0.grafana-ops.net/grafana/d/e327503188913dc38ad571c647eef643) (for the standard query path) or `Mimir / Remote Ruler Reads`
+The size of the queue is shown on the `Queue Length` dashboard panel on the `Mimir / Reads` (for the standard query path) or `Mimir / Remote Ruler Reads`
 (for the dedicated rule evaluation query path) dashboards.

 The `Queue Length` dashboard panel on the `Mimir / Reads` (for the standard query path)
diff --git a/operations/mimir-mixin/alerts/alertmanager.libsonnet b/operations/mimir-mixin/alerts/alertmanager.libsonnet
index 21d9bc4989a..5825f9e25a2 100644
--- a/operations/mimir-mixin/alerts/alertmanager.libsonnet
+++ b/operations/mimir-mixin/alerts/alertmanager.libsonnet
@@ -103,7 +103,7 @@
             message: |||
               Alertmanager %(alert_instance_variable)s in %(alert_aggregation_variables)s is using too much memory.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-scaling.json'),
         },
         {
           alert: $.alertName('AlertmanagerAllocatingTooMuchMemory'),
@@ -116,7 +116,7 @@
             message: |||
               Alertmanager %(alert_instance_variable)s in %(alert_aggregation_variables)s is using too much memory.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-scaling.json'),
         },
         {
           alert: $.alertName('AlertmanagerInstanceHasNoTenants'),
@@ -143,5 +143,12 @@
     },
   ],

-  groups+: $.withRunbookURL('https://grafana.com/docs/mimir/latest/operators-guide/mimir-runbooks/#%s', $.withExtraLabelsAnnotations(alertGroups)),
+  groups+:
+    $.withRunbookURL(
+      'https://grafana.com/docs/mimir/latest/operators-guide/mimir-runbooks/#%s',
+      $.withDashboardURL(
+        'mimir-alertmanager.json',
+        $.withExtraLabelsAnnotations(alertGroups)
+      )
+    ),
 }
diff --git a/operations/mimir-mixin/alerts/alerts-utils.libsonnet b/operations/mimir-mixin/alerts/alerts-utils.libsonnet
index 30698b57759..0216f5f0c36 100644
--- a/operations/mimir-mixin/alerts/alerts-utils.libsonnet
+++ b/operations/mimir-mixin/alerts/alerts-utils.libsonnet
@@ -60,4 +60,60 @@
     (if histogram_type == 'native' && nhcb then {
        buckets: 'custom',
      } else {}),
+
+  // Returns the absolute URL of a dashboard for use in alert annotations.
+  // Includes query parameters to preserve time range and map alert labels to dashboard variables.
+  // The Dashboard UID is dynamically computed from the filename (same as dashboard definitions).
+  // Returns null if externalGrafanaURLPrefix is empty (disables dashboard links).
+  // Usage: externalDashboardURL('mimir-writes.json')
+  externalDashboardURL(filename)::
+    if $._config.externalGrafanaURLPrefix != '' then
+      local base_url = '%s/d/%s/%s' % [
+        $._config.externalGrafanaURLPrefix,
+        std.md5(filename),
+        std.strReplace(filename, '.json', ''),
+      ];
+      // Generate var-<label>={{ $labels.<label> }} for each cluster label
+      local var_params = std.join(
+        '&',
+        std.map(
+          function(label) 'var-%s={{ $labels.%s }}' % [label, label],
+          $._config.cluster_labels
+        )
+      );
+      '%s?%s' % [base_url, var_params]
+    else
+      null,
+
+  // Returns an object with dashboard_url field if externalGrafanaURLPrefix is configured, empty object otherwise.
+  // Use this to conditionally add dashboard_url to alert annotations.
+  // Usage: annotations: { message: '...' } + $.dashboardURLAnnotation('mimir-writes.json')
+  dashboardURLAnnotation(filename)::
+    local url = $.externalDashboardURL(filename);
+    if url != null then { dashboard_url: url } else {},
+
+  // Adds a single dashboard URL to all alerts in the groups that don't already have one.
+  // This is useful for component-specific alert files where all alerts should link to the same dashboard.
+  // Skips adding dashboard_url if externalGrafanaURLPrefix is empty.
+  // Usage: withDashboardURL('mimir-alertmanager.json', alertGroups)
+  withDashboardURL(dashboard_filename, groups)::
+    local dashboard_url = $.externalDashboardURL(dashboard_filename);
+    local update_rule(rule) =
+      if std.objectHas(rule, 'alert') && !std.objectHas(rule.annotations, 'dashboard_url') && dashboard_url != null
+      then rule {
+        annotations+: {
+          dashboard_url: dashboard_url,
+        },
+      }
+      else rule;
+
+    [
+      group {
+        rules: [
+          update_rule(rule)
+          for rule in group.rules
+        ],
+      }
+      for group in groups
+    ],
 }
diff --git a/operations/mimir-mixin/alerts/alerts.libsonnet b/operations/mimir-mixin/alerts/alerts.libsonnet
index a5f0a49be19..4f031784a14 100644
--- a/operations/mimir-mixin/alerts/alerts.libsonnet
+++ b/operations/mimir-mixin/alerts/alerts.libsonnet
@@ -67,10 +67,15 @@ local utils = import 'mixin-utils/utils.libsonnet';
     'for': '15m',
     labels: $.histogramLabels({ severity: 'critical' }, histogram_type, nhcb=false),
     annotations: {
-      message: |||
-        The route {{ $labels.route }} in %(alert_aggregation_variables)s is experiencing {{ printf "%%.2f" $value }}%% errors.
-      ||| % $._config,
-    },
+                   message: |||
+                     The route {{ $labels.route }} in %(alert_aggregation_variables)s is experiencing {{ printf "%%.2f" $value }}%% errors.
+                   ||| % $._config,
+                 }
+                 // Alternative dashboards for investigation:
+                 //   - Mimir / Reads (mimir-reads.json) - for read path errors
+                 //   - Mimir / Alertmanager (mimir-alertmanager.json) - for alertmanager errors
+                 //   - Mimir / Alertmanager Resources (mimir-alertmanager-resources.json) - for resource starvation
+                 + $.dashboardURLAnnotation('mimir-writes.json'),
   },

   local rulerRemoteEvaluationFailingAlert(histogram_type) = {
@@ -85,10 +90,13 @@ local utils = import 'mixin-utils/utils.libsonnet';
     'for': '5m',
     labels: $.histogramLabels({ severity: 'warning' }, histogram_type, nhcb=false),
     annotations: {
-      message: |||
-        %(product)s rulers in %(alert_aggregation_variables)s are failing to perform {{ printf "%%.2f" $value }}%% of remote evaluations through the ruler-query-frontend.
-      ||| % $._config,
-    },
+                   message: |||
+                     %(product)s rulers in %(alert_aggregation_variables)s are failing to perform {{ printf "%%.2f" $value }}%% of remote evaluations through the ruler-query-frontend.
+                   ||| % $._config,
+                 }
+                 // Alternative dashboards for investigation:
+                 //   - Mimir / Remote ruler reads resources (mimir-remote-ruler-reads-resources.json)
+                 + $.dashboardURLAnnotation('mimir-remote-ruler-reads.json'),
   },

   local kvStoreFailure(histogram_type) = {
@@ -157,10 +165,17 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'warning',
           },
           annotations: {
-            message: |||
-              {{ $labels.%(per_job_label)s }} {{ $labels.route }} is experiencing {{ printf "%%.2f" $value }}s 99th percentile latency.
-            ||| % $._config,
-          },
+                         message: |||
+                           {{ $labels.%(per_job_label)s }} {{ $labels.route }} is experiencing {{ printf "%%.2f" $value }}s 99th percentile latency.
+                         ||| % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Scaling (mimir-scaling.json) - for scaling decisions
+                       //   - Mimir / Reads (mimir-reads.json) - for read path latency
+                       //   - Mimir / Slow Queries (mimir-slow-queries.json) - to identify slow queries
+                       //   - Mimir / Queries (mimir-queries.json) - for queue length analysis
+                       //   - Mimir / Alertmanager (mimir-alertmanager.json) - for alertmanager path
+                       + $.dashboardURLAnnotation('mimir-writes.json'),
         },
         {
           alert: $.alertName('InconsistentRuntimeConfig'),
@@ -208,10 +223,15 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'critical',
           },
           annotations: {
-            message: |||
-              There are {{ $value }} queued up queries in %(alert_aggregation_variables)s {{ $labels.%(per_job_label)s }}.
-            ||| % $._config,
-          },
+                         message: |||
+                           There are {{ $value }} queued up queries in %(alert_aggregation_variables)s {{ $labels.%(per_job_label)s }}.
+                         ||| % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Remote ruler reads (mimir-remote-ruler-reads.json)
+                       //   - Mimir / Reads Resources (mimir-reads-resources.json)
+                       //   - Mimir / Slow Queries (mimir-slow-queries.json)
+                       + $.dashboardURLAnnotation('mimir-reads.json'),
         },
         {
           alert: $.alertName('CacheRequestErrors'),
@@ -381,8 +401,13 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'warning',
           },
           annotations: {
-            message: '%(product)s store-gateway in %(alert_aggregation_variables)s is experiencing {{ $value | humanizePercentage }} errors while doing {{ $labels.operation }} on the object storage.' % $._config,
-          },
+                         message: '%(product)s store-gateway in %(alert_aggregation_variables)s is experiencing {{ $value | humanizePercentage }} errors while doing {{ $labels.operation }} on the object storage.' % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Compactor (mimir-compactor.json)
+                       //   - Mimir / Reads Resources (mimir-reads-resources.json)
+                       //   - Mimir / Tenants (mimir-tenants.json)
+                       + $.dashboardURLAnnotation('mimir-object-store.json'),
         },
         {
           // Alert if servers are receiving requests with invalid cluster validation labels (i.e. meant for other clusters).
@@ -578,7 +603,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
             message: |||
               Ingester {{ $labels.%(per_job_label)s }}/%(alert_instance_variable)s has reached {{ $value | humanizePercentage }} of its series limit.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
         {
           alert: $.alertName('IngesterReachingSeriesLimit'),
@@ -597,7 +622,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
             message: |||
               Ingester {{ $labels.%(per_job_label)s }}/%(alert_instance_variable)s has reached {{ $value | humanizePercentage }} of its series limit.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
         {
           alert: $.alertName('IngesterReachingTenantsLimit'),
@@ -616,7 +641,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
             message: |||
               Ingester {{ $labels.%(per_job_label)s }}/%(alert_instance_variable)s has reached {{ $value | humanizePercentage }} of its tenant limit.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
         {
           alert: $.alertName('IngesterReachingTenantsLimit'),
@@ -635,7 +660,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
             message: |||
               Ingester {{ $labels.%(per_job_label)s }}/%(alert_instance_variable)s has reached {{ $value | humanizePercentage }} of its tenant limit.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
         {
           alert: $.alertName('ReachingTCPConnectionsLimit'),
@@ -651,7 +676,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
             message: |||
               %(product)s instance {{ $labels.%(per_job_label)s }}/%(alert_instance_variable)s has reached {{ $value | humanizePercentage }} of its TCP connections limit for {{ $labels.protocol }} protocol.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-writes.json'),
         },
         {
           alert: $.alertName('DistributorInflightRequestsHigh'),
@@ -670,7 +695,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
             message: |||
               Distributor {{ $labels.%(per_job_label)s }}/%(alert_instance_variable)s has reached {{ $value | humanizePercentage }} of its inflight push request limit.
             ||| % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
       ],
     },
@@ -792,10 +817,13 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'warning',
           },
           annotations: {
-            message: |||
-              Instance %(alert_instance_variable)s in %(alert_aggregation_variables)s is using too much memory.
-            ||| % $._config,
-          },
+                         message: |||
+                           Instance %(alert_instance_variable)s in %(alert_aggregation_variables)s is using too much memory.
+                         ||| % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Scaling (mimir-scaling.json) - for scaling recommendations
+                       + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
         {
           alert: $.alertName('AllocatingTooMuchMemory'),
@@ -808,10 +836,13 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'critical',
           },
           annotations: {
-            message: |||
-              Instance %(alert_instance_variable)s in %(alert_aggregation_variables)s is using too much memory.
-            ||| % $._config,
-          },
+                         message: |||
+                           Instance %(alert_instance_variable)s in %(alert_aggregation_variables)s is using too much memory.
+                         ||| % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Scaling (mimir-scaling.json) - for scaling recommendations
+                       + $.dashboardURLAnnotation('mimir-writes-resources.json'),
         },
       ],
     },
@@ -857,10 +888,13 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'critical',
           },
           annotations: {
-            message: |||
-              %(product)s Ruler %(alert_instance_variable)s in %(alert_aggregation_variables)s is experiencing {{ printf "%%.2f" $value }}%% errors while evaluating rules.
-            ||| % $._config,
-          },
+                         message: |||
+                           %(product)s Ruler %(alert_instance_variable)s in %(alert_aggregation_variables)s is experiencing {{ printf "%%.2f" $value }}%% errors while evaluating rules.
+                         ||| % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Remote ruler reads resources (mimir-remote-ruler-reads-resources.json)
+                       + $.dashboardURLAnnotation('mimir-remote-ruler-reads.json'),
         },
         {
           alert: $.alertName('RulerMissedEvaluations'),
diff --git a/operations/mimir-mixin/alerts/blocks.libsonnet b/operations/mimir-mixin/alerts/blocks.libsonnet
index 03736432262..d1a7a3c1e5d 100644
--- a/operations/mimir-mixin/alerts/blocks.libsonnet
+++ b/operations/mimir-mixin/alerts/blocks.libsonnet
@@ -265,8 +265,11 @@
             severity: 'warning',
           },
           annotations: {
-            message: '%(product)s store-gateway in %(alert_aggregation_variables)s is querying level 1 blocks, indicating the compactor may not be keeping up with compaction.' % $._config,
-          },
+                         message: '%(product)s store-gateway in %(alert_aggregation_variables)s is querying level 1 blocks, indicating the compactor may not be keeping up with compaction.' % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Queries (mimir-queries.json)
+                       + $.dashboardURLAnnotation('mimir-compactor.json'),
         },
       ],
     },
diff --git a/operations/mimir-mixin/alerts/compactor.libsonnet b/operations/mimir-mixin/alerts/compactor.libsonnet
index e2466891f63..4a3b8450da8 100644
--- a/operations/mimir-mixin/alerts/compactor.libsonnet
+++ b/operations/mimir-mixin/alerts/compactor.libsonnet
@@ -187,7 +187,7 @@
           },
           annotations: {
             message: '%(product)s Compactor %(alert_instance_variable)s in %(alert_aggregation_variables)s has been OOMKilled {{ printf "%%.2f" $value }} times in the last %(time_window)s.' % ($._config + settings),
-          },
+          } + $.dashboardURLAnnotation('mimir-compactor-resources.json'),
         }
         for settings in [
           { severity: 'warning', threshold: 2, time_window: '4h' },
@@ -197,5 +197,12 @@
     },
   ],

-  groups+: $.withRunbookURL('https://grafana.com/docs/mimir/latest/operators-guide/mimir-runbooks/#%s', $.withExtraLabelsAnnotations(alertGroups)),
+  groups+:
+    $.withRunbookURL(
+      'https://grafana.com/docs/mimir/latest/operators-guide/mimir-runbooks/#%s',
+      $.withDashboardURL(
+        'mimir-compactor.json',
+        $.withExtraLabelsAnnotations(alertGroups)
+      )
+    ),
 }
diff --git a/operations/mimir-mixin/alerts/ingest-storage.libsonnet b/operations/mimir-mixin/alerts/ingest-storage.libsonnet
index 97a33aab604..85ec0cbdd57 100644
--- a/operations/mimir-mixin/alerts/ingest-storage.libsonnet
+++ b/operations/mimir-mixin/alerts/ingest-storage.libsonnet
@@ -22,7 +22,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
     labels: $.histogramLabels({ severity: 'warning' }, histogram_type, nhcb=false),
     annotations: {
       message: '%(product)s {{ $labels.%(per_instance_label)s }} in %(alert_aggregation_variables)s in "starting" phase is not reducing consumption lag of write requests read from Kafka.' % $._config,
-    },
+    } + $.dashboardURLAnnotation('mimir-writes.json'),
   },

   local runningIngesterReceiveDelayTooHigh(histogram_type, threshold_value, for_duration, threshold_label) = {
@@ -201,7 +201,7 @@ local utils = import 'mixin-utils/utils.libsonnet';
           },
           annotations: {
             message: '%(product)s {{ $labels.%(per_instance_label)s }} in %(alert_aggregation_variables)s fails to enforce strong-consistency on read-path.' % $._config,
-          },
+          } + $.dashboardURLAnnotation('mimir-queries.json'),
         },

         // Alert firing if ingesters are receiving an unexpected high number of strongly consistent requests without an offset specified.
@@ -355,8 +355,11 @@ local utils = import 'mixin-utils/utils.libsonnet';
             severity: 'critical',
           },
           annotations: {
-            message: '%(product)s ingesters in %(alert_aggregation_variables)s have fewer ingesters consuming than active partitions.' % $._config,
-          },
+                         message: '%(product)s ingesters in %(alert_aggregation_variables)s have fewer ingesters consuming than active partitions.' % $._config,
+                       }
+                       // Alternative dashboards for investigation:
+                       //   - Mimir / Reads (mimir-reads.json)
+                       + $.dashboardURLAnnotation('mimir-writes.json'),
         },
       ],
     },
diff --git a/operations/mimir-mixin/config.libsonnet b/operations/mimir-mixin/config.libsonnet
index 0663b024ead..5a9e2587dd0 100644
--- a/operations/mimir-mixin/config.libsonnet
+++ b/operations/mimir-mixin/config.libsonnet
@@ -778,5 +778,10 @@

     // Show panels that use queries for "ingest storage" ingestion (distributor -> Kafka, Kafka -> ingesters)
     show_ingest_storage_panels: true,
+
+    // External Grafana URL prefix for dashboard links in alerts.
+    // This is used to generate absolute URLs in alert annotations that link to dashboards.
+    // Set to empty string '' to disable dashboard links in alerts.
+    externalGrafanaURLPrefix: '',
   },
 }

PATCH

echo "Patch applied successfully."
