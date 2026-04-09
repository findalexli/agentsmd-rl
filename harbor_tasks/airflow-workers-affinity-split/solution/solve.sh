#!/bin/bash
set -e

cd /workspace/airflow

# Check if already applied
if grep -q "workers.kubernetes.affinity" chart/files/pod-template-file.kubernetes-helm-yaml; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/chart/files/pod-template-file.kubernetes-helm-yaml b/chart/files/pod-template-file.kubernetes-helm-yaml
index 5f067c68077d7..5aae2d8fc94ce 100644
--- a/chart/files/pod-template-file.kubernetes-helm-yaml
+++ b/chart/files/pod-template-file.kubernetes-helm-yaml
@@ -18,7 +18,7 @@
 */}}
 ---
 {{- $nodeSelector := or .Values.workers.kubernetes.nodeSelector .Values.workers.nodeSelector .Values.nodeSelector }}
-{{- $affinity := or .Values.workers.affinity .Values.affinity }}
+{{- $affinity := or .Values.workers.kubernetes.affinity .Values.workers.affinity .Values.affinity }}
 {{- $tolerations := or .Values.workers.tolerations .Values.tolerations }}
 {{- $topologySpreadConstraints := or .Values.workers.topologySpreadConstraints .Values.topologySpreadConstraints }}
 {{- $securityContext := include "airflowPodSecurityContext" (list .Values.workers.kubernetes .Values.workers .Values) }}
diff --git a/chart/newsfragments/64860.significant.rst b/chart/newsfragments/64860.significant.rst
new file mode 100644
index 0000000000000..672bd787a514c
--- /dev/null
+++ b/chart/newsfragments/64860.significant.rst
@@ -0,0 +1 @@
+``workers.affinity`` field is now deprecated in favor of ``workers.celery.affinity`` and ``workers.kubernetes.affinity``. Please update your configuration accordingly.
diff --git a/chart/templates/NOTES.txt b/chart/templates/NOTES.txt
index 44924918060b1..7728d1654f71b 100644
--- a/chart/templates/NOTES.txt
+++ b/chart/templates/NOTES.txt
@@ -717,6 +717,14 @@ DEPRECATION WARNING:

 {{- end }}

+{{- if not (empty .Values.workers.affinity) }}
+
+ DEPRECATION WARNING:
+    `workers.affinity` has been renamed to `workers.celery.affinity`/`workers.kubernetes.affinity`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
 {{- if not (empty .Values.workers.nodeSelector) }}

  DEPRECATION WARNING:
diff --git a/chart/values.schema.json b/chart/values.schema.json
index 97fadd3385ee2..a67e56b35af86 100644
--- a/chart/values.schema.json
+++ b/chart/values.schema.json
@@ -2357,7 +2357,7 @@
                     "default": null
                 },
                 "affinity": {
-                    "description": "Specify scheduling constraints for Airflow Celery worker pods and pods created with pod-template-file.",
+                    "description": "Specify scheduling constraints for Airflow Celery worker pods and pods created with pod-template-file (deprecated, use ``workers.celery.affinity`` and/or ``workers.kubernetes.affinity`` instead).",
                     "type": "object",
                     "default": "See values.yaml",
                     "$ref": "#/definitions/io.k8s.api.core.v1.Affinity"
@@ -3412,6 +3412,12 @@
                             ],
                             "default": null
                         },
+                        "affinity": {
+                            "description": "Specify scheduling constraints for Airflow Celery worker pods.",
+                            "type": "object",
+                            "default": {},
+                            "$ref": "#/definitions/io.k8s.api.core.v1.Affinity"
+                        },
                         "hostAliases": {
                             "description": "Specify HostAliases for Airflow Celery worker pods.",
                             "items": {
@@ -3888,6 +3894,12 @@
                             ],
                             "default": null
                         },
+                        "affinity": {
+                            "description": "Specify scheduling constraints for pods created with pod-template-file.",
+                            "type": "object",
+                            "default": {},
+                            "$ref": "#/definitions/io.k8s.api.core.v1.Affinity"
+                        },
                         "hostAliases": {
                             "description": "Specify HostAliases for pods created with pod-template-file.",
                             "items": {
diff --git a/chart/values.yaml b/chart/values.yaml
index 2510e3506e442..651a6779aea59 100644
--- a/chart/values.yaml
+++ b/chart/values.yaml
@@ -1081,6 +1081,7 @@ workers:
   # (deprecated, use `workers.celery.priorityClassName` and/or `workers.kubernetes.priorityClassName` instead)
   priorityClassName: ~

+  # (deprecated, use `workers.celery.affinity` and/or `workers.kubernetes.affinity` instead)
   affinity: {}
   # Default Airflow Celery worker affinity is:
   #  podAntiAffinity:
@@ -1452,6 +1453,17 @@ workers:

     priorityClassName: ~

+    affinity: {}
+    # Default Airflow Celery worker affinity is:
+    #  podAntiAffinity:
+    #    preferredDuringSchedulingIgnoredDuringExecution:
+    #    - podAffinityTerm:
+    #        labelSelector:
+    #          matchLabels:
+    #            component: worker
+    #        topologyKey: kubernetes.io/hostname
+    #      weight: 100
+
     # hostAliases to use in Airflow Celery worker pods
     # See:
     # https://kubernetes.io/docs/concepts/services-networking/add-entries-to-pod-etc-hosts-with-host-aliases/
@@ -1600,6 +1612,8 @@ workers:

     priorityClassName: ~

+    affinity: {}
+
     # hostAliases to use in pods created with pod-template-file
     # See:
     # https://kubernetes.io/docs/concepts/services-networking/add-entries-to-pod-etc-hosts-with-host-aliases/
PATCH

echo "Patch applied successfully"
