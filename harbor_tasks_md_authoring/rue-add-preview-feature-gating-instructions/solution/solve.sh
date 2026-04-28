#!/usr/bin/env bash
set -euo pipefail

cd /workspace/rue

# Idempotency guard
if grep -qF "**IMPORTANT**: New language features MUST be gated behind preview flags until co" "CLAUDE.md"; then
  echo "Gold patch already applied."
  exit 0
fi

git apply --whitespace=nowarn <<'PATCH'
diff --git a/CLAUDE.md b/CLAUDE.md
@@ -315,7 +315,62 @@ The traceability check is run as part of `./test.sh` and fails if:
 
 ## Modifying the Language
 
-When adding or changing language features, follow this checklist:
+When adding or changing language features, follow this checklist.
+
+### Preview Features (Gating New Features)
+
+**IMPORTANT**: New language features MUST be gated behind preview flags until complete. See [ADR-0005](docs/designs/0005-preview-features.md) for the full design.
+
+#### When to Use Preview Features
+
+Use preview gating when:
+- Adding new syntax (keywords, operators, constructs)
+- Adding new type system features
+- Any feature that spans multiple implementation phases
+
+#### How to Gate a Feature
+
+1. **Add to PreviewFeature enum** in `rue-error/src/lib.rs`:
+   ```rust
+   pub enum PreviewFeature {
+       MutableStrings,
+       HmInference,
+       Destructors,
+       YourNewFeature,  // Add your feature here
+   }
+   ```
+   Also update `name()`, `adr()`, `all()`, and `FromStr` impl.
+
+2. **Add the gate check in Sema** (`rue-air/src/sema.rs`):
+   ```rust
+   // At the point where the feature is used:
+   self.require_preview(PreviewFeature::YourNewFeature, "your feature description", span)?;
+   ```
+
+   **This is the critical step that actually gates the feature!** Without this call, users can use the feature without `--preview`.
+
+3. **Add spec tests with `preview` field**:
+   ```toml
+   [[case]]
+   name = "your_feature_basic"
+   spec = ["X.Y:Z"]
+   preview = "your_new_feature"  # Matches PreviewFeature::name()
+   source = """..."""
+   exit_code = 42
+   ```
+
+4. **Test that the gate works**:
+   - Without `--preview your_new_feature`: Should get "requires preview feature" error
+   - With `--preview your_new_feature`: Should compile/run
+
+#### Stabilizing a Feature
+
+When all tests pass and the feature is complete:
+
+1. Remove `preview = "..."` from spec tests
+2. Remove the `require_preview()` call from Sema
+3. Remove the variant from `PreviewFeature` enum
+4. Update the ADR status to "Implemented"
 
 ### Implementation Steps
 
@@ -331,12 +386,14 @@ When adding or changing language features, follow this checklist:
 4. **Update `rue-rir`** for new IR instructions
 
 5. **Update `rue-air`** for typed versions
+   - **If this is a new feature**: Add the `require_preview()` gate (see above)
 
 6. **Update `rue-codegen`** for code generation
 
 7. **Add spec tests** in `crates/rue-spec/cases/`
    - Include `spec = ["X.Y:Z"]` references to link to spec paragraphs
    - Cover all normative paragraphs (traceability check enforces 100% coverage)
+   - **If this is a preview feature**: Include `preview = "feature_name"` field
 
 8. **Add UI tests** in `crates/rue-ui-tests/cases/` if the feature includes:
    - New warnings or lints
PATCH

echo "Gold patch applied."
