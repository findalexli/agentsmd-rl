#!/usr/bin/env bash
set -euo pipefail

cd /workspace/trigger.dev

# Idempotent: skip if already applied
if grep -q 'webapp.ingress.enabled' hosting/k8s/helm/templates/NOTES.txt 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/docs/self-hosting/overview.mdx b/docs/self-hosting/overview.mdx
index 59f53ed50b1..93737247f2e 100644
--- a/docs/self-hosting/overview.mdx
+++ b/docs/self-hosting/overview.mdx
@@ -94,3 +94,14 @@ All fields are optional. Partial overrides are supported:
 ## Community support

 It's dangerous to go alone! Join the self-hosting channel on our [Discord server](https://discord.gg/NQTxt5NA7s).
+
+## Next steps
+
+<CardGroup>
+  <Card title="Docker compose" color="#2496ED" icon="docker" href="/self-hosting/docker">
+    Learn how to self-host Trigger.dev with Docker compose.
+  </Card>
+  <Card title="Kubernetes" color="#326CE5" icon="dharmachakra" href="/self-hosting/kubernetes">
+    Learn how to self-host Trigger.dev with Kubernetes.
+  </Card>
+</CardGroup>
diff --git a/hosting/k8s/helm/Chart.yaml b/hosting/k8s/helm/Chart.yaml
index eda7b786bfd..b6a7585eca1 100644
--- a/hosting/k8s/helm/Chart.yaml
+++ b/hosting/k8s/helm/Chart.yaml
@@ -2,7 +2,7 @@ apiVersion: v2
 name: trigger
 description: The official Trigger.dev Helm chart
 type: application
-version: 4.0.0-beta.10
+version: 4.0.0-beta.11
 appVersion: trigger-helm-rc.1
 home: https://trigger.dev
 sources:
diff --git a/hosting/k8s/helm/README.md b/hosting/k8s/helm/README.md
index 742f2215b02..17b8bfde701 100644
--- a/hosting/k8s/helm/README.md
+++ b/hosting/k8s/helm/README.md
@@ -113,14 +113,13 @@ This chart deploys the following components:
 ### Basic Configuration

 ```yaml
-# Application URLs
-config:
+webapp:
+  # Application URLs
   appOrigin: "https://trigger.example.com"
   loginOrigin: "https://trigger.example.com"
   apiOrigin: "https://trigger.example.com"

-# Bootstrap mode (auto-creates worker group)
-config:
+  # Bootstrap mode (auto-creates worker group)
   bootstrap:
     enabled: true  # Enable for combined setups
     workerGroupName: "bootstrap"
@@ -133,8 +132,7 @@ Use external managed services instead of bundled components:
 ```yaml
 # External PostgreSQL
 postgres:
-  enabled: false
-  external: true
+  deploy: false
   external:
     host: "your-postgres.rds.amazonaws.com"
     port: 5432
@@ -144,8 +142,7 @@ postgres:

 # External Redis
 redis:
-  enabled: false
-  external: true
+  deploy: false
   external:
     host: "your-redis.cache.amazonaws.com"
     port: 6379
@@ -153,8 +150,7 @@ redis:

 # External Docker Registry (e.g., Kind local registry)
 registry:
-  enabled: true
-  external: true
+  deploy: true
   external:
     host: "localhost"
     port: 5001
@@ -165,20 +161,39 @@ registry:
 ### Ingress Configuration

 ```yaml
-ingress:
-  enabled: true
-  className: "nginx"
-  annotations:
-    cert-manager.io/cluster-issuer: "letsencrypt-prod"
-  hosts:
-    - host: trigger.example.com
-      paths:
-        - path: /
-          pathType: Prefix
-  tls:
-    - secretName: trigger-tls
-      hosts:
-        - trigger.example.com
+# Webapp ingress
+webapp:
+  ingress:
+    enabled: true
+    className: "nginx"
+    annotations:
+      cert-manager.io/cluster-issuer: "letsencrypt-prod"
+    hosts:
+      - host: trigger.example.com
+        paths:
+          - path: /
+            pathType: Prefix
+    tls:
+      - secretName: trigger-tls
+        hosts:
+          - trigger.example.com
+
+# Registry ingress
+registry:
+  ingress:
+    enabled: true
+    className: "nginx"
+    annotations:
+      cert-manager.io/cluster-issuer: "letsencrypt-prod"
+    hosts:
+      - host: registry.example.com
+        paths:
+          - path: /
+            pathType: Prefix
+    tls:
+      - secretName: registry-tls
+        hosts:
+          - registry.example.com
 ```

 ### Resource Configuration
