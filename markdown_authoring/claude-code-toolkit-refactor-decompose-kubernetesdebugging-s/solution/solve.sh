#!/usr/bin/env bash
set -euo pipefail

cd /workspace/claude-code-toolkit

# Idempotency guard
if grep -qF "| CrashLoopBackOff, OOMKilled, config error, health check, liveness probe, Image" "skills/kubernetes-debugging/SKILL.md" && grep -qF "Fix: Increase `resources.limits.memory` or fix the memory leak in the applicatio" "skills/kubernetes-debugging/references/crash-diagnosis.md" && grep -qF "> **Scope**: Service resolution, DNS debugging, port-forwarding for local testin" "skills/kubernetes-debugging/references/network-debugging.md" && grep -qF "> **Scope**: CPU throttling detection, memory limits and OOMKill analysis, ephem" "skills/kubernetes-debugging/references/resource-debugging.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/skills/kubernetes-debugging/SKILL.md b/skills/kubernetes-debugging/SKILL.md
@@ -20,9 +20,19 @@ routing:
 
 Systematic diagnosis of pod failures, networking issues, and resource problems using a structured triage flow: describe, logs, events, exec.
 
+## Reference Loading Table
+
+| Signal | Reference | Size |
+|--------|-----------|------|
+| CrashLoopBackOff, OOMKilled, config error, health check, liveness probe, ImagePullBackOff, image pull, registry auth, Pending, FailedScheduling, node affinity, taint, PVC | `references/crash-diagnosis.md` | ~140 lines |
+| service resolution, DNS, nslookup, CoreDNS, port-forward, NetworkPolicy, ingress, egress | `references/network-debugging.md` | ~50 lines |
+| CPU throttling, memory limit, OOMKill, ephemeral storage, DiskPressure, debug container, distroless, kubectl reference, rollout, exec | `references/resource-debugging.md` | ~100 lines |
+
+**Load greedily.** If the user's question touches any signal keyword, load the matching reference before responding. Multiple signals matching = load all matching references.
+
 ## Instructions
 
-### Step 1: Systematic Debugging Flow
+### Triage Flow
 
 Follow this sequence for every pod or workload issue. Do not skip steps -- many failures (scheduling, image pull, volume mount) are only visible in events and describe output, not in logs, so jumping straight to logs misses them.
 
@@ -52,302 +62,20 @@ kubectl exec -it <pod-name> -n <namespace> -c <container-name> -- /bin/sh
 
 Use read-only commands (describe, logs, get) to gather evidence before proposing any modifications. Never suggest changes based on assumptions -- gather diagnostic output first.
 
-### Step 2: CrashLoopBackOff Diagnosis
-
-CrashLoopBackOff means the container starts, exits, and Kubernetes restarts it with exponential backoff. Do not `kubectl delete pod` to "fix" this -- the replacement pod will crash the same way, and you lose the previous container's logs. Read `--previous` logs and describe events first.
-
-**OOMKilled** -- container exceeded memory limit:
-
-```bash
-# Check termination reason
-kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Last State"
-# Look for: Reason: OOMKilled
-
-# Check resource limits vs actual usage
-kubectl top pod <pod-name> -n <namespace>
-```
-
-Fix: Increase `resources.limits.memory` or fix the memory leak in the application. Do not blindly increase limits without checking actual usage first -- over-provisioning wastes cluster resources, and a memory leak will eventually exceed any limit you set. Run `kubectl top pod` under realistic load, then set limits to 1.5-2x observed peak.
-
-**Application configuration error** -- missing env vars, bad config file, wrong DB host:
-
-```bash
-# Check logs from the previous (crashed) instance
-kubectl logs <pod-name> -n <namespace> --previous
-
-# Verify environment variables are set correctly
-kubectl exec <pod-name> -n <namespace> -- env | sort
-
-# Check if ConfigMap/Secret is mounted
-kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Mounts"
-```
-
-**Health check failure** -- liveness probe kills the container:
-
-```bash
-# Check probe configuration
-kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Liveness"
-
-# Common issues:
-# - initialDelaySeconds too short for slow-starting apps
-# - Probe endpoint returns non-200 during startup
-# - Probe timeout too aggressive
-```
-
-```yaml
-# Fix: add a startup probe for slow-starting applications
-spec:
-  containers:
-    - name: app
-      startupProbe:
-        httpGet:
-          path: /healthz
-          port: 8080
-        failureThreshold: 30
-        periodSeconds: 10
-      livenessProbe:
-        httpGet:
-          path: /healthz
-          port: 8080
-        periodSeconds: 10
-        timeoutSeconds: 5
-```
-
-### Step 3: ImagePullBackOff Diagnosis
-
-The kubelet cannot pull the container image.
-
-```bash
-# Check the exact error
-kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Events"
-# Look for: Failed to pull image, ErrImagePull, ImagePullBackOff
-```
-
-**Registry authentication** -- private registry requires credentials:
-
-```bash
-# Verify imagePullSecrets exist on the pod
-kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.imagePullSecrets}'
-
-# Check if the secret exists and has valid data
-kubectl get secret <pull-secret> -n <namespace> -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d
-```
-
-**Image tag does not exist** -- typo or tag was overwritten:
-
-```bash
-# Verify the image reference
-kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[0].image}'
-
-# Test pulling manually on a node or locally
-docker pull <image-reference>
-```
-
-Do not trust `:latest` tags -- they are mutable, so the image you tested locally may differ from what the node pulled. Always use image digests or immutable tags, and verify the exact image reference with the jsonpath command above.
+### Diagnosis Routing
 
