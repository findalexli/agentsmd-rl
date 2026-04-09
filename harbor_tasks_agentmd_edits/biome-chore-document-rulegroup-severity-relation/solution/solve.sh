#!/usr/bin/env bash
set -euo pipefail

cd /workspace/biome

# Idempotent: skip if already applied
if grep -q 'struct Errors {' xtask/rules_check/src/lib.rs 2>/dev/null; then
    echo "Patch already applied."
    exit 0
fi

# Apply the patch
git apply - <<'PATCH'
diff --git a/crates/biome_analyze/CONTRIBUTING.md b/crates/biome_analyze/CONTRIBUTING.md
index 94e9dbe2626d..c8a6a7641162 100644
--- a/crates/biome_analyze/CONTRIBUTING.md
+++ b/crates/biome_analyze/CONTRIBUTING.md
@@ -26,6 +26,7 @@ The analyzer allows implementors to create **three different** types of rules:
         * [Biome lint rules inspired by other lint rules](#biome-lint-rules-inspired-by-other-lint-rules)
       - [`rule_category!` macro](#rule_category-macro)
       - [Rule severity](#rule-severity)
+      - [Rule group and severity](#rule-group-and-severity)
       - [Rule domains](#rule-domains)
       - [Rule Options](#rule-options)
         * [Options for our example rule](#options-for-our-example-rule)
@@ -516,6 +517,28 @@ declare_lint_rule! {
 }
 ```

+#### Rule group and severity
+
+> [!NOTE]
+> This section is relevant to Biome maintainers when they want to move (promote) a rule to a group that is not `nursery`.
+
+We try to maintain consistency in the default severity level and group membership of the rules.
+For legacy reasons, we have some rules that don't follow these constraints.
+
+- `correctness`, `security`, and `a11y` rules **must** have a severity set to `error`.
+
+  If `error` is too strict for a rule, then it should certainly be in another group (for example `suspicious` instead of `correctness`).
+
+- `style` rules **must** have a severity set to `info` or `warn`. If in doubt, choose `info`.
+
+- `complexity` rules **must** have a severity set to `warn` or `info`. If in doubt, choose `info`.
+
+- `suspicious` rules **must** have a severity set to `warn` or `error`. If in doubt, choose `warn`.
+
+- `performance` rules **must** have a severity set to `warn`.
+
+- Actions **must** have a severity set to `info`.
+
 #### Rule domains

 Domains are very specific ways to collect rules that belong to the same "concept". Domains are a way for users to opt-in/opt-out rules that belong to the same domain.
@@ -548,6 +571,7 @@ Instead, if the rule is **recommended** but _doesn't have domains_, the rule is
 > [!NOTE]
 > Before adding a new domain, please consult with the maintainers of the project.

+
 #### Rule Options

 Some rules may allow customization [using per-rule options in `biome.json`](https://biomejs.dev/linter/#rule-options).
diff --git a/xtask/rules_check/src/lib.rs b/xtask/rules_check/src/lib.rs
index a82644afa488..81fd7da83dec 100644
--- a/xtask/rules_check/src/lib.rs
+++ b/xtask/rules_check/src/lib.rs
@@ -32,30 +32,22 @@ use std::slice;
 use std::str::FromStr;

 #[derive(Debug)]
-struct Errors(String);
-
+struct Errors {
+    message: String,
+}
 impl Errors {
-    fn style_rule_error(rule_name: impl Display) -> Self {
-        Self(format!(
-            "The rule '{rule_name}' that belongs to the group 'style' can't have Severity::Error. Lower down the severity or change the group.",
-        ))
-    }
-
-    fn action_error(rule_name: impl Display) -> Self {
-        Self(format!(
-            "The rule '{rule_name}' is an action, and it must have Severity::Information. Lower down the severity.",
-        ))
+    const fn new(message: String) -> Self {
+        Self { message }
     }
 }
-
+impl std::error::Error for Errors {}
 impl Display for Errors {
     fn fmt(&self, f: &mut Formatter<'_>) -> std::fmt::Result {
-        f.write_str(self.0.as_str())
+        let Self { message } = self;
+        f.write_str(message)
     }
 }

-impl std::error::Error for Errors {}
-
 type Data = BTreeMap<&'static str, (RuleMetadata, RuleCategory)>;
 pub fn check_rules() -> anyhow::Result<()> {
     #[derive(Default)]
@@ -73,12 +65,74 @@ pub fn check_rules() -> anyhow::Result<()> {
             if !matches!(category, RuleCategory::Lint | RuleCategory::Action) {
                 return;
             }
-            if R::Group::NAME == "style" && R::METADATA.severity == Severity::Error {
-                self.errors.push(Errors::style_rule_error(R::METADATA.name))
+            let group = R::Group::NAME;
+            let rule_name = R::METADATA.name;
+            let rule_severity = R::METADATA.severity;
+            if matches!(group, "a11y" | "correctness" | "security")
+                && rule_severity != Severity::Error
+                && !matches!(
+                    rule_name,
+                    // TODO: remove these exceptions in Biome 3.0
+                    "noNodejsModules"
+                        | "noPrivateImports"
+                        | "noUnusedFunctionParameters"
+                        | "noUnusedImports"
+                        | "noUnusedLabels"
+                        | "noUnusedPrivateClassMembers"
+                        | "noUnusedVariables"
+                        | "useImportExtensions"
+                        | "noNoninteractiveElementInteractions"
+                        | "noGlobalDirnameFilename"
+                        | "noProcessGlobal"
+                        | "noReactPropAssignments"
+                        | "noRestrictedElements"
+                        | "noSolidDestructuredProps"
+                        | "useJsonImportAttributes"
+                        | "useParseIntRadix"
+                        | "useSingleJsDocAsterisk"
+                )
+            {
+                self.errors.push(Errors::new(format!(
+                    "The rule '{rule_name}' belongs to the group '{group}' and has a severity set to '{rule_severity}'. Rules that belong to the group {group} must have a severity set to 'error'. Set the severity to 'error' or change the group of the rule."
+                )));
+            } else if matches!(group, "complexity" | "style") && rule_severity == Severity::Error {
+                self.errors.push(Errors::new(format!(
+                    "The rule '{rule_name}' belongs to the group '{group}' and has a severity set to '{rule_severity}'. Rules that belong to the group '{group}' must not have a severity set to 'error'. Lower down the severity or change the group of the rule."
+                )));
+            } else if group == "performance"
+                && rule_severity != Severity::Warning
+                && !matches!(
+                    rule_name,
+                    // TODO: remove these exceptions in Biome 3.0
+                    "noAwaitInLoops" | "useGoogleFontPreconnect" | "useSolidForComponent"
+                )
+            {
+                self.errors.push(Errors::new(format!(
+                    "The rule '{rule_name}' belongs to the group '{group}' and has a severity set to '{rule_severity}'. Rules that belong to the group '{group}' must have a severity set to 'warn'. Set the severity to 'warn' or change the group of the rule."
+                )));
+            } else if group == "suspicious"
+                && rule_severity == Severity::Information
+                && !matches!(
+                    rule_name,
+                    // TODO: remove these exceptions in Biome 3.0
+                    "noAlert"
+                        | "noBitwiseOperators"
+                        | "noConstantBinaryExpressions"
+                        | "noUnassignedVariables"
+                        | "useStaticResponseMethods"
+                        | "noQuickfixBiome"
+                        | "noDuplicateFields"
+                )
+            {
+                self.errors.push(Errors::new(format!(
+                    "The rule '{rule_name}' belongs to the group '{group}' and has a severity set to '{rule_severity}'. Rules that belong to the group '{group}' must have a severity set to 'warn' or 'error'. Change the severity or change the group of the rule."
+                )));
             } else if <R::Group as RuleGroup>::Category::CATEGORY == RuleCategory::Action
-                && R::METADATA.severity != Severity::Information
+                && rule_severity != Severity::Information
             {
-                self.errors.push(Errors::action_error(R::METADATA.name));
+                self.errors.push(Errors::new(format!(
+                    "The action '{rule_name}' has a severity set to '{rule_severity}'. Actions must have a severity set to 'info'. Set the severity of the rule to 'info'."
+                )));
             } else {
                 self.groups
                     .entry((<R::Group as RuleGroup>::NAME, R::METADATA.language))

PATCH

echo "Patch applied successfully."
