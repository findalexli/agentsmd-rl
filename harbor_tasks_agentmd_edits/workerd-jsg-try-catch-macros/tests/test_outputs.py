"""
Task: workerd-jsg-try-catch-macros
Repo: cloudflare/workerd @ bca5351754a7d3ee0568971d57435859bc3a71e6
PR:   6021

All checks must pass for reward = 1. Any failure = reward 0.
Each test function maps 1:1 to a check in eval_manifest.yaml.
"""

from pathlib import Path

REPO = "/workspace/workerd"


# ---------------------------------------------------------------------------
# Gates (pass_to_pass, static) — file integrity checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_jsg_header_exists():
    """jsg.h must exist and contain existing JSG macro infrastructure."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    assert header.exists(), "jsg.h not found"
    content = header.read_text()
    # Existing macros that must not be broken
    assert "JSG_REQUIRE" in content, "jsg.h missing JSG_REQUIRE macro"
    assert "namespace workerd::jsg" in content, "jsg.h missing namespace"


# ---------------------------------------------------------------------------
# Fail-to-pass (pr_diff) — core behavioral tests for macro implementation
# ---------------------------------------------------------------------------

# [pr_diff] fail_to_pass
def test_jsg_try_macro_defined():
    """JSG_TRY macro must be defined in jsg.h as a preprocessor macro."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    content = header.read_text()
    assert "#define JSG_TRY" in content, "JSG_TRY macro not defined in jsg.h"


# [pr_diff] fail_to_pass
def test_jsg_catch_macro_defined():
    """JSG_CATCH macro must be defined in jsg.h as a preprocessor macro."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    content = header.read_text()
    assert "#define JSG_CATCH" in content, "JSG_CATCH macro not defined in jsg.h"


# [pr_diff] fail_to_pass
def test_jsg_catch_scope_class():
    """JsgCatchScope helper class must exist in jsg.h to support the macros."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    content = header.read_text()
    assert "class JsgCatchScope" in content, "JsgCatchScope class not declared in jsg.h"
    # Must have the key methods
    assert "catchException" in content, "JsgCatchScope missing catchException method"
    assert "getCaughtException" in content, "JsgCatchScope missing getCaughtException method"


# [pr_diff] fail_to_pass
def test_jsg_catch_scope_implementation():
    """JsgCatchScope must be implemented in jsg.c++ with exception handling logic."""
    impl = Path(REPO) / "src/workerd/jsg/jsg.c++"
    content = impl.read_text()
    assert "JsgCatchScope::JsgCatchScope" in content, \
        "JsgCatchScope constructor not implemented in jsg.c++"
    assert "JsgCatchScope::catchException" in content, \
        "catchException not implemented in jsg.c++"
    # Must handle both JsExceptionThrown and kj::Exception
    assert "JsExceptionThrown" in content, \
        "Implementation must handle JsExceptionThrown"


# [pr_diff] fail_to_pass
def test_jsg_try_macro_uses_try_catch():
    """JSG_TRY macro must set up a v8::TryCatch via JsgCatchScope."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    content = header.read_text()
    # The macro should reference JsgCatchScope to set up the scope
    macro_section = content[content.index("#define JSG_TRY"):]
    assert "JsgCatchScope" in macro_section[:500], \
        "JSG_TRY macro must use JsgCatchScope"


# [pr_diff] fail_to_pass
def test_jsg_catch_handles_variadic_options():
    """JSG_CATCH must support optional ExceptionToJsOptions argument via __VA_ARGS__."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    content = header.read_text()
    # The CATCH macro should use variadic args for options
    catch_def = content[content.index("#define JSG_CATCH"):]
    assert "__VA_ARGS__" in catch_def[:500], \
        "JSG_CATCH must support variadic options via __VA_ARGS__"


# [pr_diff] fail_to_pass
def test_crypto_uses_jsg_try():
    """crypto.c++ must be refactored to use JSG_TRY/JSG_CATCH instead of js.tryCatch."""
    crypto = Path(REPO) / "src/workerd/api/crypto/crypto.c++"
    content = crypto.read_text()
    assert "JSG_TRY(js)" in content, \
        "crypto.c++ should use JSG_TRY macro"
    assert "JSG_CATCH(" in content, \
        "crypto.c++ should use JSG_CATCH macro"


# [pr_diff] fail_to_pass
def test_streams_uses_jsg_try():
    """standard.c++ must be refactored to use JSG_TRY/JSG_CATCH."""
    streams = Path(REPO) / "src/workerd/api/streams/standard.c++"
    content = streams.read_text()
    assert "JSG_TRY(js)" in content, \
        "standard.c++ should use JSG_TRY macro"
    assert "JSG_CATCH(" in content, \
        "standard.c++ should use JSG_CATCH macro"


# [pr_diff] fail_to_pass
def test_modules_uses_jsg_try():
    """modules-new.c++ must be refactored to use JSG_TRY/JSG_CATCH."""
    modules = Path(REPO) / "src/workerd/jsg/modules-new.c++"
    content = modules.read_text()
    assert "JSG_TRY(js)" in content, \
        "modules-new.c++ should use JSG_TRY macro"
    assert "JSG_CATCH(" in content, \
        "modules-new.c++ should use JSG_CATCH macro"


# [pr_diff] fail_to_pass
def test_function_test_covers_new_macros():
    """function-test.c++ must have test cases exercising JSG_TRY/JSG_CATCH."""
    test_file = Path(REPO) / "src/workerd/jsg/function-test.c++"
    content = test_file.read_text()
    assert "JSG_TRY(js)" in content, \
        "function-test.c++ must test JSG_TRY"
    assert "JSG_CATCH(" in content, \
        "function-test.c++ must test JSG_CATCH"
    # Must test nested usage
    assert "Nested" in content or "nested" in content, \
        "function-test.c++ should test nested JSG_TRY/JSG_CATCH"


# ---------------------------------------------------------------------------
# Config edit tests (config_edit) — README documentation updates
# ---------------------------------------------------------------------------

# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# [config_edit] fail_to_pass


# ---------------------------------------------------------------------------
# Pass-to-pass (static) — regression checks
# ---------------------------------------------------------------------------

# [static] pass_to_pass
def test_existing_tryCatch_method_preserved():
    """The js.tryCatch() method must still exist in the header (not removed)."""
    header = Path(REPO) / "src/workerd/jsg/jsg.h"
    content = header.read_text()
    # The tryCatch method should still be declared (macros supplement, not replace)
    assert "tryCatch" in content, \
        "js.tryCatch() method should still exist in jsg.h"
