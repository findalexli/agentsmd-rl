#!/bin/bash
set -e

cd /workspace/airflow

# Check if already patched
grep -q "workers.celery.volumeClaimTemplates" chart/values.yaml && {
    echo "Already patched"
    exit 0
}

# Apply the gold patch
cat <<'PATCH' | git apply -
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
PATCH

echo "Patch applied successfully"
