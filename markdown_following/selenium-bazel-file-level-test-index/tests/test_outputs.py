"""Behavioral tests for the file-level Bazel test-target index in
rake_tasks/bazel.rake.

Each test exercises the rake file via a Ruby driver that stubs
`Bazel.execute`, loads the rake task file, and emits a JSON document
we parse here.
"""

from __future__ import annotations

import json
import os
import subprocess
import textwrap
from pathlib import Path

REPO = "/workspace/selenium"
RAKE_FILE = f"{REPO}/rake_tasks/bazel.rake"


_RUBY_DRIVER = textwrap.dedent(r"""
    # frozen_string_literal: true
    # Stubs Bazel.execute, loads rake_tasks/bazel.rake under the
    # bazel: namespace, and emits a JSON document on stdout for the
    # Python harness to parse. Driven via ARGV[0] action.

    require 'json'
    require 'fileutils'
    require 'set'
    require 'rake'

    $bazel_queries = []
    $bazel_responses = JSON.parse(ENV.fetch('BAZEL_RESPONSES', '{}'))

    module Bazel
      def self.execute(_kind, _args, target, &block)
        $bazel_queries << target
        out = ''
        $bazel_responses.each do |pat, resp|
          if Regexp.new(pat).match?(target)
            out = resp
            break
          end
        end
        block&.call(out)
        nil
      end
    end

    BINDING_TARGETS = {
      'java' => '//java/...',
      'py' => '//py/...',
      'rb' => '//rb/...',
      'dotnet' => '//dotnet/...',
      'javascript' => '//javascript/selenium-webdriver/...'
    }.freeze

    namespace(:bazel) { load 'rake_tasks/bazel.rake' }

    def emit(payload)
      payload[:queries] = $bazel_queries
      puts JSON.generate(payload)
    end

    action = ARGV[0]

    begin
      case action
      when 'pattern_match'
        paths = ARGV[1..]
        if defined?(HIGH_IMPACT_PATTERN)
          results = paths.to_h { |p| [p, !!HIGH_IMPACT_PATTERN.match?(p)] }
          emit(action: action, defined: true, results: results)
        else
          emit(action: action, defined: false, results: {})
        end

      when 'high_impact_dirs'
        if defined?(HIGH_IMPACT_DIRS)
          emit(action: action, defined: true, dirs: HIGH_IMPACT_DIRS)
        else
          emit(action: action, defined: false, dirs: [])
        end

      when 'lookup'
        index_file = ARGV[1]
        changed_files = ARGV[2..]
        result = affected_targets_with_index(changed_files, index_file)
        emit(action: action, affected: result.sort)

      when 'build_index'
        out_file = ARGV[1]
        Rake::Task['bazel:build_test_index'].invoke(out_file)
        json = JSON.parse(File.read(out_file))
        emit(action: action, index: json)

      else
        warn "Unknown action: #{action}"
        exit 2
      end
    rescue NameError, NoMethodError => e
      emit(action: action, error: "#{e.class}: #{e.message}")
      exit 3
    end
""").strip()


def _driver_path() -> str:
    """Materialise the embedded Ruby driver into /tmp once per session."""
    p = Path("/tmp/_selenium_test_driver.rb")
    if not p.exists() or p.read_text() != _RUBY_DRIVER:
        p.write_text(_RUBY_DRIVER)
    return str(p)


