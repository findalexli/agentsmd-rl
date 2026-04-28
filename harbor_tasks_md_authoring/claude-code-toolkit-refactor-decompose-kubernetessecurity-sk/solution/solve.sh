#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-toolkit

# Idempotency guard
if grep -qF "Use loaded reference knowledge to answer with concrete YAML manifests and specif" "skills/kubernetes-security/SKILL.md" && grep -qF "Start with a default-deny policy for both ingress and egress in every namespace." "skills/kubernetes-security/references/network-policies.md" && grep -qF "Kubernetes PodSecurity admission replaces the deprecated PodSecurityPolicy. Appl" "skills/kubernetes-security/references/pod-security.md" && grep -qF "RBAC (Role-Based Access Control) is the primary authorization mechanism in Kuber" "skills/kubernetes-security/references/rbac-patterns.md" && grep -qF "Supply chain security covers image provenance, admission-time policy enforcement" "skills/kubernetes-security/references/supply-chain.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/kubernetes-security/SKILL.md b/skills/kubernetes-security/SKILL.md
@@ -1,7 +1,7 @@
 ---
 name: kubernetes-security
 description: "Kubernetes security: RBAC, PodSecurity, network policies."
-version: 1.0.0
+version: 1.1.0
 user-invocable: false
 context: fork
 agent: kubernetes-helm-engineer
@@ -19,292 +19,51 @@ routing:
 
 Harden Kubernetes clusters and workloads through RBAC, pod security, network isolation, secret management, and supply chain controls.
 
-## Instructions
+## Reference Loading Table
 
-### Step 1: RBAC -- Least-Privilege Roles and Bindings
+| Signal | Reference | Size |
+|--------|-----------|------|
+| RBAC, Role, RoleBinding, ClusterRole, ServiceAccount, least-privilege, access control, permissions | `references/rbac-patterns.md` | ~60 lines |
+| PodSecurity, SecurityContext, runAsNonRoot, readOnlyRootFilesystem, restricted, baseline, image hardening, distroless, Dockerfile | `references/pod-security.md` | ~90 lines |
+| NetworkPolicy, default-deny, allow-list, egress, ingress, DNS, lateral movement, namespace isolation | `references/network-policies.md` | ~70 lines |
+| cosign, Kyverno, OPA, admission controller, Sealed Secrets, External Secrets, supply chain, misconfiguration, privileged | `references/supply-chain.md` | ~120 lines |
 
-Grant the minimum permissions required. Prefer namespace-scoped Roles over ClusterRoles. Write exact verbs and resources in production -- even in dev clusters, because dev habits carry forward and dev manifests get promoted. Write exact verbs and resources every time.
+**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references.
 