-**Network issues** -- node cannot reach the registry:
-
-```bash
-# Check if the node has network access to the registry
-kubectl debug node/<node-name> -it --image=busybox -- nslookup registry.example.com
-```
-
-### Step 4: Pending Pods
-
-Pods stuck in Pending state have not been scheduled to any node.
-
-```bash
-# Check scheduler events
-kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Events"
-# Look for: FailedScheduling, Insufficient cpu, Insufficient memory
-```
-
-**Resource constraints** -- not enough CPU or memory on any node:
-
-```bash
-# Check node capacity and allocatable resources
-kubectl describe nodes | grep -A 5 "Allocated resources"
-
-# Check resource requests across the cluster
-kubectl top nodes
-```
-
-**Node affinity or node selector mismatch**:
-
-```bash
-# Check what the pod requires
-kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.nodeSelector}'
-kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.affinity}'
-
-# Check node labels
-kubectl get nodes --show-labels
-```
-
-**Taints and tolerations**:
-
-```bash
-# Check node taints
-kubectl describe nodes | grep -A 3 "Taints"
-
-# Check pod tolerations
-kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.tolerations}'
-```
+Based on triage output, load the appropriate reference and follow its diagnosis flow:
 
-**PersistentVolumeClaim not bound**:
-
-```bash
-# Check PVC status
-kubectl get pvc -n <namespace>
-
-# Describe the PVC for events
-kubectl describe pvc <pvc-name> -n <namespace>
-```
-
-### Step 5: Networking Debugging
-
-**Service resolution** -- pod cannot reach another service:
-
-```bash
-# Verify the service exists and has endpoints
-kubectl get svc <service-name> -n <namespace>
-kubectl get endpoints <service-name> -n <namespace>
-
-# Check if endpoints are populated (empty = no matching pods)
-kubectl describe endpoints <service-name> -n <namespace>
-```
-
-**DNS debugging**:
-
-```bash
-# Run a DNS lookup from inside the cluster
-kubectl run dns-debug --rm -it --restart=Never --image=busybox:1.36 -n <namespace> -- \
-  nslookup <service-name>.<namespace>.svc.cluster.local
-
-# Check CoreDNS pods are running
-kubectl get pods -n kube-system -l k8s-app=kube-dns
-
-# Check CoreDNS logs for errors
-kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
-```
-
-**Port-forward for local testing**:
-
-```bash
-# Forward a pod port to localhost
-kubectl port-forward pod/<pod-name> -n <namespace> 8080:8080
-
-# Forward a service port to localhost
-kubectl port-forward svc/<service-name> -n <namespace> 8080:80
-
-# Test the endpoint locally
-curl -v http://localhost:8080/healthz
-```
-
-**NetworkPolicy blocking traffic** -- see kubernetes-security skill for policy patterns:
-
-```bash
-# List network policies in the namespace
-kubectl get networkpolicy -n <namespace>
-
-# Describe a specific policy to see ingress/egress rules
-kubectl describe networkpolicy <policy-name> -n <namespace>
-```
-
-### Step 6: Resource Issues
-
-**CPU throttling** -- container is being throttled by its CPU limit:
-
-```bash
-# Check current usage vs limits
-kubectl top pod <pod-name> -n <namespace> --containers
-
-# Check throttling metrics (requires metrics-server or Prometheus)
-# Look for container_cpu_cfs_throttled_periods_total in metrics
-kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Limits"
-```
-
-**Memory limits** -- OOMKill or high memory pressure:
-
-```bash
-# Check if the pod was OOMKilled
-kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.status.containerStatuses[0].lastState}'
-
-# Check current memory usage
-kubectl top pod <pod-name> -n <namespace> --containers
-
-# Check node memory pressure
-kubectl describe node <node-name> | grep -A 5 "Conditions"
-```
-
-**Ephemeral storage pressure** -- logs or temp files fill the node disk:
-
-```bash
-# Check node disk pressure condition
-kubectl describe node <node-name> | grep -A 2 "DiskPressure"
-
-# Check pod ephemeral storage usage
-kubectl describe pod <pod-name> -n <namespace> | grep -A 3 "ephemeral-storage"
-```
-
-### Step 7: kubectl Commands Reference
-
-| Command | Purpose |
-|---------|---------|
-| `kubectl describe pod <pod> -n <ns>` | Full pod status, events, conditions |
-| `kubectl logs <pod> -n <ns> --previous` | Logs from the last crashed container |
-| `kubectl logs <pod> -n <ns> --tail=100 -f` | Stream last 100 lines and follow |
-| `kubectl get events -n <ns> --sort-by='.lastTimestamp'` | Namespace events in chronological order |
-| `kubectl top pod -n <ns>` | CPU and memory usage per pod |
-| `kubectl top nodes` | CPU and memory usage per node |
-| `kubectl get pod <pod> -n <ns> -o yaml` | Full pod spec and status in YAML |
-| `kubectl exec -it <pod> -n <ns> -- /bin/sh` | Shell into a running container |
-| `kubectl port-forward pod/<pod> -n <ns> 8080:8080` | Forward pod port to localhost |
-| `kubectl debug pod/<pod> -n <ns> --image=busybox -it` | Attach ephemeral debug container |
-| `kubectl rollout status deployment/<name> -n <ns>` | Watch deployment rollout progress |
-| `kubectl rollout undo deployment/<name> -n <ns>` | Roll back to previous revision |
-
-### Step 8: Ephemeral Debug Containers
-
-When a container has no shell (distroless, scratch), use ephemeral containers:
-
-```bash
-# Attach a debug container with networking tools
-kubectl debug -it <pod-name> -n <namespace> \
-  --image=nicolaka/netshoot \
-  --target=<container-name>
-
-# Inside the debug container, you can:
-# - Check network: curl, dig, tcpdump, ss
-# - Inspect filesystem: ls /proc/1/root (target container's filesystem)
-# - Check processes: ps aux
-```
-
-```bash
-# Debug a node directly
-kubectl debug node/<node-name> -it --image=ubuntu
-
-# This creates a pod with hostPID, hostNetwork, and mounts the node filesystem at /host
-# Useful for: checking kubelet logs, node networking, disk usage
-chroot /host
-journalctl -u kubelet --no-pager --tail=50
-```
-
----
-
-## Error Handling
-
-### Error: "kubectl exec" fails with "container not running"
-Cause: The container is in CrashLoopBackOff or has not started yet.
-Solution: Use `kubectl logs --previous` to get crash logs. If the container exits immediately, check the entrypoint command and environment variables.
+| Symptom | Reference |
+|---------|-----------|
+| Pod status CrashLoopBackOff, ImagePullBackOff, or Pending | `references/crash-diagnosis.md` |
+| Service unreachable, DNS failure, connection refused | `references/network-debugging.md` |
+| CPU throttling, OOMKill, disk pressure, need debug container | `references/resource-debugging.md` |
 
 ### Error: "no endpoints available for service"
 Cause: The Service selector does not match any running pod labels.
 Solution: Compare `kubectl get svc <name> -o yaml` selector with `kubectl get pods --show-labels`. Fix the label mismatch.
 