diff --git a/hosting/k8s/helm/templates/NOTES.txt b/hosting/k8s/helm/templates/NOTES.txt
index 659000a81b9..e70d18dd74a 100644
--- a/hosting/k8s/helm/templates/NOTES.txt
+++ b/hosting/k8s/helm/templates/NOTES.txt
@@ -24,10 +24,10 @@ To get started:
    kubectl get pods --namespace {{ .Release.Namespace }} -w

 2. Access the webapp:
-{{- if .Values.ingress.enabled }}
-{{- range $host := .Values.ingress.hosts }}
+{{- if .Values.webapp.ingress.enabled }}
+{{- range $host := .Values.webapp.ingress.hosts }}
   {{- range .paths }}
-   http{{ if $.Values.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
+   http{{ if $.Values.webapp.ingress.tls }}s{{ end }}://{{ $host.host }}{{ .path }}
   {{- end }}
 {{- end }}
 {{- else if contains "NodePort" .Values.webapp.service.type }}
@@ -86,8 +86,8 @@ Configuration:
 {{- if .Values.registry.deploy }}
 - Using internal Docker registry
 {{- else }}
-- Using external Docker registry at {{ .Values.registry.external.host }}:{{ .Values.registry.external.port }}
-{{- if eq .Values.registry.external.host "localhost" }}
+- Using external Docker registry at {{ .Values.registry.external.host }}
+{{- if hasPrefix "localhost" .Values.registry.external.host }}

 ⚠️  Registry Warning:
    Using localhost for registry. Deployments will only work when testing locally in kind or minikube.
diff --git a/hosting/k8s/helm/templates/_helpers.tpl b/hosting/k8s/helm/templates/_helpers.tpl
index 3087709f1a2..35ab8032792 100644
--- a/hosting/k8s/helm/templates/_helpers.tpl
+++ b/hosting/k8s/helm/templates/_helpers.tpl
@@ -238,9 +238,9 @@ Registry connection details
 */}}
 {{- define "trigger-v4.registry.host" -}}
 {{- if .Values.registry.deploy -}}
-{{ include "trigger-v4.fullname" . }}-registry:{{ .Values.registry.service.port }}
+{{ .Values.registry.host }}
 {{- else -}}
-{{ .Values.registry.external.host }}:{{ .Values.registry.external.port }}
+{{ .Values.registry.external.host }}
 {{- end -}}
 {{- end }}

@@ -306,20 +306,37 @@ Generate docker config for image pull secret
 {{- end }}

 {{/*
-Merge ingress annotations to avoid duplicates
+Merge webapp ingress annotations to avoid duplicates
 */}}
-{{- define "trigger-v4.ingress.annotations" -}}
+{{- define "trigger-v4.webapp.ingress.annotations" -}}
 {{- $annotations := dict -}}
-{{- if .Values.ingress.annotations -}}
-{{- $annotations = .Values.ingress.annotations -}}
+{{- if .Values.webapp.ingress.annotations -}}
+{{- $annotations = .Values.webapp.ingress.annotations -}}
 {{- end -}}
-{{- if .Values.ingress.certManager.enabled -}}
-{{- $_ := set $annotations "cert-manager.io/cluster-issuer" .Values.ingress.certManager.clusterIssuer -}}
+{{- if .Values.webapp.ingress.certManager.enabled -}}
+{{- $_ := set $annotations "cert-manager.io/cluster-issuer" .Values.webapp.ingress.certManager.clusterIssuer -}}
 {{- end -}}
