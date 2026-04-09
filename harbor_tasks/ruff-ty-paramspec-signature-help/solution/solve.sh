#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotent: skip if already applied
if grep -q 'signature_help_paramspec_generic_class_constructor_inside_subscript' crates/ty_ide/src/signature_help.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

git apply --whitespace=fix - <<'PATCH'
diff --git a/crates/ty_ide/src/completion.rs b/crates/ty_ide/src/completion.rs
index d56d31f706cb9..a9f9545894b30 100644
--- a/crates/ty_ide/src/completion.rs
+++ b/crates/ty_ide/src/completion.rs
@@ -1503,7 +1503,11 @@ fn add_function_arg_completions<'db>(
 
     for sig in &sig_help.signatures {
         for p in &sig.parameters {
-            if p.is_positional_only || !set_function_args.insert(p.name.as_str()) {
+            if p.is_positional_only
+                || p.is_variadic
+                || p.is_keyword_variadic
+                || !set_function_args.insert(p.name.as_str())
+            {
                 continue;
             }
             let mut builder = CompletionBuilder::argument(&p.name).ty(p.ty);
@@ -4580,6 +4584,45 @@ bar(o<CURSOR>
         );
     }
 
+    #[test]
+    fn call_bare_paramspec_has_no_keyword_argument_completions() {
+        let builder = completion_test_builder(
+            "\
+from typing import Callable, ParamSpec
+
+P = ParamSpec(\"P\")
+sentinel = 1
+
+def takes(f: Callable[P, None]) -> None:
+    f(<CURSOR>
+",
+        )
+        .skip_keywords()
+        .skip_builtins()
+        .skip_auto_import();
+        let completions = builder.build();
+
+        completions.contains("sentinel");
+
+        let keyword_argument_completions = completions
+            .completions()
+            .iter()
+            .filter_map(|completion| {
+                completion
+                    .insert
+                    .as_deref()
+                    .filter(|insert| insert.ends_with('='))
+            })
+            .collect::<Vec<_>>();
+
+        // Bare `ParamSpec` signatures are rendered as a synthetic parameter for
+        // signature help, but they don't correspond to a valid keyword argument.
+        assert!(
+            keyword_argument_completions.is_empty(),
+            "Unexpected keyword argument completions: {keyword_argument_completions:?}",
+        );
+    }
+
     #[test]
     fn call_blank1() {
         let builder = completion_test_builder(
diff --git a/crates/ty_ide/src/signature_help.rs b/crates/ty_ide/src/signature_help.rs
index 0e3d26d1461d1..b3913d20227d4 100644
--- a/crates/ty_ide/src/signature_help.rs
+++ b/crates/ty_ide/src/signature_help.rs
@@ -14,14 +14,15 @@ use ruff_db::parsed::parsed_module;
 use ruff_python_ast::find_node::covering_node;
 use ruff_python_ast::token::TokenKind;
 use ruff_python_ast::{self as ast, AnyNodeRef};
-use ruff_text_size::{Ranged, TextRange, TextSize};
+use ruff_text_size::{Ranged, TextSize};
 use ty_python_semantic::ResolvedDefinition;
 use ty_python_semantic::SemanticModel;
 use ty_python_semantic::semantic_index::definition::Definition;
+use ty_python_semantic::types::Type;
 use ty_python_semantic::types::ide_support::{
-    CallSignatureDetails, call_signature_details, find_active_signature_from_details,
+    CallSignatureDetails, CallSignatureParameter, call_signature_details,
+    find_active_signature_from_details,
 };
-use ty_python_semantic::types::{ParameterKind, Type};
 
 // TODO: We may want to add special-case handling for calls to constructors
 // so the class docstring is used in place of (or inaddition to) any docstring
@@ -41,6 +42,10 @@ pub struct ParameterDetails<'db> {
     pub documentation: Option<String>,
     /// True if the parameter is positional-only.
     pub is_positional_only: bool,
+    /// True if the parameter can absorb arbitrarily many positional arguments.
+    pub is_variadic: bool,
+    /// True if the parameter can absorb arbitrarily many keyword arguments.
+    pub is_keyword_variadic: bool,
 }
 
 /// Information about a function signature
@@ -93,7 +98,7 @@ pub fn signature_help(db: &dyn Db, file: File, offset: TextSize) -> Option<Signa
     let signatures: Vec<SignatureDetails> = signature_details
         .into_iter()
         .map(|details| {
-            create_signature_details_from_call_signature_details(db, &details, current_arg_index)
+            create_signature_details_from_call_signature_details(db, details, current_arg_index)
         })
         .collect();
 
@@ -179,11 +184,9 @@ fn get_argument_index(call_expr: &ast::ExprCall, offset: TextSize) -> usize {
 /// Create signature details from `CallSignatureDetails`.
 fn create_signature_details_from_call_signature_details<'db>(
     db: &dyn crate::Db,
-    details: &CallSignatureDetails<'db>,
+    details: CallSignatureDetails<'db>,
     current_arg_index: usize,
 ) -> SignatureDetails<'db> {
-    let signature_label = details.label.clone();
-
     let documentation = get_callable_documentation(db, details.definition);
 
     // Translate the argument index to parameter index using the mapping.
@@ -192,30 +195,32 @@ fn create_signature_details_from_call_signature_details<'db>(
             Some(0)
         } else {
             details
-                .argument_to_parameter_mapping
+                .argument_to_displayed_parameter_mapping
                 .get(current_arg_index)
-                .and_then(|mapping| mapping.parameters.first().copied())
+                .copied()
+                .flatten()
                 .or({
-                    // If we can't find a mapping for this argument, but we have a current
-                    // argument index, use that as the active parameter if it's within bounds.
-                    if current_arg_index < details.parameter_label_offsets.len() {
+                    // If we can't find a mapping for this argument, fall back to the argument
+                    // index when it still points at a displayed parameter. Otherwise, if the
+                    // last displayed parameter is variadic, keep it active for any later
+                    // positional or keyword arguments that would still bind there. The `- 1`
+                    // converts the parameter count to the zero-based index of that last entry.
+                    if current_arg_index < details.parameters.len() {
                         Some(current_arg_index)
+                    } else if details.parameters.last().is_some_and(|parameter| {
+                        parameter.is_variadic || parameter.is_keyword_variadic
+                    }) {
+                        Some(details.parameters.len() - 1)
                     } else {
                         None
                     }
                 })
         };
 
-    let parameters = create_parameters_from_offsets(
-        &details.parameter_label_offsets,
-        &signature_label,
-        documentation.as_ref(),
-        &details.parameter_names,
-        &details.parameter_kinds,
-        &details.parameter_types,
-    );
+    let parameters = create_parameters(details.parameters, documentation.as_ref());
+    let active_parameter = active_parameter.filter(|&index| index < parameters.len());
     SignatureDetails {
-        label: signature_label,
+        label: details.label,
         documentation,
         parameters,
         active_parameter,
@@ -230,14 +235,10 @@ fn get_callable_documentation(
     Definitions(vec![ResolvedDefinition::Definition(definition?)]).docstring(db)
 }
 
-/// Create `ParameterDetails` objects from parameter label offsets.
-fn create_parameters_from_offsets<'db>(
-    parameter_offsets: &[TextRange],
-    signature_label: &str,
+/// Create `ParameterDetails` objects from semantic displayed parameter details.
+fn create_parameters<'db>(
+    parameters: Vec<CallSignatureParameter<'db>>,
     docstring: Option<&Docstring>,
-    parameter_names: &[String],
-    parameter_kinds: &[ParameterKind],
-    parameter_types: &[Type<'db>],
 ) -> Vec<ParameterDetails<'db>> {
     // Extract parameter documentation from the function's docstring if available.
     let param_docs = if let Some(docstring) = docstring {
@@ -246,31 +247,28 @@ fn create_parameters_from_offsets<'db>(
         std::collections::HashMap::new()
     };
 
-    parameter_offsets
-        .iter()
-        .enumerate()
-        .map(|(i, offset)| {
-            // Extract the parameter label from the signature string.
-            let start = usize::from(offset.start());
-            let end = usize::from(offset.end());
-            let label = signature_label
-                .get(start..end)
-                .unwrap_or("unknown")
-                .to_string();
-
+    parameters
+        .into_iter()
+        .map(|parameter| {
+            let CallSignatureParameter {
+                label,
+                name,
+                ty,
+                is_positional_only,
+                is_variadic,
+                is_keyword_variadic,
+            } = parameter;
             // Get the parameter name for documentation lookup.
-            let param_name = parameter_names.get(i).map(String::as_str).unwrap_or("");
-            let is_positional_only = matches!(
-                parameter_kinds.get(i),
-                Some(ParameterKind::PositionalOnly { .. })
-            );
+            let documentation = param_docs.get(name.as_str()).cloned();
 
             ParameterDetails {
-                name: param_name.to_string(),
+                name,
                 label,
-                ty: parameter_types[i],
-                documentation: param_docs.get(param_name).cloned(),
+                ty,
+                documentation,
                 is_positional_only,
+                is_variadic,
+                is_keyword_variadic,
             }
         })
         .collect()
@@ -901,6 +899,47 @@ def ab(a: int, *, c: int):
         );
     }
 
+    #[test]
+    fn signature_help_paramspec_generic_class_constructor_inside_subscript() {
+        let test = cursor_test(
+            r#"
+        class A[**P]: ...
+
+        A[int,<CURSOR>]()
+        "#,
+        );
+
+        assert_snapshot!(test.signature_help_render(), @"
+
+        ============== active signature =============
+        [**P]() -> A[(int, /)]
+        ---------------------------------------------
+
+        (no active parameter specified)
+        ");
+    }
+
+    #[test]
+    fn signature_help_bare_paramspec_keeps_active_parameter_for_later_arguments() {
+        let test = cursor_test(
+            r#"
+        from typing import Callable, ParamSpec
+
+        P = ParamSpec("P")
+
+        def takes(f: Callable[P, None]) -> None:
+            f(1, <CURSOR>)
+        "#,
+        );
+
+        let result = test.signature_help().expect("Should have signature help");
+        let active_signature = &result.signatures[result.active_signature.unwrap_or(0)];
+
+        assert!(active_signature.label.starts_with("(**P"));
+        assert_eq!(active_signature.active_parameter, Some(0));
+        assert!(active_signature.parameters[0].label.starts_with("**P"));
+    }
+
     #[test]
     fn signature_help_generic_method_resolves_typevars() {
         let test = cursor_test(
diff --git a/crates/ty_python_semantic/src/types/display.rs b/crates/ty_python_semantic/src/types/display.rs
index 29f9b44b8d5fa..e38af9651a0b7 100644
--- a/crates/ty_python_semantic/src/types/display.rs
+++ b/crates/ty_python_semantic/src/types/display.rs
@@ -2245,13 +2245,15 @@ impl<'db> FmtDetailed<'db> for DisplayParameters<'_, 'db> {
                 display_parameters(self, f, self.parameters.as_slice(), arg_separator)?;
             }
             ParametersKind::ParamSpec(typevar) => {
-                write!(f, "**{}", typevar.name(self.db))?;
+                let parameter_name = format!("**{}", typevar.name(self.db));
+                let mut parameter = f.with_detail(TypeDetail::Parameter(parameter_name.clone()));
+                write!(parameter, "{parameter_name}")?;
                 let binding_context = typevar.binding_context(self.db);
                 if let Some(binding_context_name) = binding_context.name(self.db)
                     && let Some(definition) = binding_context.definition()
                     && !self.settings.active_scopes.contains(&definition)
                 {
-                    write!(f, "@{binding_context_name}")?;
+                    write!(parameter, "@{binding_context_name}")?;
                 }
             }
         }
diff --git a/crates/ty_python_semantic/src/types/ide_support.rs b/crates/ty_python_semantic/src/types/ide_support.rs
index 7d684a248ac7b..8b578e4ab6675 100644
--- a/crates/ty_python_semantic/src/types/ide_support.rs
+++ b/crates/ty_python_semantic/src/types/ide_support.rs
@@ -7,7 +7,7 @@ use crate::semantic_index::{attribute_scopes, global_scope, semantic_index, use_
 use crate::types::call::{CallArguments, CallError, MatchedArgument};
 use crate::types::class::{DynamicClassAnchor, DynamicNamedTupleAnchor};
 use crate::types::constraints::ConstraintSetBuilder;
-use crate::types::signatures::{ParameterKind, Signature};
+use crate::types::signatures::{ParametersKind, Signature};
 use crate::types::{
     CallDunderError, CallableTypes, ClassBase, ClassLiteral, ClassType, KnownClass, KnownUnion,
     Type, TypeContext, UnionType,
@@ -595,20 +595,8 @@ pub struct CallSignatureDetails<'db> {
     /// The display label for this signature (e.g., "(param1: str, param2: int) -> str")
     pub label: String,
 
-    /// Label offsets for each parameter in the signature string.
-    /// Each range specifies the start position and length of a parameter label
-    /// within the full signature string.
-    pub parameter_label_offsets: Vec<TextRange>,
-
-    /// The names of the parameters in the signature, in order.
-    /// This provides easy access to parameter names for documentation lookup.
-    pub parameter_names: Vec<String>,
-
-    /// Parameter kinds, useful to determine correct autocomplete suggestions.
-    pub parameter_kinds: Vec<ParameterKind<'db>>,
-
-    /// Annotated types of parameters. If no annotation was provided, this is `Unknown`.
-    pub parameter_types: Vec<Type<'db>>,
+    /// The displayed parameters for this signature, in left-to-right order.
+    pub parameters: Vec<CallSignatureParameter<'db>>,
 
     /// The definition where this callable was originally defined (useful for
     /// extracting docstrings).
@@ -617,6 +605,32 @@ pub struct CallSignatureDetails<'db> {
     /// Mapping from argument indices to parameter indices. This helps
     /// determine which parameter corresponds to which argument position.
     pub argument_to_parameter_mapping: Vec<MatchedArgument<'db>>,
+
+    /// Mapping from argument indices to displayed parameter indices. This accounts for
+    /// displayed signatures that synthesize parameters, like bare `ParamSpec` signatures.
+    pub argument_to_displayed_parameter_mapping: Vec<Option<usize>>,
+}
+
+/// A single displayed parameter in a callable signature for IDE support.
+#[derive(Debug, Clone)]
+pub struct CallSignatureParameter<'db> {
+    /// The rendered label of the parameter as shown in the signature.
+    pub label: String,
+
+    /// The rendered name of the parameter, used for downstream IDE features.
+    pub name: String,
+
+    /// Annotated type of the parameter after applying any inferred specialization.
+    pub ty: Type<'db>,
+
+    /// True if the parameter is positional-only.
+    pub is_positional_only: bool,
+
+    /// True if the parameter can absorb arbitrarily many positional arguments.
+    pub is_variadic: bool,
+
+    /// True if the parameter can absorb arbitrarily many keyword arguments.
+    pub is_keyword_variadic: bool,
 }
 
 impl<'db> CallSignatureDetails<'db> {
@@ -625,30 +639,27 @@ impl<'db> CallSignatureDetails<'db> {
         let specialization = binding.specialization();
         let signature = binding.signature.clone();
         let display_details = signature.display(db).to_string_parts();
-        let (parameter_kinds, parameter_types): (Vec<ParameterKind>, Vec<Type>) = signature
-            .parameters()
+        let (parameters, parameter_to_displayed_parameter_mapping) =
+            displayed_parameters_for_signature(db, &signature, &display_details, specialization);
+        let argument_to_displayed_parameter_mapping = argument_to_parameter_mapping
             .iter()
-            .map(|param| {
-                // Apply the inferred specialization (if any) to resolve TypeVars
-                // in the annotated type. For example, if `_KT` was inferred as
-                // `str` from the call arguments, this turns `_KT` into `str`.
-                let mut ty = param.annotated_type();
-                if let Some(spec) = specialization {
-                    ty = ty.apply_specialization(db, spec);
-                }
-                (param.kind().clone(), ty)
+            .map(|mapping| {
+                mapping.parameters.iter().find_map(|parameter_index| {
+                    parameter_to_displayed_parameter_mapping
+                        .get(*parameter_index)
+                        .copied()
+                        .flatten()
+                })
             })
-            .unzip();
+            .collect();
 
         CallSignatureDetails {
             definition: signature.definition(),
             signature,
             label: display_details.label,
-            parameter_label_offsets: display_details.parameter_ranges,
-            parameter_names: display_details.parameter_names,
-            parameter_kinds,
-            parameter_types,
+            parameters,
             argument_to_parameter_mapping,
+            argument_to_displayed_parameter_mapping,
         }
     }
 
@@ -667,6 +678,105 @@ impl<'db> CallSignatureDetails<'db> {
     }
 }
 
+/// Build the parameter list shown for a rendered signature.
+///
+/// Returns both the displayed parameters and a mapping from each parameter in
+/// `signature` to its displayed parameter index, if any. This accounts for
+/// rendered signatures that synthesize or omit parameters, such as bare
+/// `ParamSpec` signatures, and applies any inferred specialization to the
+/// displayed parameter types.
+fn displayed_parameters_for_signature<'db>(
+    db: &'db dyn Db,
+    signature: &Signature<'db>,
+    display_details: &crate::types::display::SignatureDisplayDetails,
+    specialization: Option<crate::types::generics::Specialization<'db>>,
+) -> (Vec<CallSignatureParameter<'db>>, Vec<Option<usize>>) {
+    // Apply any inferred specialization to displayed parameter types so
+    // call-site substitutions are reflected in the rendered signature. For
+    // example, if `_KT` was inferred as `str`, display `str` instead of `_KT`.
+    let apply_specialization =
+        |ty: Type<'db>| specialization.map_or(ty, |spec| ty.apply_specialization(db, spec));
+    let parameters = signature.parameters();
+
+    match parameters.kind() {
+        ParametersKind::Standard | ParametersKind::Concatenate(_) => {
+            let mut displayed_parameters = Vec::new();
+            let mut parameter_to_displayed_parameter_mapping = vec![None; parameters.len()];
+
+            for (parameter_index, parameter) in parameters.iter().enumerate() {
+                let Some(range) = display_details
+                    .parameter_ranges
+                    .get(parameter_index)
+                    .copied()
+                else {
+                    continue;
+                };
+                let Some(name) = display_details
+                    .parameter_names
+                    .get(parameter_index)
+                    .cloned()
+                else {
+                    continue;
+                };
+                let Some(label) = display_details
+                    .label
+                    .get(range.to_std_range())
+                    .map(ToString::to_string)
+                else {
+                    continue;
+                };
+
+                parameter_to_displayed_parameter_mapping[parameter_index] =
+                    Some(displayed_parameters.len());
+                displayed_parameters.push(CallSignatureParameter {
+                    label,
+                    name,
+                    ty: apply_specialization(parameter.annotated_type()),
+                    is_positional_only: parameter.is_positional_only(),
+                    is_variadic: parameter.is_variadic(),
+                    is_keyword_variadic: parameter.is_keyword_variadic(),
+                });
+            }
+
+            (
+                displayed_parameters,
+                parameter_to_displayed_parameter_mapping,
+            )
+        }
+        ParametersKind::ParamSpec(typevar) => {
+            let parameter_name = format!("**{}", typevar.name(db));
+            let label = display_details
+                .parameter_ranges
+                .first()
+                .and_then(|range| {
+                    display_details
+                        .label
+                        .get(range.to_std_range())
+                        .map(ToString::to_string)
+                })
+                .unwrap_or_else(|| parameter_name.clone());
+            let name = display_details
+                .parameter_names
+                .first()
+                .cloned()
+                .unwrap_or(parameter_name);
+
+            (
+                vec![CallSignatureParameter {
+                    label,
+                    name,
+                    ty: Type::TypeVar(typevar),
+                    is_positional_only: false,
+                    is_variadic: true,
+                    is_keyword_variadic: true,
+                }],
+                vec![Some(0); parameters.len()],
+            )
+        }
+        ParametersKind::Gradual | ParametersKind::Top => (Vec::new(), vec![None; parameters.len()]),
+    }
+}
+
 /// Extract signature details from a function call expression.
 /// This function analyzes the callable being invoked and returns zero or more
 /// `CallSignatureDetails` objects, each representing one possible signature

PATCH

# Rebuild ty with the fix applied (incremental — only changed files recompile).
cargo build --bin ty

# Rebuild test binary with the fix applied.
cargo test -p ty_ide --no-run

echo "Patch applied successfully."
