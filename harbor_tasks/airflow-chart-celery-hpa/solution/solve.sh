#!/bin/bash
set -e

cd /workspace/airflow

# Check if already patched (idempotency check)
if grep -q "workers.celery.hpa.enabled" chart/values.yaml; then
    echo "Already patched, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/chart/newsfragments/64734.significant.rst b/chart/newsfragments/64734.significant.rst
new file mode 100644
index 0000000000000..52c2ebaee4382
--- /dev/null
+++ b/chart/newsfragments/64734.significant.rst
@@ -0,0 +1 @@
+``workers.hpa`` section is now deprecated in favor of ``workers.celery.hpa``. Please update your configuration accordingly.
diff --git a/chart/templates/NOTES.txt b/chart/templates/NOTES.txt
index e8236398227bc..44924918060b1 100644
--- a/chart/templates/NOTES.txt
+++ b/chart/templates/NOTES.txt
@@ -517,6 +517,46 @@ DEPRECATION WARNING:

 {{- end }}

+{{- if .Values.workers.hpa.enabled }}
+
+ DEPRECATION WARNING:
+    `workers.hpa.enabled` has been renamed to `workers.celery.hpa.enabled`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
+{{- if ne (int .Values.workers.hpa.minReplicaCount) 0 }}
+
+ DEPRECATION WARNING:
+    `workers.hpa.minReplicaCount` has been renamed to `workers.celery.hpa.minReplicaCount`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
+{{- if ne (int .Values.workers.hpa.maxReplicaCount) 5 }}
+
+ DEPRECATION WARNING:
+    `workers.hpa.maxReplicaCount` has been renamed to `workers.celery.hpa.maxReplicaCount`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
+{{- if ne (toJson .Values.workers.hpa.metrics | quote) (toJson "[{\"resource\":{\"name\":\"cpu\",\"target\":{\"averageUtilization\":80,\"type\":\"Utilization\"}},\"type\":\"Resource\"}]") }}
+
+ DEPRECATION WARNING:
+    `workers.hpa.metrics` has been renamed to `workers.celery.hpa.metrics`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
+{{- if not (empty .Values.workers.hpa.behavior) }}
+
+ DEPRECATION WARNING:
+    `workers.hpa.behavior` has been renamed to `workers.celery.hpa.behavior`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
 {{- if not .Values.workers.persistence.enabled }}

  DEPRECATION WARNING:
diff --git a/chart/templates/workers/worker-deployment.yaml b/chart/templates/workers/worker-deployment.yaml
index 0d221fd003a22..340c9aaea3e13 100644
--- a/chart/templates/workers/worker-deployment.yaml
+++ b/chart/templates/workers/worker-deployment.yaml
@@ -32,11 +32,11 @@
   {{- $workers := (include "workersMergeValues" (list $mergedWorkers $workerSet "" list) | fromYaml) -}}
   {{- $_ := set $globals.Values "workers" $workers -}}
   {{- with $globals -}}
+{{- if or (contains "CeleryExecutor" .Values.executor) (contains "CeleryKubernetesExecutor" .Values.executor) }}
+---
 {{- $persistence := or .Values.workers.persistence.enabled }}
 {{- $keda := .Values.workers.keda.enabled }}
 {{- $hpa := and .Values.workers.hpa.enabled (not .Values.workers.keda.enabled) }}
-{{- if or (contains "CeleryExecutor" .Values.executor) (contains "CeleryKubernetesExecutor" .Values.executor) }}
----
 {{- $nodeSelector := or .Values.workers.nodeSelector .Values.nodeSelector }}
 {{- $affinity := or .Values.workers.affinity .Values.affinity }}
 {{- $tolerations := or .Values.workers.tolerations .Values.tolerations }}
