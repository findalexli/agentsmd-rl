#!/usr/bin/env bash
set -euo pipefail

cd /workspace/datadog-agent

# Idempotency guard
if grep -qF "This rule provides troubleshooting tips and code patterns not covered in the mai" ".cursor/rules/e2e_tests.mdc" && grep -qF "**Note**: The `-c ddagent:imagePullPassword` flags in the test command are for t" "test/new-e2e/tests/gpu/AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.cursor/rules/e2e_tests.mdc b/.cursor/rules/e2e_tests.mdc
@@ -0,0 +1,151 @@
+---
+description: Guidelines for working with E2E tests in the datadog-agent repository
+alwaysApply: false
+globs: test/new-e2e/**/*
+---
+
+# E2E Test Development Guidelines
+
+This rule provides troubleshooting tips and code patterns not covered in the main documentation. For prerequisites, setup, and basic usage, see `docs/public/how-to/test/e2e.md`.
+
+## AWS Account Configuration
+
+**CRITICAL**: E2E tests require specific AWS accounts:
+- **Local execution**: Use `agent-sandbox` AWS account
+- **CI execution**: Uses `agent-qa` AWS account
+
+Configure `~/.test_infra_config.yaml`:
+
+```yaml
+configParams:
+  aws:
+    keyPairName: "your-keypair-name"
+    publicKeyPath: "/path/to/your/public/key"
+  agent:
+    apiKey: "00000000000000000000000000000000"
+```
+
+**Common Error**: `User: arn:aws:sts::... is not authorized to perform: ecr:BatchGetImage`
+**Solution**: Verify AWS account configuration. Ensure you're authenticated with `aws-vault login sso-agent-sandbox-account-admin`.
+
+### Kubernetes Tests with ECR Authentication
+
+For Kubernetes tests that need to pull images from ECR:
+
+```bash
+E2E_DEV_MODE=true dda inv -- -e new-e2e-tests.run \
+  --targets ./tests/gpu \
+  -c ddagent:imagePullRegistry=669783387624.dkr.ecr.us-east-1.amazonaws.com \
+  -c ddagent:imagePullPassword=$(aws-vault exec sso-agent-qa-read-only -- aws ecr get-login-password) \
+  -c ddagent:imagePullUsername=AWS \
+  --run TestGPUK8sSuiteUbuntu2204
+```
+
+Note: The `-c ddagent:imagePull*` flags are for the Kubernetes agent to pull images, not for the EC2 instance. The EC2 instance uses its IAM role.
+
+## Provisioners and Environments
+
+Provisioners are in `test/e2e-framework/testing/provisioners/`:
+
+| Provider | Paths |
+|----------|-------|
+| AWS | `aws/host`, `aws/docker`, `aws/ecs`, `aws/kubernetes/eks`, `aws/kubernetes/kindvm` |
+| Azure | `azure/host/linux`, `azure/host/windows`, `azure/kubernetes/aks` |
+| GCP | `gcp/host/linux`, `gcp/kubernetes/gke` |
+| Local | `local/host/podman`, `local/kubernetes/kind` |
+
+**Key concepts:**
+- **Typed Provisioners**: Use `component.Export()` to match Environment fields with Pulumi resources.
+- **Untyped Provisioners**: Environment needs `import` tag to match resource keys.
+
+**Environments** (`test/e2e-framework/testing/environments/`):
+- `environments.Host`: fields `RemoteHost`, `FakeIntake`, `Agent`, `Updater`
+- `environments.Kubernetes`: fields `KubernetesCluster`, `FakeIntake`, `Agent`
+- `environments.DockerHost`: VM with Docker and agent in containers
+- `environments.ECS`: ECS cluster environment
+
+## Common Patterns
+
+### Installing Docker with ECR Support
+
+```go
+installEcrCredsHelperCmd, err := ec2.InstallECRCredentialsHelper(awsEnv, host)
+dockerManager, err := docker.NewManager(&awsEnv, host, utils.PulumiDependsOn(installEcrCredsHelperCmd))
+```
+
+### Pulling Docker Images
+
+```go
+func downloadDockerImages(e *aws.Environment, vm *componentsremote.Host, images []string, dependsOn ...pulumi.Resource) ([]pulumi.Resource, error) {
+    var cmds []pulumi.Resource
+    for i, image := range images {
+        pullCmd := makeRetryCommand(fmt.Sprintf("docker pull %s", image), dockerPullMaxRetries)
+        cmd, err := vm.OS.Runner().Command(
+            e.CommonNamer().ResourceName("docker-pull", strconv.Itoa(i)),
+            &command.Args{Create: pulumi.Sprintf("/bin/bash -c \"%s\"", pullCmd)},
+            utils.PulumiDependsOn(dependsOn...),
+        )
+        if err != nil {
+            return nil, err
+        }
+        cmds = append(cmds, cmd)
+    }
+    return cmds, nil
+}
+```
+
+### Diagnose Function
+
+```go
+provisioner.SetDiagnoseFunc(awskubernetes.KindDiagnoseFunc)
+```
+
+## Troubleshooting
+
+### ECR Authentication Issues
+
+When EC2 instances fail to pull images from ECR:
+1. Verify `~/.test_infra_config.yaml` is configured for `agent-sandbox`
+2. Install ECR credentials helper: `ec2.InstallECRCredentialsHelper()`
+3. Install Docker: `docker.NewManager()` configures Docker to use the credentials helper
+
+Root causes:
+- Running in wrong AWS account (should be `agent-sandbox` for local)
+- EC2 instance role missing ECR permissions
+
+### Pulumi Lock Issues
+
+If you see: `error: the stack is currently locked by 1 lock(s)...`
+
+```bash
+# Remove local Pulumi locks
+dda inv new-e2e-tests.clean
+
+# Also clean local stack state
+dda inv new-e2e-tests.clean -s
+
+# Clear local test output
+dda inv new-e2e-tests.clean --output
+```
+
+If cleanup says "Cleanup supported for local state only":
+```bash
+pulumi login --local
+```
+
+### Test Output Location
+
+Output stored in `~/e2e-output/<TestName>_<timestamp>/`:
+- Pulumi logs
+- Agent logs
+- Agent flares (on failure)
+- Test artifacts
+
+## Key Files
+
+- `test/e2e-framework/testing/e2e/suite.go`: Core BaseSuite and Run function
+- `test/e2e-framework/testing/environments/`: Environment definitions
+- `test/e2e-framework/testing/provisioners/`: Provisioner implementations
+- `test/e2e-framework/components/`: Pulumi component definitions
+- `test/e2e-framework/scenarios/`: Pre-built scenario configurations
+- `test/e2e-framework/resources/`: Cloud-specific resource definitions
diff --git a/test/new-e2e/tests/gpu/AGENTS.md b/test/new-e2e/tests/gpu/AGENTS.md
@@ -0,0 +1,129 @@
+# GPU E2E Tests
+
+## Overview
+
+GPU e2e tests are located in `test/new-e2e/tests/gpu/` and verify GPU monitoring functionality in both host and Kubernetes environments.
+
+## Test Suites
+
+### Host Tests
+- `TestGPUHostSuiteUbuntu2204`: Tests GPU monitoring on Ubuntu 22.04 host
+- `TestGPUHostSuiteUbuntu1804Driver430`: Tests on Ubuntu 18.04 with driver 430
+- `TestGPUHostSuiteUbuntu1804Driver510`: Tests on Ubuntu 18.04 with driver 510
+
+### Kubernetes Tests
+- `TestGPUK8sSuiteUbuntu2204`: Tests GPU monitoring in Kubernetes on Ubuntu 22.04
+
+## Key Components
+
+### Test Files
+- `gpu_test.go`: Main test suite definitions and test cases
+- `provisioner.go`: Infrastructure provisioning logic
+- `capabilities.go`: Environment-specific capabilities (host vs k8s)
+
+### Test Cases
+
+1. **TestGPUCheckIsEnabled**: Verifies GPU check is enabled and running
+2. **TestGPUSysprobeEndpointIsResponding**: Checks sysprobe GPU endpoint
+3. **TestLimitMetricsAreReported**: Verifies limit metrics (gpu.core.limit, gpu.memory.limit)
+4. **TestVectorAddProgramDetected**: Tests that GPU workloads are detected
+5. **TestNvmlMetricsPresent**: Verifies NVML metrics are collected
+6. **TestWorkloadmetaHasGPUs**: Checks workloadmeta contains GPU entities
+7. **TestZZAgentDidNotRestart**: Ensures agent didn't restart during tests
+
+## Provisioning
+
+### Host Provisioner
+
+The host provisioner (`gpuHostProvisioner`):
+1. Creates EC2 GPU instance (g4dn.xlarge)
+2. Validates GPU devices are present
+3. Installs ECR credentials helper
+4. Installs Docker
+5. Pre-pulls test images
+6. Validates Docker can run CUDA workloads
+7. Installs Datadog agent
+
+### Kubernetes Provisioner
+
+The Kubernetes provisioner (`gpuK8sProvisioner`):
+1. Creates EC2 GPU instance
+2. Validates GPU devices
+3. Installs ECR credentials helper
+4. **Installs Docker** (required for pre-pulling CUDA image)
+5. **Pre-pulls CUDA sanity check image** (avoids ECR auth issues)
+6. Creates Kind cluster with NVIDIA GPU operator
+7. Deploys Datadog agent via Helm
+
+## Common Issues and Solutions
+
+### ECR Authentication Failures
+
+**Problem**: EC2 instance cannot pull images from ECR during provisioning
+
+**Error**: `User: arn:aws:sts::... is not authorized to perform: ecr:BatchGetImage`
+
+**Root Cause**: Running in the wrong AWS account. E2E tests **must** run in the `agent-sandbox` AWS account.
+
+**Solution**:
+1. Verify `~/.test_infra_config.yaml` is configured correctly:
+   ```yaml
+   configParams:
+     aws:
+       keyPairName: "your-keypair-name"
+       publicKeyPath: "/path/to/your/public/key"
+   ```
+2. Ensure you're authenticated with the correct account:
+   ```bash
+   aws-vault login sso-agent-sandbox-account-admin
+   ```
+3. The default environment is `agent-sandbox` (see `test/new-e2e/pkg/runner/local_profile.go`). If you're in a different account, EC2 instances won't have the correct IAM permissions.
+
+**Note**: The `-c ddagent:imagePullPassword` flags in the test command are for the Kubernetes agent to pull images, not for the EC2 instance. The EC2 instance uses its IAM role, which requires the correct AWS account setup.
+
+## Running Tests
+
+### Kubernetes Tests
+
+```bash
+E2E_DEV_MODE=true dda inv -- -e new-e2e-tests.run \
+  --targets ./tests/gpu \
+  -c ddagent:imagePullRegistry=669783387624.dkr.ecr.us-east-1.amazonaws.com \
+  -c ddagent:imagePullPassword=$(aws-vault exec sso-agent-qa-read-only -- aws ecr get-login-password) \
+  -c ddagent:imagePullUsername=AWS \
+  --run TestGPUK8sSuiteUbuntu2204 \
+  2>&1 | tee /tmp/gpu_test_output.log
+```
+
+### Host Tests
+
+```bash
+E2E_DEV_MODE=true dda inv -- -e new-e2e-tests.run \
+  --targets ./tests/gpu \
+  --run TestGPUHostSuiteUbuntu2204
+```
+
+## System Data Configuration
+
+Each system has specific configuration:
+
+```go
+gpuSystemUbuntu2204: {
+    ami:                          "ami-03ee78da2beb5b622",
+    os:                           os.Ubuntu2204,
+    cudaSanityCheckImage:         "nvidia/cuda:12.6.3-base-ubuntu22.04",
+    hasEcrCredentialsHelper:      false, // needs to be installed
+    hasAllNVMLCriticalAPIs:       true,
+    supportsSystemProbeComponent: true,
+}
+```
+
+## GPU Instance Type
+
+Tests use `g4dn.xlarge` (the cheapest GPU instance type) with NVIDIA Tesla T4 GPUs.
+
+## Notes
+
+- Tests are **not to be run in parallel** as they wait for checks to be available
+- Some tests skip if the system doesn't have all NVML APIs or system-probe support
+- Flaky test markers are used for known transient issues (Pulumi errors, unattended-upgrades, rate limits)
PATCH

echo "Gold patch applied."
