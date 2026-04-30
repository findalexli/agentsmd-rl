#!/usr/bin/env bash
set -euo pipefail

cd /workspace/aiconfigurator

# Idempotency guard
if grep -qF "- **Dynamo profiler** (https://github.com/ai-dynamo/dynamo/tree/main/components/" ".claude/rules/generator-development.md" && grep -qF "| `src/aiconfigurator/generator/config/deployment_config.yaml` | Input schema: ~" ".claude/rules/generator/config_schema.md" && grep -qF "| 2. Templates | `src/aiconfigurator/generator/config/backend_templates/<backend" ".claude/rules/generator/cross_module_impact.md" && grep -qF "| Missing parameter in one backend | #579 | Rule not added | `.rule` file for th" ".claude/rules/generator/debugging.md" && grep -qF "| `build_config` nesting is version-dependent | SILENT | Pre-1.2.0rc5: inside `b" ".claude/rules/generator/guard_rails.md" && grep -qF "coordinated changes across multiple files. Getting any step wrong results in dep" ".claude/rules/generator/new_backend_version.md" && grep -qF "agg max_num_tokens = ((max_batch_size + SlaConfig.isl + 1500 + tokens_per_block " ".claude/rules/generator/rule_authoring.md" && grep -qF "- **New version templates**: Copy the closest prior version, modify. NEVER edit " ".claude/rules/generator/template_authoring.md" && grep -qF "runtime in CI, silent regressions, and test coverage gaps. This reference define" ".claude/rules/generator/testing.md" && grep -qF "This file adds an explicit guard for generator rule edits." "AGENTS.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/rules/generator-development.md b/.claude/rules/generator-development.md
@@ -0,0 +1,149 @@
+---
+description: >
+  Universal rules for developing the aiconfigurator generator module.
+  Covers cross-module awareness, template/rule safety, and documentation
+  discipline. Applies to all generator work including templates, rules,
+  config schemas, and rendering logic.
+paths:
+  - "src/aiconfigurator/generator/**"
+---
+
+Rules and workflows for safely modifying the aiconfigurator generator module.
+Read the relevant reference file in `.claude/rules/generator/` before starting task-specific work.
+
+## Generator Pipeline Overview
+
+The generator transforms deployment intent into backend-specific artifacts through 6 stages:
+
+```text
+Raw Input (YAML + CLI --set)
+  -> [1] Input Parsing        (api.py)
+  -> [2] Default Application   (rendering/schemas.py, deployment_config.yaml)
+  -> [3] Rule Evaluation       (rendering/rule_engine.py, rule_plugin/*.rule)
+  -> [4] Parameter Mapping     (rendering/engine.py, backend_config_mapping.yaml)
+  -> [5] Template Rendering    (rendering/engine.py, backend_templates/**/*.j2)
+  -> [6] Artifact Emission     (artifacts.py)
+  -> Generated Artifacts: k8s_deploy.yaml, run.sh, cli_args, engine configs
+```
+
+Bugs can originate at any stage but manifest at stage 5/6. Always trace backwards.
+
+## High-Risk Files
+
+Modifying these files affects the entire pipeline. Understand the full data flow
+before changing them:
+
+| File | Risk | Why |
+|---|---|---|
+| `src/aiconfigurator/generator/rendering/engine.py` | High | Context building + template rendering; changes affect ALL backends and versions |
+| `src/aiconfigurator/generator/rendering/rule_engine.py` | High | Rule DSL evaluator; bugs here corrupt ALL computed parameters silently |
+| `src/aiconfigurator/generator/rendering/schemas.py` | High | Default application; wrong defaults propagate through every downstream stage |
+| `src/aiconfigurator/generator/module_bridge.py` | Medium | SDK/profiler bridge; field name mismatches break the profiler -> generator flow |
+
+## Universal Rules
+
+These rules apply to ALL generator work regardless of task type.
+
+### Rule 1: Respect Template and Rule Comments
+
+Before modifying any `.j2` template or `.rule` file, read ALL comments in the file.
+Comments with `# Guard:` or `# Why:` encode hard-won lessons from 60+ production
+bug fixes. If the developer's requested change contradicts a guarded comment:
+
+1. Quote the guard comment to the developer
+2. Explain why the guard exists
+3. Ask the developer to confirm they want to override it
+4. Do NOT silently remove or bypass guard comments
+
+When in doubt, the `# Guard:` comments in the source files are authoritative over
+`.claude/rules/generator/guard_rails.md`. The reference is a convenient index but
+may lag behind code changes.
+
+See `.claude/rules/generator/guard_rails.md` for the full catalog of constraints by backend.
+
+### Rule 2: Assess Cross-Module Impact
+
+Before implementing a generator change, check whether it affects:
+
+- **CLI** (`src/aiconfigurator/cli/`) -- new params need CLI arg registration
+- **SDK/profiler bridge** (`src/aiconfigurator/generator/module_bridge.py`) -- field name changes break the bridge
+- **Dynamo profiler** (https://github.com/ai-dynamo/dynamo/tree/main/components/src/dynamo/profiler) -- profiler feeds data that generator consumes; schema changes propagate
+- **Generator validator** (`tools/generator_validator/`) -- new flags need validator updates
+- **Support matrix** (`tools/support_matrix/`) -- new backends/models may need matrix updates
+- **Collector** (`collector/`) -- performance data collection may reference generator params
+
+See `.claude/rules/generator/cross_module_impact.md` for the detailed dependency map.
+
+### Rule 3: Update Documentation
+
+After completing a feature or adding a new user-facing parameter, update the
+relevant docs under `docs/`. Skip doc updates for small bug fixes or internal
+refactors that don't change user-visible behavior.
+
+| Change Type | Update |
+|---|---|
+| Pipeline/rendering logic | `docs/generator_overview.md` |
+| New CLI parameter | `docs/cli_user_guide.md` |
+| Model config changes | `docs/add_a_new_model.md` |
+| K8s/deployment changes | `docs/dynamo_deployment_guide.md` |
+| New backend version | `docs/support-matrix/` |
+| Tuning parameters | `docs/advanced_tuning.md` |
+
+If no existing doc covers the change, note this to the developer and suggest where
+documentation should be added.
+
+## Task Routing
+
+Read the appropriate reference file BEFORE starting work:
+
+| Task Type | Reference File |
+|---|---|
+| Adding/modifying Jinja2 templates | `.claude/rules/generator/template_authoring.md` |
+| Writing/modifying .rule files | `.claude/rules/generator/rule_authoring.md` |
+| Modifying deployment_config.yaml or backend_config_mapping.yaml | `.claude/rules/generator/config_schema.md` |
+| Debugging generator output bugs | `.claude/rules/generator/debugging.md` |
+| Writing tests for generator changes | `.claude/rules/generator/testing.md` |
+| Adding a new backend engine version | `.claude/rules/generator/new_backend_version.md` |
+| Understanding backend-specific constraints | `.claude/rules/generator/guard_rails.md` |
+| Checking cross-module dependencies | `.claude/rules/generator/cross_module_impact.md` |
+
+## Cross-Backend Consistency
+
+The generator supports 3 backends: **TRT-LLM**, **vLLM**, **SGLang**.
+Each has its own templates, rules, and parameter mappings.
+
+When modifying any backend-specific file, ALWAYS check the other two backends:
+
+1. Does the same parameter/rule/template block exist in the other backends?
+2. If yes, does it need the same change?
+3. If the change is intentionally different across backends, document WHY.
+
+The most common generator bug pattern is fixing something in one backend and
+forgetting the others (PR #579: MoE TP rule missing from SGLang).
+
+## Versioned Template Discipline
+
+- Each backend has versioned templates (e.g., `cli_args.0.16.0.j2`)
+- The renderer picks the HIGHEST version <= requested version (floor match)
+- When fixing or updating versioned templates, check
+  `src/aiconfigurator/generator/config/backend_version_matrix.yaml` to identify
+  active versions. Generally only modify templates for the **latest 5 Dynamo versions**
+  and their associated backend versions. If the change requires touching more than 5
+  versions, confirm with the developer before proceeding.
+- To support a new version: copy the closest prior template, modify the copy
+- Only create a new version template when the backend CLI interface actually changed
+
+## Quick Validation
+
+After any generator change:
+
+```bash
+# Run existing unit tests
+pytest tests/unit/generator/ -v
+
+# Generate a test config and inspect output
+python -m aiconfigurator generate --model <model> --system <system> --backend <backend> -o /tmp/test_output
+
+# Run generator validator (if backend images available)
+python tools/generator_validator/validator.py --backend <backend> --path /tmp/test_output/
+```
diff --git a/.claude/rules/generator/config_schema.md b/.claude/rules/generator/config_schema.md
@@ -0,0 +1,133 @@
+# Config Schema Modification Reference
+
+The generator's behavior is driven by two declarative YAML files. This reference
+covers safe practices for modifying them.
+
+## When to Use This Reference
+
+- Adding a new user-facing configuration parameter
+- Modifying defaults (global or backend-specific)
+- Adding a parameter mapping for a backend
+- Changing parameter constraints or required status
+- Adding a new config section (namespace)
+
+## Key Files
+
+| File | Purpose |
+|---|---|
+| `src/aiconfigurator/generator/config/deployment_config.yaml` | Input schema: ~54 params, defaults, constraints |
+| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Unified param -> backend CLI flag mapping |
+| `src/aiconfigurator/generator/rendering/schemas.py` | Schema validation, default application |
+
+## Schema File Structures
+
+**deployment_config.yaml entry:**
+```yaml
+- key: <Section>.<param_name>        # e.g., K8sConfig.k8s_namespace
+  required: true|false
+  default: <value or Jinja2 expr>    # e.g., '"default-ns"' or 'model_path.split("/")[-1]'
+  backend_defaults:                   # Optional: override default per backend
+    trtllm: <value or expr>
+    vllm: <value or expr>
+    sglang: <value or expr>
+  backends:                            # Optional: restrict to specific backends
+    - trtllm
+```
+
+**backend_config_mapping.yaml entry:**
+```yaml
+- param_key: <unified_name>          # e.g., tensor_parallel_size
+  vllm: <cli_flag_name>             # e.g., tensor-parallel-size (or null if unsupported)
+  sglang: <cli_flag_name>
+  trtllm: <cli_flag_name>
+  # OR with value transformation:
+  sglang:
+    key: disable-cuda-graph-padding
+    value: "not cuda_graph_enable_padding"  # Jinja2 expression
+```
+
+## Workflow
+
+### 1. Define the Parameter
+
+- What section does it belong to? (ServiceConfig, K8sConfig, ModelConfig, etc.)
+- Is it required or optional?
+- What is the default value? Is it static or computed?
+- Does the default differ by backend?
+- Which backends support this parameter?
+
+### 2. Add to deployment_config.yaml
+
+- Place in the correct section (entries are grouped by section)
+- If default uses an expression, test it:
+  1. What variables does the expression reference?
+  2. Are those variables available at default-evaluation time?
+  3. Test with missing/None values of referenced variables
+- If backend-specific: add `backend_defaults` block
+- If backend-restricted: add `backend_constraint` list
+
+### 3. Add to backend_config_mapping.yaml
+
+- Add entry with unified `param_key`
+- For each backend:
+  - If supported: add the CLI flag name
+  - If unsupported: set to null
+  - If value needs transformation: use `{key:, value:}` format
+- VERIFY the CLI flag names:
+  - TRT-LLM: check `tensorrt_llm` Python API or docs
+  - vLLM: check `vllm.engine.arg_utils.EngineArgs`
+  - SGLang: check `sglang.srt.server_args.ServerArgs`
+
+### 4. Update Rule Files (if needed)
+
+If the parameter requires computation, add rules.
+See `.claude/rules/generator/rule_authoring.md` for rule authoring details.
+
+### 5. Update Templates (if needed)
+
+If the parameter needs special handling in artifacts.
+See `.claude/rules/generator/template_authoring.md` for template authoring details.
+
+### 6. Validate
+
+- Run generator with the new parameter set to a test value
+- Run generator with the parameter omitted (verify default works)
+- Run generator validator to check output against backend API schemas
+- Verify the parameter appears in `--generator-help` output
+
+## Common Mistakes
+
+1. **Jinja2 expression quoting**: String defaults must be double-quoted inside single
+   quotes: `default: '"my-string"'`. Without inner quotes, YAML interprets it as a
+   bare string and Jinja2 evaluation breaks.
+
+2. **Missing null handling in expressions**: If `default: 'model_path.split("/")[-1]'`
+   and `model_path` is None, the expression throws. Guard with:
+   `'model_path.split("/")[-1] if model_path else ""'`.
+
+3. **Backend flag name format mismatch**: TRT-LLM uses underscores (`kv_cache_dtype`),
+   vLLM/SGLang use dashes (`kv-cache-dtype`). Always check the actual backend CLI.
+
+4. **Mapping value transformation gotchas**: SGLang's `disable-cuda-graph-padding` is
+   the INVERSE of the unified `cuda_graph_enable_padding`. The mapping
+   `value: "not cuda_graph_enable_padding"` handles this. Forgetting the inversion
+   produces a silent semantic bug.
+
+5. **Circular default references**: If param A defaults to an expression using param B,
+   and B defaults to an expression using A, the schema loader will silently produce
+   None for both. Verify the dependency chain is acyclic.
+
+## Checklist
+
+```text
+[ ] Define parameter: section, required/optional, default, backend support
+[ ] Add entry to deployment_config.yaml with correct syntax
+[ ] Test default expression with edge cases (None, empty string)
+[ ] Add entry to backend_config_mapping.yaml
+[ ] Verify CLI flag names against actual backend APIs
+[ ] Add rules if parameter needs computation
+[ ] Add template changes if needed
+[ ] Run generator with parameter set and omitted
+[ ] Run generator validator
+[ ] Verify --generator-help output includes new parameter
+```
diff --git a/.claude/rules/generator/cross_module_impact.md b/.claude/rules/generator/cross_module_impact.md
@@ -0,0 +1,115 @@
+# Cross-Module Impact Map
+
+When modifying the generator, check this map to identify affected modules outside
+`src/aiconfigurator/generator/`.
+
+## Dependency Directions
+
+```text
+CLI (cli/)
+  |-- calls --> generator/api.py (generate_config_from_input_dict, parse_cli_params)
+  |-- calls --> generator/main.py (render-config, render-artifacts subcommands)
+  |-- reads --> generator/config/deployment_config.yaml (for --generator-help)
+
+SDK/Profiler Bridge (generator/module_bridge.py)
+  |-- reads <-- sdk/task.py (TaskConfig)
+  |-- reads <-- sdk/perf_database.py (result DataFrame)
+  |-- calls --> generator/api.py (generate_config_from_input_dict)
+
+Dynamo Profiler (external: ai-dynamo/dynamo/components/src/dynamo/profiler)
+  |-- produces --> performance CSV data consumed by sdk/perf_database.py
+  |-- field names must match --> model_configs/*.json + systems/*.yaml
+
+Generator Validator (tools/generator_validator/)
+  |-- reads <-- generated artifacts (cli_args, engine configs, k8s manifests)
+  |-- validates against --> actual backend engine APIs (vLLM, SGLang, TRT-LLM)
+
+Support Matrix (tools/support_matrix/)
+  |-- reads <-- model_configs/*.json, systems/*.yaml
+  |-- reads <-- generator/config/backend_version_matrix.yaml
+
+Collector (collector/)
+  |-- produces --> performance data CSVs
+  |-- references --> generator parameter names for benchmark configs
+```
+
+## Impact by Change Type
+
+### Adding a New Parameter
+
+| Step | File(s) | Why |
+|---|---|---|
+| 1. Schema | `src/aiconfigurator/generator/config/deployment_config.yaml` | Define the param, default, backend support |
+| 2. Mapping | `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Map to backend CLI flag names |
+| 3. CLI | `src/aiconfigurator/cli/main.py` or CLI arg group | Expose via `--generator-set` (auto if in schema) |
+| 4. Bridge | `src/aiconfigurator/generator/module_bridge.py` | Pass from SDK search results if profiler-sourced |
+| 5. Validator | `tools/generator_validator/` | Add to expected flags if new CLI flag |
+| 6. Docs | `docs/cli_user_guide.md` | Document the new parameter |
+
+### Renaming a Parameter
+
+| Step | File(s) | Why |
+|---|---|---|
+| 1. Schema | `deployment_config.yaml` | Update key name |
+| 2. Mapping | `backend_config_mapping.yaml` | Update param_key |
+| 3. Bridge | `module_bridge.py` | Update field extraction from TaskConfig/DataFrame |
+| 4. Rules | `rule_plugin/*.rule` | Update all references in rule expressions |
+| 5. Templates | `backend_templates/**/*.j2` | Update variable references |
+| 6. Aggregators | `aggregators.py` | Update if param is aggregated there |
+| 7. Tests | `tests/unit/generator/` | Update test fixtures and assertions |
+| 8. Backward compat | `aggregators.py` or `api.py` | Add alias if old name was user-facing |
+
+### Modifying Rule Logic
+
+| Check | File(s) | Why |
+|---|---|---|
+| 1. All backends | `rule_plugin/*.rule` | Same rule may need update in all backends |
+| 2. Benchmark rules | `rule_plugin/benchmark/*.rule` | Benchmark may need different logic |
+| 3. Bridge output | `module_bridge.py` | If rule uses fields from bridge output |
+| 4. Template consumers | `backend_templates/**/*.j2` | Templates may assume rule output format |
+| 5. Validator | `tools/generator_validator/` | New computed values may need validation |
+
+### Adding a New Backend Version
+
+| Step | File(s) | Why |
+|---|---|---|
+| 1. Version matrix | `src/aiconfigurator/generator/config/backend_version_matrix.yaml` | Map Dynamo -> backend version |
+| 2. Templates | `src/aiconfigurator/generator/config/backend_templates/<backend>/` | Version-specific templates if CLI changed |
+| 3. Image defaults | `deployment_config.yaml` | Container image tag expressions |
+| 4. Support matrix | `tools/support_matrix/` | Update supported combinations |
+| 5. Validator | `tools/generator_validator/` | May need new backend image for validation |
+
+### Modifying Template Output Format
+
+| Check | File(s) | Why |
+|---|---|---|
+| 1. K8s manifests | Verify YAML is valid K8s | `kubectl apply --dry-run` |
+| 2. Run scripts | Verify bash syntax | `bash -n generated_run.sh` |
+| 3. Engine configs | Verify against backend schema | `tools/generator_validator/` |
+| 4. Collector | `collector/` | If collector parses generated configs |
+
+## External Dependencies
+
+### Dynamo Profiler (ai-dynamo/dynamo)
+
+The Dynamo profiler runs benchmarks and produces performance data that the SDK
+consumes. Generator changes that affect:
+
+- **Worker topology** (TP, PP, DP dimensions) -- profiler must benchmark matching configs
+- **Batch size computation** -- profiler's benchmark configs must align
+- **K8s deployment format** -- Dynamo's DynamoGraphDeployment CRD must accept generated manifests
+- **Entry points** (e.g., `python3 -m dynamo.vllm`) -- must match Dynamo runtime
+
+When changing these areas, verify compatibility with the Dynamo profiler or flag
+the change to the developer as potentially requiring upstream Dynamo updates.
+
+### Backend Engines (vLLM, SGLang, TRT-LLM)
+
+The generator produces CLI arguments and config files consumed by these engines.
+Changes to generated flags must be validated against the actual engine version's API:
+
+- **vLLM**: `vllm.engine.arg_utils.EngineArgs`
+- **SGLang**: `sglang.srt.server_args.ServerArgs`
+- **TRT-LLM**: `tensorrt_llm` Python API / `trtllm-serve` CLI
+
+Use `tools/generator_validator/` when backend images are available.
diff --git a/.claude/rules/generator/debugging.md b/.claude/rules/generator/debugging.md
@@ -0,0 +1,135 @@
+# Generator Debugging Reference
+
+Generator bugs have distinct patterns: silent output corruption, mode confusion,
+version template drift, and MoE edge cases. This reference provides a systematic
+backwards-tracing diagnostic approach.
+
+## When to Use This Reference
+
+- Generator produces wrong output (invalid CLI args, missing config blocks, wrong values)
+- Engine startup fails with generated config
+- Generator validator reports mismatches
+- User reports deployment failure with generated artifacts
+
+## Diagnostic Pipeline
+
+The generator has 6 stages. A bug can originate at any stage but manifests at the output.
+Trace backwards from the output:
+
+```text
+Stage 6: TEMPLATE RENDERING (most visible)
+  Symptom: Wrong CLI flag name, missing block, wrong YAML structure
+  Check:   Read the template (.j2 file), verify variable names match context
+  Tool:    Diff the template output against a known-good output
+
+Stage 5: RULE EVALUATION (most common source)
+  Symptom: Wrong computed value (batch size, TP, token budget)
+  Check:   Read the .rule file, trace expression evaluation
+  Tool:    Add debug logging in rule_engine.py:apply_rule_plugins()
+
+Stage 4: PARAMETER MAPPING (subtle bugs)
+  Symptom: Correct value, wrong flag name or inverted boolean
+  Check:   Read backend_config_mapping.yaml for the parameter
+  Tool:    Grep for the param_key across all mapping entries
+
+Stage 3: DEFAULT APPLICATION (silent failures)
+  Symptom: Parameter is None/missing when it should have a value
+  Check:   Read deployment_config.yaml for the entry's default expression
+  Tool:    Evaluate the default expression manually with test inputs
+
+Stage 2: INPUT PARSING (user-facing)
+  Symptom: Override not taking effect, wrong section targeting
+  Check:   Read api.py:parse_cli_params(), check dotted-path resolution
+  Tool:    Print parsed input dict before processing
+
+Stage 1: SCHEMA LOADING (rare)
+  Symptom: Schema validation error or missing field
+  Check:   Read rendering/schemas.py:apply_defaults()
+```
+
+## Workflow
+
+### 1. Reproduce
+
+- Get the exact input config (YAML + CLI overrides)
+- Get the backend and version
+- Run the generator and capture output
+- Identify the specific wrong output (CLI flag, YAML block, value)
+
+### 2. Trace Backwards from Output
+
+Start at Stage 6 and work backwards:
+
+**a. TEMPLATE**: Find the template that produced the wrong output
+- Glob: `src/aiconfigurator/generator/config/backend_templates/<backend>/<artifact>*.j2`
+- Find the exact version template used (check `backend_version_matrix.yaml`)
+- Read the template, identify which variable is wrong
+
+**b. CONTEXT**: Check what value the variable had in the rendering context
+- Read `src/aiconfigurator/generator/rendering/engine.py:make_worker_context()`
+- Trace how the variable gets into the context dict
+
+**c. RULE**: Check if a rule computed the wrong value
+- Read `src/aiconfigurator/generator/rule_plugin/<backend>.rule`
+- Find the rule for this variable
+- Check scope prefix (agg vs prefill vs decode)
+- Evaluate the expression manually with known inputs
+
+**d. MAPPING**: Check if the mapping is correct
+- Read `src/aiconfigurator/generator/config/backend_config_mapping.yaml`
+- Verify the param_key -> backend flag mapping
+- Check for value transformations
+
+**e. DEFAULT**: Check if the default was applied correctly
+- Read `src/aiconfigurator/generator/config/deployment_config.yaml` for the parameter
+- Evaluate the default expression
+- Check `backend_defaults` if applicable
+
+### 3. Identify Root Cause
+
+Common root causes:
+- Wrong scope prefix in `.rule` file (e.g., `agg` instead of `agg_prefill_decode`)
+- Stale variable reference in template after context restructuring
+- Missing null guard in expression `(value or 0)`
+- Parameter only fixed in one backend's `.rule`, not all
+- Version template not updated (fix in v1.0.0 but not v1.1.0)
+
+### 4. Fix
+
+- Apply fix at the correct stage (don't patch templates for rule bugs)
+- Check ALL backends and ALL version templates for the same issue
+- Use `.claude/rules/generator/template_authoring.md` if fixing templates
+- Use `.claude/rules/generator/rule_authoring.md` if fixing rules
+
+### 5. Verify
+
+- Re-run with the original failing input
+- Run generator validator
+- Check other backends for the same bug pattern
+- Add regression test
+
+## Bug Pattern Catalog
+
+| Pattern | Example PR | Root Cause | Fix Location |
+|---|---|---|---|
+| Wrong value for one mode | #609 | Rule scope wrong | `.rule` file scope prefix |
+| Missing parameter in one backend | #579 | Rule not added | `.rule` file for that backend |
+| Invalid CLI flag | #613 | Backend doesn't support it | mapping yaml + template |
+| Stale template variable | #540 | Context restructured | ALL version templates |
+| RFC-1123 violation | #490 | No sanitization | `naive.py` or `aggregators.py` |
+| Disagg config in agg mode | #609 | Missing mode guard | Template `{% if %}` block |
+| Version mismatch | #519 | Deprecated flag | Version-specific template |
+
+## Checklist
+
+```text
+[ ] Reproduce the bug with exact inputs
+[ ] Identify the wrong output (specific flag/value/block)
+[ ] Trace backwards through the 6-stage pipeline
+[ ] Identify root cause stage and specific file
+[ ] Check all backends for the same bug pattern
+[ ] Check all version templates for the same bug pattern
+[ ] Apply fix at the correct stage
+[ ] Add regression test
+[ ] Run generator validator
+```
diff --git a/.claude/rules/generator/guard_rails.md b/.claude/rules/generator/guard_rails.md
@@ -0,0 +1,104 @@
+# Guard Rails Reference
+
+Distilled from ~60 merged PRs. These are constraints that MUST NOT be violated.
+Each guard has a severity level indicating the impact of violation.
+
+Severity: **CRASH** (engine won't start), **OOM** (out of memory), **SILENT** (wrong results),
+**K8S** (pod failure), **PERF** (degraded performance)
+
+---
+
+## TRT-LLM Backend
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| `build_config` nesting is version-dependent | SILENT | Pre-1.2.0rc5: inside `build_config`. Post-1.2.0rc5: top-level. Wrong placement silently ignored. |
+| Template variables must be top-level keys | SILENT | `engine.py` flattens context; nested paths like `build_config.max_batch_size` are undefined. |
+| `cache_transceiver_config` lifecycle | CRASH | Absent pre-1.0.0rc4. In engine YAML 1.0.0rc4-1.3.0rc1. In CLI `--override-engine-args` post-1.3.0rc5. |
+| `cache_transceiver_config.backend` must be `'DEFAULT'` | CRASH | Omitting backend field causes TRT-LLM to reject config in disagg mode. |
+| Engine params go into `--override-engine-args` JSON | CRASH | TRT-LLM's Dynamo argparser only accepts specific direct CLI flags. |
+| `max_num_tokens % tokens_per_block == 0` | CRASH | TRT-LLM asserts block alignment; violation crashes engine startup. |
+| `cache_transceiver_max_tokens_in_buffer` must align to block | CRASH | Same block-alignment assertion applies. |
+| Prefill: `disable_overlap_scheduler = true` | CRASH | Overlap scheduler on prefill causes hangs. |
+| Decode/agg: `disable_overlap_scheduler = false` | PERF | Disabling on decode/agg hurts throughput. |
+| MoE: `TP = moe_tp * moe_ep` | OOM | Without this, model may replicate per GPU. |
+| KV cache dtype `"float16"`/`"bfloat16"` -> `"auto"` | CRASH | TRT-LLM doesn't accept literal dtype strings. |
+
+## SGLang Backend
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| MoE: `TP = moe_tp * moe_ep` | OOM | SGLang uses unified TP; without this, `tp=1` -> full model replicated per GPU. |
+| Do NOT emit `--moe-dense-tp-size` | CRASH | SGLang only accepts value 1 or None; other values crash startup. |
+| KV transfer backend default: `"nixl"` | CRASH | SGLang >=0.5.6.post2 requires explicit transfer backend for disagg. |
+| `enable_mixed_chunk = true` for agg mode | PERF | Without it, poor prefill/decode scheduling. |
+| KV cache dtype `"fp8"` -> `"fp8_e4m3"` | SILENT | SGLang accepts `"fp8_e4m3"` not `"fp8"`. |
+| KV cache dtype `"float16"` -> `"auto"` | SILENT | SGLang interprets `"float16"` literally. |
+| Wideep vs non-wideep are exclusive | CRASH | SGLang doesn't support mixed `moe_tp + moe_ep` configurations. |
+| `enable_attention_dp` when DP > 1 and MoE | SILENT | MoE models with DP>1 require attention DP. |
+| NVFP4 models need explicit `--quantization` | OOM | SGLang can't auto-detect NVFP4; loads in FP16/BF16 without it. |
+
+## vLLM Backend
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| `--cudagraph-capture-sizes` uses space-separated values | CRASH | Commas treated as part of value strings; startup failure. |
+| `--kv-transfer-config` required for disagg | SILENT | Without it, KV cache silently fails to transfer. |
+| `--max-model-len` and `--max-num-batched-tokens` required | OOM | Without these, vLLM uses model default max length. |
+| `enable_expert_parallel` when `moe_ep > 1` | SILENT | vLLM requires explicit flag; EP silently disabled without it. |
+| KV cache dtype `"float16"` -> `"auto"` | CRASH | vLLM doesn't accept `"float16"` as literal. |
+
+## Cross-Backend Rules
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| `gpus_per_worker = TP * PP * DP` | K8S | Wrong value causes pod scheduling failure or idle GPUs. |
+| Prefix caching: `disable_prefix_cache=false` AND `enable_router=true` | SILENT | Both must be set when `ModelConfig.prefix > 0`. |
+| Speculative decoding type string differs by backend | CRASH | TRT-LLM: `"MTP"`, SGLang: `"NEXTN"`, vLLM: `"mtp"`. |
+| Prefill `max_batch_size` must never be 0 | CRASH | Fallback to 1; zero causes division-by-zero. |
+| Do NOT extract common K8s templates | N/A | PR #314 attempted; PR #340 reverted. Keep templates standalone per backend. |
+
+## K8s Template Guards
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| PVC mounts on WORKER pods, not frontend | K8S | SGLang frontend doesn't need model files. |
+| `k8s_model_cache` must be present for vllm/sglang | K8S | Missing PVC param omits volume mount entirely. |
+| `k8s_etcd_endpoints` must be rendered when configured | K8S | Disagg mode requires etcd for service discovery. |
+| `k8s_hf_home` defaults to `/workspace/model_cache` when PVC set | SILENT | Ensures HF downloads go to persistent volume. |
+| DGD name must be RFC 1123 compliant | K8S | Lowercase, alphanumeric, hyphens only, max 63 chars. |
+| Use `MODEL_PATH` not `MODEL` as env var | SILENT | Aligns with trtllm convention; `MODEL` caused conflicts. |
+
+## Version & Template Selection
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| Template version selection: floor match (highest <= requested) | SILENT | Not every version has its own template. |
+| Catch unsupported system/backend/version combos early | PERF | Late failures after profiling waste user time. |
+| `--generator-dynamo-version` vs `--generated-config-version` | SILENT | Different purposes: Dynamo image tag vs template selection. |
+
+## Run Script Guards
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| `#!/bin/bash` shebang and `set -e` | CRASH | Missing shebang causes exec format error. |
+| Benchmark templates must include `--artifact-dir` | CRASH | Default path may be read-only in containers. |
+| Dynamo >=0.8.0 entry points: `python3 -m dynamo.<backend>` | CRASH | Old entry points fail on new Dynamo versions. |
+| Multi-node disagg: per-node scripts, `include_frontend` only node 0 | K8S | Workers assigned to non-existent GPU slots. |
+
+## Model Detection
+
+| Guard | Severity | Key Detail |
+|---|---|---|
+| MoE detection from `config.json`, not model name | SILENT | Name patterns miss non-standard naming. |
+| Use `model_family` not `model_name` for compatibility | SILENT | `model_name` includes size/quant info. |
+| `safe_model_name` generated BEFORE saving results | CRASH | Race condition with raw `model_path` containing slashes. |
+| Quantization inferred from model config, not name | SILENT | Name patterns are inconsistent. |
+
+## Benchmark vs Deployment Differences
+
+| Parameter | Deployment | Benchmark |
+|---|---|---|
+| `agg_decode max_batch_size` | `max(512, batch*2)` | `max(128, batch)` |
+| `cuda_graph_batch_sizes` | Coarse-grained ranges | All sizes `range(1, max+1)` |
+| Rule selection | `--generator-set rule=default` | `--generator-set rule=benchmark` |
diff --git a/.claude/rules/generator/new_backend_version.md b/.claude/rules/generator/new_backend_version.md
@@ -0,0 +1,169 @@
+# Adding a New Backend Version Reference
+
+Adding a new backend version is one of the most frequent generator tasks. It involves
+coordinated changes across multiple files. Getting any step wrong results in deployment
+failures that only surface when users try the new version.
+
+## When to Use This Reference
+
+- Adding support for a new backend engine version (TRT-LLM, vLLM, SGLang)
+- Bumping the default Dynamo version
+- Handling deprecated/renamed backend CLI flags
+- Updating container image references
+
+## Workflow
+
+### 1. Gather Version Information
+
+- What is the new backend version? (e.g., vLLM 0.17.0)
+- What Dynamo release maps to it? (e.g., Dynamo 1.1.0)
+- What changed in this backend version?
+  - New CLI flags added
+  - Deprecated/removed CLI flags
+  - Renamed flags
+  - Changed default behaviors
+  - New model architecture support
+- Source: backend release notes, changelog, arg_utils diff
+
+### 2. Update Version Matrix
+
+File: `src/aiconfigurator/generator/config/backend_version_matrix.yaml`
+
+- Add new Dynamo version entry (or update existing)
+- Map to new backend version
+- Example:
+  ```yaml
+  - dynamo_version: "1.1.0"
+    backends:
+      trtllm: "1.4.0"
+      vllm: "0.17.0"
+      sglang: "0.6.0"
+  ```
+
+### 3. Create Version-Specific Templates (if needed)
+
+Only create new version templates if the backend CLI interface changed.
+
+1. Identify which artifact templates need new versions:
+   - `cli_args.j2` -- if CLI flags changed
+   - `extra_engine_args.yaml.j2` -- if engine config format changed (TRT-LLM)
+   - `k8s_deploy.yaml.j2` -- usually version-independent
+   - `run.sh.j2` -- if startup command changed
+
+2. Copy the closest prior version template:
+   ```bash
+   cp cli_args.0.16.0.j2 cli_args.0.17.0.j2
+   ```
+
+3. Modify the new template:
+   - Add new flags
+   - Remove deprecated flags
+   - Update renamed flags
+   - Adjust conditionals for changed behavior
+
+4. **DO NOT modify the prior version template** -- it must continue working for
+   existing deployments.
+
+### 4. Update Parameter Mapping (if needed)
+
+File: `src/aiconfigurator/generator/config/backend_config_mapping.yaml`
+
+If new parameters were added:
+- Add `param_key` entry
+- Set CLI flag names for each backend (null if unsupported)
+
+If parameters were renamed:
+- Update the backend-specific flag name
+- Keep the unified `param_key` stable (don't rename the internal name)
+
+### 5. Update Deployment Config (if needed)
+
+File: `src/aiconfigurator/generator/config/deployment_config.yaml`
+
+If new user-facing parameters were added:
+- Add schema entry with section, default, required status
+- Add `backend_defaults` if behavior differs by backend
+
+### 6. Update Rule Files (if needed)
+
+Files: `src/aiconfigurator/generator/rule_plugin/<backend>.rule` (production)
+and `src/aiconfigurator/generator/rule_plugin/benchmark/<backend>.rule` (benchmark)
+
+If parameter computation logic changed:
+- Update expressions
+- Add new rules for new parameters
+- Check: did a previously-valid flag become invalid? (PR #613: `moe_dense_tp_size`)
+
+### 7. Update Container Images
+
+If the Dynamo release includes new container images:
+- Verify default image expressions in `deployment_config.yaml`
+- Check that version tag resolution works for new version
+
+### 8. Test
+
+- Generate config for the new version with a representative model
+- Compare output against manually-written reference config
+- Run generator validator if backend image available
+- Test all modes: agg, disagg-prefill, disagg-decode
+- Test with MoE model if backend version added MoE changes
+- **MOST IMPORTANT: Test that OLD version still works**
+
+## Deprecated Flag Handling
+
+When a backend deprecates a CLI flag:
+
+1. Identify the deprecation:
+   - Old flag: `--connector` (deprecated in version X)
+   - New flag: `--kv-transfer-config '{"connector": "..."}'`
+
+2. Create version-specific template:
+   - Old template (< boundary version): keeps old flag
+   - New template (>= boundary version): uses new flag
+
+3. Update version matrix to ensure correct version -> template mapping
+
+4. **DO NOT modify old templates** -- users on old versions must still work
+
+## Version Template Selection Logic
+
+The rendering engine selects templates by version:
+
+1. Look for exact version match: `cli_args.<version>.j2`
+2. Fall back to closest prior version (highest version <= requested)
+3. Fall back to base template: `cli_args.j2`
+
+You only need a new version template when the interface CHANGES, not for every
+version bump.
+
+## Anti-Patterns
+
+1. **Don't edit prior version templates** -- They serve existing deployments. Create
+   a new version template instead.
+
+2. **Don't create a new version template for no-op changes** -- If the CLI interface
+   didn't change, the existing template works fine. The version fallback logic handles it.
+
+3. **Don't forget to test the OLD version** -- Adding version 0.17.0 support must not
+   break 0.16.0 generation.
+
+4. **Don't hardcode version checks in rendering engine** -- Use the version template
+   naming convention and fallback logic. No `if version >= "0.17.0"` in Python code.
+
+## Checklist
+
+```text
+[ ] Gather new version info: what changed (new/deprecated/renamed flags)
+[ ] Update backend_version_matrix.yaml
+[ ] Determine if version-specific templates are needed
+[ ] Create new version templates (copy closest prior, modify)
+[ ] DO NOT modify prior version templates
+[ ] Update backend_config_mapping.yaml for new/changed parameters
+[ ] Update deployment_config.yaml for new user-facing parameters
+[ ] Update rule files for changed computation logic
+[ ] Handle deprecated flags with version-specific templates
+[ ] Update container image references if needed
+[ ] Test: generate config for new version, all modes
+[ ] Test: generate config for OLD version still works
+[ ] Run generator validator
+```
diff --git a/.claude/rules/generator/rule_authoring.md b/.claude/rules/generator/rule_authoring.md
@@ -0,0 +1,143 @@
+# Rule Plugin Authoring Reference
+
+The rule plugin system (`.rule` files) computes derived parameters using a custom DSL.
+This reference covers safe practices for writing and modifying rules.
+
+## When to Use This Reference
+
+- Adding a new computed parameter to the generator
+- Modifying parameter computation logic (batch size, parallelism, CUDA graphs)
+- Adding MoE, speculative decoding, or prefix caching support
+- Creating a new rule mode (like `benchmark/`)
+
+## Key Files
+
+| File | Purpose |
+|---|---|
+| `src/aiconfigurator/generator/rule_plugin/*.rule` | Production rules per backend |
+| `src/aiconfigurator/generator/rule_plugin/benchmark/*.rule` | Benchmark rules per backend |
+| `src/aiconfigurator/generator/rendering/rule_engine.py` | Rule DSL evaluation engine |
+| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Parameter backend support |
+
+## DSL Reference
+
+```text
+# === SCOPE PREFIXES ===
+# Apply to specific worker roles:
+prefill <key> = <expr>              # Only prefill workers
+decode <key> = <expr>               # Only decode workers
+agg <key> = <expr>                  # Only aggregated (single) workers
+agg_decode <key> = <expr>           # Both agg and decode workers
+prefill_decode <key> = <expr>       # Both prefill and decode workers
+agg_prefill_decode <key> = <expr>   # ALL worker roles
+
+# === ASSIGNMENT ===
+<scope> <key> = <expression>
+# Expression uses Jinja2 syntax, evaluated via compile_expression()
+
+# === CONDITIONALS ===
+when <condition>:
+    <scope> <key> = <expr>
+    <scope> <key> = <expr>
+
+# === CONFIG GROUP TARGETING (global, not per-worker) ===
+DynConfig.enable_router = true
+BenchConfig.estimated_concurrency = <expr>
+
+# === AVAILABLE CONTEXT VARIABLES ===
+# From deployment_config.yaml:  ServiceConfig.*, K8sConfig.*, ModelConfig.*, SlaConfig.*
+# From params (per-worker):     tensor_parallel_size, max_batch_size, max_num_tokens, etc.
+# Special shorthand:            isl, osl, bs, is_moe
+```
+
+## Workflow
+
+### 1. Understand the Parameter
+
+- What is the parameter's purpose?
+- Which backends support it? (check `backend_config_mapping.yaml`)
+- Which worker roles need it? (prefill, decode, agg, or all?)
+- Does it depend on other computed parameters?
+
+### 2. Check Existing Rules
+
+- Read ALL `.rule` files: `trtllm.rule`, `vllm.rule`, `sglang.rule`
+- Check `benchmark/` variants too
+- Identify if the parameter is already computed elsewhere
+- Identify dependencies (e.g., `max_num_tokens` depends on `max_batch_size`)
+
+### 3. Write the Rule
+
+- Use the correct scope prefix (most common mistake!)
+- Guard nullable values: `(value or 0)`, `(value if value else default)`
+- Place new rules AFTER their dependencies in the file
+- Use Jinja2 expression syntax (not Python -- no list comprehensions, no f-strings)
+
+### 4. Cross-Backend Consistency
+
+For each backend's `.rule` file:
+
+1. Does this backend support the parameter? (check mapping yaml)
+2. If yes, does the rule exist? If not, add it.
+3. If the computation differs by backend, document WHY.
+4. If the parameter is null for this backend in mapping, skip it.
+
+### 5. Test
+
+- Write a test case that exercises the rule with known inputs
+- Test edge cases: MoE models, disagg mode, nullable params
+- Verify rule ordering: if rule B depends on rule A's output, A must come first
+
+## Common Patterns
+
+```python
+# Pattern: Scale batch size for production (agg + decode get bigger batches)
+agg_decode max_batch_size = (512 if (max_batch_size or 0) < 512 else (max_batch_size * 2))
+prefill max_batch_size = (max_batch_size if max_batch_size else 1)
+
+# Pattern: MoE parallelism remapping (TP = moe_tp * moe_ep)
+when ModelConfig.is_moe and (moe_tensor_parallel_size and moe_expert_parallel_size):
+    agg_prefill_decode tensor_parallel_size = moe_tensor_parallel_size * moe_expert_parallel_size
+
+# Pattern: Feature toggle based on model config
+when (ModelConfig.prefix or 0) > 0:
+    agg_prefill_decode disable_prefix_cache = false
+    DynConfig.enable_router = true
+
+# Pattern: Token budget alignment to block size
+agg max_num_tokens = ((max_batch_size + SlaConfig.isl + 1500 + tokens_per_block - 1) // tokens_per_block) * tokens_per_block
+```
+
+## Gotchas
+
+1. **`agg_prefill_decode` means ALL roles**, not a special combined role. Use it when
+   a rule applies universally.
+
+2. **Rule ordering matters** -- Rules are evaluated top-to-bottom. If rule B uses
+   `max_batch_size` that rule A modifies, A must appear before B.
+
+3. **Nullable guards are mandatory** -- `SlaConfig.isl` can be None. Always use
+   `(SlaConfig.isl or 0)` in arithmetic.
+
+4. **`when` blocks don't nest** -- There's no `when` inside `when`. Combine conditions:
+   `when A and B:`.
+
+5. **Backend-specific parameters** -- Some params only exist for one backend (e.g.,
+   `moe_dense_tp_size` was SGLang-only but removed as invalid per PR #613). Check
+   mapping yaml before adding.
+
+6. **Config group targeting is global** -- `DynConfig.enable_router = true` applies to
+   the entire deployment, not per-worker.
+
+## Checklist
+
+```text
+[ ] Identify parameter purpose, backend support, and worker scope
+[ ] Read all existing .rule files (production + benchmark)
+[ ] Write rule with correct scope prefix and null guards
+[ ] Verify rule ordering (dependencies first)
+[ ] Add equivalent rule to all applicable backend .rule files
+[ ] Document intentional cross-backend differences
+[ ] Add test case covering the new rule
+[ ] Test with MoE and disagg scenarios if applicable
+```
diff --git a/.claude/rules/generator/template_authoring.md b/.claude/rules/generator/template_authoring.md
@@ -0,0 +1,117 @@
+# Template Authoring Reference
+
+Backend templates are the most error-prone part of the generator. This reference
+covers safe practices for adding and modifying Jinja2 templates.
+
+## When to Use This Reference
+
+- Adding a new backend version template
+- Modifying existing templates (bug fix, feature addition)
+- Adding a new parameter to template rendering context
+- Adding a new artifact type (e.g., sflow templates)
+
+## Key Files
+
+| File | Purpose |
+|---|---|
+| `src/aiconfigurator/generator/config/backend_templates/<backend>/` | Jinja2 templates |
+| `src/aiconfigurator/generator/config/backend_config_mapping.yaml` | Param name mapping |
+| `src/aiconfigurator/generator/config/deployment_config.yaml` | Input schema + defaults |
+| `src/aiconfigurator/generator/config/backend_version_matrix.yaml` | Version compatibility |
+| `src/aiconfigurator/generator/rendering/engine.py` | Template rendering + context building |
+| `src/aiconfigurator/generator/rule_plugin/*.rule` | Rule DSL files |
+| `tools/generator_validator/` | Post-generation validation |
+
+## Template Types by Backend
+
+```text
+backend_templates/
+  vllm/       cli_args[.version].j2, k8s_deploy.yaml.j2, run.sh.j2
+  sglang/     cli_args[.version].j2, k8s_deploy.yaml.j2, run.sh.j2, sflow_deploy.yaml.j2
+  trtllm/     cli_args.j2, extra_engine_args[.version].yaml.j2, k8s_deploy.yaml.j2, run.sh.j2
+  benchmark/  bench_run.sh.j2, k8s_bench.yaml.j2
+```
+
+## Workflow
+
+### 1. Identify Scope
+
+- Which backends are affected? (trtllm, vllm, sglang, benchmark, sflow)
+- Which artifact types? (cli_args, engine_config, k8s_deploy, run.sh, bench)
+- Which versions need the change? (check `backend_version_matrix.yaml`)
+
+### 2. Read Current State
+
+- Read the target template(s)
+- Read `backend_config_mapping.yaml` for the parameter mapping
+- Read `rendering/engine.py:make_worker_context()` to understand context shape
+- Read the corresponding `.rule` file to see if rules compute the variable
+
+### 3. Cross-Backend Parity Check
+
+For each affected parameter:
+
+1. Grep all backend templates for the parameter name
+2. Compare handling across backends
+3. Flag any backend that is missing the parameter or handles it differently
+4. Document intentional differences vs. accidental omissions
+
+### 4. Implement
+
+- **New version templates**: Copy the closest prior version, modify. NEVER edit prior versions.
+- **Fixes**: Apply to ALL affected version templates (list them explicitly).
+- **New parameters**:
+  1. Add to `backend_config_mapping.yaml` if it's a mapped param
+  2. Add to `deployment_config.yaml` if it's a new input
+  3. Add to `.rule` file if it requires computation
+  4. Add to template(s)
+
+### 5. Verify Template Variables
+
+List all variables referenced in the modified template(s). For each variable,
+confirm its source:
+
+- [ ] Direct from `deployment_config.yaml` input
+- [ ] Computed by rule plugin
+- [ ] Mapped via `backend_config_mapping.yaml`
+- [ ] Injected by `rendering/engine.py` context
+
+Flag any variable that cannot be traced to a source.
+
+### 6. Test
+
+- Run existing generator unit tests
+- If adding a new parameter: add a test in `test_<backend>_cli_args.py`
+- Use generator validator (`tools/generator_validator/`) to check output validity
+- Compare output diff against golden artifacts if available
+
+## Anti-Patterns
+
+1. **Don't extract shared templates** -- PR #314 attempted shared macros; PR #340 reverted
+   it because backend-specific variations broke override mechanisms. Keep templates
+   standalone per backend.
+
+2. **Don't fix one version and forget the rest** -- Always enumerate ALL version-specific
+   templates. Use `glob backend_templates/<backend>/<artifact>*.j2` to list them.
+
+3. **Don't assume parameter names are the same across backends** -- Check
+   `backend_config_mapping.yaml`. SGLang uses `disable-cuda-graph-padding` (inverted!)
+   while TRT-LLM uses `cuda_graph_enable_padding`.
+
+4. **Don't add a template variable without a source** -- Every variable must be traceable
+   through the pipeline: input -> default -> rule -> mapping -> context -> template.
+
+## Checklist
+
+```text
+[ ] Identify all affected backends and version templates
+[ ] Read current template + mapping + rule file
+[ ] Cross-backend parity check for affected parameters
+[ ] Implement changes in ALL affected templates
+[ ] Verify all template variables have traced sources
+[ ] Update backend_config_mapping.yaml if needed
+[ ] Update deployment_config.yaml if needed
+[ ] Update .rule files if needed
+[ ] Run unit tests
+[ ] Run generator validator on output
+```
diff --git a/.claude/rules/generator/testing.md b/.claude/rules/generator/testing.md
@@ -0,0 +1,155 @@
+# Generator Testing Reference
+
+Generator testing has unique challenges: combinatorial output space, no backend
+runtime in CI, silent regressions, and test coverage gaps. This reference defines
+the testing strategy.
+
+## When to Use This Reference
+
+- After any generator code change (templates, rules, schemas, rendering)
+- Adding test coverage for untested generator components
+- Setting up golden output snapshots
+- Running the generator validator
+
+## Test Strategy Layers
+
+```text
+Layer 1: UNIT TESTS (fast, always run)
+  - Test individual functions in isolation
+  - Mock: schema loading, template rendering
+  - Files: tests/unit/generator/test_*.py
+
+Layer 2: INTEGRATION TESTS (medium, run on PR)
+  - Test full pipeline: input -> artifacts
+  - Compare output against golden snapshots
+  - No external dependencies
+
+Layer 3: VALIDATOR TESTS (slow, run in specialized CI)
+  - Import actual backend engine modules
+  - Compare generated flags against engine API schemas
+  - Requires docker images with backends installed
+```
+
+## Workflow
+
+### 1. Determine Test Layer
+
+- Pure logic change (expression, calculation): Unit test
+- Template/rule/schema change (output-affecting): Integration + golden snapshot
+- New parameter or flag: Validator test
+
+### 2. Write Unit Tests
+
+Location: `tests/unit/generator/`
+
+For aggregators/API changes:
+```python
+def test_new_parameter_default(self):
+    result = collect_generator_params(
+        service={"model_path": "test/model", "served_model_name": "test"},
+        k8s={"k8s_namespace": "test"},
+        backend="trtllm"
+    )
+    assert result["SectionConfig"]["new_param"] == expected_value
+```
+
+For rule evaluation:
+```python
+def test_moe_tp_remapping(self):
+    params = {"tensor_parallel_size": 1, "moe_tensor_parallel_size": 2,
+              "moe_expert_parallel_size": 4}
+    model_config = {"is_moe": True}
+    result = apply_rule_plugins("trtllm", params, model_config=model_config)
+    assert result["agg"]["tensor_parallel_size"] == 8  # 2 * 4
+```
+
+### 3. Write Golden Snapshot Tests
+
+Purpose: Catch any unintended output change.
+
+1. Generate reference outputs for key configurations:
+   - Minimal config (just model_path + backend)
+   - Full disagg config (prefill + decode workers)
+   - MoE model config
+   - Each backend x version combination
+
+2. Store as golden files:
+   ```
+   tests/golden/generator/<backend>/<version>/<mode>/
+     cli_args.txt
+     k8s_deploy.yaml
+     run.sh
+   ```
+
+3. Test compares current output against golden:
+   ```python
+   def test_trtllm_agg_golden(self):
+       output = generate_backend_artifacts(params, backend="trtllm", ...)
+       golden = read_golden("trtllm/1.3.0rc5/agg/cli_args.txt")
+       assert output["cli_args"] == golden
+   ```
+
+4. Update goldens intentionally:
+   ```bash
+   UPDATE_GOLDEN=1 pytest tests/golden/ -k trtllm
+   git diff tests/golden/  # review changes
+   ```
+
+### 4. Use Generator Validator
+
+When available (specialized CI or local with backend images):
+
+```bash
+# Validate generated TRT-LLM config against engine API
+python tools/generator_validator/validator.py --backend trtllm --path output/
+
+# Validate vLLM CLI args
+python tools/generator_validator/validator.py --backend vllm --path output/
+```
+
+### 5. Test Edge Cases
+
+Always test these scenarios:
+
+- [ ] MoE model (`is_moe=True`, `moe_tensor_parallel_size` set)
+- [ ] Disagg mode (prefill + decode workers)
+- [ ] Agg mode (single worker)
+- [ ] Speculative decoding (`ModelConfig.nextn > 0`)
+- [ ] Prefix caching (`ModelConfig.prefix > 0`)
+- [ ] Minimal config (only required fields)
+- [ ] PVC configuration (`k8s_pvc_name` set, `k8s_hf_home` auto-derived)
+- [ ] Each backend (trtllm, vllm, sglang)
+- [ ] Benchmark mode (`rule=benchmark`)
+
+## Test File Organization
+
+```text
+tests/
+  unit/
+    generator/
+      test_aggregators.py       # Parameter collection, defaults
+      test_naive.py             # Naive TP calculation, RFC-1123
+      test_trtllm_cli_args.py   # TRT-LLM specific rendering
+      test_vllm_cli_args.py     # vLLM specific rendering
+      test_sglang_cli_args.py   # SGLang specific rendering
+      test_rule_engine.py       # Rule DSL evaluation
+      test_schema_defaults.py   # Default expression evaluation
+      test_config_mapping.py    # Parameter mapping correctness
+  golden/
+    generator/
+      trtllm/<version>/<mode>/  # Golden outputs per combination
+      vllm/<version>/<mode>/
+      sglang/<version>/<mode>/
+```
+
+## Checklist
+
+```text
+[ ] Determine test layer (unit / integration / validator)
+[ ] Write unit tests for changed logic
+[ ] Update or create golden snapshots for output-affecting changes
+[ ] Test MoE, disagg, speculative decoding edge cases
+[ ] Test all affected backends
+[ ] Run generator validator if backend images available
+[ ] Verify test passes in CI
+```
diff --git a/AGENTS.md b/AGENTS.md
@@ -0,0 +1,11 @@
+# AGENTS
+
+This file adds an explicit guard for generator rule edits.
+
+## Required First Step
+
+Before making any change under:
+- `aiconfigurator/src/aiconfigurator/generator/**`
+
+MUST read:
+- `aiconfigurator/.claude/rules/generator-development.md`
\ No newline at end of file
PATCH

echo "Gold patch applied."