diff --git a/chart/values.schema.json b/chart/values.schema.json
index 05c3d6de3760c..97fadd3385ee2 100644
--- a/chart/values.schema.json
+++ b/chart/values.schema.json
@@ -1951,27 +1951,27 @@
                     }
                 },
                 "hpa": {
-                    "description": "HPA configuration for Airflow Celery workers.",
+                    "description": "HPA configuration for Airflow Celery workers (deprecated, use ``workers.celery.hpa`` instead).",
                     "type": "object",
                     "additionalProperties": false,
                     "properties": {
                         "enabled": {
-                            "description": "Allow HPA autoscaling (KEDA must be disabled).",
+                            "description": "Allow HPA autoscaling (KEDA must be disabled) (deprecated, use ``workers.celery.hpa.enabled`` instead).",
                             "type": "boolean",
                             "default": false
                         },
                         "minReplicaCount": {
-                            "description": "Minimum number of Airflow Celery workers created by HPA.",
+                            "description": "Minimum number of Airflow Celery workers created by HPA (deprecated, use ``workers.celery.hpa.minReplicaCount`` instead).",
                             "type": "integer",
                             "default": 0
                         },
                         "maxReplicaCount": {
-                            "description": "Maximum number of Airflow Celery workers created by HPA.",
+                            "description": "Maximum number of Airflow Celery workers created by HPA (deprecated, use ``workers.celery.hpa.maxReplicaCount`` instead).",
                             "type": "integer",
                             "default": 5
                         },
                         "metrics": {
-                            "description": "Specifications for which to use to calculate the desired replica count.",
+                            "description": "Specifications for which to use to calculate the desired replica count (deprecated, use ``workers.celery.hpa.metrics`` instead).",
                             "type": "array",
                             "default": [
                                 {
@@ -1990,7 +1990,7 @@
                             }
                         },
                         "behavior": {
-                            "description": "HorizontalPodAutoscalerBehavior configures the scaling behavior of the target.",
+                            "description": "HorizontalPodAutoscalerBehavior configures the scaling behavior of the target (deprecated, use ``workers.celery.hpa.behavior`` instead).",
                             "type": "object",
                             "default": {},
                             "$ref": "#/definitions/io.k8s.api.autoscaling.v2.HorizontalPodAutoscalerBehavior"
@@ -3051,6 +3051,54 @@
                                 }
                             }
                         },
+                        "hpa": {
+                            "description": "HPA configuration for Airflow Celery workers.",
+                            "type": "object",
+                            "additionalProperties": false,
+                            "properties": {
+                                "enabled": {
+                                    "description": "Allow HPA autoscaling (KEDA must be disabled).",
+                                    "type": [
+                                        "boolean",
+                                        "null"
+                                    ],
+                                    "default": null
+                                },
+                                "minReplicaCount": {
+                                    "description": "Minimum number of Airflow Celery workers created by HPA.",
+                                    "type": [
+                                        "integer",
+                                        "null"
+                                    ],
+                                    "default": null
+                                },
+                                "maxReplicaCount": {
+                                    "description": "Maximum number of Airflow Celery workers created by HPA.",
+                                    "type": [
+                                        "integer",
+                                        "null"
+                                    ],
+                                    "default": null
+                                },
+                                "metrics": {
+                                    "description": "Specifications for which to use to calculate the desired replica count.",
+                                    "type": [
+                                        "array",
+                                        "null"
+                                    ],
+                                    "default": null,
+                                    "items": {
+                                        "$ref": "#/definitions/io.k8s.api.autoscaling.v2.MetricSpec"
+                                    }
+                                },
+                                "behavior": {
+                                    "description": "HorizontalPodAutoscalerBehavior configures the scaling behavior of the target.",
+                                    "type": "object",
+                                    "default": {},
+                                    "$ref": "#/definitions/io.k8s.api.autoscaling.v2.HorizontalPodAutoscalerBehavior"
+                                }
+                            }
+                        },
                         "persistence": {
                             "description": "Persistence configuration for Airflow Celery workers.",
                             "type": "object",
@@ -864,16 +864,21 @@ workers:
      usePgbouncer: true

    # Allow HPA for Airflow Celery workers (KEDA must be disabled)
+  # (deprecated, use `workers.celery.hpa` instead)
    hpa:
+    # (deprecated, use `workers.celery.hpa.enabled` instead)
      enabled: false

      # Minimum number of Airflow Celery workers created by HPA
+    # (deprecated, use `workers.celery.hpa.minReplicaCount` instead)
      minReplicaCount: 0

      # Maximum number of Airflow Celery workers created by HPA
+    # (deprecated, use `workers.celery.hpa.maxReplicaCount` instead)
      maxReplicaCount: 5

      # Specifications for which to use to calculate the desired replica count
+    # (deprecated, use `workers.celery.hpa.metrics` instead)
      metrics:
        - type: Resource
          resource:
@@ -884,6 +889,7 @@ workers:
              averageUtilization: 80

      # Scaling behavior of the target in both Up and Down directions
+    # (deprecated, use `workers.celery.hpa.behavior` instead)
      behavior: {}

    # Persistence volume configuration for Airflow Celery workers
@@ -1334,6 +1340,22 @@ workers:
        # This configuration will be ignored if PGBouncer is not enabled
        usePgbouncer: ~

+    # Allow HPA for Airflow Celery workers (KEDA must be disabled)
+    hpa:
+      enabled: ~
+
+      # Minimum number of Airflow Celery workers created by HPA
+      minReplicaCount: ~
+
+      # Maximum number of Airflow Celery workers created by HPA
+      maxReplicaCount: ~
+
+      # Specifications for which to use to calculate the desired replica count
+      metrics: ~
+
+      # Scaling behavior of the target in both Up and Down directions
+      behavior: {}
+
      # Persistence volume configuration for Airflow Celery workers
      persistence:
        # Enable persistent volumes
diff --git a/helm-tests/tests/helm_tests/airflow_core/test_worker.py b/helm-tests/tests/helm_tests/airflow_core/test_worker.py
index a247f15ca478f..50975cceefef5 100644
--- a/helm-tests/tests/helm_tests/airflow_core/test_worker.py
+++ b/helm-tests/tests/helm_tests/airflow_core/test_worker.py
@@ -2191,29 +2191,26 @@ class TestWorkerHPAAutoScaler:
     """Tests worker HPA auto scaler."""

     @pytest.mark.parametrize(
-        "workers_keda_values",
+        "workers_values",
         [
-            {"keda": {"enabled": True}},
-            {"celery": {"keda": {"enabled": True}}},
+            {"keda": {"enabled": True}, "hpa": {"enabled": True}},
+            {"celery": {"keda": {"enabled": True}}, "hpa": {"enabled": True}},
+            {"celery": {"keda": {"enabled": True}, "hpa": {"enabled": True}}},
+            {"keda": {"enabled": True}, "celery": {"hpa": {"enabled": True}}},
         ],
     )
-    def test_should_be_disabled_on_keda_enabled(self, workers_keda_values):
+    def test_should_be_disabled_on_keda_enabled(self, workers_values):
         docs = render_chart(
             values={
                 "executor": "CeleryExecutor",
-                "workers": {
-                    **workers_keda_values,
-                    "hpa": {"enabled": True},
-                    "labels": {"test_label": "test_label_value"},
-                },
+                "workers": workers_values,
             },
             show_only=[
                 "templates/workers/worker-kedaautoscaler.yaml",
                 "templates/workers/worker-hpa.yaml",
             ],
         )
-        assert "test_label" in jmespath.search("metadata.labels", docs[0])
-        assert jmespath.search("metadata.labels", docs[0])["test_label"] == "test_label_value"
+
         assert len(docs) == 1

     def test_should_add_component_specific_labels(self):
@@ -2221,7 +2218,7 @@ def test_should_add_component_specific_labels(self):
             values={
                 "executor": "CeleryExecutor",
                 "workers": {
-                    "hpa": {"enabled": True},
+                    "celery": {"hpa": {"enabled": True}},
                     "labels": {"test_label": "test_label_value"},
                 },
             },
@@ -2243,51 +2240,112 @@ def test_should_remove_replicas_field(self):
         )
         assert "replicas" not in jmespath.search("spec", docs[0])

+    @pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
     @pytest.mark.parametrize(
-        ("metrics", "executor", "expected_metrics"),
+        "workers_values",
         [
-            # default metrics
-            (
-                None,
-                "CeleryExecutor",
-                {
-                    "type": "Resource",
-                    "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 80}},
+            {"hpa": {"enabled": True}},
+            {"celery": {"hpa": {"enabled": True}}},
+        ],
+    )
+    def test_hpa_metrics_default(self, executor, workers_values):
+        docs = render_chart(
+            values={
+                "executor": executor,
+                "workers": workers_values,
+            },
+            show_only=["templates/workers/worker-hpa.yaml"],
+        )
+
+        assert jmespath.search("spec.metrics", docs[0]) == [
+            {
+                "type": "Resource",
+                "resource": {"name": "cpu", "target": {"type": "Utilization", "averageUtilization": 80}},
+            }
+        ]
+
+    @pytest.mark.parametrize("executor", ["CeleryExecutor", "CeleryKubernetesExecutor"])
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "hpa": {
+                    "enabled": True,
+                    "metrics": [
+                        {
+                            "type": "Pods",
+                            "pods": {
+                                "metric": {"name": "custom"},
+                                "target": {"type": "Utilization", "averageUtilization": 80},
+                            },
+                        }
+                    ],
+                }
+            },
+            {
+                "celery": {
+                    "hpa": {
+                        "enabled": True,
+                        "metrics": [
+                            {
+                                "type": "Pods",
+                                "pods": {
+                                    "metric": {"name": "custom"},
+                                    "target": {"type": "Utilization", "averageUtilization": 80},
+                                },
+                            }
+                        ],
+                    }
+                }
+            },
+            {
+                "hpa": {
+                    "enabled": True,
+                    "metrics": [
+                        {
+                            "type": "Resource",
+                            "resource": {
+                                "name": "memory",
+                                "target": {"type": "Utilization", "averageUtilization": 1},
+                            },
+                        }
+                    ],
                 },
-            ),
-            # custom metric
-            (
-                [
-                    {
-                        "type": "Pods",
-                        "pods": {
-                            "metric": {"name": "custom"},
-                            "target": {"type": "Utilization", "averageUtilization": 80},
-                        },
+                "celery": {
+                    "hpa": {
+                        "enabled": True,
+                        "metrics": [
+                            {
+                                "type": "Pods",
+                                "pods": {
+                                    "metric": {"name": "custom"},
+                                    "target": {"type": "Utilization", "averageUtilization": 80},
+                                },
+                            }
+                        ],
                     }
-                ],
-                "CeleryKubernetesExecutor",
-                {
-                    "type": "Pods",
-                    "pods": {
-                        "metric": {"name": "custom"},
-                        "target": {"type": "Utilization", "averageUtilization": 80},
-                    },
                 },
-            ),
+            },
         ],
     )
-    def test_should_use_hpa_metrics(self, metrics, executor, expected_metrics):
+    def test_hpa_metrics_override(self, executor, workers_values):
         docs = render_chart(
             values={
                 "executor": executor,
-                "workers": {
-                    "hpa": {"enabled": True, **({"metrics": metrics} if metrics else {})},
-                },
+                "workers": workers_values,
             },
             show_only=["templates/workers/worker-hpa.yaml"],
         )
-        assert expected_metrics == jmespath.search("spec.metrics[0]", docs[0])
+
+        assert jmespath.search("spec.metrics", docs[0]) == [
+            {
+                "type": "Pods",
+                "pods": {
+                    "metric": {"name": "custom"},
+                    "target": {"type": "Utilization", "averageUtilization": 80},
+                },
+            }
+        ]


 class TestWorkerNetworkPolicy:
diff --git a/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py b/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
index d15554ab0f832..18edc03c6c250 100644
--- a/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
+++ b/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
@@ -1734,8 +1734,8 @@ def test_create_hpa_sets(self, enable_default, expected):
             name="test",
             values={
                 "workers": {
-                    "hpa": {"enabled": True},
                     "celery": {
+                        "hpa": {"enabled": True},
                         "enableDefault": enable_default,
                         "sets": [
                             {"name": "set1"},
@@ -1749,56 +1749,116 @@ def test_create_hpa_sets(self, enable_default, expected):

         assert jmespath.search("[*].metadata.name", docs) == expected

-    def test_overwrite_hpa_enabled(self):
-        docs = render_chart(
-            values={
-                "workers": {
-                    "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": True}}]},
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {"celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": True}}]}},
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "hpa": {"enabled": False},
+                    "sets": [{"name": "test", "hpa": {"enabled": True}}],
                 }
             },
