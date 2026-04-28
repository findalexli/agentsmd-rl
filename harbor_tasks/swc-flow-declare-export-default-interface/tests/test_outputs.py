"""Tests for swc PR #11692 — Flow `declare export default interface` parsing.

The fail-to-pass tests use a small Rust regression test that we drop into the
swc_ecma_parser crate at test time.  Doing it this way keeps the regression
test invisible to the agent (the /tests directory is mounted only at
verification time) and lets us assert exact AST shape with the parser
library directly, instead of relying on snapshot fixtures.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import textwrap
from pathlib import Path

REPO = Path("/workspace/swc")
REGRESSION_RS = REPO / "crates/swc_ecma_parser/tests/_pr11692_regression.rs"

REGRESSION_SOURCE = r"""#![cfg(feature = "flow")]
//! Programmatic regression checks for PR #11692
//! (`declare export default interface ...` Flow strip path).

use swc_common::{sync::Lrc, FileName, SourceMap};
use swc_ecma_ast::{Decl, EsVersion, ModuleItem, Program, Stmt};
use swc_ecma_parser::{lexer::Lexer, FlowSyntax, Parser, StringInput, Syntax};

fn parse_flow(src: &str) -> (Program, Vec<String>) {
    let cm: Lrc<SourceMap> = Default::default();
    let fm = cm.new_source_file(FileName::Custom("test.js".into()).into(), String::from(src));
    let lexer = Lexer::new(
        Syntax::Flow(FlowSyntax::default()),
        EsVersion::Es2015,
        StringInput::from(&*fm),
        None,
    );
    let mut parser = Parser::new_from(lexer);
    let program = parser
        .parse_program()
        .unwrap_or_else(|e| panic!("parse_program failed: {:?}", e));
    let errs: Vec<String> = parser
        .take_errors()
        .into_iter()
        .map(|e| format!("{:?}", e))
        .collect();
    (program, errs)
}

fn first_stmt(program: &Program) -> &Stmt {
    match program {
        Program::Script(s) => s.body.first().expect("script has no statements"),
        Program::Module(m) => match m.body.first().expect("module has no items") {
            ModuleItem::Stmt(s) => s,
            ModuleItem::ModuleDecl(_) => panic!("expected a statement, got a module decl"),
        },
    }
}

#[test]
fn declare_export_default_interface_basic() {
    let (program, errs) = parse_flow("declare export default interface Foo {\n  x: number;\n}\n");
    assert!(errs.is_empty(), "unexpected parser errors: {:?}", errs);
    match first_stmt(&program) {
        Stmt::Decl(Decl::TsInterface(iface)) => {
            assert!(iface.declare, "interface should be marked declare");
            assert_eq!(&*iface.id.sym, "Foo");
            assert!(iface.extends.is_empty(), "should have no extends clause");
            assert_eq!(iface.body.body.len(), 1, "expected 1 interface member");
        }
        other => panic!("expected TsInterface decl, got {:?}", other),
    }
}

#[test]
fn declare_export_default_interface_with_extends() {
    let (program, errs) =
        parse_flow("declare export default interface Bar extends Base { y: string; }");
    assert!(errs.is_empty(), "unexpected parser errors: {:?}", errs);
    match first_stmt(&program) {
        Stmt::Decl(Decl::TsInterface(iface)) => {
            assert!(iface.declare);
            assert_eq!(&*iface.id.sym, "Bar");
            assert_eq!(iface.extends.len(), 1, "expected 1 extends clause");
            assert_eq!(iface.body.body.len(), 1);
        }
        other => panic!("expected TsInterface decl, got {:?}", other),
    }
}

#[test]
fn declare_export_default_class_still_works() {
    // Pre-existing behavior must not regress.
    let (program, errs) = parse_flow("declare export default class C {\n  x: number;\n}");
    assert!(errs.is_empty(), "unexpected parser errors: {:?}", errs);
    match first_stmt(&program) {
        Stmt::Decl(Decl::Class(cls)) => {
            assert!(cls.declare);
            assert_eq!(&*cls.ident.sym, "C");
        }
        other => panic!("expected Class decl, got {:?}", other),
    }
}

