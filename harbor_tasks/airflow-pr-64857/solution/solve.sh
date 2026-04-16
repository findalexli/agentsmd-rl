#!/bin/bash
# Gold solution for apache/airflow#64857
# Adds workers.celery.waitForMigrations config section to Helm chart

set -euo pipefail

cd /workspace/airflow

# Idempotency check - skip if already applied
if grep -q "workers.celery.waitForMigrations" chart/values.schema.json 2>/dev/null; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
patch -p1 <<'PATCH'
diff --git a/chart/newsfragments/62054.significant.rst b/chart/newsfragments/62054.significant.rst
new file mode 100644
index 0000000000000..7b564a363f48d
--- /dev/null
+++ b/chart/newsfragments/62054.significant.rst
@@ -0,0 +1 @@
+``workers.waitForMigrations`` section is now deprecated in favor of ``workers.celery.waitForMigrations``. Please update your configuration accordingly.
diff --git a/chart/templates/NOTES.txt b/chart/templates/NOTES.txt
index f752f3f5ef0cb..104832aef2c96 100644
--- a/chart/templates/NOTES.txt
+++ b/chart/templates/NOTES.txt
@@ -685,6 +685,30 @@ DEPRECATION WARNING:

 {{- end }}

+{{- if not .Values.workers.waitForMigrations.enabled }}
+
+ DEPRECATION WARNING:
+    `workers.waitForMigrations.enabled` has been renamed to `workers.celery.waitForMigrations.enabled`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
+{{- if not (empty .Values.workers.waitForMigrations.env) }}
+
+ DEPRECATION WARNING:
+    `workers.waitForMigrations.env` has been renamed to `workers.celery.waitForMigrations.env`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
+{{- if not (empty .Values.workers.waitForMigrations.securityContexts.container) }}
+
+ DEPRECATION WARNING:
+    `workers.waitForMigrations.securityContexts.container` has been renamed to `workers.celery.waitForMigrations.securityContexts.container`.
+    Please change your values as support for the old name will be dropped in a future release.
+
+{{- end }}
+
 {{- if not (empty .Values.webserver.defaultUser) }}

  DEPRECATION WARNING:
diff --git a/chart/values.schema.json b/chart/values.schema.json
index 56ed23ea74ae3..df088e1bb93e4 100644
--- a/chart/values.schema.json
+++ b/chart/values.schema.json
@@ -2520,17 +2520,17 @@
                     }
                 },
                 "waitForMigrations": {
-                    "description": "Configuration of wait-for-airflow-migration init container for Airflow Celery workers.",
+                    "description": "Configuration of wait-for-airflow-migration init container for Airflow Celery workers (deprecated, use ``workers.celery.waitForMigrations`` instead).",
                     "type": "object",
                     "additionalProperties": false,
                     "properties": {
                         "enabled": {
-                            "description": "Enable wait-for-airflow-migrations init container.",
+                            "description": "Enable wait-for-airflow-migrations init container (deprecated, use ``workers.celery.waitForMigrations.enabled`` instead).",
                             "type": "boolean",
                             "default": true
                         },
                         "env": {
-                            "description": "Add additional env vars to wait-for-airflow-migrations init container.",
+                            "description": "Add additional env vars to wait-for-airflow-migrations init container (deprecated, use ``workers.celery.waitForMigrations.env`` instead).",
                             "type": "array",
                             "default": [],
                             "items": {
@@ -2551,12 +2551,12 @@
                             }
                         },
                         "securityContexts": {
-                            "description": "Security context definition for the wait-for-airflow-migrations container. If not set, the values from global `securityContexts` will be used.",
+                            "description": "Security context definition for the wait-for-airflow-migrations container (deprecated, use ``workers.celery.waitForMigrations.securityContexts`` instead). If not set, the values from global `securityContexts` will be used.",
                             "type": "object",
                             "x-docsSection": "Kubernetes",
                             "properties": {
                                 "container": {
-                                    "description": "Container security context definition for the wait-for-airflow-migrations container.",
+                                    "description": "Container security context definition for the wait-for-airflow-migrations container (deprecated, use ``workers.celery.waitForMigrations.securityContexts.container`` instead).",
                                     "type": "object",
                                     "$ref": "#/definitions/io.k8s.api.core.v1.SecurityContext",
                                     "default": {},
@@ -3348,6 +3348,66 @@
                                 }
                             ]
                         },
+                        "waitForMigrations": {
+                            "description": "Configuration of wait-for-airflow-migration init container for Airflow Celery workers.",
+                            "type": "object",
+                            "additionalProperties": false,
+                            "properties": {
+                                "enabled": {
+                                    "description": "Whether to create init container to wait for db migrations.",
+                                    "type": [
+                                        "boolean",
+                                        "null"
+                                    ],
+                                    "default": null
+                                },
+                                "env": {
+                                    "description": "Add additional env vars to wait-for-airflow-migrations init container.",
+                                    "type": "array",
+                                    "default": [],
+                                    "items": {
+                                        "type": "object",
+                                        "properties": {
+                                            "name": {
+                                                "type": "string"
+                                            },
+                                            "value": {
+                                                "type": "string"
+                                            }
+                                        },
+                                        "required": [
+                                            "name",
+                                            "value"
+                                        ],
+                                        "additionalProperties": false
+                                    }
+                                },
+                                "securityContexts": {
+                                    "description": "Security context definition for the wait-for-airflow-migrations container. If not set, the values from ``workers.waitForMigrations.securityContexts`` will be used.",
+                                    "type": "object",
+                                    "x-docsSection": "Kubernetes",
+                                    "properties": {
+                                        "container": {
+                                            "description": "Container security context definition for the wait-for-airflow-migrations container.",
+                                            "type": "object",
+                                            "$ref": "#/definitions/io.k8s.api.core.v1.SecurityContext",
+                                            "default": {},
+                                            "x-docsSection": "Kubernetes",
+                                            "examples": [
+                                                {
+                                                    "allowPrivilegeEscalation": false,
+                                                    "capabilities": {
+                                                        "drop": [
+                                                            "ALL"
+                                                        ]
+                                                    }
+                                                }
+                                            ]
+                                        }
+                                    }
+                                }
+                            }
+                        },
                         "volumeClaimTemplates": {
                             "description": "Specify additional volume claim template for Airflow Celery workers.",
                             "type": "array",
diff --git a/chart/values.yaml b/chart/values.yaml
index 7167588d97a1b..e88893aaea086 100644
--- a/chart/values.yaml
+++ b/chart/values.yaml
@@ -1136,14 +1136,19 @@ workers:
     env: []

   # Configuration of wait-for-airflow-migration init container for Airflow Celery workers
+  # (deprecated, use `workers.celery.waitForMigrations` instead)
   waitForMigrations:
     # Whether to create init container to wait for db migrations
+    # (deprecated, use `workers.celery.waitForMigrations.enabled` instead)
     enabled: true

+    # (deprecated, use `workers.celery.waitForMigrations.env` instead)
     env: []

     # Detailed default security context for wait-for-airflow-migrations container
+    # (deprecated, use `workers.celery.waitForMigrations.securityContexts` instead)
     securityContexts:
+      # (deprecated, use `workers.celery.waitForMigrations.securityContexts.container` instead)
       container: {}

   # Additional env variable configuration for Airflow Celery workers and pods created with pod-template-file
@@ -1404,6 +1409,17 @@ workers:
     #   hostnames:
     #   - "test.hostname.two"

+    # Configuration of wait-for-airflow-migration init container for Airflow Celery workers
+    waitForMigrations:
+      # Whether to create init container to wait for db migrations
+      enabled: ~
+
+      env: []
+
+      # Detailed default security context for wait-for-airflow-migrations container
+      securityContexts:
+        container: {}
+
     # Additional volume claim templates for Airflow Celery workers.
     # Requires mounting of specified volumes under extraVolumeMounts.
     volumeClaimTemplates: []
diff --git a/helm-tests/tests/helm_tests/airflow_core/test_worker.py b/helm-tests/tests/helm_tests/airflow_core/test_worker.py
index 03188cda33074..0032e50e06ca5 100644
--- a/helm-tests/tests/helm_tests/airflow_core/test_worker.py
+++ b/helm-tests/tests/helm_tests/airflow_core/test_worker.py
@@ -203,13 +203,16 @@ def test_should_template_extra_containers(self):
             "name": "release-name-test-container"
         }

-    def test_disable_wait_for_migration(self):
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {"waitForMigrations": {"enabled": False}},
+            {"celery": {"waitForMigrations": {"enabled": False}}},
+        ],
+    )
+    def test_disable_wait_for_migration(self, workers_values):
         docs = render_chart(
-            values={
-                "workers": {
-                    "waitForMigrations": {"enabled": False},
-                },
-            },
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-deployment.yaml"],
         )
         actual = jmespath.search(
@@ -362,13 +365,20 @@ def test_should_add_extraEnvs(self):
             "valueFrom": {"configMapKeyRef": {"name": "my-config-map", "key": "my-key"}},
         } in jmespath.search("spec.template.spec.containers[0].env", docs[0])

