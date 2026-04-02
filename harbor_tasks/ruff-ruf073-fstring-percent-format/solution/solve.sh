#!/usr/bin/env bash
set -euo pipefail

cd /workspace/ruff

# Idempotency: check if already applied
if grep -q 'FStringPercentFormat' crates/ruff_linter/src/rules/ruff/rules/mod.rs 2>/dev/null; then
    echo "Patch already applied"
    exit 0
fi

git apply - <<'PATCH'
diff --git a/crates/ruff_linter/resources/test/fixtures/ruff/RUF073.py b/crates/ruff_linter/resources/test/fixtures/ruff/RUF073.py
new file mode 100644
index 0000000000000..b5d83ddf5894e
--- /dev/null
+++ b/crates/ruff_linter/resources/test/fixtures/ruff/RUF073.py
@@ -0,0 +1,24 @@
+name = "world"
+banana = "banana"
+
+# Errors: f-string used with % operator
+f"{banana}" % banana  # RUF073
+f"hello %s" % "world"  # RUF073
+f"hello %s %s" % (1, 2)  # RUF073
+f"{name} %s" % "extra"  # RUF073
+f"no placeholders" % banana  # RUF073
+f"{'nested'} %s" % 42  # RUF073
+
+# OK: regular string with % operator
+"hello %s" % "world"
+"%s %s" % (1, 2)
+"hello %s" % name
+b"hello %s" % (name,)
+
+# OK: f-string without % operator
+f"hello {name}"
+f"{banana}"
+
+# OK: modulo on non-string types
+42 % 10
+x = 100 % 3
diff --git a/crates/ruff_linter/src/checkers/ast/analyze/expression.rs b/crates/ruff_linter/src/checkers/ast/analyze/expression.rs
index dd62add929580..9798cf43f6d45 100644
--- a/crates/ruff_linter/src/checkers/ast/analyze/expression.rs
+++ b/crates/ruff_linter/src/checkers/ast/analyze/expression.rs
@@ -1532,6 +1532,9 @@ pub(crate) fn expression(expr: &Expr, checker: &Checker) {
                     flake8_bandit::rules::hardcoded_sql_expression(checker, expr);
                 }
             }
