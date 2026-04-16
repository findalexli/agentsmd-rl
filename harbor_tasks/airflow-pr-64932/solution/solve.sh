#!/bin/bash
# Gold solution for apache/airflow#64932
# Adds workers.celery.extraContainers & workers.kubernetes.extraContainers

set -e

cd /workspace/airflow

# Check idempotency - if already applied, exit successfully
if grep -q "workers.kubernetes.extraContainers .Values.workers.extraContainers" chart/files/pod-template-file.kubernetes-helm-yaml 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

# Apply the gold patch
git apply --whitespace=nowarn <<'PATCH'
diff --git a/chart/docs/using-additional-containers.rst b/chart/docs/using-additional-containers.rst
index 60ce810492655..958708f1dd2ef 100644
--- a/chart/docs/using-additional-containers.rst
+++ b/chart/docs/using-additional-containers.rst
@@ -22,7 +22,7 @@ Sidecar Containers
 ------------------

 If you want to deploy your own sidecar container, you can add it through the ``extraContainers`` parameter.
-You can define different containers for the scheduler, webserver, api server, worker, triggerer, dag processor, flower, create user job and migrate database job pods.
+You can define different containers for the scheduler, webserver/api-server, Kubernetes/Celery workers, triggerer, dag processor, flower, create user job and migrate database job pods.

 For example, sidecars that sync Dags from object storage:

@@ -34,15 +34,17 @@ For example, sidecars that sync Dags from object storage:
        - name: s3-sync
          image: my-company/s3-sync:latest
          imagePullPolicy: Always
+
    workers:
-     extraContainers:
-       - name: s3-sync
-         image: my-company/s3-sync:latest
-         imagePullPolicy: Always
+     kubernetes:
+       extraContainers:
+         - name: s3-sync
+           image: my-company/s3-sync:latest
+           imagePullPolicy: Always

 .. note::

-   If you use ``workers.extraContainers`` with ``KubernetesExecutor``, you are responsible for signaling
+   If you use ``workers.kubernetes.extraContainers`` (dedicated for ``KubernetesExecutor``), you are responsible for signaling
    sidecars to exit when the main container finishes so Airflow can continue the worker shutdown process.


diff --git a/chart/files/pod-template-file.kubernetes-helm-yaml b/chart/files/pod-template-file.kubernetes-helm-yaml
index 5aae2d8fc94ce..e9108745a82c3 100644
--- a/chart/files/pod-template-file.kubernetes-helm-yaml
+++ b/chart/files/pod-template-file.kubernetes-helm-yaml
@@ -213,8 +213,8 @@ spec:
         {{- include "custom_airflow_environment" . | indent 6 }}
         {{- include "standard_airflow_environment" . | indent 6 }}
     {{- end }}
-    {{- if .Values.workers.extraContainers }}
-      {{- tpl (toYaml .Values.workers.extraContainers) . | nindent 4 }}
+    {{- if or .Values.workers.kubernetes.extraContainers .Values.workers.extraContainers }}
+      {{- tpl (toYaml (.Values.workers.kubernetes.extraContainers | default .Values.workers.extraContainers)) . | nindent 4 }}
     {{- end }}
   {{- if or .Values.workers.kubernetes.priorityClassName .Values.workers.priorityClassName }}
   priorityClassName: {{ .Values.workers.kubernetes.priorityClassName | default .Values.workers.priorityClassName }}
diff --git a/chart/newsfragments/64739.significant.rst b/chart/newsfragments/64739.significant.rst
new file mode 100644
index 0000000000000..3ae49c41234e6
--- /dev/null
+++ b/chart/newsfragments/64739.significant.rst
@@ -0,0 +1 @@
+``workers.extraContainers`` field is now deprecated in favor of ``workers.celery.extraContainers`` and ``workers.kubernetes.extraContainers``. Please update your configuration accordingly.
diff --git a/chart/templates/NOTES.txt b/chart/templates/NOTES.txt
index 7728d1654f71b..840e55e43ed23 100644
--- a/chart/templates/NOTES.txt
+++ b/chart/templates/NOTES.txt
@@ -701,6 +701,14 @@ DEPRECATION WARNING:

 {{- end }}