def _run_driver(args: list[str], responses: dict | None = None, timeout: int = 60) -> dict:
    env = os.environ.copy()
    if responses is not None:
        env["BAZEL_RESPONSES"] = json.dumps(responses)
    result = subprocess.run(
        ["ruby", _driver_path(), *args],
        cwd=REPO,
        env=env,
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    stdout = result.stdout.strip()
    last_line = stdout.splitlines()[-1] if stdout else ""
    try:
        return json.loads(last_line)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"driver did not emit JSON on last stdout line. "
            f"exit={result.returncode}\nstdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        ) from e


# ───────────────────────── f2p: behavioral tests ──────────────────────────


def test_high_impact_pattern_matches_required_dirs():
    """Files under common/, rust/src/, javascript/atoms/, javascript/webdriver/atoms/
    must be flagged as high-impact (so all bindings re-run)."""
    paths_expected_to_match = [
        "common/foo.txt",
        "common/src/sub/bar.go",
        "rust/src/main.rs",
        "rust/src/handler/mod.rs",
        "javascript/atoms/foo.js",
        "javascript/webdriver/atoms/bar.js",
    ]
    out = _run_driver(["pattern_match", *paths_expected_to_match])
    assert out.get("defined") == True, (  # noqa: E712
        f"HIGH_IMPACT_PATTERN constant is not defined in rake_tasks/bazel.rake: {out}"
    )
    expected = {p: True for p in paths_expected_to_match}
    assert out["results"] == expected, (
        f"HIGH_IMPACT_PATTERN match results differ from expected.\n"
        f"expected: {expected}\nactual:   {out['results']}"
    )


def test_high_impact_pattern_excludes_unrelated_dirs():
    """The pattern must use directory boundaries — sibling-prefix paths and
    non-listed top-level dirs must NOT be treated as high-impact."""
    paths_expected_no_match = [
        "rust/foo.rs",
        "mycommon/foo.txt",
        "javascript/atoms-helper/foo.js",
        "java/foo.java",
        "py/some/file.py",
        "rb/lib/x.rb",
    ]
    out = _run_driver(["pattern_match", *paths_expected_no_match])
    assert out.get("defined") == True, (  # noqa: E712
        f"HIGH_IMPACT_PATTERN constant is not defined in rake_tasks/bazel.rake: {out}"
    )
    expected = {p: False for p in paths_expected_no_match}
    assert out["results"] == expected, (
        f"HIGH_IMPACT_PATTERN must not match these paths.\n"
        f"expected: {expected}\nactual:   {out['results']}"
    )


def test_high_impact_dirs_constant_value():
    """HIGH_IMPACT_DIRS must contain the four documented entries — and must
    NOT contain plain 'rust' (only 'rust/src' is high-impact)."""
    out = _run_driver(["high_impact_dirs"])
    assert out.get("defined") is True, f"HIGH_IMPACT_DIRS constant missing: {out}"
    dirs = out["dirs"]
    assert isinstance(dirs, list)
    assert "common" in dirs, f"missing 'common' in HIGH_IMPACT_DIRS: {dirs}"
    assert "rust/src" in dirs, f"missing 'rust/src' in HIGH_IMPACT_DIRS: {dirs}"
    assert "javascript/atoms" in dirs, f"missing 'javascript/atoms' in HIGH_IMPACT_DIRS: {dirs}"
    assert "javascript/webdriver/atoms" in dirs, (
        f"missing 'javascript/webdriver/atoms' in HIGH_IMPACT_DIRS: {dirs}"
    )
    assert "rust" not in dirs, (
        f"'rust' alone must NOT be high-impact (only rust/src is): {dirs}"
    )


def test_index_lookup_uses_filepath_keys(tmp_path: Path):
    """affected_targets_with_index must look up tests by FULL relative
    file path, not by Bazel package — so an index keyed by file paths
    yields the mapped tests directly."""
    index = {
        "py/some_source.py": ["//py:test_a", "//py:test_b"],
        "rb/lib/foo.rb": ["//rb:tests"],
    }
    idx_path = tmp_path / "file_index.json"
    idx_path.write_text(json.dumps(index))

    out = _run_driver(
        ["lookup", str(idx_path), "py/some_source.py"],
        responses={},
    )
    affected = out.get("affected", [])
    assert "//py:test_a" in affected, (
        f"file-level lookup of 'py/some_source.py' should return its mapped "
        f"tests, got: {affected}"
    )
    assert "//py:test_b" in affected, f"missing //py:test_b: {affected}"


def test_index_lookup_with_multiple_files(tmp_path: Path):
    """Each changed file should contribute its mapped tests to the
    affected set; tests from different files must union (not replace)."""
    index = {
        "py/file_a.py": ["//py:test_a"],
        "rb/file_b.rb": ["//rb:test_b"],
    }
    idx_path = tmp_path / "multi.json"
    idx_path.write_text(json.dumps(index))

    out = _run_driver(
        ["lookup", str(idx_path), "py/file_a.py", "rb/file_b.rb"],
        responses={},
    )
    affected = set(out.get("affected", []))
    assert "//py:test_a" in affected, (
        f"missing //py:test_a from union of file-level lookups: {affected}"
    )
    assert "//rb:test_b" in affected, (
        f"missing //rb:test_b from union of file-level lookups: {affected}"
    )


def test_build_test_index_emits_filepath_keys(tmp_path: Path):
    """`bazel:build_test_index` must produce an index whose keys are
    relative source-file paths (containing '/'), not bare Bazel package
    names. We drive the indexing by mocking the underlying Bazel
    queries — and respond with the same mocked source list to whichever
    query syntax the implementation chooses (so the test isn't coupled
    to one particular Bazel-query style)."""
    sources = "//py:source.py\n//py:other.py\n"
    responses = {
        # Initial test enumeration must come first so it isn't masked
        # by the broader src-returning patterns below.
        r"^kind\(_test": "//py:foo_test\n",
        # Deps of each test (matches `deps(test)` and the more
        # qualified `deps(test) intersect //... except ...` form).
        r"^deps\(": "//py:lib\n",
        # Per-dep source enumeration: any of the canonical Bazel
        # query verbs that resolve to "the source files of this target"
        # are accepted.
        r"^labels\(srcs": sources,
        r"^attr\(srcs": sources,
        r"^kind\(.*source.*deps": sources,
    }
    out_file = tmp_path / "built.json"
    out = _run_driver(
        ["build_index", str(out_file)],
        responses=responses,
    )
    index = out["index"]
    keys = list(index.keys())
    assert keys, f"index is empty: {out}"

    # Every key must be a file path (contain '/'), not a bare package name.
    bare_pkg_keys = [k for k in keys if "/" not in k]
    assert not bare_pkg_keys, (
        f"index has bare-package keys (file-level indexing not used): "
        f"{bare_pkg_keys}; full index: {index}"
    )
    # The mocked source files must appear as keys in the generated index.
    assert "py/source.py" in index, (
        f"expected 'py/source.py' as a key in the built file-level index, "
        f"got keys: {keys}"
    )
    assert "py/other.py" in index, (
        f"expected 'py/other.py' as a key in the built file-level index, "
        f"got keys: {keys}"
    )


# ─────────────────────── p2p: repo-shape sanity tests ─────────────────────


def test_rake_file_ruby_syntax_valid():
    """The rake file must parse as valid Ruby (no agent-introduced
    syntax errors)."""
    r = subprocess.run(
        ["ruby", "-c", RAKE_FILE],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert r.returncode == 0, (
        f"ruby -c failed on {RAKE_FILE}:\n"
        f"stdout: {r.stdout}\nstderr: {r.stderr}"
    )


def test_rake_file_loads_with_stubbed_bazel():
    """The rake file must load successfully under the test driver, with
    `Bazel.execute` stubbed (so the namespace declaration / requires /
    constant references all resolve)."""
    out = _run_driver(["high_impact_dirs"])
    assert "error" not in out, f"loading rake file raised: {out['error']}"