-```yaml
-# Good: namespace-scoped Role with specific verbs and resources
-apiVersion: rbac.authorization.k8s.io/v1
-kind: Role
-metadata:
-  namespace: app-team
-  name: deployment-reader
-rules:
-  - apiGroups: ["apps"]
-    resources: ["deployments"]
-    verbs: ["get", "list", "watch"]
-```
-
-```yaml
-# Bind the Role to a specific ServiceAccount, not a user or group wildcard
-apiVersion: rbac.authorization.k8s.io/v1
-kind: RoleBinding
-metadata:
-  namespace: app-team
-  name: deployment-reader-binding
-subjects:
-  - kind: ServiceAccount
-    name: ci-deployer
-    namespace: app-team
-roleRef:
-  kind: Role
-  name: deployment-reader
-  apiGroup: rbac.authorization.k8s.io
-```
-
-ServiceAccount best practices:
-- Create dedicated ServiceAccounts per workload -- create dedicated ServiceAccounts per workload
-- Set `automountServiceAccountToken: false` on pods that have no need for Kubernetes API access
-- Regularly audit which ServiceAccounts have ClusterRole bindings
-
-### Step 2: PodSecurityStandards -- Baseline vs Restricted
-
-Kubernetes PodSecurity admission replaces the deprecated PodSecurityPolicy. Apply labels at the namespace level. All containers must run as non-root with a read-only root filesystem unless there is a documented exception -- if an app claims it needs root, it usually just needs a writable `/tmp`; it usually just needs a writable `/tmp`, which an emptyDir volume solves.
-
-```yaml
-# Enforce restricted profile, warn on baseline violations
-apiVersion: v1
-kind: Namespace
-metadata:
-  name: production
-  labels:
-    pod-security.kubernetes.io/enforce: restricted
-    pod-security.kubernetes.io/warn: restricted
-    pod-security.kubernetes.io/audit: restricted
-```
-
-SecurityContext for a restricted-compliant pod:
-
-```yaml
-apiVersion: v1
-kind: Pod
-metadata:
-  name: secure-app
-spec:
-  securityContext:
-    runAsNonRoot: true
-    seccompProfile:
-      type: RuntimeDefault
-  containers:
-    - name: app
-      image: registry.example.com/app:v1.2.3@sha256:abc123
-      securityContext:
-        allowPrivilegeEscalation: false
-        readOnlyRootFilesystem: true
-        runAsUser: 1000
-        runAsGroup: 1000
-        capabilities:
-          drop: ["ALL"]
-      resources:
-        limits:
-          memory: "256Mi"
-          cpu: "500m"
-        requests:
-          memory: "128Mi"
-          cpu: "100m"
-```
-
-Key differences:
-- **Baseline** -- blocks known privilege escalations (hostNetwork, privileged, hostPID) but allows running as root
-- **Restricted** -- enforces non-root, drops all capabilities, requires seccomp profile, disallows privilege escalation
-
-### Step 3: Network Policies -- Default Deny and Allow-Lists
-
-Start with a default-deny policy for both ingress and egress in every namespace. Apply this on day one, not later -- without network policies, lateral movement between compromised pods is trivial.
-
-```yaml
-# Default deny all traffic in the namespace
-apiVersion: networking.k8s.io/v1
-kind: NetworkPolicy
-metadata:
-  name: default-deny-all
-  namespace: production
-spec:
-  podSelector: {}
-  policyTypes:
-    - Ingress
-    - Egress
-```
-
-Then add specific allow rules:
-
-```yaml
-# Allow frontend pods to reach backend on port 8080
-apiVersion: networking.k8s.io/v1
-kind: NetworkPolicy
-metadata:
-  name: allow-frontend-to-backend
-  namespace: production
-spec:
-  podSelector:
-    matchLabels:
-      app: backend
-  policyTypes:
-    - Ingress
-  ingress:
-    - from:
-        - podSelector:
-            matchLabels:
-              app: frontend
-      ports:
-        - protocol: TCP
-          port: 8080
-```
-
-```yaml
-# Allow DNS egress for all pods (required for service discovery)
-apiVersion: networking.k8s.io/v1
-kind: NetworkPolicy
-metadata:
-  name: allow-dns-egress
-  namespace: production
-spec:
-  podSelector: {}
-  policyTypes:
-    - Egress
-  egress:
-    - to: []
-      ports:
-        - protocol: UDP
-          port: 53
-        - protocol: TCP
-          port: 53
-```
-
-### Step 4: Secret Management
-
-Store secrets using Sealed Secrets or External Secrets Operator, environment variables from manifests, or checked-in YAML. Secrets exposed as env vars are visible in `kubectl describe pod` output, which makes them trivially discoverable after any pod compromise. Use one of these approaches instead:
-
-**Sealed Secrets** -- encrypts secrets client-side so they are safe in Git:
-
-```bash
-# Encrypt a secret with kubeseal
-kubectl create secret generic db-creds \
-  --from-literal=password=supersecret \
-  --dry-run=client -o yaml | \
-  kubeseal --format yaml > sealed-db-creds.yaml
-```
-
-**External Secrets Operator** -- syncs secrets from external vaults:
-
-```yaml
-apiVersion: external-secrets.io/v1beta1
-kind: ExternalSecret
-metadata:
-  name: db-credentials
-  namespace: production
-spec:
-  refreshInterval: 1h
-  secretStoreRef:
-    name: vault-backend
-    kind: ClusterSecretStore
-  target:
-    name: db-credentials
-  data:
-    - secretKey: password
-      remoteRef:
-        key: secret/data/production/db
-        property: password
-```
-
-Use these alternatives instead:
-- Mounting secrets as environment variables in the pod spec (visible in `kubectl describe pod`)
-- Storing secrets in ConfigMaps
-- Hardcoding credentials in container images or Dockerfiles
-
-### Step 5: Image Security
-
-Containers should instead run as privileged or with elevated capabilities unless explicitly justified -- privileged mode grants full host access to an attacker if the pod is compromised. Use specific capabilities or debug containers instead.
-
-Build minimal, non-root container images:
-
-```dockerfile
-# Use distroless or minimal base images
-FROM gcr.io/distroless/static-debian12:nonroot
-COPY --chown=65532:65532 app /app
-USER 65532:65532
-ENTRYPOINT ["/app"]
-```
-
-Requirements:
-- **Non-root user**: Always set `USER` in the Dockerfile and `runAsNonRoot: true` in the SecurityContext
-- **Read-only root filesystem**: Use `readOnlyRootFilesystem: true` and mount writable volumes only where needed
-- **Distroless or scratch**: No shell, no package manager -- reduces attack surface
-- **Pin image digests**: Use `image:tag@sha256:...` to prevent tag mutation attacks
-- **Scan images**: Run Trivy, Grype, or Snyk in CI before pushing to registry
+---
 