+            {
+                "hpa": {"enabled": False},
+                "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": True}}]},
+            },
+        ],
+    )
+    def test_overwrite_hpa_enabled(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-hpa.yaml"],
         )

         assert len(docs) == 1

-    def test_overwrite_hpa_disable(self):
-        docs = render_chart(
-            values={
-                "workers": {
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "celery": {
+                    "enableDefault": False,
                     "hpa": {"enabled": True},
-                    "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": False}}]},
+                    "sets": [{"name": "test", "hpa": {"enabled": False}}],
                 }
             },
+            {
+                "hpa": {"enabled": True},
+                "celery": {"enableDefault": False, "sets": [{"name": "test", "hpa": {"enabled": False}}]},
+            },
+        ],
+    )
+    def test_overwrite_hpa_disable(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-hpa.yaml"],
         )

         assert len(docs) == 0

-    def test_overwrite_hpa_min_replica_count(self):
-        docs = render_chart(
-            values={
-                "workers": {
-                    "celery": {
-                        "enableDefault": False,
-                        "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
-                    },
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
+                }
+            },
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "hpa": {"minReplicaCount": 7},
+                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
                 }
             },
+            {
+                "hpa": {"minReplicaCount": 7},
+                "celery": {
+                    "enableDefault": False,
+                    "sets": [{"name": "test", "hpa": {"enabled": True, "minReplicaCount": 10}}],
+                },
+            },
+        ],
+    )
+    def test_overwrite_hpa_min_replica_count(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-hpa.yaml"],
         )

         assert jmespath.search("spec.minReplicas", docs[0]) == 10