-{{- if .Values.ingress.externalDns.enabled -}}
-{{- $_ := set $annotations "external-dns.alpha.kubernetes.io/hostname" .Values.ingress.externalDns.hostname -}}
-{{- $_ := set $annotations "external-dns.alpha.kubernetes.io/ttl" (.Values.ingress.externalDns.ttl | toString) -}}
+{{- if .Values.webapp.ingress.externalDns.enabled -}}
+{{- $_ := set $annotations "external-dns.alpha.kubernetes.io/hostname" .Values.webapp.ingress.externalDns.hostname -}}
+{{- $_ := set $annotations "external-dns.alpha.kubernetes.io/ttl" (.Values.webapp.ingress.externalDns.ttl | toString) -}}
 {{- end -}}
 {{- toYaml $annotations -}}
 {{- end }}

+{{/*
+Merge registry ingress annotations to avoid duplicates
+*/}}
+{{- define "trigger-v4.registry.ingress.annotations" -}}
+{{- $annotations := dict -}}
+{{- if .Values.registry.ingress.annotations -}}
+{{- $annotations = .Values.registry.ingress.annotations -}}
+{{- end -}}
+{{- if .Values.registry.ingress.certManager.enabled -}}
+{{- $_ := set $annotations "cert-manager.io/cluster-issuer" .Values.registry.ingress.certManager.clusterIssuer -}}
+{{- end -}}
+{{- if .Values.registry.ingress.externalDns.enabled -}}
+{{- $_ := set $annotations "external-dns.alpha.kubernetes.io/hostname" .Values.registry.ingress.externalDns.hostname -}}
+{{- $_ := set $annotations "external-dns.alpha.kubernetes.io/ttl" (.Values.registry.ingress.externalDns.ttl | toString) -}}
+{{- end -}}
+{{- toYaml $annotations -}}
+{{- end }}
diff --git a/hosting/k8s/helm/templates/registry-ingress.yaml b/hosting/k8s/helm/templates/registry-ingress.yaml
new file mode 100644
index 00000000000..ca9191a42ed
--- /dev/null
+++ b/hosting/k8s/helm/templates/registry-ingress.yaml
@@ -0,0 +1,52 @@
+{{- if and .Values.registry.deploy .Values.registry.ingress.enabled -}}
+{{- $fullName := include "trigger-v4.fullname" . -}}
+{{- $svcPort := .Values.registry.service.port -}}
+apiVersion: networking.k8s.io/v1
+kind: Ingress
+metadata:
+  name: {{ $fullName }}-registry
+  labels:
+    {{- $component := "registry" }}
+    {{- include "trigger-v4.componentLabels" (dict "Chart" .Chart "Release" .Release "Values" .Values "component" $component) | nindent 4 }}
+  annotations:
+    {{- include "trigger-v4.registry.ingress.annotations" . | nindent 4 }}
+spec:
+  {{- if .Values.registry.ingress.className }}
+  ingressClassName: {{ .Values.registry.ingress.className }}
+  {{- end }}
+  {{- if .Values.registry.ingress.tls }}
+  tls:
+    {{- range .Values.registry.ingress.tls }}
+    - hosts:
+        {{- range .hosts }}
+        - {{ . | quote }}
+        {{- end }}
+      secretName: {{ .secretName }}
+    {{- end }}
+  {{- end }}
+  rules:
+    {{- range .Values.registry.ingress.hosts }}
+    - host: {{ .host | quote }}
+      http:
+        paths:
+          {{- if .paths }}
+          {{- range .paths }}
+          - path: {{ .path }}
+            pathType: {{ .pathType | default "Prefix" }}
+            backend:
+              service:
+                name: {{ $fullName }}-registry
+                port:
+                  number: {{ $svcPort }}
+          {{- end }}
+          {{- else }}
+          - path: /
+            pathType: Prefix
+            backend:
+              service:
+                name: {{ $fullName }}-registry
+                port:
+                  number: {{ $svcPort }}
+          {{- end }}
+    {{- end }}
+{{- end }}
\ No newline at end of file
diff --git a/hosting/k8s/helm/templates/validate-external-config.yaml b/hosting/k8s/helm/templates/validate-external-config.yaml
index c3bd1e07561..47998f7d23a 100644
--- a/hosting/k8s/helm/templates/validate-external-config.yaml
+++ b/hosting/k8s/helm/templates/validate-external-config.yaml
@@ -33,8 +33,8 @@ This template will fail the Helm deployment if external config is missing for re
 {{- end }}

 {{- if not .Values.registry.deploy }}