-### Step 6: Supply Chain Security
+## Phase 1: IDENTIFY
 
-**Image signing with cosign:**
+Determine which security domain the user is asking about.
 
-```bash
-# Sign an image after building
-cosign sign --key cosign.key registry.example.com/app:v1.2.3@sha256:abc123
+| Domain | Reference |
+|--------|-----------|
+| Access control, permissions, roles | `references/rbac-patterns.md` |
+| Pod hardening, container security | `references/pod-security.md` |
+| Network isolation, traffic rules | `references/network-policies.md` |
+| Image signing, secrets, admission control | `references/supply-chain.md` |
 
-# Verify before deploying
-cosign verify --key cosign.pub registry.example.com/app:v1.2.3@sha256:abc123
-```
+If the question spans multiple domains, load all relevant references. Most production hardening tasks touch at least RBAC + pod security.
 
-**Admission controllers** to enforce policy at deploy time:
-- **Kyverno** or **OPA Gatekeeper** -- reject pods that violate security policies
-- **Sigstore Policy Controller** -- verify image signatures before admission
+**Gate**: Domain identified. Reference(s) loaded. Proceed to Phase 2.
 
-Example Kyverno policy to require non-root containers:
+---
 
-```yaml
-apiVersion: kyverno.io/v1
-kind: ClusterPolicy
-metadata:
-  name: require-run-as-nonroot
-spec:
-  validationFailureAction: Enforce
-  rules:
-    - name: run-as-non-root
-      match:
-        any:
-          - resources:
-              kinds:
-                - Pod
-      validate:
-        message: "Containers must run as non-root"
-        pattern:
-          spec:
-            containers:
-              - securityContext:
-                  runAsNonRoot: true
-```
+## Phase 2: RESPOND
 
-### Step 7: Detect Common Misconfigurations
+Use loaded reference knowledge to answer with concrete YAML manifests and specific configurations. The references contain complete, copy-paste-ready examples for each security domain.
 
-Watch for these frequent security mistakes:
+For general Kubernetes debugging, pair with the `kubernetes-debugging` skill.
 
-| Misconfiguration | Risk | Fix |
-|------------------|------|-----|
-| `privileged: true` | Full host access | Remove or use specific capabilities |
-| `hostNetwork: true` | Pod shares host network stack | Use CNI networking |
-| `hostPID: true` / `hostIPC: true` | Can see/signal host processes | Remove unless debugging |
-| Wildcard RBAC verbs (`*`) | Grants all operations | List specific verbs |
-| `automountServiceAccountToken: true` on workloads | Token exposed to compromised pod | Set to `false` unless API access needed |
-| No resource limits | Pod can exhaust node resources (DoS) | Set CPU and memory limits |
-| Latest tag without digest | Image can change without notice | Pin by digest |
-| Secrets as env vars in pod spec | Visible in `kubectl describe` | Mount as files or use external secrets |
+**Gate**: Question answered with reference-backed manifests, not generic advice.
 
-## Error Handling
+---
 
-### Error: Pod rejected by PodSecurity admission
-Cause: Pod spec violates the namespace's PodSecurity level (e.g., missing `runAsNonRoot`, `privileged: true`).
-Solution: Check the admission warning message, then update the pod's SecurityContext to comply with the enforced level.
+## Phase 3: VERIFY
 
-### Error: NetworkPolicy blocking legitimate traffic
-Cause: Default-deny is in place but the allow-list rule is missing or has incorrect label selectors.
-Solution: Verify pod labels match the NetworkPolicy `podSelector` and `from`/`to` selectors. Use `kubectl describe networkpolicy` to inspect rules.
+Validate the security posture against the misconfiguration table in `references/supply-chain.md`. Flag any of the 8 common misconfigurations if present in the user's manifests.
 