-    def test_overwrite_hpa_max_replica_count(self):
-        docs = render_chart(
-            values={
-                "workers": {
-                    "celery": {
-                        "enableDefault": False,
-                        "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
-                    },
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
                 }
             },
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "hpa": {"maxReplicaCount": 7},
+                    "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
+                }
+            },
+            {
+                "hpa": {"maxReplicaCount": 7},
+                "celery": {
+                    "enableDefault": False,
+                    "sets": [{"name": "test", "hpa": {"enabled": True, "maxReplicaCount": 10}}],
+                },
+            },
+        ],
+    )
+    def test_overwrite_hpa_max_replica_count(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-hpa.yaml"],
         )

@@ -1862,6 +1922,39 @@ def test_overwrite_hpa_max_replica_count(self):
                     ],
                 },
             },
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "hpa": {
+                        "metrics": [
+                            {
+                                "type": "Resource",
+                                "resource": {
+                                    "name": "memory",
+                                    "target": {"type": "Utilization", "averageUtilization": 1},
+                                },
+                            }
+                        ],
+                    },
+                    "sets": [
+                        {
+                            "name": "test",
+                            "hpa": {
+                                "enabled": True,
+                                "metrics": [
+                                    {
+                                        "type": "Resource",
+                                        "resource": {
+                                            "name": "cpu",
+                                            "target": {"type": "Utilization", "averageUtilization": 80},
+                                        },
+                                    }
+                                ],
+                            },
+                        }
+                    ],
+                },
+            },
         ],
     )
     def test_overwrite_hpa_metrics(self, workers_values):
