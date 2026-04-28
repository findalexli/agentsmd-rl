#!/usr/bin/env bash
set -euo pipefail

cd /workspace/morphir

# Idempotency guard
if grep -qF "When specification documents (`docs/spec/`) need to match design documents (`doc" ".claude/skills/technical-writer/SKILL.md" && grep -qF "Package and module paths expand to fully split directories. Definition files (`." ".claude/skills/technical-writer/references/spec-design-consistency.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/.claude/skills/technical-writer/SKILL.md b/.claude/skills/technical-writer/SKILL.md
@@ -18,6 +18,7 @@ You are a technical writing assistant specialized in Morphir documentation. You
 6. **Create Tutorials** - Build well-structured, effective tutorials
 7. **Manage JSON Schemas** - Convert YAML schemas to JSON and detect drift
 8. **Generate llms.txt** - Create LLM-friendly documentation files
+9. **Spec/Design Consistency** - Verify specification docs match design docs
 
 ## Documentation Structure
 
@@ -111,6 +112,49 @@ Key items:
 - [ ] Tutorials are complete and tested
 - [ ] Links work and formatting is correct
 
+### Spec/Design Consistency Review
+
+When specification documents (`docs/spec/`) need to match design documents (`docs/design/`), use the consistency checklist at [spec-design-consistency.md](references/spec-design-consistency.md).
+
+**Key consistency checks:**
+
+1. **Naming Format Validation**
+   - FQName format: `package/path:module/path#local-name`
+   - Path format: `segment/segment` (no `:` or `#`)
+   - Name format: `kebab-case` with `(abbreviations)` for letter sequences
+   - Validate all examples parse correctly
+
+2. **Node Coverage**
+   - All type nodes from design are in spec
+   - All value nodes from design are in spec
+   - v4-specific additions marked with `(v4)`
+
+3. **JSON Example Validation**
+   - Examples use correct wrapper object format
+   - Field names match design
+   - Examples are valid JSON
+
+4. **Directory Structure Validation**
+   - Directory tree examples match actual/expected structure
+   - File name patterns are consistent (e.g., `.type.json`, `.value.json`, `module.json`)
+   - Path separators and naming conventions align with canonical format
+
+5. **Terminology Alignment**
+   - Specs and definitions explained consistently
+   - Same terms used in both design and spec
+
+**Workflow for consistency review:**
+
+```bash
+# 1. Open design and spec side-by-side
+# 2. Walk through each section
+# 3. Validate JSON examples
+# 4. Verify directory structure examples
+# 5. Fix discrepancies
+# 6. Regenerate llms.txt
+python .claude/skills/technical-writer/scripts/generate_llms_txt.py
+```
+
 ## Writing Guidelines
 
 ### Quick Reference