-    def test_should_add_extraEnvs_to_wait_for_migration_container(self):
-        docs = render_chart(
-            values={
-                "workers": {
-                    "waitForMigrations": {"env": [{"name": "TEST_ENV_1", "value": "test_env_1"}]},
-                },
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {"waitForMigrations": {"env": [{"name": "TEST_ENV_1", "value": "test_env_1"}]}},
+            {"celery": {"waitForMigrations": {"env": [{"name": "TEST_ENV_1", "value": "test_env_1"}]}}},
+            {
+                "waitForMigrations": {"env": [{"name": "TEST", "value": "test"}]},
+                "celery": {"waitForMigrations": {"env": [{"name": "TEST_ENV_1", "value": "test_env_1"}]}},
             },
+        ],
+    )
+    def test_should_add_extraEnvs_to_wait_for_migration_container(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-deployment.yaml"],
         )

diff --git a/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py b/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
index b706c61153bfa..1d71fe813caa9 100644
--- a/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
+++ b/helm-tests/tests/helm_tests/airflow_core/test_worker_sets.py
@@ -2866,16 +2866,27 @@ def test_overwrite_labels(self, workers_values):
         assert labels["test"] == "echo"
         assert labels.get("echo") is None

-    def test_overwrite_wait_for_migration_disable(self):
-        docs = render_chart(
-            values={
-                "workers": {
-                    "celery": {
-                        "enableDefault": False,
-                        "sets": [{"name": "set1", "waitForMigrations": {"enabled": False}}],
-                    },
-                },
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "celery": {
+                    "enableDefault": False,
+                    "sets": [{"name": "set1", "waitForMigrations": {"enabled": False}}],
+                }
             },
+            {
+                "celery": {
+                    "waitForMigrations": {"enabled": True},
+                    "enableDefault": False,
+                    "sets": [{"name": "set1", "waitForMigrations": {"enabled": False}}],
+                }
+            },
+        ],
+    )
+    def test_overwrite_wait_for_migration_disable(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-deployment.yaml"],
         )
         assert (
@@ -2885,17 +2896,28 @@ def test_overwrite_wait_for_migration_disable(self):
             is None
         )

-    def test_overwrite_wait_for_migration_enable(self):
-        docs = render_chart(
-            values={
-                "workers": {
-                    "waitForMigrations": {"enabled": False},
-                    "celery": {
-                        "enableDefault": False,
-                        "sets": [{"name": "set1", "waitForMigrations": {"enabled": True}}],
-                    },
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {
+                "waitForMigrations": {"enabled": False},
+                "celery": {
+                    "enableDefault": False,
+                    "sets": [{"name": "set1", "waitForMigrations": {"enabled": True}}],
                 },
             },
+            {
+                "celery": {
+                    "waitForMigrations": {"enabled": False},
+                    "enableDefault": False,
+                    "sets": [{"name": "set1", "waitForMigrations": {"enabled": True}}],
+                }
+            },
+        ],
+    )
+    def test_overwrite_wait_for_migration_enable(self, workers_values):
+        docs = render_chart(
+            values={"workers": workers_values},
             show_only=["templates/workers/worker-deployment.yaml"],
         )
         assert (
@@ -2924,6 +2946,18 @@ def test_overwrite_wait_for_migration_enable(self, workers_values):
                     ],
                 },
             },
+            {
+                "celery": {
+                    "waitForMigrations": {"env": [{"name": "TEST", "value": "test"}]},
+                    "enableDefault": False,
+                    "sets": [
+                        {
+                            "name": "set1",
+                            "waitForMigrations": {"env": [{"name": "TEST_ENV_1", "value": "test_env_1"}]},
+                        }
+                    ],
+                },
+            },
         ],
     )
     def test_overwrite_wait_for_migration_env(self, workers_values):