@@ -1903,6 +1996,18 @@ def test_overwrite_hpa_metrics(self, workers_values):
                     ],
                 },
             },
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "hpa": {"behavior": {"scaleUp": {"selectPolicy": "Min"}}},
+                    "sets": [
+                        {
+                            "name": "test",
+                            "hpa": {"enabled": True, "behavior": {"scaleDown": {"selectPolicy": "Max"}}},
+                        }
+                    ],
+                },
+            },
         ],
     )
     def test_overwrite_hpa_behavior(self, workers_values):
diff --git a/helm-tests/tests/helm_tests/other/test_hpa.py b/helm-tests/tests/helm_tests/other/test_hpa.py
index 83bcf68b12c8a..1f2f632e6a19d 100644
--- a/helm-tests/tests/helm_tests/other/test_hpa.py
+++ b/helm-tests/tests/helm_tests/other/test_hpa.py
@@ -25,7 +25,6 @@ class TestHPA:
     """Tests HPA."""

     def test_hpa_disabled_by_default(self):
-        """Disabled by default."""
         docs = render_chart(
             values={},
             show_only=["templates/workers/worker-hpa.yaml"],
@@ -40,11 +39,21 @@ def test_hpa_disabled_by_default(self):
             "CeleryExecutor,KubernetesExecutor",
         ],
     )