diff --git a/.claude/skills/technical-writer/references/spec-design-consistency.md b/.claude/skills/technical-writer/references/spec-design-consistency.md
@@ -0,0 +1,152 @@
+# Spec/Design Consistency Checklist
+
+Use this checklist when reviewing specification documents (`docs/spec/`) against design documents (`docs/design/`).
+
+## Naming Conventions
+
+### Canonical String Format Consistency
+- [ ] FQName examples use correct format: `package/path:module/path#local-name`
+- [ ] Path examples use correct format: `segment/segment` (not mixed with FQName separators)
+- [ ] Name examples use correct format: `kebab-case` with `(abbreviations)` for letter sequences
+- [ ] No confusion between paths and FQNames (paths don't have `:` or `#`)
+
+### Common Naming Errors
+| Error | Example | Correct |
+|-------|---------|---------|
+| Path with FQName separators | `morphir/sdk:string` | `morphir/sdk` (path) or `morphir/sdk:string#string` (FQName) |
+| Missing local name in FQName | `morphir/sdk:list` | `morphir/sdk:list#map` |
+| Abbreviation not marked | `morphir/sdk` | `morphir/(sdk)` only if S-D-K, else `morphir/sdk` for word "sdk" |
+
+## Type/Value Node Consistency
+
+### Type Expressions
+- [ ] All type nodes from design are documented in spec
+- [ ] Structure notation matches design (e.g., `Type attributes name` vs `Type(attributes, name)`)
+- [ ] Components list matches design fields
+- [ ] v4-specific nodes are marked with `(v4)`
+
+### Value Expressions
+- [ ] All value nodes from design are documented in spec
+- [ ] v4 additions present: `Hole`, `Native`, `External`
+- [ ] `ValueDefinitionBody` variants documented: `ExpressionBody`, `NativeBody`, `ExternalBody`, `IncompleteBody`
+
+### Specifications vs Definitions
+- [ ] Clear distinction explained between specs and definitions
+- [ ] All spec types listed: `TypeAliasSpecification`, `OpaqueTypeSpecification`, `CustomTypeSpecification`, `DerivedTypeSpecification`
+- [ ] All definition types listed: `TypeAliasDefinition`, `CustomTypeDefinition`, `IncompleteTypeDefinition`
+- [ ] Derivation rules documented (definition → specification)
+
+## JSON Serialization Consistency
+
+### Format Examples
+- [ ] JSON examples are valid JSON
+- [ ] Wrapper object format matches design: `{ "NodeType": { "field": value } }`
+- [ ] Shorthand formats documented where applicable
+- [ ] Legacy format compatibility documented
+
+### Field Naming
+- [ ] JSON field names match design (camelCase vs snake_case)
+- [ ] Required vs optional fields match design
+- [ ] Default values documented where applicable
+
+## Directory Structure Consistency
+
+### File Naming Patterns
+- [ ] Document Tree file suffixes are consistent: `.type.json`, `.value.json`, `module.json`
+- [ ] Directory examples use canonical name format (kebab-case)
+- [ ] Path separators are forward slashes `/`
+
+### Expected Directory Structure
+
+Package and module paths expand to fully split directories. Definition files (`.type.json`, `.value.json`) reside directly in the module directory—the suffixes distinguish types from values.
+
+```
+pkg/my-org/my-project/
+└── orders/
+    ├── module.json
+    ├── order.type.json
+    ├── line-item.type.json
+    ├── create-order.value.json
+    ├── calculate-total.value.json
+    └── shipping/
+        ├── module.json
+        ├── address.type.json
+        └── calculate-cost.value.json
+```
+
+### Common Directory Structure Errors
+| Error | Example | Correct |
+|-------|---------|---------|
+| Wrong suffix | `user.json` | `user.type.json` |
+| CamelCase in path | `pkg/Main/Domain/` | `pkg/main/domain/` |
+| Collapsed path segments | `pkg/my-org-my-project/` | `pkg/my-org/my-project/` |
+| Unnecessary subfolders | `types/user.type.json` | `user.type.json` (directly in module) |
+| Inconsistent separators | `pkg\main\domain` | `pkg/main/domain` |
+
+## Cross-Reference Validation
+
+### Internal Links
+- [ ] References to other spec documents use correct paths
+- [ ] References to design documents are accurate
+- [ ] No dangling references to removed/renamed concepts
+
+### Terminology
+- [ ] Terms used consistently across spec and design
+- [ ] No conflicting definitions of the same concept
+- [ ] Abbreviations/acronyms explained on first use
+
+## Completeness Checklist
+
+### From Design to Spec
+For each design document in `docs/design/draft/ir/`:
+- [ ] `naming.md` → `docs/spec/draft/names.md`
+- [ ] `types.md` → `docs/spec/draft/types.md`
+- [ ] `values.md` → `docs/spec/draft/values.md`
+- [ ] `modules.md` → `docs/spec/draft/modules.md`
+- [ ] `packages.md` → `docs/spec/draft/packages.md`
+
+### Key Design Concepts to Verify
+| Design Concept | Should Be In Spec |
+|----------------|-------------------|
+| AccessControlled wrapper | Definitions section |
+| Documented wrapper | Modules/Packages section |
+| Documentation type | Modules section |
+| Incompleteness type | Types & Values sections |
+| HoleReason type | Types & Values sections |
+| NativeInfo/NativeHint | Values section |
+| ValueDefinitionBody variants | Values section |
+
+## Common Discrepancy Patterns
+
+### 1. Outdated Examples
+**Symptom**: Examples don't compile or parse
+**Check**: Validate all code/JSON examples against current schema
+
+### 2. Missing v4 Features
+**Symptom**: Design has features not in spec
+**Check**: Search design for `(v4)` or "v4" and verify spec coverage
+
+### 3. Inconsistent Structure Notation
+**Symptom**: Spec uses different notation than design
+**Check**: Align on one notation style (recommend design's Gleam-like notation)
+
+### 4. Partial Updates
+**Symptom**: Some sections updated, others stale
+**Check**: Review entire document when updating any section
+
+## Review Process
+
+1. **Open both documents side-by-side** - spec and corresponding design
+2. **Walk through design section by section** - verify each concept in spec
+3. **Validate all examples** - copy-paste and check they parse
+4. **Check cross-references** - ensure links resolve correctly
+5. **Note discrepancies** - create issues or fix directly
+6. **Update llms.txt** - regenerate after fixes
+
+## Automated Checks (TODO)
+
+Future script `check_spec_design_consistency.py` should:
+- Parse JSON examples and validate syntax
+- Extract canonical name examples and validate format
+- Cross-reference type/value node lists
+- Report missing v4 features
PATCH

echo "Gold patch applied."
