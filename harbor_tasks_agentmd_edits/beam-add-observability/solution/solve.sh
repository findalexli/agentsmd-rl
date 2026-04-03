#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'USE_PROMETHEUS' examples/terraform/envoy-ratelimiter/ratelimit.tf 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/examples/terraform/envoy-ratelimiter/README.md b/examples/terraform/envoy-ratelimiter/README.md
index bb974873591d..b1275fbf2009 100644
--- a/examples/terraform/envoy-ratelimiter/README.md
+++ b/examples/terraform/envoy-ratelimiter/README.md
@@ -38,7 +38,7 @@ Example Beam Java Pipelines using it:
   - **Cloud NAT (Prerequisite)**: Allows private nodes to pull Docker images.
 - **Envoy Rate Limit Service**: A stateless Go/gRPC service that handles rate limit logic.
 - **Redis**: Stores the rate limit counters.
-- **StatsD Exporter**: Sidecar container that converts StatsD metrics to Prometheus format, exposed on port `9102`.
+- **Prometheus Metrics**: Exposes Prometheus metrics on port `9090`. These metrics are exported to Google Cloud Monitoring.
 - **Internal Load Balancer**: A Google Cloud TCP Load Balancer exposing the Rate Limit service internally within the VPC.

 ## Prerequisites:
@@ -82,7 +82,7 @@ cluster_name          = "ratelimit-cluster"         # Name of the GKE cluster
 deletion_protection   = true                        # Prevent accidental cluster deletion (set "true" for prod)
 control_plane_cidr    = "172.16.0.0/28"             # CIDR for GKE control plane (must not overlap with subnet)
 namespace             = "envoy-ratelimiter"         # Kubernetes namespace for deployment
-enable_metrics        = false                       # Deploy statsd-exporter sidecar
+enable_metrics        = true                        # Enable metrics export to Google Cloud Monitoring
 ratelimit_replicas    = 1                           # Initial number of Rate Limit pods
 min_replicas          = 1                           # Minimum HPA replicas
 max_replicas          = 5                           # Maximum HPA replicas
@@ -110,25 +110,34 @@ EOF
 ```

 # Deploy Envoy Rate Limiter:
-1. Initialize Terraform to download providers and modules:
+
+1. **Deploy Script (Recommended)**:
+Run the helper script to handle the deployment process automatically:
 ```bash
-terraform init
+./deploy.sh
 ```
+The script will provide the ip address of the load balancer once the deployment is complete.

-2. Plan and apply the changes:
+2. **Deploy (Manual Alternative)**:
+If you prefer running Terraform manually, you can use the following commands:
 ```bash
-terraform plan -out=tfplan
-terraform apply tfplan
+# Step 1: Initialize Terraform
+terraform init
+
+# Step 2: Create Cluster
+terraform apply -target=time_sleep.wait_for_cluster
+
+# Step 3: Create Resources
+terraform apply
 ```

-3. Connect to the service:
 After deployment, get the **Internal** IP address:
 ```bash
 terraform output load_balancer_ip
 ```
 The service is accessible **only from within the VPC** (e.g., via Dataflow workers or GCE instances in the same network) at `<INTERNAL_IP>:8081`.

-4. **Test with Dataflow Workflow**:
+3. **Test with Dataflow Workflow**:
    Verify connectivity and rate limiting logic by running the example Dataflow pipeline.

    ```bash
