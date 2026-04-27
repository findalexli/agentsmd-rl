"""Behavioral tests for the `uv cache clear` alias task.

Each `def test_*` maps 1:1 to a check in eval_manifest.yaml.
"""
import os
import subprocess
import tempfile
from pathlib import Path

REPO = "/workspace/uv"
UV = f"{REPO}/target/debug/uv"


def _run_uv(*args, timeout=60, cache_dir=None):
    env = os.environ.copy()
    if cache_dir is not None:
        env["UV_CACHE_DIR"] = cache_dir
    return subprocess.run(
        [UV, *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=REPO,
        env=env,
    )


# -------------------- fail_to_pass --------------------

def test_uv_binary_exists():
    """Sanity check that the uv binary was rebuilt."""
    assert os.path.isfile(UV), f"uv binary not found at {UV}"
    assert os.access(UV, os.X_OK), f"uv binary at {UV} is not executable"


def test_cache_clear_help_succeeds():
    """`uv cache clear --help` must exit 0 once the alias is registered.

    Without the alias, clap rejects `clear` as an unknown subcommand and
    exits with a non-zero status (typically 2).
    """
    r = _run_uv("cache", "clear", "--help")
    assert r.returncode == 0, (
        f"`uv cache clear --help` exited {r.returncode}\n"
        f"stderr: {r.stderr[:600]}\nstdout: {r.stdout[:300]}"
    )


def test_cache_clear_runs_on_empty_cache():
    """`uv cache clear` should run successfully (alias of `clean`)."""
    with tempfile.TemporaryDirectory() as tmp:
        cache = os.path.join(tmp, "uv-cache")
        os.makedirs(cache)
        r = _run_uv("cache", "clear", "--cache-dir", cache)
        assert r.returncode == 0, (
            f"`uv cache clear` exited {r.returncode}\n"
            f"stderr: {r.stderr[:600]}"
        )


def test_cache_clear_actually_clears():
    """Populate the cache with a sentinel file, then `cache clear` must
    remove the cache directory contents (proving `clear` is wired to the
    same handler as `clean`, not silently no-op'd)."""
    with tempfile.TemporaryDirectory() as tmp:
        cache = os.path.join(tmp, "uv-cache")
        os.makedirs(cache)
        sentinel = os.path.join(cache, "marker.txt")
        Path(sentinel).write_text("hello")
        assert os.path.isfile(sentinel)

        r = _run_uv("cache", "clear", "--cache-dir", cache)
        assert r.returncode == 0, f"clear failed: {r.stderr[:600]}"

        # uv removes the cache dir entirely; tolerate both "dir gone" and
        # "dir present but empty".
        if os.path.isdir(cache):
            assert os.listdir(cache) == [], (
                f"cache dir not cleared: {os.listdir(cache)}"
            )


def test_cache_clear_matches_clean_help():
    """The `clear` alias must surface the SAME help as `clean` (i.e. it
    is genuinely an alias of the same subcommand, not a separate sibling).
    """
    clean = _run_uv("cache", "clean", "--help")
    clear = _run_uv("cache", "clear", "--help")
    assert clean.returncode == 0, f"clean --help failed: {clean.stderr[:300]}"
    assert clear.returncode == 0, f"clear --help failed: {clear.stderr[:300]}"

    def _strip_invocation(text):
        # The "Usage:" line will mention `clean` vs `clear` — drop it so
        # the rest of the help can be compared verbatim.
        return "\n".join(
            line for line in text.splitlines()
            if not line.lstrip().lower().startswith("usage:")
        ).strip()

    assert _strip_invocation(clean.stdout) == _strip_invocation(clear.stdout), (
        "`clear --help` and `clean --help` differ beyond the Usage line — "
        "`clear` is not a true alias of `clean`."
    )


# -------------------- pass_to_pass --------------------

def test_uv_help_runs():
    """Top-level `uv --help` must work (regression guard)."""
    r = _run_uv("--help")
    assert r.returncode == 0, f"`uv --help` failed: {r.stderr[:400]}"
    assert "cache" in r.stdout.lower()


def test_uv_cache_clean_still_works():
    """`uv cache clean` must continue to work — the alias addition must
    not break the original subcommand name."""
    with tempfile.TemporaryDirectory() as tmp:
        cache = os.path.join(tmp, "uv-cache")
        os.makedirs(cache)
        r = _run_uv("cache", "clean", "--cache-dir", cache)
        assert r.returncode == 0, (
            f"`uv cache clean` regressed: {r.stderr[:600]}"
        )


def test_cargo_check_uv_cli():
    """The `uv-cli` crate must compile (compilation pass_to_pass)."""
    r = subprocess.run(
        ["cargo", "check", "-p", "uv-cli", "-j", "4"],
        capture_output=True, text=True, timeout=900, cwd=REPO,
    )
    assert r.returncode == 0, f"cargo check failed:\n{r.stderr[-1500:]}"
