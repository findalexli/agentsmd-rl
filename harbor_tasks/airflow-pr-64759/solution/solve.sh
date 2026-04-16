#!/bin/bash
# Licensed under the Apache License, Version 2.0
# Solution script for airflow-helm-scheduler-name task

set -e

cd /workspace/airflow

# Check if patch is already applied (idempotency)
if grep -q "workers.kubernetes.schedulerName .Values.workers.schedulerName .Values.schedulerName" chart/files/pod-template-file.kubernetes-helm-yaml 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply --verbose - <<'PATCH'
diff --git a/chart/files/pod-template-file.kubernetes-helm-yaml b/chart/files/pod-template-file.kubernetes-helm-yaml
index 59fd6d82f7dfc..902391cd1a9e5 100644
--- a/chart/files/pod-template-file.kubernetes-helm-yaml
+++ b/chart/files/pod-template-file.kubernetes-helm-yaml
@@ -30,7 +30,7 @@
 {{- $containerLifecycleHooks := or .Values.workers.kubernetes.containerLifecycleHooks .Values.workers.containerLifecycleHooks .Values.containerLifecycleHooks }}
 {{- $safeToEvict := dict "cluster-autoscaler.kubernetes.io/safe-to-evict" (or .Values.workers.kubernetes.safeToEvict (and (not (has .Values.workers.kubernetes.safeToEvict (list true false))) .Values.workers.safeToEvict) | toString) }}
 {{- $podAnnotations := mergeOverwrite (deepCopy .Values.airflowPodAnnotations) $safeToEvict .Values.workers.podAnnotations }}
-{{- $schedulerName := or .Values.workers.schedulerName .Values.schedulerName }}
+{{- $schedulerName := or .Values.workers.kubernetes.schedulerName .Values.workers.schedulerName .Values.schedulerName }}
 apiVersion: v1
 kind: Pod
 metadata:
diff --git a/chart/newsfragments/62030.significant.rst b/chart/newsfragments/62030.significant.rst
new file mode 100644
index 0000000000000..3606c90d11b65
--- /dev/null
+++ b/chart/newsfragments/62030.significant.rst
@@ -0,0 +1 @@
+``workers.schedulerName`` field is now deprecated in favor of ``workers.celery.schedulerName`` and ``workers.kubernetes.schedulerName``. Please update your configuration accordingly.
diff --git a/chart/templates/NOTES.txt b/chart/templates/NOTES.txt
index 520717c6b2908..fc7b9474c1c25 100644
--- a/chart/templates/NOTES.txt
+++ b/chart/templates/NOTES.txt
@@ -669,6 +669,14 @@ DEPRECATION WARNING:

 {{- end }}

+{{- if not (empty .Values.workers.schedulerName) }}
+
+ DEPRECATION WARNING:
+    `workers.schedulerName` has been renamed to `workers.celery.schedulerName`/`workers.kubernetes.schedulerName`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
 {{- if not (empty .Values.webserver.defaultUser) }}

  DEPRECATION WARNING:
diff --git a/chart/values.schema.json b/chart/values.schema.json
index de8aca2a4fc73..c3c08557b9ffb 100644
--- a/chart/values.schema.json
+++ b/chart/values.schema.json
@@ -2419,7 +2419,7 @@
                     }
                 },
                 "schedulerName": {
-                    "description": "Specify kube scheduler name for Airflow Celery workers objects and pods created with pod-template-file.",
+                    "description": "Specify kube scheduler name for Airflow Celery workers objects and pods created with pod-template-file (deprecated, use ``workers.celery.schedulerName`` and/or ``workers.kubernetes.schedulerName`` instead).",
                     "type": [
                         "string",
                         "null"
@@ -3347,6 +3347,15 @@
                                     ]
                                 }
                             ]
+                        },
+                        "schedulerName": {
+                            "description": "Specify kube scheduler name for Airflow Celery worker pods.",
+                            "type": [
+                                "string",
+                                "null"
+                            ],
+                            "default": null,
+                            "x-docsSection": "Common"
                         }
                     }
                 },
@@ -3682,6 +3691,15 @@
                                     ]
                                 }
                             ]
+                        },
+                        "schedulerName": {
+                            "description": "Specify kube scheduler name for pods created with pod-template-file.",
+                            "type": [
+                                "string",
+                                "null"
+                            ],
+                            "default": null,
+                            "x-docsSection": "Common"
                         }
                     }
                 }
diff --git a/chart/values.yaml b/chart/values.yaml
index 66c2e056dd0ec..28a632061b4c0 100644
--- a/chart/values.yaml
+++ b/chart/values.yaml
@@ -1173,6 +1173,9 @@ workers:
   #         requests:
   #           storage: "20Gi"

+  # (deprecated, use `workers.celery.schedulerName` and/or `workers.kubernetes.schedulerName` instead)
+  schedulerName: ~
+
   celery:
     # Number of Airflow Celery workers
     replicas: ~
@@ -1400,6 +1403,8 @@ workers:
     #   hostnames:
     #   - "test.hostname.two"

+    schedulerName: ~
+
   kubernetes:
     # Command to use in pod-template-file (templated)
     command: ~
@@ -1488,6 +1493,8 @@ workers:
     #   hostnames:
     #   - "test.hostname.two"

+    schedulerName: ~
+
 # Airflow scheduler settings
 scheduler:
   enabled: true
PATCH

echo "Patch applied successfully"