@@ -2960,6 +2994,20 @@ def test_overwrite_wait_for_migration_env(self, workers_values):
                     ],
                 },
             },
+            {
+                "celery": {
+                    "waitForMigrations": {
+                        "securityContexts": {"container": {"allowPrivilegeEscalation": False}}
+                    },
+                    "enableDefault": False,
+                    "sets": [
+                        {
+                            "name": "set1",
+                            "waitForMigrations": {"securityContexts": {"container": {"runAsUser": 10}}},
+                        }
+                    ],
+                },
+            },
         ],
     )
     def test_overwrite_wait_for_migration_security_context_container(self, workers_values):
diff --git a/helm-tests/tests/helm_tests/security/test_security_context.py b/helm-tests/tests/helm_tests/security/test_security_context.py
index dd9da798f5630..a5e9d70816b5f 100644
--- a/helm-tests/tests/helm_tests/security/test_security_context.py
+++ b/helm-tests/tests/helm_tests/security/test_security_context.py
@@ -671,7 +671,28 @@ def test_worker_kerberos_init_container_security_contexts(self, workers_values):
         ) == {"runAsUser": 2000}

     # Test securityContexts for the wait-for-migrations init containers
-    def test_wait_for_migrations_init_container_setting_airflow_2(self):
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {"waitForMigrations": {"securityContexts": {"container": {"allowPrivilegeEscalation": False}}}},
+            {
+                "celery": {
+                    "waitForMigrations": {
+                        "securityContexts": {"container": {"allowPrivilegeEscalation": False}}
+                    }
+                }
+            },
+            {
+                "waitForMigrations": {"securityContexts": {"container": {"runAsUser": 0}}},
+                "celery": {
+                    "waitForMigrations": {
+                        "securityContexts": {"container": {"allowPrivilegeEscalation": False}}
+                    }
+                },
+            },
+        ],
+    )
+    def test_wait_for_migrations_init_container_setting_airflow_2(self, workers_values):
         ctx_value = {"allowPrivilegeEscalation": False}
         spec = {
             "waitForMigrations": {
@@ -684,7 +705,7 @@ def test_wait_for_migrations_init_container_setting_airflow_2(self):
                 "scheduler": spec,
                 "webserver": spec,
                 "triggerer": spec,
-                "workers": {"waitForMigrations": {"securityContexts": {"container": ctx_value}}},
+                "workers": workers_values,
                 "airflowVersion": "2.11.0",
             },
             show_only=[
@@ -698,7 +719,28 @@ def test_wait_for_migrations_init_container_setting_airflow_2(self):
         for doc in docs:
             assert ctx_value == jmespath.search("spec.template.spec.initContainers[0].securityContext", doc)

-    def test_wait_for_migrations_init_container_setting(self):
+    @pytest.mark.parametrize(
+        "workers_values",
+        [
+            {"waitForMigrations": {"securityContexts": {"container": {"allowPrivilegeEscalation": False}}}},
+            {
+                "celery": {
+                    "waitForMigrations": {
+                        "securityContexts": {"container": {"allowPrivilegeEscalation": False}}
+                    }
+                }
+            },
+            {
+                "waitForMigrations": {"securityContexts": {"container": {"runAsUser": 0}}},
+                "celery": {
+                    "waitForMigrations": {
+                        "securityContexts": {"container": {"allowPrivilegeEscalation": False}}
+                    }
+                },
+            },
+        ],
+    )
+    def test_wait_for_migrations_init_container_setting(self, workers_values):
         ctx_value = {"allowPrivilegeEscalation": False}
         spec = {
             "waitForMigrations": {
@@ -712,7 +754,7 @@ def test_wait_for_migrations_init_container_setting(self):
                 "apiServer": spec,
                 "triggerer": spec,
                 "dagProcessor": spec,
-                "workers": {"waitForMigrations": {"securityContexts": {"container": ctx_value}}},
+                "workers": workers_values,
             },
             show_only=[
                 "templates/scheduler/scheduler-deployment.yaml",
PATCH

echo "Patch applied successfully"