-{{- if or (not .Values.registry.external.host) (not .Values.registry.external.port) }}
-{{- fail "Registry external configuration is required when registry.deploy=false. Please provide registry.external.host and registry.external.port" }}
+{{- if or (not .Values.registry.external.host) }}
+{{- fail "Registry external configuration is required when registry.deploy=false. Please provide registry.external.host" }}
 {{- end }}
 {{- end }}

diff --git a/hosting/k8s/helm/templates/ingress.yaml b/hosting/k8s/helm/templates/webapp-ingress.yaml
similarity index 64%
rename from hosting/k8s/helm/templates/ingress.yaml
rename to hosting/k8s/helm/templates/webapp-ingress.yaml
index ba9640b9fe8..b293c993798 100644
--- a/hosting/k8s/helm/templates/ingress.yaml
+++ b/hosting/k8s/helm/templates/webapp-ingress.yaml
@@ -1,21 +1,22 @@
-{{- if .Values.ingress.enabled -}}
+{{- if .Values.webapp.ingress.enabled -}}
 {{- $fullName := include "trigger-v4.fullname" . -}}
 {{- $svcPort := .Values.webapp.service.port -}}
 apiVersion: networking.k8s.io/v1
 kind: Ingress
 metadata:
-  name: {{ $fullName }}
+  name: {{ $fullName }}-webapp
   labels:
-    {{- include "trigger-v4.labels" . | nindent 4 }}
+    {{- $component := "webapp" }}
+    {{- include "trigger-v4.componentLabels" (dict "Chart" .Chart "Release" .Release "Values" .Values "component" $component) | nindent 4 }}
   annotations:
-    {{- include "trigger-v4.ingress.annotations" . | nindent 4 }}
+    {{- include "trigger-v4.webapp.ingress.annotations" . | nindent 4 }}
 spec:
-  {{- if .Values.ingress.className }}
-  ingressClassName: {{ .Values.ingress.className }}
+  {{- if .Values.webapp.ingress.className }}
+  ingressClassName: {{ .Values.webapp.ingress.className }}
   {{- end }}
-  {{- if .Values.ingress.tls }}
+  {{- if .Values.webapp.ingress.tls }}
   tls:
-    {{- range .Values.ingress.tls }}
+    {{- range .Values.webapp.ingress.tls }}
     - hosts:
         {{- range .hosts }}
         - {{ . | quote }}
@@ -24,7 +25,7 @@ spec:
     {{- end }}
   {{- end }}
   rules:
-    {{- range .Values.ingress.hosts }}
+    {{- range .Values.webapp.ingress.hosts }}
     - host: {{ .host | quote }}
       http:
         paths:
diff --git a/hosting/k8s/helm/templates/webapp.yaml b/hosting/k8s/helm/templates/webapp.yaml
index d1cd06508f1..b5c98ff1550 100644
--- a/hosting/k8s/helm/templates/webapp.yaml
+++ b/hosting/k8s/helm/templates/webapp.yaml
@@ -172,11 +172,11 @@ spec:
             {{- toYaml .Values.webapp.resources | nindent 12 }}
           env:
             - name: APP_ORIGIN
-              value: {{ .Values.config.appOrigin | quote }}
+              value: {{ .Values.webapp.appOrigin | quote }}
             - name: LOGIN_ORIGIN
-              value: {{ .Values.config.loginOrigin | quote }}
+              value: {{ .Values.webapp.loginOrigin | quote }}
             - name: API_ORIGIN
-              value: {{ .Values.config.apiOrigin | quote }}
+              value: {{ .Values.webapp.apiOrigin | quote }}
             - name: ELECTRIC_ORIGIN
               value: {{ include "trigger-v4.electric.url" . | quote }}
             - name: DATABASE_URL
@@ -194,7 +194,7 @@ spec:
             - name: APP_LOG_LEVEL
               value: {{ .Values.webapp.logLevel | quote }}
             - name: DEV_OTEL_EXPORTER_OTLP_ENDPOINT