+            if checker.is_rule_enabled(Rule::FStringPercentFormat) {
+                ruff::rules::fstring_percent_format(checker, bin_op);
+            }
         }
         Expr::BinOp(ast::ExprBinOp {
             op: Operator::Add, ..
diff --git a/crates/ruff_linter/src/codes.rs b/crates/ruff_linter/src/codes.rs
index 0559059f79e64..057de14bfcec1 100644
--- a/crates/ruff_linter/src/codes.rs
+++ b/crates/ruff_linter/src/codes.rs
@@ -1070,6 +1070,7 @@ pub fn code_to_rule(linter: Linter, code: &str) -> Option<(RuleGroup, Rule)> {
         (Ruff, "070") => rules::ruff::rules::UnnecessaryAssignBeforeYield,
         (Ruff, "071") => rules::ruff::rules::OsPathCommonprefix,
         (Ruff, "072") => rules::ruff::rules::UselessFinally,
+        (Ruff, "073") => rules::ruff::rules::FStringPercentFormat,

         (Ruff, "100") => rules::ruff::rules::UnusedNOQA,
         (Ruff, "101") => rules::ruff::rules::RedirectedNOQA,
diff --git a/crates/ruff_linter/src/rules/ruff/mod.rs b/crates/ruff_linter/src/rules/ruff/mod.rs
index 78ae80e1026ed..30baf22418d00 100644
--- a/crates/ruff_linter/src/rules/ruff/mod.rs
+++ b/crates/ruff_linter/src/rules/ruff/mod.rs
@@ -734,6 +734,7 @@ mod tests {
     #[test_case(Rule::UnnecessaryAssignBeforeYield, Path::new("RUF070.py"))]
     #[test_case(Rule::OsPathCommonprefix, Path::new("RUF071.py"))]
     #[test_case(Rule::UselessFinally, Path::new("RUF072.py"))]
+    #[test_case(Rule::FStringPercentFormat, Path::new("RUF073.py"))]
     fn preview_rules(rule_code: Rule, path: &Path) -> Result<()> {
         let snapshot = format!(
             "preview__{}_{}",
diff --git a/crates/ruff_linter/src/rules/ruff/rules/fstring_percent_format.rs b/crates/ruff_linter/src/rules/ruff/rules/fstring_percent_format.rs
new file mode 100644
index 0000000000000..ac282b22e49e2
--- /dev/null
+++ b/crates/ruff_linter/src/rules/ruff/rules/fstring_percent_format.rs
@@ -0,0 +1,54 @@
+use ruff_macros::{ViolationMetadata, derive_message_formats};
+use ruff_python_ast::{self as ast, Expr, Operator};
+use ruff_text_size::Ranged;
+
+use crate::Violation;
+use crate::checkers::ast::Checker;
+
+/// ## What it does
+/// Checks for uses of the `%` operator on f-strings.
+///
+/// ## Why is this bad?
+/// F-strings already support interpolation via `{...}` expressions.
+/// Using the `%` operator on an f-string is almost certainly a mistake,
+/// since the f-string's interpolation and `%`-formatting serve the same
+/// purpose. This typically indicates that the developer intended to use
+/// either an f-string or `%`-formatting, but not both.
+///
+/// ## Example
+/// ```python
+/// f"{name}" % name
+/// f"hello %s %s" % (first, second)
+/// ```
+///
+/// Use instead:
+/// ```python
+/// f"{name}"
+/// f"hello {first} {second}"
+/// ```
+#[derive(ViolationMetadata)]
+#[violation_metadata(preview_since = "NEXT_RUFF_VERSION")]
+pub(crate) struct FStringPercentFormat;
+
+impl Violation for FStringPercentFormat {
+    #[derive_message_formats]
+    fn message(&self) -> String {
+        "`%` operator used on an f-string".to_string()
+    }
+}
+
+/// RUF073
+pub(crate) fn fstring_percent_format(checker: &Checker, expr: &ast::ExprBinOp) {
+    let ast::ExprBinOp {
+        left,
+        op: Operator::Mod,
+        ..
+    } = expr
+    else {
+        return;
+    };
+
+    if matches!(left.as_ref(), Expr::FString(_)) {
+        checker.report_diagnostic(FStringPercentFormat, expr.range());
+    }
+}
diff --git a/crates/ruff_linter/src/rules/ruff/rules/mod.rs b/crates/ruff_linter/src/rules/ruff/rules/mod.rs
index dfa6d0900bb06..b2310a717151b 100644
--- a/crates/ruff_linter/src/rules/ruff/rules/mod.rs
+++ b/crates/ruff_linter/src/rules/ruff/rules/mod.rs
@@ -12,6 +12,7 @@ pub(crate) use duplicate_entry_in_dunder_all::*;
 pub(crate) use explicit_f_string_type_conversion::*;
 pub(crate) use falsy_dict_get_fallback::*;
 pub(crate) use float_equality_comparison::*;
+pub(crate) use fstring_percent_format::*;
 pub(crate) use function_call_in_dataclass_default::*;
 pub(crate) use if_key_in_dict_del::*;
 pub(crate) use implicit_classvar_in_dataclass::*;
@@ -85,6 +86,7 @@ mod duplicate_entry_in_dunder_all;
 mod explicit_f_string_type_conversion;
 mod falsy_dict_get_fallback;
 mod float_equality_comparison;
+mod fstring_percent_format;
 mod function_call_in_dataclass_default;
 mod if_key_in_dict_del;
 mod implicit_classvar_in_dataclass;
diff --git a/ruff.schema.json b/ruff.schema.json
index 9dbae611cc90a..405a94d1f7a56 100644
--- a/ruff.schema.json
+++ b/ruff.schema.json
@@ -4219,6 +4219,7 @@
         "RUF070",
         "RUF071",
         "RUF072",
+        "RUF073",
         "RUF1",
         "RUF10",
         "RUF100",

PATCH
