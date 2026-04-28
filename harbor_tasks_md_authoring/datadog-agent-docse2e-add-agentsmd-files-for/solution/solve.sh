#!/usr/bin/env bash
set -euo pipefail

cd /workspace/datadog-agent

# Idempotency guard
if grep -qF "description: Write E2E tests for the Datadog Agent using the new-e2e framework w" ".claude/skills/write-e2e/SKILL.md" && grep -qF "arrive in **fakeintake** (a mock Datadog intake). By default the fakeintake forw" "AGENTS.md" && grep -qF "| custom environment | user-defined struct | `e2e.WithPulumiProvisioner()` | Age" "test/e2e-framework/AGENTS.md" && grep -qF "@../../CLAUDE.md" "test/e2e-framework/CLAUDE.md" && grep -qF "| `/api/v2/contlcycle` | ContainerLifecycleAggregator | `GetContainerLifecycleEv" "test/fakeintake/AGENTS.md" && grep -qF "@../../CLAUDE.md" "test/fakeintake/CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/write-e2e/SKILL.md b/.claude/skills/write-e2e/SKILL.md
@@ -0,0 +1,44 @@
+---
+name: write-e2e
+description: Write E2E tests for the Datadog Agent using the new-e2e framework with fakeintake assertions
+allowed-tools: Read, Write, Edit, Glob, Grep, Bash, Agent
+argument-hint: "<feature-or-check-name> [--platform linux|windows|both] [--env host|docker|k8s]"
+---
+
+Write end-to-end tests for the Datadog Agent using the `test/e2e-framework/` framework.
+Parse `$ARGUMENTS` to determine what to test.
+
+## Where to find what you need
+
+| What | Where |
+|------|-------|
+| Framework API (environments, provisioners, agentparams) | `test/e2e-framework/AGENTS.md` |
+| Fakeintake API (payload types, client methods, extending) | `test/fakeintake/AGENTS.md` |
+| Setup, prerequisites, running tests | `docs/public/how-to/test/e2e.md` |
+| Real tests to use as patterns | `test/new-e2e/tests/` (see lookup table in e2e-framework AGENTS.md) |
+| Check system overview | root `AGENTS.md` § "Check System" |
+| Test placement / team ownership | `CODEOWNERS` |
+| CI job definitions | `.gitlab/test/e2e/e2e.yml`, `.gitlab/windows/test/e2e/windows.yml` |
+| CI trigger rules | `.gitlab-ci.yml` (search for `.on_*_or_e2e_changes`) |
+| Examples | `test/new-e2e/examples/` |
+
+Read the first two files before writing any test. Browse examples and a few real tests
+that match your use case.
+
+## Checklist
+
+1. Read the feature's implementation to understand what payloads it sends
+2. Check if E2E tests already exist under `test/new-e2e/tests/`
+3. Place tests in the right `<area>` directory (check `CODEOWNERS`);
+   one file per platform target (e.g., `disk_nix_test.go`, `disk_win_test.go`)
+4. Verify compilation: `cd test/new-e2e && go vet ./tests/<area>/...`
+5. **Run the test locally before pushing** — compilation alone is not enough:
+   `dda inv new-e2e-tests.run --targets=./tests/<area>/...`
+   See `test/e2e-framework/AGENTS.md` § "Validating E2E tests" if it fails
+6. Check CI wiring: `grep -n 'TARGETS:.*<area>' .gitlab/test/e2e/e2e.yml`
+
+## Output
+
+Show the user: files created, how to compile-check, how to run locally
+(`dda inv new-e2e-tests.run --targets=./tests/<area>/...`), and whether
+CI changes are needed.
diff --git a/AGENTS.md b/AGENTS.md
@@ -116,7 +116,13 @@ The development configuration file should be placed at `dev/dist/datadog.yaml`.
 - Run with `dda inv test --targets=<package>`
 
 ### End-to-End Tests