@@ -150,11 +159,40 @@ The service is accessible **only from within the VPC** (e.g., via Dataflow worke
    ```


+# Observability & Metrics:
+This module supports exporting native Prometheus metrics to **Google Cloud Monitoring**.
+
+ `enable_metrics` is set to `true` by default.
+
+### Sample Metrics
+| Metric Name | Description |
+| :--- | :--- |
+| `ratelimit_service_rate_limit_total_hits` | Total rate limit requests received. |
+| `ratelimit_service_rate_limit_over_limit` | Requests that exceeded the limit (HTTP 429). |
+| `ratelimit_service_rate_limit_near_limit` | Requests that are approaching the limit. |
+| `ratelimit_service_call_should_rate_limit` | Total valid gRPC calls to the service. |
+
+*Note: You will also see many other Go runtime metrics (`go_*`) and Redis client metrics (`redis_*`)
+
+### Viewing in Google Cloud Console
+1. Go to **Monitoring** > **Metrics Explorer**.
+2. Click **Select a metric**.
+3. Search for `ratelimit` and select **Prometheus Target** > **ratelimit**.
+4. Select a metric (e.g., `ratelimit_service_rate_limit_over_limit`) and click **Apply**.
+5. Use **Filters** to drill down by `domain`, `key`, and `value` (e.g., `key=database`, `value=users`).
+
 # Clean up resources:
 To destroy the cluster and all created resources:
+
+```bash
+./deploy.sh destroy
+```
+
+Alternatively:
 ```bash
 terraform destroy
 ```
+
 *Note: If `deletion_protection` was enabled, you must set it to `false` in `terraform.tfvars` before destroying.*

 # Variables description:
@@ -169,7 +207,7 @@ terraform destroy
 |control_plane_cidr     |CIDR block for GKE control plane                     |172.16.0.0/28                    |
 |cluster_name           |Name of the GKE cluster                              |ratelimit-cluster                |
 |namespace              |Kubernetes namespace to deploy resources into        |envoy-ratelimiter                |
-|enable_metrics         |Deploy statsd-exporter sidecar                       |false                            |
+|enable_metrics         |Enable metrics export to Google Cloud Monitoring     |true                             |
 |deletion_protection    |Prevent accidental cluster deletion                  |false                            |
 |ratelimit_replicas     |Initial number of Rate Limit pods                    |1                                |
 |min_replicas           |Minimum HPA replicas                                 |1                                |
diff --git a/examples/terraform/envoy-ratelimiter/deploy.sh b/examples/terraform/envoy-ratelimiter/deploy.sh
new file mode 100755
index 000000000000..2ac0e081f7e5
--- /dev/null
+++ b/examples/terraform/envoy-ratelimiter/deploy.sh
@@ -0,0 +1,66 @@
+#!/bin/bash
+#
+# Licensed to the Apache Software Foundation (ASF) under one or more
+# contributor license agreements.  See the NOTICE file distributed with
+# this work for additional information regarding copyright ownership.
+# The ASF licenses this file to You under the Apache License, Version 2.0
+# (the "License"); you may not use this file except in compliance with
+# the License.  You may obtain a copy of the License at
+#
+#    http://www.apache.org/licenses/LICENSE-2.0
+#
+# Unless required by applicable law or agreed to in writing, software
+# distributed under the License is distributed on an "AS IS" BASIS,
+# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
+# See the License for the specific language governing permissions and
+# limitations under the License.
+#
+
+# This script deploys the Envoy Rate Limiter on GKE.
+
+set -e
+
+COMMAND=${1:-"apply"}
+
+# 1. Initialize Terraform
+if [ ! -d ".terraform" ]; then
+    echo "Initializing Terraform..."
+    terraform init
+else
+    # Verify terraform initialization is valid, or re-initialize
+    terraform init -upgrade=false >/dev/null 2>&1 || terraform init
+fi
+
+if [ "$COMMAND" = "destroy" ]; then
+    echo "Destroying Envoy Rate Limiter Resources..."
+    terraform destroy -auto-approve
+    exit $?
+fi
+
+if [ "$COMMAND" = "apply" ]; then
+    echo "Deploying Envoy Rate Limiter..."
+
+    echo "--------------------------------------------------"
+    echo "Creating/Updating GKE Cluster..."
+    echo "--------------------------------------------------"
+    # Deploy the cluster and wait for it to be ready.
+    terraform apply -target=time_sleep.wait_for_cluster -auto-approve
+
+    echo ""
+    echo "--------------------------------------------------"
+    echo "Deploying Application Resources..."
+    echo "--------------------------------------------------"
+    # Deploy the rest of the resources
+    terraform apply -auto-approve
+
+    echo ""
+    echo "Deployment Complete!"
+    echo "Cluster Name: $(terraform output -raw cluster_name)"
+    echo "Load Balancer IP: $(terraform output -raw load_balancer_ip)"
+    exit 0
+fi
+
+echo "Usage:"
+echo "  ./deploy.sh [apply]    # Initialize and deploy resources (Default)"
+echo "  ./deploy.sh destroy    # Destroy resources"
+exit 1
diff --git a/examples/terraform/envoy-ratelimiter/prerequisites.tf b/examples/terraform/envoy-ratelimiter/prerequisites.tf
index 41151fae91cc..44f321457a27 100644
--- a/examples/terraform/envoy-ratelimiter/prerequisites.tf
+++ b/examples/terraform/envoy-ratelimiter/prerequisites.tf
@@ -21,6 +21,7 @@ resource "google_project_service" "required" {
     "container",
     "iam",
     "compute",
+    "monitoring",
   ])

   service            = "${each.key}.googleapis.com"
diff --git a/examples/terraform/envoy-ratelimiter/ratelimit.tf b/examples/terraform/envoy-ratelimiter/ratelimit.tf
index c95e48927cb7..96638e23563b 100644
--- a/examples/terraform/envoy-ratelimiter/ratelimit.tf
+++ b/examples/terraform/envoy-ratelimiter/ratelimit.tf
@@ -158,11 +158,36 @@ resource "kubernetes_deployment" "ratelimit" {
           port {
             container_port = 6070
           }
+          dynamic "port" {
+            for_each = var.enable_metrics ? [1] : []
+            content {
+              name           = "metrics"
+              container_port = 9090
+            }
+          }

           env {
-            name  = "USE_STATSD"
+            name  = "USE_PROMETHEUS"
             value = var.enable_metrics ? "true" : "false"
           }
+          dynamic "env" {
+            for_each = var.enable_metrics ? [1] : []
+            content {
+              name  = "PROMETHEUS_ADDR"
+              value = ":9090"
+            }
+          }
+          dynamic "env" {
+            for_each = var.enable_metrics ? [1] : []
+            content {
+              name  = "PROMETHEUS_PATH"
+              value = "/metrics"
+            }
+          }
+          env {
+            name  = "USE_STATSD"
+            value = "false"
+          }
           env {
             name  = "DISABLE_STATS"
             value = var.enable_metrics ? "false" : "true"
@@ -203,14 +228,6 @@ resource "kubernetes_deployment" "ratelimit" {
             name  = "CONFIG_TYPE"
             value = "FILE"
           }
-          env {
-            name  = "STATSD_HOST"
-            value = "localhost"
-          }
-          env {
-            name  = "STATSD_PORT"
-            value = "9125"
-          }
           env {
             name  = "GRPC_MAX_CONNECTION_AGE"
             value = var.ratelimit_grpc_max_connection_age
@@ -231,41 +248,7 @@ resource "kubernetes_deployment" "ratelimit" {
           }
         }

-        dynamic "container" {
-          for_each = var.enable_metrics ? [1] : []
-          content {
-            name  = "statsd-exporter"
-            image = var.statsd_exporter_image
-            args  = ["--log.format=json"]
-
-            dynamic "port" {
-              for_each = var.enable_metrics ? [1] : []
-              content {
-                name           = "metrics"
-                container_port = 9102
-              }
-            }
-            dynamic "port" {
-              for_each = var.enable_metrics ? [1] : []
-              content {
-                name           = "statsd-udp"
-                container_port = 9125
-                protocol       = "UDP"
-              }
-            }
-            # statsd-exporter does not use much resources, so setting resources to the minimum
-            resources {
-              requests = {
-                cpu    = "50m"
-                memory = "64Mi"
-              }
-              limits = {
-                cpu    = "100m"
-                memory = "128Mi"
-              }
-            }
-          }
-        }
+

         volume {
           name = "config-volume"
@@ -361,8 +344,8 @@ resource "kubernetes_service" "ratelimit" {
       for_each = var.enable_metrics ? [1] : []
       content {
         name        = "metrics"
-        port        = 9102
-        target_port = 9102
+        port        = 9090
+        target_port = 9090
       }
     }
   }
@@ -398,15 +381,38 @@ resource "kubernetes_service" "ratelimit_external" {
       port        = 6070
       target_port = 6070
     }
-    dynamic "port" {
-      for_each = var.enable_metrics ? [1] : []
-      content {
-        name        = "metrics"
-        port        = 9102
-        target_port = 9102
-      }
-    }
+
   }

   depends_on = [kubernetes_namespace.ratelimit_namespace]
 }
+
+# Pod Monitoring
+resource "kubernetes_manifest" "ratelimit_pod_monitoring" {
+  manifest = {
+    apiVersion = "monitoring.googleapis.com/v1"
+    kind       = "PodMonitoring"
+    metadata = {
+      name      = "ratelimit-monitoring"
+      namespace = var.namespace
+    }
+    spec = {
+      selector = {
+        matchLabels = {
+          app = "ratelimit"
+        }
+      }
+      endpoints = [
+        {
+          port = "metrics"
+          path = "/metrics"
+          interval = "15s"
+        }
+      ]
+    }
+  }
+  depends_on = [
+    kubernetes_deployment.ratelimit,
+    time_sleep.wait_for_cluster
+  ]
+}
diff --git a/examples/terraform/envoy-ratelimiter/variables.tf b/examples/terraform/envoy-ratelimiter/variables.tf
index b7a771148215..3d732372acff 100644
--- a/examples/terraform/envoy-ratelimiter/variables.tf
+++ b/examples/terraform/envoy-ratelimiter/variables.tf
@@ -183,7 +183,7 @@ variable "namespace" {
 }

 variable "enable_metrics" {
-  description = "Whether to deploy the statsd-exporter sidecar for Prometheus metrics"
+  description = "Enable metrics export to Google Cloud Monitoring"
   type        = bool
-  default     = false
+  default     = true
 }

PATCH

echo "Patch applied successfully."
