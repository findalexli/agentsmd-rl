#!/usr/bin/env bash
set -euo pipefail

cd /workspace/beam

# Idempotent: skip if already applied
if grep -q 'set = \[' .github/gh-actions-self-hosted-runners/arc/helm.tf 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/.github/gh-actions-self-hosted-runners/arc/README.md b/.github/gh-actions-self-hosted-runners/arc/README.md
index e5055826d00c..2880f5dc987d 100644
--- a/.github/gh-actions-self-hosted-runners/arc/README.md
+++ b/.github/gh-actions-self-hosted-runners/arc/README.md
@@ -96,7 +96,26 @@ terraform init -backend-config="bucket=bucket_name"
 terraform apply -var-file=environments/environment_name.env
 ```

+# Updating
+If you need to update the configuration (e.g. upgrading the github runner image, changing resource settings, etc), follow the steps below:
+
+1. From this directory, login to your gcloud account that you created the bucket with and init terraform. Replace bucket_name with the bucket for storing terraform state, e.g. `beam-arc-state`.
+```
+gcloud auth login
+gcloud auth application-default login
+terraform init -backend-config="bucket=bucket_name"
+```
+
+2. Terraform plan. Replace environment_name.env with the file under environments, e.g. `beam.env`. Fix config problems if any.
+```
+terraform plan -var-file=environments/environment_name.env
+```
+
+3. Terraform apply. Replace environment_name.env with the file under environments, e.g. `beam.env`.
+```
+terraform apply -var-file=environments/environment_name.env
+```
+
 # Maintanance

 - To access the ARC k8s cluster call the `get_kubeconfig_command` terraform output and run the command
-
diff --git a/.github/gh-actions-self-hosted-runners/arc/helm.tf b/.github/gh-actions-self-hosted-runners/arc/helm.tf
index 4c2badaf3239..aa5bd25cef78 100644
--- a/.github/gh-actions-self-hosted-runners/arc/helm.tf
+++ b/.github/gh-actions-self-hosted-runners/arc/helm.tf
@@ -22,14 +22,16 @@ resource "helm_release" "cert-manager" {
   create_namespace = true
   repository = "https://charts.jetstack.io"
   chart      = "cert-manager"
-
+
   atomic = "true"
   timeout = 100

-  set {
-    name  = "installCRDs"
-    value = "true"
-  }
+  set = [
+    {
+      name  = "installCRDs"
+      value = "true"
+    }
+  ]
   depends_on = [ google_container_node_pool.main-actions-runner-pool ]
 }

@@ -43,12 +45,11 @@ resource "helm_release" "arc" {
   atomic = "true"
   timeout = 120

-  dynamic "set" {
-    for_each = local.arc_values
-    content {
-      name = set.key
-      value = set.value
+  set = [
+    for k, v in local.arc_values : {
+      name  = k
+      value = v
     }
-  }
+  ]
   depends_on = [ helm_release.cert-manager ]
 }
diff --git a/.github/gh-actions-self-hosted-runners/arc/provider.tf b/.github/gh-actions-self-hosted-runners/arc/provider.tf
index dc557b62a559..81e8625afc0b 100644
--- a/.github/gh-actions-self-hosted-runners/arc/provider.tf
+++ b/.github/gh-actions-self-hosted-runners/arc/provider.tf
@@ -25,7 +25,7 @@ terraform {
   required_providers {
     google = {
       source = "hashicorp/google"
-      version = "~> 4.62.0"
+      version = "~> 6.7.0"
     }
     kubectl = {
       source  = "alekc/kubectl"
@@ -40,7 +40,7 @@ provider "google" {
 }

 provider "helm" {
-  kubernetes {
+  kubernetes = {
     host                    = "https://${google_container_cluster.actions-runner-gke.endpoint}"
     token                   = data.google_client_config.provider.access_token
     cluster_ca_certificate  = base64decode(google_container_cluster.actions-runner-gke.master_auth.0.cluster_ca_certificate)
@@ -66,4 +66,4 @@ provider "github" {
   }
   owner = var.organization

-}
\ No newline at end of file
+}

PATCH

echo "Patch applied successfully."
