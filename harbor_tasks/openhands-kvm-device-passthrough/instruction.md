# Add KVM Device Passthrough Support

## Problem

The Docker sandbox service does not currently support passing through the `/dev/kvm` device to sandbox containers. This prevents sandboxes from running KVM-accelerated virtual machines, forcing them to use slower emulation instead. When a user requests hardware virtualization support, the sandbox should transparently provide access to the host's KVM device.

## Background

The `DockerSandboxService` class manages sandbox lifecycle (create, start, stop). The `start_sandbox` method currently does not pass any device nodes to the Docker container. There is an existing pattern for boolean configuration that reads from environment variables — see the existing `_get_use_host_network_default()` function and how `use_host_network` is plumbed from injector to service.

## Requirements

1. **Environment-based configuration**: The sandbox service should support an environment variable that controls whether KVM device passthrough is enabled. Truthy values should include `'true'`, `'1'`, `'yes'` (case-insensitive). All other values should be falsy.

2. **Service-level flag**: The `DockerSandboxService` class needs a boolean attribute to track whether KVM passthrough is enabled. This flag should be plumbed from the configuration layer into the service instance.

3. **Device passthrough**: When KVM passthrough is enabled, the `start_sandbox` method should pass the host's KVM device node to the container. The device should be mounted with read-write-mainly access (`rwm`).

4. **Informative logging**: When KVM passthrough is active, an informational log message should be emitted at sandbox start time.

5. **Injector configuration**: The `DockerSandboxServiceInjector` class needs a field that reads the environment variable default and carries the value into the service instance. The field's description should document the environment variable name.

## Relevant Files

- `openhands/app_server/sandbox/docker_sandbox_service.py` - Contains both `DockerSandboxService` and `DockerSandboxServiceInjector` classes

## What to Implement

Add a `_get_kvm_enabled_default()` function that reads the `SANDBOX_KVM_ENABLED` environment variable and returns a boolean. Follow the same pattern as `_get_use_host_network_default()`.

The injector class should have a `kvm_enabled` field (boolean, defaulting via the factory function) with a description that mentions the `SANDBOX_KVM_ENABLED` environment variable. When `inject()` creates a `DockerSandboxService`, it should pass `kvm_enabled=self.kvm_enabled`.

The `DockerSandboxService` class should have a `kvm_enabled` dataclass field (default `False`). In `start_sandbox`, when `kvm_enabled` is true, construct a devices list containing the KVM device path and pass it to `docker_client.containers.run()` via a `devices` parameter.

The exact device string to pass is `/dev/kvm:/dev/kvm:rwm` — the host path, container path, and mode. Use a variable named `devices` when constructing the list.

## Verification

After implementation:
- Import `_get_kvm_enabled_default` from the module — it should be callable with no arguments and return a boolean
- Setting `SANDBOX_KVM_ENABLED=true` (and variants like `1`, `yes`) should cause the function to return `True`
- The `DockerSandboxService` class should accept `kvm_enabled` as an `__init__` parameter with a default of `False`
- The `start_sandbox` source should contain a `devices` variable constructed based on `kvm_enabled`
- The `devices` parameter should be passed to `containers.run()`
- The `DockerSandboxServiceInjector.inject` method should pass `kvm_enabled` when creating the service