#[test]
fn declare_export_default_type_still_works() {
    // Pre-existing fallback path must not regress: bare type at default
    // position becomes a synthetic type alias.
    let (program, errs) = parse_flow("declare export default number;");
    assert!(errs.is_empty(), "unexpected parser errors: {:?}", errs);
    match first_stmt(&program) {
        Stmt::Decl(Decl::TsTypeAlias(alias)) => {
            assert!(alias.declare);
        }
        other => panic!("expected TsTypeAlias decl, got {:?}", other),
    }
}
"""


def _ensure_regression_rs() -> None:
    """Drop the regression test file into the parser crate."""
    REGRESSION_RS.parent.mkdir(parents=True, exist_ok=True)
    REGRESSION_RS.write_text(REGRESSION_SOURCE)


def _run_cargo(args: list[str], timeout: int = 900) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["cargo", *args],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ, "CARGO_TERM_COLOR": "never"},
    )


# ----- Fail-to-pass: behavioral checks via regression test crate ---------- #

def test_parses_declare_export_default_interface_basic():
    """Behavior: `declare export default interface Foo { x: number; }` must
    parse to a `TsInterfaceDeclaration` with `declare = true` (fail-to-pass)."""
    _ensure_regression_rs()
    r = _run_cargo(
        [
            "test",
            "-p",
            "swc_ecma_parser",
            "--features",
            "flow",
            "--test",
            "_pr11692_regression",
            "--",
            "declare_export_default_interface_basic",
            "--exact",
            "--nocapture",
        ],
        timeout=900,
    )
    assert r.returncode == 0, (
        "Regression test failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout, (
        f"Test did not run.\nstdout:\n{r.stdout[-2000:]}\nstderr:\n{r.stderr[-2000:]}"
    )


def test_parses_declare_export_default_interface_with_extends():
    """Behavior: extended interface form parses too (fail-to-pass)."""
    _ensure_regression_rs()
    r = _run_cargo(
        [
            "test",
            "-p",
            "swc_ecma_parser",
            "--features",
            "flow",
            "--test",
            "_pr11692_regression",
            "--",
            "declare_export_default_interface_with_extends",
            "--exact",
            "--nocapture",
        ],
        timeout=900,
    )
    assert r.returncode == 0, (
        "Regression (with-extends) failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )
    assert "test result: ok. 1 passed" in r.stdout


# ----- Pass-to-pass: pre-existing behavior must keep working -------------- #

def test_existing_declare_export_default_class_unaffected():
    """Pre-existing form `declare export default class C` must still parse."""
    _ensure_regression_rs()
    r = _run_cargo(
        [
            "test",
            "-p",
            "swc_ecma_parser",
            "--features",
            "flow",
            "--test",
            "_pr11692_regression",
            "--",
            "declare_export_default_class_still_works",
            "--exact",
            "--nocapture",
        ],
        timeout=900,
    )
    assert r.returncode == 0, (
        "Regression (class still works) failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


def test_existing_declare_export_default_type_unaffected():
    """Pre-existing form `declare export default <type>;` must still parse
    via the synthetic-type-alias fallback path."""
    _ensure_regression_rs()
    r = _run_cargo(
        [
            "test",
            "-p",
            "swc_ecma_parser",
            "--features",
            "flow",
            "--test",
            "_pr11692_regression",
            "--",
            "declare_export_default_type_still_works",
            "--exact",
            "--nocapture",
        ],
        timeout=900,
    )
    assert r.returncode == 0, (
        "Regression (type still works) failed.\n"
        f"--- stdout ---\n{r.stdout[-2000:]}\n--- stderr ---\n{r.stderr[-2000:]}"
    )


# ----- Pass-to-pass from repo CI ---------------------------------------- #

def test_repo_cargo_check_parser():
    """Repo's own `cargo check` for the parser crate keeps passing."""
    r = _run_cargo(
        ["check", "-p", "swc_ecma_parser", "--features", "flow", "--tests"],
        timeout=900,
    )
    assert r.returncode == 0, (
        f"cargo check failed:\n{r.stderr[-2000:]}"
    )


def test_repo_cargo_fmt_clean():
    """Touched parser source must be `rustfmt --check` clean."""
    r = subprocess.run(
        [
            "rustfmt",
            "--check",
            "--edition",
            "2021",
            "crates/swc_ecma_parser/src/parser/typescript.rs",
        ],
        cwd=str(REPO),
        capture_output=True,
        text=True,
        timeout=120,
    )
    assert r.returncode == 0, (
        "rustfmt --check reported formatting issues in the touched parser file:\n"
        f"{r.stdout[-2000:]}\n{r.stderr[-2000:]}"
    )

# === CI-mined tests (taskforge.ci_check_miner) ===
def test_ci_test_with__swc_cli_prepare():
    """pass_to_pass | CI job 'Test with @swc/cli' → step 'Prepare'"""
    r = subprocess.run(
        ["bash", "-lc", 'rustup target add wasm32-wasip1 && yarn && yarn build:dev && cargo clean && cargo clean) && npm install -g @swc/cli@0.1.56 && npm link && npm install -g file:$PWD'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Prepare' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_with__swc_cli_print_info():
    """pass_to_pass | CI job 'Test with @swc/cli' → step 'Print info'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm list -g'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Print info' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_with__swc_cli_swc_redux():
    """pass_to_pass | CI job 'Test with @swc/cli' → step '(swc) redux'"""
    r = subprocess.run(
        ["bash", "-lc", "yarn) && npx jest '.*.js' --modulePathIgnorePatterns 'typescript')"], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '(swc) redux' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_test_with__swc_cli_swcpack_example_react_app():
    """pass_to_pass | CI job 'Test with @swc/cli' → step '(swcpack) example react app'"""
    r = subprocess.run(
        ["bash", "-lc", 'npm install && npx spack)'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step '(swcpack) example react app' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")

def test_ci_check_license_of_dependencies_check_licenses():
    """pass_to_pass | CI job 'Check license of dependencies' → step 'Check licenses'"""
    r = subprocess.run(
        ["bash", "-lc", 'cargo deny check'], cwd=REPO,
        capture_output=True, text=True, timeout=300)
    assert r.returncode == 0, (
        f"CI step 'Check licenses' failed (returncode={r.returncode}):\n"
        f"stdout: {r.stdout[-1500:]}\nstderr: {r.stderr[-1500:]}")