-    def test_hpa_enabled(self, executor):
-        """HPA should only be created when enabled and executor is Celery or CeleryKubernetes."""
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {"hpa": {"enabled": True}, "celery": {"persistence": {"enabled": False}}},
+            {"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}}},
+            {
+                "hpa": {"enabled": False},
+                "celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}},
+            },
+        ],
+    )
+    def test_hpa_enabled(self, executor, workers_values):
         docs = render_chart(
             values={
-                "workers": {"hpa": {"enabled": True}, "celery": {"persistence": {"enabled": False}}},
+                "workers": workers_values,
                 "executor": executor,
             },
             show_only=["templates/workers/worker-hpa.yaml"],
@@ -52,69 +61,118 @@ def test_hpa_enabled(self, executor):

         assert jmespath.search("metadata.name", docs[0]) == "release-name-worker"

+    def test_min_max_replicas_default(self):
+        docs = render_chart(
+            values={"workers": {"celery": {"hpa": {"enabled": True}}}},
+            show_only=["templates/workers/worker-hpa.yaml"],
+        )
+
+        assert jmespath.search("spec.minReplicas", docs[0]) == 0
+        assert jmespath.search("spec.maxReplicas", docs[0]) == 5
+
     @pytest.mark.parametrize(
-        ("min_replicas", "max_replicas"),
+        "workers_values",
         [
-            (None, None),
-            (2, 8),
+            {"hpa": {"enabled": True, "minReplicaCount": 2, "maxReplicaCount": 8}},
+            {"celery": {"hpa": {"enabled": True, "minReplicaCount": 2, "maxReplicaCount": 8}}},
+            {
+                "hpa": {"enabled": True, "minReplicaCount": 1, "maxReplicaCount": 10},
+                "celery": {"hpa": {"enabled": True, "minReplicaCount": 2, "maxReplicaCount": 8}},
+            },
         ],
     )
-    def test_min_max_replicas(self, min_replicas, max_replicas):
-        """Verify minimum and maximum replicas."""
+    def test_min_max_replicas(self, workers_values):
         docs = render_chart(
-            values={
-                "workers": {
-                    "hpa": {
-                        "enabled": True,
-                        **({"minReplicaCount": min_replicas} if min_replicas else {}),
-                        **({"maxReplicaCount": max_replicas} if max_replicas else {}),
-                    }
-                },
-            },
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-hpa.yaml"],
         )
-        assert jmespath.search("spec.minReplicas", docs[0]) == 0 if min_replicas is None else min_replicas
-        assert jmespath.search("spec.maxReplicas", docs[0]) == 5 if max_replicas is None else max_replicas
+
+        assert jmespath.search("spec.minReplicas", docs[0]) == 2
+        assert jmespath.search("spec.maxReplicas", docs[0]) == 8

     @pytest.mark.parametrize(
         "executor", ["CeleryExecutor", "CeleryKubernetesExecutor", "CeleryExecutor,KubernetesExecutor"]
     )
-    def test_hpa_behavior(self, executor):
-        """Verify HPA behavior."""
-        expected_behavior = {
-            "scaleDown": {
-                "stabilizationWindowSeconds": 300,
-                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
-            }
-        }
-        docs = render_chart(
-            values={
-                "workers": {
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "hpa": {
+                    "enabled": True,
+                    "behavior": {
+                        "scaleDown": {
+                            "stabilizationWindowSeconds": 300,
+                            "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
+                        }
+                    },
+                }
+            },
+            {
+                "celery": {
                     "hpa": {
                         "enabled": True,
-                        "behavior": expected_behavior,
-                    },
+                        "behavior": {
+                            "scaleDown": {
+                                "stabilizationWindowSeconds": 300,
+                                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
+                            }
+                        },
+                    }
+                }
+            },
+            {
+                "hpa": {
+                    "behavior": {
+                        "scaleUp": {
+                            "stabilizationWindowSeconds": 300,
+                            "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
+                        }
+                    }
+                },
+                "celery": {
+                    "hpa": {
+                        "enabled": True,
+                        "behavior": {
+                            "scaleDown": {
+                                "stabilizationWindowSeconds": 300,
+                                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
+                            }
+                        },
+                    }
                 },
+            },
+        ],
+    )
+    def test_hpa_behavior(self, executor, workers_values):
+        """Verify HPA behavior."""
+        docs = render_chart(
+            values={
+                "workers": workers_values,
                 "executor": executor,
             },
             show_only=["templates/workers/worker-hpa.yaml"],
         )