-              value: "{{ .Values.config.appOrigin }}/otel"
+              value: "{{ .Values.webapp.appOrigin }}/otel"
             - name: DEPLOY_REGISTRY_HOST
               value: {{ include "trigger-v4.registry.host" . | quote }}
             - name: DEPLOY_REGISTRY_NAMESPACE
diff --git a/hosting/k8s/helm/values-production-example.yaml b/hosting/k8s/helm/values-production-example.yaml
index 7d8132b0d7c..0ba12be7124 100644
--- a/hosting/k8s/helm/values-production-example.yaml
+++ b/hosting/k8s/helm/values-production-example.yaml
@@ -12,33 +12,30 @@ secrets:
     accessKeyId: "your-access-key"
     secretAccessKey: "your-secret-key"

-# Production configuration
-config:
+# Production webapp configuration
+webapp:
+  # Origin configuration
   appOrigin: "https://trigger.example.com"
   loginOrigin: "https://trigger.example.com"
   apiOrigin: "https://trigger.example.com"

-# Production ingress
-ingress:
-  enabled: true
-  className: "nginx"
-  annotations:
-    cert-manager.io/cluster-issuer: "letsencrypt-prod"
-    nginx.ingress.kubernetes.io/ssl-redirect: "true"
-  hosts:
-    - host: trigger.example.com
-      paths:
-        - path: /
-          pathType: Prefix
-  tls:
-    - secretName: trigger-tls
-      hosts:
-        - trigger.example.com
+  # Production ingress
+  ingress:
+    enabled: true
+    className: "nginx"
+    annotations:
+      cert-manager.io/cluster-issuer: "letsencrypt-prod"
+      nginx.ingress.kubernetes.io/ssl-redirect: "true"
+    hosts:
+      - host: trigger.example.com
+        paths:
+          - path: /
+            pathType: Prefix
+    tls:
+      - secretName: trigger-tls
+        hosts:
+          - trigger.example.com

-# Production webapp configuration
-webapp:
-  bootstrap:
-    enabled: false # Usually disabled in production
   resources:
     limits:
       cpu: 2000m
@@ -114,6 +111,23 @@ registry:
     size: 100Gi
     storageClass: "standard"

+  # Production ingress
+  ingress:
+    enabled: true
+    className: "nginx"
+    annotations:
+      cert-manager.io/cluster-issuer: "letsencrypt-prod"
+      nginx.ingress.kubernetes.io/ssl-redirect: "true"
+    hosts:
+      - host: registry.example.com
+        paths:
+          - path: /
+            pathType: Prefix
+    tls:
+      - secretName: registry-tls
+        hosts:
+          - registry.example.com
+
 # Production Supervisor (Kubernetes worker orchestrator)
 supervisor:
   resources:
diff --git a/hosting/k8s/helm/values.yaml b/hosting/k8s/helm/values.yaml
index d44b83cd7ef..8cebb1dbe40 100644
--- a/hosting/k8s/helm/values.yaml
+++ b/hosting/k8s/helm/values.yaml
@@ -6,12 +6,6 @@ global:
 nameOverride: ""
 fullnameOverride: ""

-# Shared application configuration (used by multiple services)
-config:
-  appOrigin: "http://localhost:3040"
-  loginOrigin: "http://localhost:3040"
-  apiOrigin: "http://localhost:3040"
-
 # Secrets configuration
 # IMPORTANT: The default values below are for TESTING ONLY and should NOT be used in production
 # For production deployments:
@@ -56,6 +50,11 @@ webapp:
     tag: "" # Defaults to Chart.appVersion when empty
     pullPolicy: IfNotPresent

+  # Origin configuration
+  appOrigin: "http://localhost:3040"
+  loginOrigin: "http://localhost:3040"
+  apiOrigin: "http://localhost:3040"
+
   replicaCount: 1

   service:
@@ -170,6 +169,34 @@ webapp:
       exporterEnabled: "0"
       exporterIntervalMs: 30000

