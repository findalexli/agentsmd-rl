#!/bin/bash
set -e

cd /workspace/OpenHands

# Check if already patched (idempotency check)
if grep -q "_get_kvm_enabled_default" openhands/app_server/sandbox/docker_sandbox_service.py; then
    echo "Patch already applied, skipping"
    exit 0
fi

# Apply the gold patch
cat <<'PATCH' | git apply -
diff --git a/openhands/app_server/sandbox/docker_sandbox_service.py b/openhands/app_server/sandbox/docker_sandbox_service.py
index 4225a1434503..e99f60e080b8 100644
--- a/openhands/app_server/sandbox/docker_sandbox_service.py
+++ b/openhands/app_server/sandbox/docker_sandbox_service.py
@@ -52,6 +52,12 @@ def _get_use_host_network_default() -> bool:
     return value.lower() in ('true', '1', 'yes')


+def _get_kvm_enabled_default() -> bool:
+    """Get the default value for kvm_enabled from environment variables."""
+    value = os.getenv('SANDBOX_KVM_ENABLED', '')
+    return value.lower() in ('true', '1', 'yes')
+
+
 class VolumeMount(BaseModel):
     """Mounted volume within the container."""

@@ -95,6 +101,7 @@ class DockerSandboxService(SandboxService):
     docker_client: docker.DockerClient = field(default_factory=get_docker_client)
     startup_grace_seconds: int = STARTUP_GRACE_SECONDS
     use_host_network: bool = False
+    kvm_enabled: bool = False

     def _find_unused_port(self) -> int:
         """Find an unused port on the host machine."""
@@ -435,9 +442,17 @@ async def start_sandbox(
         if self.use_host_network:
             _logger.info(f'Starting sandbox {container_name} with host network mode')

+        # Determine devices to pass through (e.g., /dev/kvm for hardware virtualization)
+        devices = ['/dev/kvm:/dev/kvm:rwm'] if self.kvm_enabled else None
+
+        if self.kvm_enabled:
+            _logger.info(
+                f'Starting sandbox {container_name} with KVM device passthrough'
+            )
+
         try:
             # Create and start the container
-            container = self.docker_client.containers.run(  # type: ignore[call-overload]
+            container = self.docker_client.containers.run(  # type: ignore[call-overload,misc]
                 image=sandbox_spec.id,
                 command=sandbox_spec.command,  # Use default command from image
                 remove=False,
@@ -459,6 +474,8 @@ async def start_sandbox(
                 else None,
                 # Network mode: 'host' for host networking, None for default bridge
                 network_mode=network_mode,
+                # Device passthrough for KVM hardware virtualization
+                devices=devices,
             )

             sandbox_info = await self._container_to_sandbox_info(container)
@@ -620,6 +637,16 @@ class DockerSandboxServiceInjector(SandboxServiceInjector):
             'is problematic. Configure via AGENT_SERVER_USE_HOST_NETWORK environment variable.'
         ),
     )
+    kvm_enabled: bool = Field(
+        default_factory=_get_kvm_enabled_default,
+        description=(
+            'Whether to pass through /dev/kvm to sandbox containers for hardware '
+            'virtualization support. When enabled, sandboxes can run KVM-accelerated '
+            'virtual machines instead of using slower emulation. Requires the host '
+            'to have KVM available (/dev/kvm must exist and be accessible). '
+            'Configure via SANDBOX_KVM_ENABLED environment variable.'
+        ),
+    )

     async def inject(
         self, state: InjectorState, request: Request | None = None
@@ -654,4 +681,5 @@ async def inject(
                 extra_hosts=self.extra_hosts,
                 startup_grace_seconds=self.startup_grace_seconds,
                 use_host_network=self.use_host_network,
+                kvm_enabled=self.kvm_enabled,
             )
PATCH

echo "Patch applied successfully"