-- E2E framework in `test/new-e2e/`
+- E2E tests live in `test/new-e2e/tests/` and use the framework in `test/e2e-framework/`
+- Tests provision real AWS, GCP or Azure infrastructure, deploy the agent, and assert payloads
+  arrive in **fakeintake** (a mock Datadog intake). By default the fakeintake forwards payloads to `dddev` org account.
+- Key docs: `test/e2e-framework/AGENTS.md` (framework), `test/fakeintake/AGENTS.md`
+  (intake mock), `docs/public/how-to/test/e2e.md` (setup & running)
+- Use `/write-e2e` skill or read those docs directly to write new E2E tests
+- Run locally: `dda inv new-e2e-tests.run --targets=./tests/<area>/...`
 
 ### Linting
 - Go: golangci-lint via `dda inv linter.go`
@@ -266,16 +272,42 @@ If a PR changes behavior but doesn't update the corresponding docs, comments,
 or doc strings, flag it. Stale docs lead to bugs: contributors build on
 incorrect assumptions.
 
-## Maintaining this file
+## Keeping AI context accurate
 
-This file is read by AI code reviewers (Codex reads it natively, Claude Code
-reads it via the `@AGENTS.md` include in `CLAUDE.md`). It should evolve with
-the codebase.
+AI agents read `AGENTS.md`, `CLAUDE.md`, and skill files to understand the
+codebase. These files must stay accurate — stale guidance causes recurring
+mistakes across sessions.
 
-Update this file whenever important context is missing — but keep rules
-generalizable. A good guideline covers a class of bugs, not a single incident.
-Think bias/variance: too specific and it only catches one bug; too generic and
-it's noise.
+### File hierarchy
 