+  # Webapp ingress configuration
+  ingress:
+    enabled: false
+    className: "traefik"
+    # Custom annotations for the ingress resource
+    # Note: The following annotation keys are reserved and will be automatically set:
+    # - cert-manager.io/cluster-issuer (when certManager.enabled is true)
+    # - external-dns.alpha.kubernetes.io/hostname (when externalDns.enabled is true)
+    # - external-dns.alpha.kubernetes.io/ttl (when externalDns.enabled is true)
+    annotations: {}
+    certManager:
+      enabled: false
+      clusterIssuer: "letsencrypt-prod"
+    externalDns:
+      enabled: false
+      hostname: ""
+      ttl: "300"
+    hosts:
+      - host: trigger.local
+        paths:
+          - path: /
+            pathType: Prefix
+    tls:
+      []
+      # - secretName: trigger-tls
+      #   hosts:
+      #     - trigger.local
+
 # Supervisor configuration
 supervisor:
   image:
@@ -492,20 +519,34 @@ s3:

 # Docker Registry configuration
 registry:
-  # EXPERIMENTAL - requires TLS setup or additional cluster configuration. Configure `external` details instead.
+  # EXPERIMENTAL - requires ingress/TLS setup or additional cluster configuration. Configure `external` details instead.
   deploy: false

-  repositoryNamespace: "trigger" # Docker repository namespace for deployed images, will be part of the image ref
+  # This will be used when deploy: true
+  host: "registry.example.com"
+
+  # Docker repository namespace for deployed images, will be part of the image ref
+  repositoryNamespace: "trigger"
+
   image:
     registry: docker.io
     repository: registry
     tag: "2"
     pullPolicy: IfNotPresent
+
   auth:
     enabled: true
     username: "registry-user"
     password: "very-secure-indeed"

+  # External Registry connection (when deploy: false)
+  external:
+    host: "localhost:5001"
+    auth:
+      enabled: false
+      username: ""
+      password: ""
+
   podAnnotations: {}

   # podSecurityContext:
@@ -571,21 +612,40 @@ registry:
     failureThreshold: 60
     successThreshold: 1

-  # External Registry connection (when deploy: false)
-  external:
-    host: "localhost"
-    port: 5001
-    auth:
-      enabled: false
-      username: ""
-      password: ""
-
   # Extra environment variables for Registry
   extraEnvVars:
     []
     # - name: CUSTOM_VAR
     #   value: "custom-value"

+  # Registry ingress configuration
+  ingress:
+    enabled: false
+    className: "traefik"
+    # Custom annotations for the ingress resource
+    # Note: The following annotation keys are reserved and will be automatically set:
+    # - cert-manager.io/cluster-issuer (when certManager.enabled is true)
+    # - external-dns.alpha.kubernetes.io/hostname (when externalDns.enabled is true)
+    # - external-dns.alpha.kubernetes.io/ttl (when externalDns.enabled is true)
+    annotations: {}
+    certManager:
+      enabled: false
+      clusterIssuer: "letsencrypt-prod"
+    externalDns:
+      enabled: false
+      hostname: ""
+      ttl: "300"
+    hosts:
+      - host: registry.local
+        paths:
+          - path: /
+            pathType: Prefix
+    tls:
+      []
+      # - secretName: registry-tls
+      #   hosts:
+      #     - registry.local
+
 # Shared persistent volumes
 persistence:
   # This is used for the worker token file
@@ -597,32 +657,6 @@ persistence:
     storageClass: ""
     retain: true # Prevents deletion on uninstall

-ingress:
-  enabled: false
-  className: "traefik"
-  # Custom annotations for the ingress resource
-  # Note: The following annotation keys are reserved and will be automatically set:
-  # - cert-manager.io/cluster-issuer (when certManager.enabled is true)
-  # - external-dns.alpha.kubernetes.io/hostname (when externalDns.enabled is true)
-  # - external-dns.alpha.kubernetes.io/ttl (when externalDns.enabled is true)
-  annotations: {}
-  certManager:
-    enabled: false
-    clusterIssuer: "letsencrypt-prod"
-  externalDns:
-    enabled: false
-    hostname: ""
-    ttl: "300"
-  hosts:
-    - host: trigger.local
-      paths:
-        - path: /
-          pathType: Prefix
-  tls:
-    []
-    # - secretName: trigger-tls
-    #   hosts:
-    #     - trigger.local

 # Telemetry configuration
 telemetry:

PATCH

echo "Patch applied successfully."
