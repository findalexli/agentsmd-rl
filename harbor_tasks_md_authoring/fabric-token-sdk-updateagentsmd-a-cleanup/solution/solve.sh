#!/usr/bin/env bash
set -euo pipefail

cd /workspace/fabric-token-sdk

# Idempotency guard
if grep -qF "- **Focused Tests**: Modify `It(...)` to `FIt(...)` to focus, or `XIt(...)` to s" "AGENTS.md" && grep -qF "CLAUDE.md" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/AGENTS.md b/AGENTS.md
@@ -1,164 +1,234 @@
-# Gemini CLI Context: Fabric Token SDK
-
-This directory contains the **Fabric Token SDK**, a project under Hyperledger Labs that provides APIs and services for building token-based distributed applications on Hyperledger Fabric and other platforms.
-
-## Project Overview
-
-*   **Purpose:** Simplify the development of tokenized applications with support for fungible/non-fungible tokens, privacy-preserving transactions (via Idemix/zkatdlog), and atomic swaps.
-*   **Architecture:** Leverages the **Fabric Smart Client (FSC)** for transaction orchestration, storage, and wallet management.
-    *   **Driver Consistency:** Core drivers (`fabtoken`, `zkatdlog`) follow a consistent architectural pattern using common interfaces defined in `token/driver` and shared logic in `token/core/common`.
-*   **Core Components:**
-    *   `token/`: The main SDK code.
-        *   `core/`: Contains the specific driver implementations (`fabtoken`, `zkatdlog`) and shared logic.
-        *   `driver/`: Defines the interfaces that drivers must implement.
-        *   `services/`: High-level services (Identity, Network, Storage, TTX).
-        *   `sdk/`: The public-facing API for developers building on top of the SDK.
-    *   `integration/`: Integration tests and the Network Orchestrator (NWO).
-*   **Key Technologies:** Go (1.24+), Hyperledger Fabric, Fabric Smart Client, Idemix, Mathlib, Ginkgo (testing), Cobra (CLI).
-
-## Architecture & Design Patterns
-*   **Driver Pattern:** The SDK uses a plugin architecture. `token/driver` defines the interfaces (Ports). `token/core` contains the Adapters (Implementations).
-    *   **Goal:** Allow swapping the underlying token technology (e.g., from cleartext UTXO to ZK-UTXO) without changing the application logic.
-    *   **Agent Tip:** When analyzing bugs, check if the issue is in the *interface definition* (`driver`) or a specific *implementation* (`core/fabtoken` vs `core/zkatdlog`).
-*   **Service Pattern:** High-level logic is encapsulated in services (`token/services`).
-    *   **Token Transaction (TTX):** The most critical service. It orchestrates the lifecycle of a token transaction (Request -> Assemble -> Sign -> Commit).
-*   **Network Orchestrator (NWO):** Used for integration tests to programmatically define and spin up Fabric networks. It replaces manual `docker-compose` setups for testing.
-
-## Building and Running
-
-### Development Environment Setup
-1.  **Install Tools:**
-    ```bash
-    make install-tools
-    ```
-    *Tools dependency source of truth is `tools/tools.go`.*
-2.  **Download Fabric Binaries:**
-    Critical for integration tests.
-    ```bash
-    make download-fabric
-    export FAB_BINS=$PWD/../fabric/bin
-    ```
-    *Note: Do not store binaries inside the repo to avoid path issues.*
-3.  **Prepare Docker Images:**
-    Required for integration tests.
-    ```bash
-    make docker-images
-    make testing-docker-images
-    ```
-
-### Common Commands
-*   **Linting:**
-    *   Check: `make lint`
-    *   **Auto-fix:** `make lint-auto-fix` (Highly recommended before committing)
-*   **Unit Tests:**
-    *   Standard: `make unit-tests`
-    *   Race Detection: `make unit-tests-race`
-    *   Regression: `make unit-tests-regression`
-*   **Integration Tests:**
-    *   Format: `make integration-tests-<target>`
-    *   Common Targets:
-        *   `dlog-fabric-t1` (Zero-Knowledge, Basic)
-        *   `fabtoken-fabric-t1` (Cleartext, Basic)
-        *   `nft-dlog` (NFTs with Privacy)
-        *   `dvp-fabtoken` (Delivery vs Payment)
-    *   *Requires `FAB_BINS` to be set and Docker to be running.*
-*   **Cleanup:**
-    *   Artifacts: `make clean`
-    *   Containers: `make clean-all-containers`
-*   **Generate Mocks:** `go generate ./...` (uses `counterfeiter`)
-*   **Tidy Modules:** `make tidy`
-
-## Development Conventions
-
-### Source Control & Contributions
-*   **DCO Sign-off:** All commits **MUST** be signed off (`git commit -s`).
-*   **Linear History:** Use a rebase workflow; avoid merge commits.
-*   **License:** Apache License, Version 2.0.
-
-### Coding Standards (Idiomatic Go)
-*   **Error Handling:**
-    *   Handle errors explicitly.
-    *   Avoid `_` for error returns.
-    *   Use `errors.Is` and `errors.As` for checking error types.
-*   **Interfaces:**
-    *   Define small, focused interfaces on the *consumer* side.
-    *   Favor composition over inheritance.
-*   **Concurrency:**
-    *   Use goroutines and channels; avoid shared state where possible.
-    *   Use `make unit-tests-race` to catch race conditions.
-*   **Global Variables:** Avoid them to ensure testability and reduce side effects.
-*   **Linting:** Zero-tolerance policy. Use `golangci-lint` (via `make lint`) to enforce standards.
-
-### Documentation
-*   **GoDocs:** All exported functions, structs, and interfaces **MUST** have clear, concise comments explaining their purpose, parameters, and return values.
-*   **Test Documentation:** Test functions should briefly describe the scenario being tested (e.g., "Given X, when Y, then Z").
-*   **System Documentation:** Any changes to the SDK's behavior, architecture, or public API **MUST** be reflected in the `docs/` directory. Keep diagrams (PUML) and markdown files in sync with the code.
-
-### Testing Strategy
-*   **Unit Tests:** Should be co-located with the code (`*_test.go`).
-*   **Integration Tests:** Located in `integration/`. Use the **Network Orchestrator (NWO)** in `integration/nwo` to spin up ephemeral Fabric networks.
-    *   **Fabric-X:** Tests starting with `fabricx` require additional setup (`make fxconfig configtxgen fabricx-docker-images`).
-*   **Mocking:**
-    *   Use `counterfeiter` for generating mocks.
-    *   **Metrics:** Use `disabled.Provider` to avoid nil panics.
-    *   **Tracing:** Use `noop.NewTracerProvider()`.
-
-### Testing Best Practices
-*   **Frameworks:** Use `github.com/stretchr/testify/assert` for values and `github.com/stretchr/testify/require` for error checking/termination.
-*   **Table-Driven Tests:** Preferred for service logic to cover multiple edge cases efficiently.
-*   **Mock Management:**
-    *   Create a **Context Struct** (e.g., `TestContext`) to hold the object under test and all its mocks.
-    *   Use a **Setup Helper** (e.g., `newTestContext(t)`) to initialize mocks with default "happy path" behaviors.
-    *   This pattern (seen in `token/services/ttx`) drastically reduces boilerplate.
-*   **Subtests:** Use `t.Run("Scenario Name", ...)` to group related assertions.
-*   **Dependency Injection:** Design constructors to accept interfaces, facilitating easy mock injection.
-
-## Key Files & Directories
-*   `Makefile`: The central control hub. Read this to discover new targets.
-*   `go.mod`: Project dependencies.
-*   `tools/tools.go`: Tool dependencies (install with `make install-tools`).
-*   `token/`: Core SDK logic.
-    *   `driver/`: **Interfaces** defining the contract for token drivers.
-    *   `core/`: **Implementations** of drivers.
-        *   `fabtoken`: UTXO-based driver (cleartext).
-        *   `zkatdlog`: UTXO-based driver with Zero-Knowledge Privacy (Idemix).
-    *   `services/`: High-level services consumed by the SDK.
-        *   `identity/`: Manages user identities and MSP interactions.
-        *   `network/`: Handles communication with the Fabric network (or other DLTs).
-        *   `ttx/`: **Token Transaction (TTX)** service for orchestration and atomic swaps.
-    *   `sdk/`: Public API entry points for applications.
-*   `integration/`: Integration tests.
-    *   `nwo/`: **Network Orchestrator** for spinning up test networks.
-    *   `token/`: Actual integration test suites (e.g., `fungible`, `nft`, `dvp`).
-
-## Debugging & Advanced Testing
-*   **Focused Integration Tests:**
-    *   Use `TEST_FILTER` to run specific tests (uses Ginkgo labels).
-        ```bash
-        # Run only tests matching label "T1" in the dlog-fabric suite
-        make integration-tests-dlog-fabric TEST_FILTER="T1"
-        ```
-    *   Alternatively, modify the test code: change `It("...", ...)` to `FIt("...", ...)` to focus, or `XIt("...", ...)` to skip. **Do not commit these changes.**
-*   **Locating Logs:**
-    *   **Integration Test Logs:** Found in the system's temporary directory (e.g., `/tmp/fsc-integration-<random>/...`).
-    *   **Container Logs:** Use `docker logs <container_name>` to inspect running containers.
-    *   **Tip:** To persist logs for debugging, you may temporarily modify the test to use `NewLocalTestSuite` (see `integration/token/test_utils.go`), which outputs to `./testdata`.
-*   **Debugging Helpers:**
-    *   **Wait for Input:** In integration tests, use `time.Sleep()` or a pause loop if you need to manually inspect the Docker state (containers will be torn down on test exit unless configured otherwise).
-    *   **Preserve Network:** Check if the Make target supports a `no-cleanup` option or manually comment out the cleanup code in the test suite `AfterSuite`.
-
-## Troubleshooting
-*   **"Chaincode packaging failed":** Usually means `FAB_BINS` is not set or points to an invalid location.
-*   **Docker errors:** Ensure `make testing-docker-images` has been run.
-*   **Linting errors on commit:** Run `make lint-auto-fix`.
-*   **Test timeouts:** Integration tests can be slow. Ensure you have allocated enough resources to Docker.
-
-## Workflow Rules
-
-- Before implementing any task, create a `plan.md` file in the project root containing:
-    - A clear description of the goal
-    - A numbered list of implementation steps
-    - An "Implementation Progress" section with each step marked as `[ ] Pending`
-- As you complete each step, update `plan.md` immediately, marking the step as `[x] Done` and adding a brief note about what was changed
-- If you encounter a blocker or make a significant decision, log it under a `## Notes & Decisions` section in `plan.md`
-- Mark the plan as `✅ COMPLETE` once all steps are done
\ No newline at end of file
+# Fabric Token SDK
+
+> **Performance Tip**: Use `Ctrl+F` to jump to sections using anchor links (e.g., `#building-and-running`)
+
+## 🚀 Quick Reference Commands
+
+### Testing
+- `make unit-tests` - Run unit tests
+- `make unit-tests-race` - Unit tests with race detector
+- `make integration-tests-fabtoken-fabric-t1` - Fabtoken integration tests
+- `make integration-tests-dlog-fabric-t1 TEST_FILTER="T1"` - ZK integration tests with T1 filter
+
+### Development & CI Preparation
+- `make fmt` - Format code using gofmt
+- `make lint` - Check code style
+- `make lint-auto-fix` - Auto-fix linting issues (recommended pre-commit)
+- `make install-tools` - Install development dependencies
+- `make checks` - Run all pre-CI checks (license, fmt, vet, etc.)
+- `make download-fabric` - Download Fabric binaries
+- `make docker-images` - Prepare Docker images
+- `make testing-docker-images` - Prepare test Docker images
+
+### Maintenance
+- `make clean` - Remove build artifacts
+- `make clean-all-containers` - Remove Docker containers
+- `make tidy` - Synchronize Go dependencies
+- `go generate ./...` - Generate mocks
+
+## 📁 Project Structure
+```
+token/
+├── core/          # Driver implementations (fabtoken, zkatdlog)
+├── driver/        # Interface definitions (ports)
+├── services/      # High-level services (identity, network, ttx, storage)
+└── sdk/           # Public API entry points
+integration/
+├── nwo/           # Network Orchestrator for test networks
+└── token/         # Actual test suites (fungible, nft, dvp, etc.)
+```
+
+## 🔧 Development Workflow
+
+### 1. Setup (One-time)
+```bash
+make install-tools
+make download-fabric
+export FAB_BINS=$PWD/../fabric/bin
+make docker-images
+make testing-docker-images
+```
+
+### 2. Daily Development
+```bash
+# Code quality
+make lint-auto-fix
+make checks
+
+# Testing
+make unit-tests          # Standard
+make unit-tests-race     # With race detection
+make integration-tests-fabtoken-fabric-t1  # Integration tests
+```
+
+### 3. Debugging
+```bash
+# Performance profiling
+go test -cpuprofile=cpu.out ./...
+go test -memprofile=mem.out ./...
+
+# Focused testing
+make integration-tests-dlog-fabric TEST_FILTER="T1"
+```
+
+## 🐛 Troubleshooting Quick Reference
+
+- **Chaincode packaging failed**: Verify `FAB_BINS` is set correctly and points to valid Fabric binaries
+- **Docker errors**: Run `make testing-docker-images`
+- **Linting errors on commit**: Run `make lint-auto-fix`
+- **Test timeouts**: Increase Docker resource allocation
+- **Permission denied**: `chmod +x` on Fabric binaries in `$FAB_BINS`
+- **Container conflicts**: `make clean-all-containers`
+- **Go module issues**: `make tidy`
+- **Mock generation failures**: `make install-tools` (ensures counterfeiter is installed)
+
+## 🔄 CI Workflow Overview
+
+To ensure your commits pass CI automatically, understand what runs:
+
+### 🔧 Pre-Merge Checks (GitHub Actions)
+All PRs and pushes to `main` trigger these workflows:
+
+1. **Checks Job** (Prerequisite):
+   - License verification
+   - Code formatting (`gofmt`, `goimports`)
+   - Static analysis (`govet`, `staticcheck`, `ineffassign`, `misspell`)
+   - *Run locally with:* `make checks`
+
+2. **Unit Testing**:
+   - Race detector enabled tests
+   - Regression tests
+   - Coverage reporting to Coveralls
+
+3. **Integration Testing** (Extensive Matrix):
+   - Fabtoken (cleartext tokens): t1-t5
+   - ZKATDLog (privacy tokens): t1-t13
+   - Fabric-X, Interop, NFT, DVP, Update tests
+   - Stress tests
+   - All with coverage reporting
+
+4. **Separate Workflows**:
+   - **golangci-lint**: Comprehensive linting (30 min timeout)
+   - **Markdown links**: Validates all doc links
+   - **CodeQL**: Security analysis (weekly + on push/PR)
+
+### 💡 Best Practices for CI Success
+- **Always run** `make checks` and `make lint-auto-fix` before committing
+- **Verify** `FAB_BINS` is set for integration test compatibility
+- **Address** all linting and static check warnings promptly
+- **Keep** dependencies updated with `make tidy`
+
+## 🏗️ Architecture Overview
+
+### Core Patterns
+- **Driver Pattern**: Swappable token technologies via interfaces in `token/driver`
+- **Service Pattern**: Encapsulated high-level logic in `token/services`
+- **TTX Service**: Orchestrates token transaction lifecycle (Request → Assemble → Sign → Commit)
+
+### Key Technologies
+- Go 1.24+
+- Hyperledger Fabric
+- Fabric Smart Client (FSC)
+- Idemix/zkatdlog (privacy)
+- Mathlib
+- Ginkgo (testing framework)
+- Cobra (CLI framework)
+
+## 🧪 Testing Strategy
+
+### Unit Tests
+- Located alongside implementation code (`*_test.go`)
+- Use testify for assertions (`assert` for values, `require` for error handling)
+- Prefer table-driven tests for service logic
+- Use context struct pattern to minimize mock boilerplate
+
+### Integration Tests
+- Located in `integration/` directory
+- Utilize Network Orchestrator (NWO) for ephemeral Fabric networks
+- Use `TEST_FILTER` environment variable with Ginkgo labels for focused testing
+- Example: `TEST_FILTER="T1"` runs only tests with T1 label
+
+### Mocking Best Practices
+- Generate mocks with `counterfeiter` (`go generate ./...`)
+- Use `disabled.Provider` for metrics to avoid nil panics
+- Use `noop.NewTracerProvider()` for tracing
+- Employ Context Struct + Setup Helper pattern (see `token/services/ttx` for example)
+
+## 📝 Development Conventions
+
+### Coding Standards
+- **Error Handling**: Handle errors explicitly; avoid blank identifier for errors
+- **Interfaces**: Define small, focused interfaces on consumer side; favor composition
+- **Concurrency**: Use goroutines and channels; avoid shared state; validate with race detector
+- **Globals**: Avoid global variables for testability
+- **Documentation**: All exported functions MUST have Godoc comments
+
+### Git Workflow
+- **DCO Sign-off**: All commits MUST be signed off (`git commit -s`)
+- **Linear History**: Use rebase workflow; avoid merge commits
+- **License**: Apache License, Version 2.0
+
+### Plan Documentation (Workflow Rule)
+Before implementing any task:
+1. Create `plan.md` in project root with:
+   - Clear goal description
+   - Numbered implementation steps
+   - "Implementation Progress" section with `[ ] Pending` checkboxes
+2. Update immediately when completing steps: `[x] Done` + brief change notes
+3. Log blockers/decisions under `## Notes & Decisions`
+4. Mark plan as `✅ COMPLETE` when finished
+
+## 🔍 Debugging & Advanced Testing
+
+### Log Locations
+- **Integration Tests**: System temp directory (`/tmp/fsc-integration-<random>/...`)
+- **Containers**: `docker logs <container_name>`
+- **Persisted Logs**: Temporarily modify test to use `NewLocalTestSuite` (outputs to `./testdata`)
+
+### Debugging Techniques
+- **Manual Inspection**: Use `time.Sleep()` or pause loops in tests to inspect Docker state
+- **Network Preservation**: Check for `no-cleanup` option or manually comment test suite cleanup
+- **Focused Tests**: Modify `It(...)` to `FIt(...)` to focus, or `XIt(...)` to skip (never commit these changes)
+
+## 📚 Key Files & Directories
+- `Makefile`: Central control hub - read to discover targets
+- `go.mod`: Project dependencies
+- `tools/tools.go`: Tool dependencies source of truth (install with `make install-tools`)
+- `token/`: Core SDK logic
+- `integration/`: Integration tests and Network Orchestrator
+
+## 🔄 CI Workflow Overview
+
+To ensure your commits pass CI automatically, understand what runs:
+
+### 🔧 Pre-Merge Checks (GitHub Actions)
+All PRs and pushes to `main` trigger these workflows:
+
+1. **Checks Job** (Prerequisite):
+   - License verification
+   - Code formatting (`gofmt`, `goimports`)
+   - Static analysis (`govet`, `staticcheck`, `ineffassign`, `misspell`)
+   - *Run locally with:* `make checks`
+
+2. **Unit Testing**:
+   - Race detector enabled tests
+   - Regression tests
+   - Coverage reporting to Coveralls
+
+3. **Integration Testing** (Extensive Matrix):
+   - Fabtoken (cleartext tokens): t1-t5
+   - ZKATDLog (privacy tokens): t1-t13
+   - Fabric-X, Interop, NFT, DVP, Update tests
+   - Stress tests
+   - All with coverage reporting
+
+4. **Separate Workflows**:
+   - **golangci-lint**: Comprehensive linting (30 min timeout)
+   - **Markdown links**: Validates all doc links
+   - **CodeQL**: Security analysis (weekly + on push/PR)
+
+### 💡 Best Practices for CI Success
+- **Always run** `make checks` and `make lint-auto-fix` before committing
+- **Verify** `FAB_BINS` is set for integration test compatibility
+- **Address** all linting and static check warnings promptly
+- **Keep** dependencies updated with `make tidy`
\ No newline at end of file
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -0,0 +1 @@
+@AGENTS.md
\ No newline at end of file
PATCH

echo "Gold patch applied."
