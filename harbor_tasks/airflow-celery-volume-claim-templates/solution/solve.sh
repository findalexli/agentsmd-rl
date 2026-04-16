#!/bin/bash
set -e

cd /workspace/airflow

# Apply the gold patch for PR #64779
cat <<'PATCH' | patch -p1
From 0b8d9f9d716836789f54e377379acf4bb213ff42 Mon Sep 17 00:00:00 2001
From: "github-actions[bot]" <41898282+github-actions[bot]@users.noreply.github.com>
Date: Mon, 6 Apr 2026 16:27:15 +0000
Subject: [chart/v1-2x-test] Add workers.celery.volumeClaimTemplates (#62048)

* Add workers.celery.volumeClaimTemplates

* Add newsfragment
(cherry picked from commit 3d83580c22b8cb1a6dd6e47e0213223992e85357)

Co-authored-by: Przemysław Mirowski <17602603+Miretpl@users.noreply.github.com>
---
diff --git a/chart/newsfragments/62048.significant.rst b/chart/newsfragments/62048.significant.rst
new file mode 100644
index 0000000000000..7607c2518f56e
--- /dev/null
+++ b/chart/newsfragments/62048.significant.rst
@@ -0,0 +1 @@
+``workers.volumeClaimTemplates`` field is now deprecated in favor of ``workers.celery.volumeClaimTemplates``. Please update your configuration accordingly.
diff --git a/chart/templates/NOTES.txt b/chart/templates/NOTES.txt
index fc7b9474c1c25..f752f3f5ef0cb 100644
--- a/chart/templates/NOTES.txt
+++ b/chart/templates/NOTES.txt
@@ -669,6 +669,14 @@ DEPRECATION WARNING:

 {{- end }}

+{{- if not (empty .Values.workers.volumeClaimTemplates) }}
+
+ DEPRECATION WARNING:
+    `workers.volumeClaimTemplates` has been renamed to `workers.celery.volumeClaimTemplates`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
 {{- if not (empty .Values.workers.schedulerName) }}

  DEPRECATION WARNING:
diff --git a/chart/values.schema.json b/chart/values.schema.json
index c3c08557b9ffb..17eae47f3e377 100644
--- a/chart/values.schema.json
+++ b/chart/values.schema.json
@@ -2634,7 +2634,7 @@
                     }
                 },
                 "volumeClaimTemplates": {
-                    "description": "Specify additional volume claim template for Airflow Celery workers.",
+                    "description": "Specify additional volume claim template for Airflow Celery workers (deprecated, use ``workers.celery.volumeClaimTemplates`` instead).",
                     "type": "array",
                     "default": [],
                     "items": {
@@ -3348,6 +3348,40 @@
                                 }
                             ]
                         },
