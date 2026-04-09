# Task: Add KVM Device Passthrough Support

## Problem

The Docker sandbox service currently does not support passing through the `/dev/kvm` device to sandbox containers. This means that workloads needing hardware virtualization acceleration (like running VMs inside sandboxes) must use slower emulation instead of KVM.

You need to add support for a `SANDBOX_KVM_ENABLED` environment variable that, when set to `true`, `1`, or `yes`, will pass the `/dev/kvm` device through to sandbox containers when they are started.

## Files to Modify

- `openhands/app_server/sandbox/docker_sandbox_service.py` - The main Docker sandbox service implementation

## Key Areas to Address

1. **Environment variable parsing**: Create a function (similar to the existing `_get_use_host_network_default()`) to read `SANDBOX_KVM_ENABLED` and return a boolean.

2. **DockerSandboxService dataclass**: Add a `kvm_enabled` boolean field to the dataclass.

3. **DockerSandboxServiceInjector**: Add a `kvm_enabled` pydantic Field that:
   - Uses the environment variable function as default_factory
   - Has a clear description explaining the KVM device passthrough feature
   - References the `SANDBOX_KVM_ENABLED` environment variable

4. **Container startup**: Modify the `start_sandbox()` method to:
   - Pass `devices=['/dev/kvm:/dev/kvm:rwm']` to the Docker container run call when `kvm_enabled=True`
   - Add appropriate logging when KVM passthrough is enabled

5. **Injector**: Ensure `kvm_enabled` is passed to `DockerSandboxService` in the `inject()` method.

## Testing

The implementation should:
- Return `True` for environment variable values `true`, `1`, `yes` (case-insensitive)
- Return `False` for empty string, `false`, `0`, `no`, or any other value
- Include appropriate type annotations and docstrings following the existing code style
- Follow the same pattern as the existing `use_host_network` feature

## Notes

- You do NOT need actual KVM hardware to complete this task - focus on the configuration and device passing logic
- Follow the existing patterns in the file for environment variable handling (see `_get_use_host_network_default()` and `use_host_network`)
- The Docker `devices` parameter accepts a list of device mappings in the format `host_path:container_path:permissions`
