#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'variable "namespace"' examples/terraform/envoy-ratelimiter/variables.tf 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/examples/terraform/envoy-ratelimiter/README.md b/examples/terraform/envoy-ratelimiter/README.md
index 47d66832487d..bb974873591d 100644
--- a/examples/terraform/envoy-ratelimiter/README.md
+++ b/examples/terraform/envoy-ratelimiter/README.md
@@ -25,10 +25,13 @@ Apache Beam pipelines often process data at massive scale, which can easily over

 This Terraform module deploys a **centralized Rate Limit Service (RLS)** using Envoy. Beam workers can query this service to coordinate global quotas across thousands of distributed workers, ensuring you stay within safe API limits without hitting `429 Too Many Requests` errors.

-Example Beam Pipelines using it:
+Example Beam Python Pipelines using it:
 *   [Simple DoFn RateLimiter](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/rate_limiter_simple.py)
 *   [Vertex AI RateLimiter](https://github.com/apache/beam/blob/master/sdks/python/apache_beam/examples/inference/rate_limiter_vertex_ai.py)

+Example Beam Java Pipelines using it:
+*   [Simple DoFn RateLimiter](https://github.com/apache/beam/blob/master/examples/java/src/main/java/org/apache/beam/examples/RateLimiterSimple.java)
+
 ## Architectures:
 - **GKE Autopilot**: Fully managed, serverless Kubernetes environment.
   - **Private Cluster**: Nodes have internal IPs only.
@@ -78,6 +81,8 @@ region                = "us-central1"               # GCP Region for deployment
 cluster_name          = "ratelimit-cluster"         # Name of the GKE cluster
 deletion_protection   = true                        # Prevent accidental cluster deletion (set "true" for prod)
 control_plane_cidr    = "172.16.0.0/28"             # CIDR for GKE control plane (must not overlap with subnet)
+namespace             = "envoy-ratelimiter"         # Kubernetes namespace for deployment
+enable_metrics        = false                       # Deploy statsd-exporter sidecar
 ratelimit_replicas    = 1                           # Initial number of Rate Limit pods
 min_replicas          = 1                           # Minimum HPA replicas
 max_replicas          = 5                           # Maximum HPA replicas
@@ -163,6 +168,8 @@ terraform destroy
 |region                 |GCP Region for deployment                            |us-central1                      |
 |control_plane_cidr     |CIDR block for GKE control plane                     |172.16.0.0/28                    |
 |cluster_name           |Name of the GKE cluster                              |ratelimit-cluster                |
+|namespace              |Kubernetes namespace to deploy resources into        |envoy-ratelimiter                |
+|enable_metrics         |Deploy statsd-exporter sidecar                       |false                            |
 |deletion_protection    |Prevent accidental cluster deletion                  |false                            |
 |ratelimit_replicas     |Initial number of Rate Limit pods                    |1                                |
 |min_replicas           |Minimum HPA replicas                                 |1                                |
diff --git a/examples/terraform/envoy-ratelimiter/gke.tf b/examples/terraform/envoy-ratelimiter/gke.tf
index b0fadbf5f87b..d044a448febb 100644
--- a/examples/terraform/envoy-ratelimiter/gke.tf
+++ b/examples/terraform/envoy-ratelimiter/gke.tf
@@ -31,8 +31,8 @@ resource "google_container_cluster" "primary" {

   # Private Cluster Configuration
   private_cluster_config {
-    enable_private_nodes    = true            # Nodes have internal IPs only
-    enable_private_endpoint = false           # Master is accessible via Public IP (required for Terraform from outside VPC)
+    enable_private_nodes    = true  # Nodes have internal IPs only
+    enable_private_endpoint = false # Master is accessible via Public IP (required for Terraform from outside VPC)
     master_ipv4_cidr_block  = var.control_plane_cidr
   }
 }
\ No newline at end of file
diff --git a/examples/terraform/envoy-ratelimiter/ratelimit.tf b/examples/terraform/envoy-ratelimiter/ratelimit.tf
index 2f0004043c1f..c95e48927cb7 100644
--- a/examples/terraform/envoy-ratelimiter/ratelimit.tf
+++ b/examples/terraform/envoy-ratelimiter/ratelimit.tf
@@ -25,23 +25,35 @@ resource "time_sleep" "wait_for_cluster" {
   depends_on = [google_container_cluster.primary]
 }

+# Namespace
+resource "kubernetes_namespace" "ratelimit_namespace" {
+  metadata {
+    name = var.namespace
+  }
+
+  depends_on = [time_sleep.wait_for_cluster]
+}
+
+
 # ConfigMap
 resource "kubernetes_config_map" "ratelimit_config" {
   metadata {
-    name = "ratelimit-config"
+    name      = "ratelimit-config"
+    namespace = var.namespace
   }

   data = {
     "config.yaml" = var.ratelimit_config_yaml
   }

-  depends_on = [time_sleep.wait_for_cluster]
+  depends_on = [kubernetes_namespace.ratelimit_namespace]
 }

 # Redis Deployment
 resource "kubernetes_deployment" "redis" {
   metadata {
-    name = "redis"
+    name      = "redis"
+    namespace = var.namespace
     labels = {
       app = "redis"
     }
@@ -81,13 +93,14 @@ resource "kubernetes_deployment" "redis" {
     }
   }

-  depends_on = [time_sleep.wait_for_cluster]
+  depends_on = [kubernetes_namespace.ratelimit_namespace]
 }

 # Redis Service
 resource "kubernetes_service" "redis" {
   metadata {
-    name = "redis"
+    name      = "redis"
+    namespace = var.namespace
   }

   spec {
@@ -101,13 +114,14 @@ resource "kubernetes_service" "redis" {
     }
   }

-  depends_on = [time_sleep.wait_for_cluster]
+  depends_on = [kubernetes_namespace.ratelimit_namespace]
 }

 # Rate Limit Deployment
 resource "kubernetes_deployment" "ratelimit" {
   metadata {
-    name = "ratelimit"
+    name      = "ratelimit"
+    namespace = var.namespace
     labels = {
       app = "ratelimit"
     }
@@ -131,8 +145,8 @@ resource "kubernetes_deployment" "ratelimit" {

       spec {
         container {
-          name  = "ratelimit"
-          image = var.ratelimit_image
+          name    = "ratelimit"
+          image   = var.ratelimit_image
           command = ["/bin/ratelimit"]

           port {
@@ -147,7 +161,15 @@ resource "kubernetes_deployment" "ratelimit" {

           env {
             name  = "USE_STATSD"
-            value = "true"
+            value = var.enable_metrics ? "true" : "false"
+          }
+          env {
+            name  = "DISABLE_STATS"
+            value = var.enable_metrics ? "false" : "true"
+          }
+          env {
+            name  = "LOG_FORMAT"
+            value = "json"
           }
           env {
             name  = "LOG_LEVEL"
@@ -209,28 +231,38 @@ resource "kubernetes_deployment" "ratelimit" {
           }
         }

-        container {
-          name  = "statsd-exporter"
-          image = var.statsd_exporter_image
-
-          port {
-            name           = "metrics"
-            container_port = 9102
-          }
-          port {
-            name           = "statsd-udp"
-            container_port = 9125
-            protocol       = "UDP"
-          }
-          # statsd-exporter does not use much resources, so setting resources to the minimum
-          resources {
-            requests = {
-              cpu    = "50m"
-              memory = "64Mi"
+        dynamic "container" {
+          for_each = var.enable_metrics ? [1] : []
+          content {
+            name  = "statsd-exporter"
+            image = var.statsd_exporter_image
+            args  = ["--log.format=json"]
+
+            dynamic "port" {
+              for_each = var.enable_metrics ? [1] : []
+              content {
+                name           = "metrics"
+                container_port = 9102
+              }
+            }
+            dynamic "port" {
+              for_each = var.enable_metrics ? [1] : []
+              content {
+                name           = "statsd-udp"
+                container_port = 9125
+                protocol       = "UDP"
+              }
             }
-            limits = {
-              cpu    = "100m"
-              memory = "128Mi"
+            # statsd-exporter does not use much resources, so setting resources to the minimum
+            resources {
+              requests = {
+                cpu    = "50m"
+                memory = "64Mi"
+              }
+              limits = {
+                cpu    = "100m"
+                memory = "128Mi"
+              }
             }
           }
         }
@@ -246,7 +278,7 @@ resource "kubernetes_deployment" "ratelimit" {
   }

   depends_on = [
-    time_sleep.wait_for_cluster,
+    kubernetes_namespace.ratelimit_namespace,
     kubernetes_config_map.ratelimit_config,
     kubernetes_service.redis
   ]
@@ -258,7 +290,8 @@ resource "kubernetes_deployment" "ratelimit" {

 resource "kubernetes_horizontal_pod_autoscaler_v2" "ratelimit" {
   metadata {
-    name = "ratelimit-hpa"
+    name      = "ratelimit-hpa"
+    namespace = var.namespace
   }

   spec {
@@ -274,7 +307,7 @@ resource "kubernetes_horizontal_pod_autoscaler_v2" "ratelimit" {
     metric {
       type = "Resource"
       resource {
-        name  = "cpu"
+        name = "cpu"
         target {
           type                = "Utilization"
           average_utilization = var.hpa_cpu_target_percentage
@@ -285,7 +318,7 @@ resource "kubernetes_horizontal_pod_autoscaler_v2" "ratelimit" {
     metric {
       type = "Resource"
       resource {
-        name  = "memory"
+        name = "memory"
         target {
           type                = "Utilization"
           average_utilization = var.hpa_memory_target_percentage
@@ -294,13 +327,14 @@ resource "kubernetes_horizontal_pod_autoscaler_v2" "ratelimit" {
     }
   }

-  depends_on = [time_sleep.wait_for_cluster]
+  depends_on = [kubernetes_namespace.ratelimit_namespace]
 }

 # Rate Limit Internal Service
 resource "kubernetes_service" "ratelimit" {
   metadata {
-    name = "ratelimit"
+    name      = "ratelimit"
+    namespace = var.namespace
   }

   spec {
@@ -323,20 +357,24 @@ resource "kubernetes_service" "ratelimit" {
       port        = 6070
       target_port = 6070
     }
-    port {
-      name        = "metrics"
-      port        = 9102
-      target_port = 9102
+    dynamic "port" {
+      for_each = var.enable_metrics ? [1] : []
+      content {
+        name        = "metrics"
+        port        = 9102
+        target_port = 9102
+      }
     }
   }

-  depends_on = [time_sleep.wait_for_cluster]
+  depends_on = [kubernetes_namespace.ratelimit_namespace]
 }

 # Rate Limit External Service (LoadBalancer)
 resource "kubernetes_service" "ratelimit_external" {
   metadata {
-    name = "ratelimit-external"
+    name      = "ratelimit-external"
+    namespace = var.namespace
     annotations = {
       "networking.gke.io/load-balancer-type" = "Internal"
     }
@@ -360,12 +398,15 @@ resource "kubernetes_service" "ratelimit_external" {
       port        = 6070
       target_port = 6070
     }
-    port {
-      name        = "metrics"
-      port        = 9102
-      target_port = 9102
+    dynamic "port" {
+      for_each = var.enable_metrics ? [1] : []
+      content {
+        name        = "metrics"
+        port        = 9102
+        target_port = 9102
+      }
     }
   }

-  depends_on = [time_sleep.wait_for_cluster]
+  depends_on = [kubernetes_namespace.ratelimit_namespace]
 }
diff --git a/examples/terraform/envoy-ratelimiter/variables.tf b/examples/terraform/envoy-ratelimiter/variables.tf
index 714638934c9f..b7a771148215 100644
--- a/examples/terraform/envoy-ratelimiter/variables.tf
+++ b/examples/terraform/envoy-ratelimiter/variables.tf
@@ -107,7 +107,7 @@ variable "hpa_memory_target_percentage" {
 variable "ratelimit_image" {
   description = "Docker image for Envoy Rate Limit service"
   type        = string
-  default     = "envoyproxy/ratelimit:e9ce92cc"
+  default     = "envoyproxy/ratelimit:e9ce92cc"
 }

 variable "redis_image" {
@@ -125,7 +125,7 @@ variable "statsd_exporter_image" {
 variable "ratelimit_log_level" {
   description = "Log level for ratelimit service"
   type        = string
-  default     = "debug"
+  default     = "info"
 }

 variable "ratelimit_grpc_max_connection_age" {
@@ -175,4 +175,15 @@ variable "ratelimit_resources" {
       memory = "512Mi"
     }
   }
-}
\ No newline at end of file
+}
+variable "namespace" {
+  description = "The Kubernetes namespace to deploy resources into"
+  type        = string
+  default     = "envoy-ratelimiter"
+}
+
+variable "enable_metrics" {
+  description = "Whether to deploy the statsd-exporter sidecar for Prometheus metrics"
+  type        = bool
+  default     = false
+}

PATCH

echo "Patch applied successfully."