-### Error: "kubectl debug" not available
-Cause: Ephemeral containers require Kubernetes 1.25+ and the feature gate to be enabled.
-Solution: Check cluster version with `kubectl version`. For older clusters, create a standalone debug pod in the same namespace with `kubectl run`.
-
 ---
 
 ## References
diff --git a/skills/kubernetes-debugging/references/crash-diagnosis.md b/skills/kubernetes-debugging/references/crash-diagnosis.md
@@ -0,0 +1,162 @@
+# Crash Diagnosis Reference
+
+> **Scope**: CrashLoopBackOff (OOMKilled, config errors, health check failures), ImagePullBackOff (auth, tags, network), and Pending pod diagnosis (scheduling, affinity, taints, PVC). Does NOT cover networking or resource monitoring.
+> **Version range**: Kubernetes 1.25+ (ephemeral containers assumed available)
+> **Generated**: 2026-04-16
+
+---
+
+## CrashLoopBackOff Diagnosis
+
+CrashLoopBackOff means the container starts, exits, and Kubernetes restarts it with exponential backoff. Do not `kubectl delete pod` to "fix" this -- the replacement pod will crash the same way, and you lose the previous container's logs. Read `--previous` logs and describe events first.
+
+### OOMKilled -- container exceeded memory limit
+
+```bash
+# Check termination reason
+kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Last State"
+# Look for: Reason: OOMKilled
+
+# Check resource limits vs actual usage
+kubectl top pod <pod-name> -n <namespace>
+```
+
+Fix: Increase `resources.limits.memory` or fix the memory leak in the application. Do not blindly increase limits without checking actual usage first -- over-provisioning wastes cluster resources, and a memory leak will eventually exceed any limit you set. Run `kubectl top pod` under realistic load, then set limits to 1.5-2x observed peak.
+
+### Application configuration error -- missing env vars, bad config file, wrong DB host
+
+```bash
+# Check logs from the previous (crashed) instance
+kubectl logs <pod-name> -n <namespace> --previous
+
+# Verify environment variables are set correctly
+kubectl exec <pod-name> -n <namespace> -- env | sort
+
+# Check if ConfigMap/Secret is mounted
+kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Mounts"
+```
+
+### Health check failure -- liveness probe kills the container
+
+```bash
+# Check probe configuration
+kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Liveness"
+
+# Common issues:
+# - initialDelaySeconds too short for slow-starting apps
+# - Probe endpoint returns non-200 during startup
+# - Probe timeout too aggressive
+```
+
+```yaml
+# Fix: add a startup probe for slow-starting applications
+spec:
+  containers:
+    - name: app
+      startupProbe:
+        httpGet:
+          path: /healthz
+          port: 8080
+        failureThreshold: 30
+        periodSeconds: 10
+      livenessProbe:
+        httpGet:
+          path: /healthz
+          port: 8080
+        periodSeconds: 10
+        timeoutSeconds: 5
+```
+
+---
+
+## ImagePullBackOff Diagnosis
+
+The kubelet cannot pull the container image.
+
+```bash
+# Check the exact error
+kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Events"
+# Look for: Failed to pull image, ErrImagePull, ImagePullBackOff
+```
+
+### Registry authentication -- private registry requires credentials
+
+```bash
+# Verify imagePullSecrets exist on the pod
+kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.imagePullSecrets}'
+
+# Check if the secret exists and has valid data
+kubectl get secret <pull-secret> -n <namespace> -o jsonpath='{.data.\.dockerconfigjson}' | base64 -d
+```
+
+### Image tag does not exist -- typo or tag was overwritten
+
+```bash
+# Verify the image reference
+kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.containers[0].image}'
+
+# Test pulling manually on a node or locally
+docker pull <image-reference>
+```
+
+Do not trust `:latest` tags -- they are mutable, so the image you tested locally may differ from what the node pulled. Always use image digests or immutable tags, and verify the exact image reference with the jsonpath command above.
+
+### Network issues -- node cannot reach the registry
+
+```bash
+# Check if the node has network access to the registry
+kubectl debug node/<node-name> -it --image=busybox -- nslookup registry.example.com
+```
+
+---
+
+## Pending Pods
+
+Pods stuck in Pending state have not been scheduled to any node.
+
+```bash
+# Check scheduler events
+kubectl describe pod <pod-name> -n <namespace> | grep -A 10 "Events"
+# Look for: FailedScheduling, Insufficient cpu, Insufficient memory
+```
+
+### Resource constraints -- not enough CPU or memory on any node
+
+```bash
+# Check node capacity and allocatable resources
+kubectl describe nodes | grep -A 5 "Allocated resources"
+
+# Check resource requests across the cluster
+kubectl top nodes
+```
+
+### Node affinity or node selector mismatch
+
+```bash
+# Check what the pod requires
+kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.nodeSelector}'
+kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.affinity}'
+
+# Check node labels
+kubectl get nodes --show-labels
+```
+
+### Taints and tolerations
+
+```bash
+# Check node taints
+kubectl describe nodes | grep -A 3 "Taints"
+
+# Check pod tolerations
+kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.spec.tolerations}'
+```
+
+### PersistentVolumeClaim not bound
+
+```bash
+# Check PVC status
+kubectl get pvc -n <namespace>
+
+# Describe the PVC for events
+kubectl describe pvc <pvc-name> -n <namespace>
+```
diff --git a/skills/kubernetes-debugging/references/network-debugging.md b/skills/kubernetes-debugging/references/network-debugging.md
@@ -0,0 +1,63 @@
+# Network Debugging Reference
+
+> **Scope**: Service resolution, DNS debugging, port-forwarding for local testing, and NetworkPolicy verification. Does NOT cover pod crash diagnosis or resource limits.
+> **Version range**: Kubernetes 1.25+ (ephemeral containers assumed available)
+> **Generated**: 2026-04-16
+
+---
+
+## Service Resolution -- pod cannot reach another service
+
+```bash
+# Verify the service exists and has endpoints
+kubectl get svc <service-name> -n <namespace>
+kubectl get endpoints <service-name> -n <namespace>
+
+# Check if endpoints are populated (empty = no matching pods)
+kubectl describe endpoints <service-name> -n <namespace>
+```
+
+---
+
+## DNS Debugging
+
+```bash
+# Run a DNS lookup from inside the cluster
+kubectl run dns-debug --rm -it --restart=Never --image=busybox:1.36 -n <namespace> -- \
+  nslookup <service-name>.<namespace>.svc.cluster.local
+
+# Check CoreDNS pods are running
+kubectl get pods -n kube-system -l k8s-app=kube-dns
+
+# Check CoreDNS logs for errors
+kubectl logs -n kube-system -l k8s-app=kube-dns --tail=50
+```
+
+---
+
+## Port-Forward for Local Testing
+
+```bash
+# Forward a pod port to localhost
+kubectl port-forward pod/<pod-name> -n <namespace> 8080:8080
+
+# Forward a service port to localhost
+kubectl port-forward svc/<service-name> -n <namespace> 8080:80
+
+# Test the endpoint locally
+curl -v http://localhost:8080/healthz
+```
+
+---
+
+## NetworkPolicy Blocking Traffic
+
+See kubernetes-security skill for full policy patterns.
+
+```bash
+# List network policies in the namespace
+kubectl get networkpolicy -n <namespace>
+
+# Describe a specific policy to see ingress/egress rules
+kubectl describe networkpolicy <policy-name> -n <namespace>
+```
diff --git a/skills/kubernetes-debugging/references/resource-debugging.md b/skills/kubernetes-debugging/references/resource-debugging.md
@@ -0,0 +1,104 @@
+# Resource Debugging Reference
+
+> **Scope**: CPU throttling detection, memory limits and OOMKill analysis, ephemeral storage pressure, ephemeral debug containers, and kubectl command reference table. Does NOT cover crash diagnosis root causes or networking.
+> **Version range**: Kubernetes 1.25+ (ephemeral containers assumed available)
+> **Generated**: 2026-04-16
+
+---
+
+## CPU Throttling -- container is being throttled by its CPU limit
+
+```bash
+# Check current usage vs limits
+kubectl top pod <pod-name> -n <namespace> --containers
+
+# Check throttling metrics (requires metrics-server or Prometheus)
+# Look for container_cpu_cfs_throttled_periods_total in metrics
+kubectl describe pod <pod-name> -n <namespace> | grep -A 5 "Limits"
+```
+
+---
+
+## Memory Limits -- OOMKill or high memory pressure
+
+```bash
+# Check if the pod was OOMKilled
+kubectl get pod <pod-name> -n <namespace> -o jsonpath='{.status.containerStatuses[0].lastState}'
+
+# Check current memory usage
+kubectl top pod <pod-name> -n <namespace> --containers
+
+# Check node memory pressure
+kubectl describe node <node-name> | grep -A 5 "Conditions"
+```
+
+---
+
+## Ephemeral Storage Pressure -- logs or temp files fill the node disk
+
+```bash
+# Check node disk pressure condition
+kubectl describe node <node-name> | grep -A 2 "DiskPressure"
+
+# Check pod ephemeral storage usage
+kubectl describe pod <pod-name> -n <namespace> | grep -A 3 "ephemeral-storage"
+```
+
+---
+
+## Ephemeral Debug Containers
+
+When a container has no shell (distroless, scratch), use ephemeral containers:
+
+```bash
+# Attach a debug container with networking tools
+kubectl debug -it <pod-name> -n <namespace> \
+  --image=nicolaka/netshoot \
+  --target=<container-name>
+
+# Inside the debug container, you can:
+# - Check network: curl, dig, tcpdump, ss
+# - Inspect filesystem: ls /proc/1/root (target container's filesystem)
+# - Check processes: ps aux
+```
+
+```bash
+# Debug a node directly
+kubectl debug node/<node-name> -it --image=ubuntu
+
+# This creates a pod with hostPID, hostNetwork, and mounts the node filesystem at /host
+# Useful for: checking kubelet logs, node networking, disk usage
+chroot /host
+journalctl -u kubelet --no-pager --tail=50
+```
+
+---
+
+## kubectl Commands Reference
+
+| Command | Purpose |
+|---------|---------|
+| `kubectl describe pod <pod> -n <ns>` | Full pod status, events, conditions |
+| `kubectl logs <pod> -n <ns> --previous` | Logs from the last crashed container |
+| `kubectl logs <pod> -n <ns> --tail=100 -f` | Stream last 100 lines and follow |
+| `kubectl get events -n <ns> --sort-by='.lastTimestamp'` | Namespace events in chronological order |
+| `kubectl top pod -n <ns>` | CPU and memory usage per pod |
+| `kubectl top nodes` | CPU and memory usage per node |
+| `kubectl get pod <pod> -n <ns> -o yaml` | Full pod spec and status in YAML |
+| `kubectl exec -it <pod> -n <ns> -- /bin/sh` | Shell into a running container |
+| `kubectl port-forward pod/<pod> -n <ns> 8080:8080` | Forward pod port to localhost |
+| `kubectl debug pod/<pod> -n <ns> --image=busybox -it` | Attach ephemeral debug container |
+| `kubectl rollout status deployment/<name> -n <ns>` | Watch deployment rollout progress |
+| `kubectl rollout undo deployment/<name> -n <ns>` | Roll back to previous revision |
+
+---
+
+## Error Handling
+
+### Error: "kubectl exec" fails with "container not running"
+Cause: The container is in CrashLoopBackOff or has not started yet.
+Solution: Use `kubectl logs --previous` to get crash logs. If the container exits immediately, check the entrypoint command and environment variables.
+
+### Error: "kubectl debug" not available
+Cause: Ephemeral containers require Kubernetes 1.25+ and the feature gate to be enabled.
+Solution: Check cluster version with `kubectl version`. For older clusters, create a standalone debug pod in the same namespace with `kubectl run`.
PATCH

echo "Gold patch applied."