-        assert jmespath.search("spec.behavior", docs[0]) == expected_behavior
+        assert jmespath.search("spec.behavior", docs[0]) == {
+            "scaleDown": {
+                "stabilizationSeconds": 300,
+                "policies": [{"type": "Percent", "value": 100, "periodSeconds": 15}],
+            }
+        }

     @pytest.mark.parametrize(
-        ("workers_persistence_values", "kind"),
+        ("workers_values", "kind"),
         [
-            ({"celery": {"persistence": {"enabled": True}}}, "StatefulSet"),
-            ({"celery": {"persistence": {"enabled": False}}}, "Deployment"),
-            ({"persistence": {"enabled": True}}, "StatefulSet"),
-            ({"persistence": {"enabled": False}}, "Deployment"),
+            ({"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": True}}}, "StatefulSet"),
+            ({"celery": {"hpa": {"enabled": True}, "persistence": {"enabled": False}}}, "Deployment"),
+            ({"persistence": {"enabled": True}, "celery": {"hpa": {"enabled": True}}}, "StatefulSet"),
+            ({"persistence": {"enabled": False}, "celery": {"hpa": {"enabled": True}}}, "Deployment"),
         ],
     )
-    def test_persistence(self, workers_persistence_values, kind):
+    def test_persistence(self, workers_values, kind):
         """If worker persistence is enabled, scaleTargetRef should be StatefulSet else Deployment."""
         docs = render_chart(
             values={
-                "workers": {"hpa": {"enabled": True}, **workers_persistence_values},
+                "workers": workers_values,
                 "executor": "CeleryExecutor",
             },
             show_only=["templates/workers/worker-hpa.yaml"],
PATCH

echo "Patch applied successfully"