+{{- if not (empty .Values.workers.extraContainers) }}
+
+ DEPRECATION WARNING:
+    `workers.extraContainers` has been renamed to `workers.celery.extraContainers`/`workers.kubernetes.extraContainers`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
 {{- if not (empty .Values.workers.runtimeClassName) }}

  DEPRECATION WARNING:
diff --git a/chart/values.schema.json b/chart/values.schema.json
index a67e56b35af86..9809be9468b43 100644
--- a/chart/values.schema.json
+++ b/chart/values.schema.json
@@ -2293,7 +2293,7 @@
                     "default": false
                 },
                 "extraContainers": {
-                    "description": "Launch additional containers into Airflow Celery workers and pods created with pod-template-file (templated). Note, if used with KubernetesExecutor, you are responsible for signaling sidecars to exit when the main container finishes so Airflow can continue the worker shutdown process!",
+                    "description": "Launch additional containers into Airflow Celery workers and pods created with pod-template-file (templated) (deprecated, use ``workers.celery.extraContainers`` and/or ``workers.kubernetes.extraContainers`` instead). Note, if used with KubernetesExecutor, you are responsible for signaling sidecars to exit when the main container finishes so Airflow can continue the worker shutdown process!",
                     "type": "array",
                     "default": [],
                     "items": {
@@ -3380,6 +3380,14 @@
                             ],
                             "default": null
                         },
+                        "extraContainers": {
+                            "description": "Launch additional containers into Airflow Celery worker (templated).",
+                            "type": "array",
+                            "default": [],
+                            "items": {
+                                "$ref": "#/definitions/io.k8s.api.core.v1.Container"
+                            }
+                        },
                         "extraPorts": {
                             "description": "Expose additional ports of Airflow Celery worker container.",
                             "type": "array",
@@ -3870,6 +3878,14 @@
                             ],
                             "default": null
                         },
+                        "extraContainers": {
+                            "description": "Launch additional containers into pods created with pod-template-file (templated). Note, you are responsible for signaling sidecars to exit when the main container finishes so Airflow can continue the worker shutdown process!",
+                            "type": "array",
+                            "default": [],
+                            "items": {
+                                "$ref": "#/definitions/io.k8s.api.core.v1.Container"
+                            }
+                        },
                         "nodeSelector": {
                             "description": "Select certain nodes for pods created with pod-template-file.",
                             "type": "object",
diff --git a/chart/values.yaml b/chart/values.yaml
index 651a6779aea59..f4b4499bac255 100644
--- a/chart/values.yaml
+++ b/chart/values.yaml
@@ -1042,6 +1042,10 @@ workers:

   # Launch additional containers into Airflow Celery worker
   # and pods created with pod-template-file (templated).
+  # (deprecated, use
+  #   `workers.celery.extraContainers` and/or
+  #   `workers.kubernetes.extraContainers`
+  # instead)
   # Note: If used with KubernetesExecutor, you are responsible for signaling sidecars to exit when the main
   # container finishes so Airflow can continue the worker shutdown process!
   extraContainers: []
@@ -1443,6 +1447,9 @@ workers:
     # This setting tells Kubernetes that its ok to evict when it wants to scale a node down
     safeToEvict: ~

+    # Launch additional containers into Airflow Celery worker (templated)
+    extraContainers: []
+
     # Expose additional ports of Airflow Celery workers. These can be used for additional metric collection.
     extraPorts: []

@@ -1605,6 +1612,11 @@ workers:
     # This setting tells Kubernetes that its ok to evict when it wants to scale a node down
     safeToEvict: ~

+    # Launch additional containers into pods created with pod-template-file (templated).
+    # Note: You are responsible for signaling sidecars to exit when the main
+    # container finishes so Airflow can continue the worker shutdown process!
+    extraContainers: []
+
     # Select certain nodes for pods created with pod-template-file
     nodeSelector: {}

PATCH

echo "Patch applied successfully"