-**AI reviewers:** when reviewing a PR, if you notice a gap in these guidelines,
-suggest an update to this file — either in the same PR or as a follow-up.
+```
+AGENTS.md                          ← repo-wide: architecture, workflow, review guidelines
+├── test/e2e-framework/AGENTS.md   ← E2E framework: environments, provisioners, agentparams
+├── test/fakeintake/AGENTS.md      ← fakeintake: endpoints, client API, extension guide
+├── pkg/.../AGENTS.md              ← package-level: structure, patterns, pitfalls
+└── .claude/skills/*/SKILL.md      ← task-specific: step-by-step procedures
+```
+
+Each level inherits context from its parent via `CLAUDE.md` (`@../../CLAUDE.md`
+→ `@AGENTS.md`). Keep information at the right level — don't duplicate
+repo-wide rules in sub-project files.
+
+### What to update and when
+
+| File | Update when |
+|------|-------------|
+| `AGENTS.md` (root) | Architecture, workflow, build commands, or review guidelines change |
+| Sub-project `AGENTS.md` | APIs, conventions, or extension patterns in that sub-project change |
+| `.claude/skills/*/SKILL.md` | A skill's steps, examples, or recommendations become outdated |
+
+Keep rules generalizable. A good guideline covers a class of bugs, not a single
+incident. Think bias/variance: too specific and it only catches one bug; too
+generic and it's noise.
+
+### Self-improvement expectation
+
+**AI agents:** when working on any task (reviewing, writing code, running
+tests), if you notice a gap or inaccuracy in an `AGENTS.md` or skill file, fix
+it — either in the same PR or as a follow-up. Small, incremental improvements
+are preferred over large rewrites. This creates a feedback loop where every
+session leaves the context more accurate for the next one.
diff --git a/test/e2e-framework/AGENTS.md b/test/e2e-framework/AGENTS.md
@@ -0,0 +1,174 @@
+# E2E Framework
+
+## Overview
+
+The E2E framework provides infrastructure-as-code test harnesses using Pulumi.
+It provisions real cloud infrastructure (AWS, Azure, GCP), deploys the Datadog
+Agent, and exposes typed environments for tests to interact with.
+
+Tests live in `test/new-e2e/tests/` and import this framework.
+
+## Structure
+
+```
+test/e2e-framework/
+├── testing/
+│   ├── e2e/              # Test harness: BaseSuite, Run(), SuiteOption
+│   ├── environments/     # Environment types: Host, DockerHost, Kubernetes, ECS
+│   ├── provisioners/     # Provisioner interfaces + cloud-specific implementations
+│   │   ├── aws/          # host, docker, ecs, kubernetes (eks, kindvm)
+│   │   ├── azure/        # host (linux, windows), kubernetes (aks)
+│   │   ├── gcp/          # host (linux), kubernetes (gke, openshiftvm)
+│   │   └── local/        # host (podman), kubernetes (kind)
+│   └── components/       # Test-side wrappers: RemoteHost, Agent, FakeIntake
+├── scenarios/
+│   └── aws/              # Pulumi programs: ec2, ec2docker, ecs, eks, kindvm
+├── components/
+│   ├── datadog/          # Pulumi components: agent, agentparams, fakeintake
+│   │   ├── agentparams/  # Agent configuration options (WithAgentConfig, etc.)
+│   │   └── fakeintake/   # Fakeintake deployment component
+│   ├── os/               # OS descriptors (Ubuntu, Windows, etc.)
+│   ├── kubernetes/       # K8s components (KinD, OpenShift, Helm addons)
+│   ├── docker/           # Docker compose components
+│   └── remote/           # Remote host SSH management
+├── resources/
+│   └── aws/              # Low-level Pulumi resources (EC2, ECS, EKS, IAM)
+├── common/
+│   └── config/           # Configuration (AWS account, key pairs, agent params)
+└── README.md             # Full setup and troubleshooting guide
+```
+
+## Key concepts
+
+### Environments
+
+An environment defines what infrastructure a test needs:
+
+| Type | Components | Provisioner | Use when |
+|------|-----------|-------------|----------|
+| `environments.Host` | VM + Agent + FakeIntake | `awshost.Provisioner()` | System checks, agent commands, file-based config |
+| `environments.DockerHost` | VM + Docker + FakeIntake | `awsdocker.Provisioner()` | Container checks, Docker integrations |
+| `environments.Kubernetes` | K8s cluster + Agent + FakeIntake | `awskubernetes.Provisioner()` | K8s checks, DaemonSet, Cluster Agent |
+| `environments.ECS` | ECS cluster + Agent + FakeIntake | `awsecs.Provisioner()` | ECS-specific tests |
+| custom environment | user-defined struct | `e2e.WithPulumiProvisioner()` | Agent on host + workloads on docker, multi-VM, extra services |
+
+### Provisioners
+
+Provisioners create the environment's infrastructure. Built-in provisioners
+live in `testing/provisioners/` organized by cloud provider (aws, azure, gcp, local).
+
+```go
+// Host on AWS EC2
+awshost.Provisioner(
+    awshost.WithRunOptions(
+        ec2.WithEC2InstanceOptions(ec2.WithOS(e2eos.Ubuntu2204)),
+        ec2.WithAgentOptions(
+            agentparams.WithAgentConfig(config),
+            agentparams.WithIntegration("check.d", checkConfig),
+        ),
+    ),
+)
+```
+
+### BaseSuite
+
+All E2E tests embed `e2e.BaseSuite[Env]` and use `e2e.Run()`:
+
+```go
+type mySuite struct {
+    e2e.BaseSuite[environments.Host]
+}
+
+func TestMySuite(t *testing.T) {
+    t.Parallel()
+    e2e.Run(t, &mySuite{}, e2e.WithProvisioner(awshost.Provisioner()))
+}
+```
+
+Key helpers on BaseSuite:
+- `s.Env()` — access the provisioned environment
+- `s.UpdateEnv(provisioner)` — change agent config mid-suite
+- `s.EventuallyWithT(fn, timeout, interval)` — retry assertions until they pass;
+  use `require` (not `assert`) inside the callback so failures short-circuit the
+  current retry iteration instead of accumulating silently
+
+## Agent configuration
+
+Use `agentparams` to configure the agent on provisioned infrastructure:
+
+- `WithAgentConfig(yaml)` — override `datadog.yaml`
+- `WithIntegration(name, yaml)` — add check config under `conf.d/`
+- `WithLogs()` — enable log collection
+- `WithSystemProbeConfig(yaml)` — system-probe config
+- `WithFile(path, content, useSudo)` — place arbitrary files on the host
+
+## Beyond out of the box environments
+
+The stock environments are highly customizable via provisioner options (OS,
+agent config, with/without fakeintake, etc.) — explore the `With*` options on
+each provisioner before creating a custom environment.
+
+When that's not enough, common advanced patterns:
+
+- **Custom environment structs** — define your own struct with extra components
+  (e.g., a second `RemoteHost`, multiple fakeintakes, an HTTPBin service).
+  Use `e2e.WithPulumiProvisioner()` to wire it up with inline Pulumi code.
+  Start from the examples in `test/new-e2e/examples/customenv_*` and see
+  `test/new-e2e/tests/npm/` and `test/new-e2e/tests/ha-agent/` for real usage.
+- **Custom provisioners** — environments also support custom provisioners beyond
+  the stock ones. Implement the `provisioners.Provisioner` interface to
+  target different infrastructure.
+- **`e2e.WithUntypedPulumiProvisioner()`** — escape hatch for fully custom Pulumi
+  programs when no typed environment fits.
+- **`s.UpdateEnv(provisioner)`** — re-provision the agent mid-suite (e.g., change
+  config, toggle features) without destroying the underlying infra. Widely used
+  but error-prone; may be removed in the future.
+
+### Useful suite options
+
+- **`e2e.WithDevMode()`** — keep infrastructure alive after test for faster iteration.
+- **`e2e.WithStackName(name)`** — custom Pulumi stack naming for parameterized tests.
+
+### Example tests by pattern
+
+| Pattern | Look at |
+|---------|---------|
+| Stock host test | `test/new-e2e/tests/agent-runtimes/` |
+| Custom environment (extra hosts/services) | `test/new-e2e/tests/npm/`, `test/new-e2e/tests/ha-agent/` |
+| K8s + Helm | `test/new-e2e/tests/ssi/` |
+| Multi-fakeintake | `test/new-e2e/tests/agent-runtimes/forwarder/` |
+| GPU / specialized hardware | `test/new-e2e/tests/gpu/` |
+| Windows | `test/new-e2e/tests/windows/` |
+| Docker Compose | `test/new-e2e/tests/agent-health/` |
+| ECS / Fargate | `test/new-e2e/tests/cws/` |
+
+## Validating E2E tests
+
+E2E tests provision real cloud infrastructure (~10 min per run). **Always run
+the test locally before pushing** — `go vet` catches compilation errors but not
+runtime failures:
+
+```bash
+dda inv new-e2e-tests.run --targets=./tests/<area>/...
+```
+
+Use `e2e.WithDevMode()` to keep infrastructure alive after a failure so you can
+SSH in and inspect the agent directly.
+
+## Key files
+
+- `testing/e2e/suite.go` — `BaseSuite` and `Run()` (test entry point)
+- `testing/e2e/suite_params.go` — `SuiteOption` (WithProvisioner, WithDevMode, etc.)
+- `testing/environments/host.go` — Host environment definition
+- `testing/provisioners/aws/host/host.go` — AWS host provisioner
+- `components/datadog/agentparams/params.go` — agent configuration options
+- `scenarios/aws/ec2/run.go` — EC2 + Agent + FakeIntake Pulumi program
+- `common/config/environment.go` — Pulumi config management
+- `README.md` — setup guide, troubleshooting, examples
+
+## Keeping this file accurate
+
+This file is part of the `AGENTS.md` hierarchy (see root `AGENTS.md` §
+"Keeping AI context accurate"). Update it when environments, provisioners,
+agentparams, or key APIs change. AI agents should fix inaccuracies they
+encounter during tasks.
diff --git a/test/e2e-framework/CLAUDE.md b/test/e2e-framework/CLAUDE.md
@@ -0,0 +1,2 @@
+@../../CLAUDE.md
+@AGENTS.md
diff --git a/test/fakeintake/AGENTS.md b/test/fakeintake/AGENTS.md
@@ -0,0 +1,110 @@
+# Fakeintake
+
+## Overview
+
+Fakeintake is a mock Datadog intake server used by E2E tests. It captures all
+payloads the agent sends (metrics, logs, traces, check runs, etc.) and exposes
+them via a query API so tests can assert on agent output.
+
+## Structure
+
+```
+test/fakeintake/
+├── api/              # Shared types (Payload, ResponseOverride)
+├── aggregator/       # Payload parsers — one per Datadog endpoint
+├── client/           # Go client library used by E2E tests
+├── server/           # HTTP server + in-memory store
+│   └── serverstore/  # Storage layer and payload parsers
+└── cmd/
+    ├── server/       # Server binary entry point
+    └── client/       # CLI tool (fakeintakectl)
+```
+
+## Supported endpoints
+
+| Route | Aggregator | Client method |
+|-------|-----------|---------------|
+| `/api/v2/series` | MetricAggregator | `FilterMetrics()` |
+| `/api/v1/check_run` | CheckRunAggregator | `FilterCheckRuns()` |
+| `/api/v2/logs` | LogAggregator | `FilterLogs()` |
+| `/intake/` | EventAggregator | `FilterEvents()` |
+| `/api/v0.2/traces` | TraceAggregator | `GetTraces()` |
+| `/api/v0.2/stats` | APMStatsAggregator | `GetAPMStats()` |
+| `/api/v1/collector` | ProcessAggregator | `GetProcesses()` |
+| `/api/v1/connections` | ConnectionsAggregator | `GetConnections()` |
+| `/api/v1/container` | ContainerAggregator | `GetContainers()` |
+| `/api/v2/contimage` | ContainerImageAggregator | `GetContainerImages()` |
+| `/api/v2/contlcycle` | ContainerLifecycleAggregator | `GetContainerLifecycleEvents()` |
+| `/api/v2/sbom` | SBOMAggregator | `GetSBOMs()` |
+| `/api/v2/orch` | OrchestratorAggregator | `GetOrchestratorResources()` |
+| `/api/v2/ndmflow` | NDMFlowAggregator | GetNDMFlows() |
+| `/api/v2/netpath` | NetpathAggregator | `GetLatestNetpathEvents()` |
+| `/api/v2/agenthealth` | AgentHealthAggregator | GetAgentHealth() |
+| `/support/flare` | Flare parser | `GetLatestFlare()` |
+
+## Client usage
+
+```go
+import (
+    "github.com/DataDog/datadog-agent/test/fakeintake/client"
+    "github.com/DataDog/datadog-agent/test/fakeintake/aggregator"
+)
+
+fakeintake := s.Env().FakeIntake.Client()
+
+// Filter metrics by name + tags
+metrics, err := fakeintake.FilterMetrics("system.cpu.user",
+    client.WithTags[*aggregator.MetricSeries]([]string{"env:prod"}),
+    client.WithMetricValueHigherThan(0),
+)
+
+// Filter logs by service
+logs, err := fakeintake.FilterLogs("myservice",
+    client.WithMessageContaining("error"),
+)
+
+// Filter check runs
+checks, err := fakeintake.FilterCheckRuns("ntp.in_sync")
+
+// Reset state between tests
+fakeintake.FlushServerAndResetAggregators()
+
+// Debug: list all received metric names
+names, _ := fakeintake.GetMetricNames()
+```
+
+## Adding a new payload type
+
+When the agent starts sending a new type of data to a new endpoint:
+
+1. **Create an aggregator** in `aggregator/<type>Aggregator.go`:
+   - Define a struct implementing the `PayloadItem` interface (`name()`,
+     `GetTags()`, `GetCollectedTime()`)
+   - Write a `Parse<Type>(payload api.Payload) ([]*<Type>, error)` function
+   - Create a `<Type>Aggregator` wrapping `Aggregator[*<Type>]`
+
+2. **Register the parser** in `server/serverstore/parser.go`:
+   - Add the route → parser mapping to `parserMap`
+
+3. **Add client methods** in `client/client.go`:
+   - Add the aggregator field to the `Client` struct
+   - Create `get<Type>()` to fetch from the endpoint
+   - Create public `Filter<Type>()` / `Get<Type>()` methods
+   - Add filter options (`MatchOpt[*<Type>]`) as needed
+
+4. **Add tests** for the new aggregator and client methods
+
+## Key files
+
+- `client/client.go` — main client API (filter methods, match options)
+- `aggregator/common.go` — generic `Aggregator[T]` base (compression, storage)
+- `server/server.go` — HTTP handler routing
+- `server/serverstore/in_memory.go` — payload storage
+- `api/api.go` — shared types (`Payload`, `ResponseOverride`)
+
+## Keeping this file accurate
+
+This file is part of the `AGENTS.md` hierarchy (see root `AGENTS.md` §
+"Keeping AI context accurate"). Update it when endpoints, client methods, or
+extension patterns change. AI agents should fix inaccuracies they encounter
+during tasks.
diff --git a/test/fakeintake/CLAUDE.md b/test/fakeintake/CLAUDE.md
@@ -0,0 +1,2 @@
+@../../CLAUDE.md
+@AGENTS.md
PATCH

echo "Gold patch applied."