+                        "volumeClaimTemplates": {
+                            "description": "Specify additional volume claim template for Airflow Celery workers.",
+                            "type": "array",
+                            "default": [],
+                            "items": {
+                                "$ref": "#/definitions/io.k8s.api.core.v1.PersistentVolumeClaimTemplate"
+                            },
+                            "examples": [
+                                {
+                                    "name": "data-volume-1",
+                                    "storageClassName": "storage-class-1",
+                                    "accessModes": [
+                                        "ReadWriteOnce"
+                                    ],
+                                    "resources": {
+                                        "requests": {
+                                            "storage": "10Gi"
+                                        }
+                                    }
+                                },
+                                {
+                                    "name": "data-volume-2",
+                                    "storageClassName": "storage-class-2",
+                                    "accessModes": [
+                                        "ReadWriteOnce"
+                                    ],
+                                    "resources": {
+                                        "requests": {
+                                            "storage": "20Gi"
+                                        }
+                                    }
+                                }
+                            ]
+                        },
                         "schedulerName": {
                             "description": "Specify kube scheduler name for Airflow Celery worker pods.",
                             "type": [

diff --git a/chart/values.yaml b/chart/values.yaml
index 28a632061b4c0..e07901ba03a29 100644
--- a/chart/values.yaml
+++ b/chart/values.yaml
@@ -1151,6 +1151,7 @@ workers:

   # Additional volume claim templates for Airflow Celery workers.
   # Requires mounting of specified volumes under extraVolumeMounts.
+  # (deprecated, use `workers.celery.volumeClaimTemplates` instead)
   volumeClaimTemplates: []
   # Volume Claim Templates example:
   # volumeClaimTemplates:
@@ -1403,6 +1404,30 @@ workers:
     #   hostnames:
     #   - "test.hostname.two"

+    # Additional volume claim templates for Airflow Celery workers.
+    # Requires mounting of specified volumes under extraVolumeMounts.
+    volumeClaimTemplates: []
+    # Volume Claim Templates example:
+    # volumeClaimTemplates:
+    #   - metadata:
+    #       name: data-volume-1
+    #     spec:
+    #       storageClassName: "storage-class-1"
+    #       accessModes:
+    #         - "ReadWriteOnce"
+    #       resources:
+    #         requests:
+    #           storage: "10Gi"
+    #   - metadata:
+    #       name: data-volume-2
+    #     spec:
+    #       storageClassName: "storage-class-2"
+    #       accessModes:
+    #         - "ReadWriteOnce"
+    #       resources:
+    #         requests:
+    #           storage: "20Gi"
+
     schedulerName: ~

   kubernetes:

diff --git a/helm-tests/tests/helm_tests/airflow_core/test_worker.py b/helm-tests/tests/helm_tests/airflow_core/test_worker.py
index b017476b56976..03188cda33074 100644
--- a/helm-tests/tests/helm_tests/airflow_core/test_worker.py
+++ b/helm-tests/tests/helm_tests/airflow_core/test_worker.py
@@ -1541,11 +1541,63 @@ def test_safetoevict_annotations(self, globalScope, localScope, precedence):
             == precedence
         )

-    def test_should_add_extra_volume_claim_templates(self):
-        docs = render_chart(
-            values={
-                "executor": "CeleryExecutor",
-                "workers": {
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "volumeClaimTemplates": [
+                    {
+                        "metadata": {"name": "test-volume-airflow-1"},
+                        "spec": {
+                            "storageClassName": "storage-class-1",
+                            "accessModes": ["ReadWriteOnce"],
+                            "resources": {"requests": {"storage": "10Gi"}},
+                        },
+                    },
+                    {
+                        "metadata": {"name": "test-volume-airflow-2"},
+                        "spec": {
+                            "storageClassName": "storage-class-2",
+                            "accessModes": ["ReadWriteOnce"],
+                            "resources": {"requests": {"storage": "20Gi"}},
+                        },
+                    },
+                ]
+            },
+            {
+                "celery": {
+                    "volumeClaimTemplates": [
+                        {
+                            "metadata": {"name": "test-volume-airflow-1"},
+                            "spec": {
+                                "storageClassName": "storage-class-1",
+                                "accessModes": ["ReadWriteOnce"],
+                                "resources": {"requests": {"storage": "10Gi"}},
+                            },
+                        },
+                        {
+                            "metadata": {"name": "test-volume-airflow-2"},
+                            "spec": {
+                                "storageClassName": "storage-class-2",
+                                "accessModes": ["ReadWriteOnce"],
+                                "resources": {"requests": {"storage": "20Gi"}},
+                            },
+                        },
+                    ]
+                }
+            },
+            {
+                "volumeClaimTemplates": [
+                    {
+                        "metadata": {"name": "test"},
+                        "spec": {
+                            "storageClassName": "storage",
+                            "accessModes": ["ReadOnce"],
+                            "resources": {"requests": {"storage": "1Gi"}},
+                        },
+                    }
+                ],
+                "celery": {
                     "volumeClaimTemplates": [
                         {
                             "metadata": {"name": "test-volume-airflow-1"},
@@ -1566,31 +1618,36 @@ def test_should_add_extra_volume_claim_templates(self):
                     ]
                 },
             },
+        ],
+    )
+    def test_should_add_extra_volume_claim_templates(self, workers_values):
+        docs = render_chart(
+            values={
+                "executor": "CeleryExecutor",
+                "workers": workers_values,
+            },
             show_only=["templates/workers/worker-deployment.yaml"],
         )

-        assert (
-            jmespath.search("spec.volumeClaimTemplates[1].metadata.name", docs[0]) == "test-volume-airflow-1"
-        )
-        assert (
-            jmespath.search("spec.volumeClaimTemplates[2].metadata.name", docs[0]) == "test-volume-airflow-2"
-        )
-        assert (
-            jmespath.search("spec.volumeClaimTemplates[1].spec.storageClassName", docs[0])
-            == "storage-class-1"
-        )
-        assert (
-            jmespath.search("spec.volumeClaimTemplates[2].spec.storageClassName", docs[0])
-            == "storage-class-2"
-        )
-        assert jmespath.search("spec.volumeClaimTemplates[1].spec.accessModes", docs[0]) == ["ReadWriteOnce"]
-        assert jmespath.search("spec.volumeClaimTemplates[2].spec.accessModes", docs[0]) == ["ReadWriteOnce"]
-        assert (
-            jmespath.search("spec.volumeClaimTemplates[1].spec.resources.requests.storage", docs[0]) == "10Gi"
-        )
-        assert (
-            jmespath.search("spec.volumeClaimTemplates[2].spec.resources.requests.storage", docs[0]) == "20Gi"
-        )
+        # Skipping the first object as it is logs volume claim
+        assert jmespath.search("spec.volumeClaimTemplates[1:]", docs[0]) == [
+            {
+                "metadata": {"name": "test-volume-airflow-1"},
+                "spec": {
+                    "storageClassName": "storage-class-1",
+                    "accessModes": ["ReadWriteOnce"],
+                    "resources": {"requests": {"storage": "10Gi"}},
+                },
+            },
+            {
+                "metadata": {"name": "test-volume-airflow-2"},
+                "spec": {
+                    "storageClassName": "storage-class-2",
+                    "accessModes": ["ReadWriteOnce"],
+                    "resources": {"requests": {"storage": "20Gi"}},
+                },
+            },
+        ]

     def test_should_add_extra_volume_claim_templates_with_logs_persistence_enabled(self):
         """
@@ -1604,17 +1661,19 @@ def test_should_add_extra_volume_claim_templates_with_logs_persistence_enabled(
             values={
                 "executor": "CeleryExecutor",
                 "workers": {
-                    "celery": {"persistence": {"enabled": True}},
-                    "volumeClaimTemplates": [
-                        {
-                            "metadata": {"name": "data"},
-                            "spec": {
-                                "storageClassName": "longhorn",
-                                "accessModes": ["ReadWriteOnce"],
-                                "resources": {"requests": {"storage": "10Gi"}},
+                    "celery": {
+                        "persistence": {"enabled": True},
+                        "volumeClaimTemplates": [
+                            {
+                                "metadata": {"name": "data"},
+                                "spec": {
+                                    "storageClassName": "longhorn",
+                                    "accessModes": ["ReadWriteOnce"],
+                                    "resources": {"requests": {"storage": "10Gi"}},
+                                },
                             },
-                        },
-                    ],
+                        ],
+                    },
                 },
                 "logs": {
                     "persistence": {"enabled": True},  # This is the key: logs persistence enabled
@@ -1724,8 +1783,10 @@ def test_volume_claim_templates_conditional_logic(
             values={
                 "executor": "CeleryExecutor",
                 "workers": {
-                    "celery": {"persistence": {"enabled": workers_persistence_enabled}},
-                    "volumeClaimTemplates": custom_templates,
+                    "celery": {
+                        "persistence": {"enabled": workers_persistence_enabled},
+                        "volumeClaimTemplates": custom_templates,
+                    },
                 },
                 "logs": {
                     "persistence": {"enabled": logs_persistence_enabled},

diff --git a/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py b/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
index 50e7ff454c4df..b706c61153bfa 100644
--- a/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
+++ b/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
@@ -3050,6 +3050,36 @@ def test_overwrite_env(self, workers_values):
                     ],
                 },
             },
+            {
+                "celery": {
+                    "volumeClaimTemplates": [
+                        {
+                            "metadata": {"name": "test-volume"},
+                            "spec": {
+                                "storageClassName": "class",
+                                "accessModes": ["ReadOnce"],
+                                "resources": {"requests": {"storage": "1Gi"}},
+                            },
+                        }
+                    ],
+                    "enableDefault": False,
+                    "sets": [
+                        {
+                            "name": "set1",
+                            "volumeClaimTemplates": [
+                                {
+                                    "metadata": {"name": "test-volume-airflow-1"},
+                                    "spec": {
+                                        "storageClassName": "storage-class-1",
+                                        "accessModes": ["ReadWriteOnce"],
+                                        "resources": {"requests": {"storage": "10Gi"}},
+                                    },
+                                }
+                            ],
+                        }
+                    ],
+                },
+            },
         ],
     )
     def test_overwrite_volume_claim_templates(self, workers_values):
PATCH

# Idempotency check - verify a distinctive line from the patch is present
grep -q "workers.celery.volumeClaimTemplates" /workspace/airflow/chart/values.yaml
echo "Gold patch applied successfully"