-### Error: RBAC "access denied" errors in application logs
-Cause: ServiceAccount lacks required permissions.
-Solution: Identify the API group, resource, and verb from the error message. Create or update a Role with the exact permissions needed -- list specific verbs and resources.
+---
 
 ## References
 
diff --git a/skills/kubernetes-security/references/network-policies.md b/skills/kubernetes-security/references/network-policies.md
@@ -0,0 +1,88 @@
+# Network Policies
+
+> **Scope**: Default-deny NetworkPolicy YAML, allow-list patterns, DNS egress rules, and namespace isolation
+> **Version range**: Kubernetes 1.26+ (NetworkPolicy v1 stable)
+> **Generated**: 2026-04-16 — verify against current Kubernetes Network Policies documentation
+
+---
+
+## Overview
+
+Start with a default-deny policy for both ingress and egress in every namespace. Apply this on day one, not later. Without network policies, lateral movement between compromised pods is trivial.
+
+---
+
+## Default Deny All Traffic
+
+```yaml
+# Default deny all traffic in the namespace
+apiVersion: networking.k8s.io/v1
+kind: NetworkPolicy
+metadata:
+  name: default-deny-all
+  namespace: production
+spec:
+  podSelector: {}
+  policyTypes:
+    - Ingress
+    - Egress
+```
+
+---
+
+## Allow-List: Frontend to Backend
+
+```yaml
+# Allow frontend pods to reach backend on port 8080
+apiVersion: networking.k8s.io/v1
+kind: NetworkPolicy
+metadata:
+  name: allow-frontend-to-backend
+  namespace: production
+spec:
+  podSelector:
+    matchLabels:
+      app: backend
+  policyTypes:
+    - Ingress
+  ingress:
+    - from:
+        - podSelector:
+            matchLabels:
+              app: frontend
+      ports:
+        - protocol: TCP
+          port: 8080
+```
+
+---
+
+## DNS Egress (Required for Service Discovery)
+
+```yaml
+# Allow DNS egress for all pods (required for service discovery)
+apiVersion: networking.k8s.io/v1
+kind: NetworkPolicy
+metadata:
+  name: allow-dns-egress
+  namespace: production
+spec:
+  podSelector: {}
+  policyTypes:
+    - Egress
+  egress:
+    - to: []
+      ports:
+        - protocol: UDP
+          port: 53
+        - protocol: TCP
+          port: 53
+```
+
+---
+
+## Error Handling
+
+### Error: NetworkPolicy blocking legitimate traffic
+Cause: Default-deny is in place but the allow-list rule is missing or has incorrect label selectors.
+Solution: Verify pod labels match the NetworkPolicy `podSelector` and `from`/`to` selectors. Use `kubectl describe networkpolicy` to inspect rules.
diff --git a/skills/kubernetes-security/references/pod-security.md b/skills/kubernetes-security/references/pod-security.md
@@ -0,0 +1,98 @@
+# Pod Security
+
+> **Scope**: PodSecurityStandards (Baseline, Restricted, Privileged), SecurityContext configuration, non-root enforcement, and image hardening
+> **Version range**: Kubernetes 1.25+ (PodSecurity admission GA, PodSecurityPolicy removed)
+> **Generated**: 2026-04-16 — verify against current Kubernetes Pod Security Standards documentation
+
+---
+
+## Overview
+
+Kubernetes PodSecurity admission replaces the deprecated PodSecurityPolicy. Apply labels at the namespace level. All containers must run as non-root with a read-only root filesystem unless there is a documented exception. If an app claims it needs root, it usually just needs a writable `/tmp`, which an emptyDir volume solves.
+
+---
+
+## Namespace-Level PodSecurity Labels
+
+```yaml
+# Enforce restricted profile, warn on baseline violations
+apiVersion: v1
+kind: Namespace
+metadata:
+  name: production
+  labels:
+    pod-security.kubernetes.io/enforce: restricted
+    pod-security.kubernetes.io/warn: restricted
+    pod-security.kubernetes.io/audit: restricted
+```
+
+---
+
+## Restricted-Compliant Pod SecurityContext
+
+```yaml
+apiVersion: v1
+kind: Pod
+metadata:
+  name: secure-app
+spec:
+  securityContext:
+    runAsNonRoot: true
+    seccompProfile:
+      type: RuntimeDefault
+  containers:
+    - name: app
+      image: registry.example.com/app:v1.2.3@sha256:abc123
+      securityContext:
+        allowPrivilegeEscalation: false
+        readOnlyRootFilesystem: true
+        runAsUser: 1000
+        runAsGroup: 1000
+        capabilities:
+          drop: ["ALL"]
+      resources:
+        limits:
+          memory: "256Mi"
+          cpu: "500m"
+        requests:
+          memory: "128Mi"
+          cpu: "100m"
+```
+
+---
+
+## PodSecurity Levels
+
+- **Baseline** — blocks known privilege escalations (hostNetwork, privileged, hostPID) but allows running as root
+- **Restricted** — enforces non-root, drops all capabilities, requires seccomp profile, disallows privilege escalation
+
+---
+
+## Image Hardening
+
+Containers should never run as privileged or with elevated capabilities unless explicitly justified. Privileged mode grants full host access to an attacker if the pod is compromised. Use specific capabilities or debug containers instead.
+
+Build minimal, non-root container images:
+
+```dockerfile
+# Use distroless or minimal base images
+FROM gcr.io/distroless/static-debian12:nonroot
+COPY --chown=65532:65532 app /app
+USER 65532:65532
+ENTRYPOINT ["/app"]
+```
+
+Requirements:
+- **Non-root user**: Always set `USER` in the Dockerfile and `runAsNonRoot: true` in the SecurityContext
+- **Read-only root filesystem**: Use `readOnlyRootFilesystem: true` and mount writable volumes only where needed
+- **Distroless or scratch**: No shell, no package manager — reduces attack surface
+- **Pin image digests**: Use `image:tag@sha256:...` to prevent tag mutation attacks
+- **Scan images**: Run Trivy, Grype, or Snyk in CI before pushing to registry
+
+---
+
+## Error Handling
+
+### Error: Pod rejected by PodSecurity admission
+Cause: Pod spec violates the namespace's PodSecurity level (e.g., missing `runAsNonRoot`, `privileged: true`).
+Solution: Check the admission warning message, then update the pod's SecurityContext to comply with the enforced level.
diff --git a/skills/kubernetes-security/references/rbac-patterns.md b/skills/kubernetes-security/references/rbac-patterns.md
@@ -0,0 +1,65 @@
+# RBAC Patterns
+
+> **Scope**: Role, RoleBinding, ClusterRole YAML manifests and ServiceAccount best practices for least-privilege Kubernetes access control
+> **Version range**: Kubernetes 1.26+ (RBAC v1 stable)
+> **Generated**: 2026-04-16 — verify against current Kubernetes RBAC documentation
+
+---
+
+## Overview
+
+RBAC (Role-Based Access Control) is the primary authorization mechanism in Kubernetes. Grant the minimum permissions required. Prefer namespace-scoped Roles over ClusterRoles. Write exact verbs and resources in production. Even in dev clusters, because dev habits carry forward and dev manifests get promoted. Write exact verbs and resources every time.
+
+---
+
+## Namespace-Scoped Role
+
+```yaml
+# Good: namespace-scoped Role with specific verbs and resources
+apiVersion: rbac.authorization.k8s.io/v1
+kind: Role
+metadata:
+  namespace: app-team
+  name: deployment-reader
+rules:
+  - apiGroups: ["apps"]
+    resources: ["deployments"]
+    verbs: ["get", "list", "watch"]
+```
+
+---
+
+## RoleBinding
+
+```yaml
+# Bind the Role to a specific ServiceAccount, not a user or group wildcard
+apiVersion: rbac.authorization.k8s.io/v1
+kind: RoleBinding
+metadata:
+  namespace: app-team
+  name: deployment-reader-binding
+subjects:
+  - kind: ServiceAccount
+    name: ci-deployer
+    namespace: app-team
+roleRef:
+  kind: Role
+  name: deployment-reader
+  apiGroup: rbac.authorization.k8s.io
+```
+
+---
+
+## ServiceAccount Best Practices
+
+- Create dedicated ServiceAccounts per workload
+- Set `automountServiceAccountToken: false` on pods that have no need for Kubernetes API access
+- Regularly audit which ServiceAccounts have ClusterRole bindings
+
+---
+
+## Error Handling
+
+### Error: RBAC "access denied" errors in application logs
+Cause: ServiceAccount lacks required permissions.
+Solution: Identify the API group, resource, and verb from the error message. Create or update a Role with the exact permissions needed. List specific verbs and resources.
diff --git a/skills/kubernetes-security/references/supply-chain.md b/skills/kubernetes-security/references/supply-chain.md
@@ -0,0 +1,119 @@
+# Supply Chain Security
+
+> **Scope**: Image signing with cosign, admission controllers (Kyverno, OPA Gatekeeper), secret management (Sealed Secrets, External Secrets Operator), and common misconfiguration detection
+> **Version range**: cosign v2+, Kyverno v1.10+, External Secrets Operator v0.9+
+> **Generated**: 2026-04-16 — verify against current tool documentation
+
+---
+
+## Overview
+
+Supply chain security covers image provenance, admission-time policy enforcement, secret management, and misconfiguration detection. These controls complement RBAC, pod security, and network policies by securing the software delivery pipeline and runtime configuration.
+
+---
+
+## Image Signing with cosign
+
+```bash
+# Sign an image after building
+cosign sign --key cosign.key registry.example.com/app:v1.2.3@sha256:abc123
+
+# Verify before deploying
+cosign verify --key cosign.pub registry.example.com/app:v1.2.3@sha256:abc123
+```
+
+---
+
+## Admission Controllers
+
+Enforce policy at deploy time:
+- **Kyverno** or **OPA Gatekeeper** — reject pods that violate security policies
+- **Sigstore Policy Controller** — verify image signatures before admission
+
+### Kyverno Policy: Require Non-Root Containers
+
+```yaml
+apiVersion: kyverno.io/v1
+kind: ClusterPolicy
+metadata:
+  name: require-run-as-nonroot
+spec:
+  validationFailureAction: Enforce
+  rules:
+    - name: run-as-non-root
+      match:
+        any:
+          - resources:
+              kinds:
+                - Pod
+      validate:
+        message: "Containers must run as non-root"
+        pattern:
+          spec:
+            containers:
+              - securityContext:
+                  runAsNonRoot: true
+```
+
+---
+
+## Secret Management
+
+Store secrets using Sealed Secrets or External Secrets Operator, not environment variables from manifests or checked-in YAML. Secrets exposed as env vars are visible in `kubectl describe pod` output, which makes them trivially discoverable after any pod compromise.
+
+### Sealed Secrets
+
+Encrypts secrets client-side so they are safe in Git:
+
+```bash
+# Encrypt a secret with kubeseal
+kubectl create secret generic db-creds \
+  --from-literal=password=supersecret \
+  --dry-run=client -o yaml | \
+  kubeseal --format yaml > sealed-db-creds.yaml
+```
+
+### External Secrets Operator
+
+Syncs secrets from external vaults:
+
+```yaml
+apiVersion: external-secrets.io/v1beta1
+kind: ExternalSecret
+metadata:
+  name: db-credentials
+  namespace: production
+spec:
+  refreshInterval: 1h
+  secretStoreRef:
+    name: vault-backend
+    kind: ClusterSecretStore
+  target:
+    name: db-credentials
+  data:
+    - secretKey: password
+      remoteRef:
+        key: secret/data/production/db
+        property: password
+```
+
+### Anti-Patterns (Do Not Use)
+
+- Mounting secrets as environment variables in the pod spec (visible in `kubectl describe pod`)
+- Storing secrets in ConfigMaps
+- Hardcoding credentials in container images or Dockerfiles
+
+---
+
+## Common Misconfiguration Detection
+
+| Misconfiguration | Risk | Fix |
+|------------------|------|-----|
+| `privileged: true` | Full host access | Remove or use specific capabilities |
+| `hostNetwork: true` | Pod shares host network stack | Use CNI networking |
+| `hostPID: true` / `hostIPC: true` | Can see/signal host processes | Remove unless debugging |
+| Wildcard RBAC verbs (`*`) | Grants all operations | List specific verbs |
+| `automountServiceAccountToken: true` on workloads | Token exposed to compromised pod | Set to `false` unless API access needed |
+| No resource limits | Pod can exhaust node resources (DoS) | Set CPU and memory limits |
+| Latest tag without digest | Image can change without notice | Pin by digest |
+| Secrets as env vars in pod spec | Visible in `kubectl describe` | Mount as files or use external secrets |
PATCH

echo "Gold patch applied."
